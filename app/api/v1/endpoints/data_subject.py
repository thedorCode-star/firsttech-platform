"""
Data Subject Rights Endpoints - POPIA Compliance
Implements data subject rights: access, correction, deletion, portability
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from app.core.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.compliance.audit import log_audit_event
from app.models.audit_log import AuditAction
import json

router = APIRouter()


class DataAccessResponse(BaseModel):
    """Response for data access request"""
    user_data: Dict[str, Any]
    transactions: list[Dict[str, Any]]
    consents: list[Dict[str, Any]]
    audit_logs: list[Dict[str, Any]]
    exported_at: datetime


@router.get("/access", response_model=DataAccessResponse)
async def access_personal_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Section 23: Right to Access
    Data subject can request access to their personal information
    """
    # Collect all user data
    user_result = await db.execute(
        "SELECT * FROM users WHERE id = :user_id",
        {"user_id": current_user.id}
    )
    user = user_result.fetchone()
    
    # Get transactions
    transactions_result = await db.execute(
        "SELECT * FROM transactions WHERE user_id = :user_id ORDER BY created_at DESC",
        {"user_id": current_user.id}
    )
    transactions = transactions_result.fetchall()
    
    # Get consents
    consents_result = await db.execute(
        "SELECT * FROM consents WHERE user_id = :user_id ORDER BY created_at DESC",
        {"user_id": current_user.id}
    )
    consents = consents_result.fetchall()
    
    # Get audit logs (user's own access)
    audit_result = await db.execute(
        """
        SELECT * FROM audit_logs 
        WHERE user_id = :user_id 
        ORDER BY timestamp DESC 
        LIMIT 100
        """,
        {"user_id": current_user.id}
    )
    audit_logs = audit_result.fetchall()
    
    # Log data access (POPIA: audit all data access)
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DATA_EXPORT,
        resource_type="data_subject",
        description="Data subject accessed personal information",
    )
    
    return DataAccessResponse(
        user_data={
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
            "mfa_enabled": user.mfa_enabled,
            "consent_given": user.consent_given,
            "consent_date": user.consent_date.isoformat() if user.consent_date else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        transactions=[
            {
                "id": t.id,
                "transaction_type": t.transaction_type,
                "status": t.status,
                "amount": str(t.amount),
                "currency": t.currency,
                "reference": t.reference,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
        consents=[
            {
                "id": c.id,
                "purpose": c.purpose,
                "consent_given": c.consent_given,
                "given_at": c.given_at.isoformat() if c.given_at else None,
                "withdrawn_at": c.withdrawn_at.isoformat() if c.withdrawn_at else None,
            }
            for c in consents
        ],
        audit_logs=[
            {
                "id": a.id,
                "action": a.action,
                "resource_type": a.resource_type,
                "description": a.description,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in audit_logs
        ],
        exported_at=datetime.utcnow(),
    )


class DataCorrectionRequest(BaseModel):
    """Request to correct personal data"""
    field: str  # e.g., "first_name", "last_name", "phone_number"
    new_value: str


@router.put("/correct")
async def correct_personal_data(
    correction: DataCorrectionRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Section 24: Right to Correction
    Data subject can request correction of inaccurate personal information
    """
    allowed_fields = ["first_name", "last_name", "phone_number"]
    
    if correction.field not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field '{correction.field}' cannot be corrected via this endpoint",
        )
    
    # Update field
    await db.execute(
        f"UPDATE users SET {correction.field} = :value, updated_at = NOW() WHERE id = :user_id",
        {"value": correction.new_value, "user_id": current_user.id}
    )
    await db.commit()
    
    # Log correction
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        resource_type="user",
        resource_id=current_user.id,
        description=f"Data subject corrected field: {correction.field}",
        metadata={"field": correction.field, "old_value": "***", "new_value": "***"},
    )
    
    return {"message": f"Field '{correction.field}' updated successfully"}


@router.delete("/delete")
async def delete_personal_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Section 25: Right to Deletion
    Data subject can request deletion of personal information
    Note: Financial records may need to be retained for legal compliance
    """
    # Check if user has active transactions (may need retention)
    result = await db.execute(
        "SELECT COUNT(*) as count FROM transactions WHERE user_id = :user_id",
        {"user_id": current_user.id}
    )
    count = result.fetchone()
    
    if count and count.count > 0:
        # Soft delete: Mark for deletion but retain for legal compliance
        await db.execute(
            """
            UPDATE users 
            SET is_active = false, 
                data_retention_until = NOW() + INTERVAL '7 years',
                updated_at = NOW()
            WHERE id = :user_id
            """,
            {"user_id": current_user.id}
        )
        await db.commit()
        
        # Log deletion request
        await log_audit_event(
            db=db,
            user_id=current_user.id,
            action=AuditAction.DELETE,
            resource_type="user",
            resource_id=current_user.id,
            description="Data subject requested deletion (soft delete - retained for compliance)",
        )
        
        return {
            "message": "Account marked for deletion. Data will be retained for 7 years for legal compliance, then permanently deleted.",
            "deletion_date": None,  # Will be calculated
        }
    else:
        # Hard delete if no transactions
        await db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": current_user.id})
        await db.commit()
        
        return {"message": "Account and all personal data deleted successfully"}


@router.get("/export")
async def export_personal_data(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA: Right to Data Portability
    Export personal data in machine-readable format (JSON)
    """
    # Get all data (same as access endpoint)
    access_data = await access_personal_data(current_user, db)
    
    # Convert to JSON
    export_data = {
        "user_data": access_data.user_data,
        "transactions": access_data.transactions,
        "consents": access_data.consents,
        "exported_at": access_data.exported_at.isoformat(),
        "format": "JSON",
        "version": "1.0",
    }
    
    # Log export
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DATA_EXPORT,
        resource_type="data_subject",
        description="Data subject exported personal information",
    )
    
    return export_data

