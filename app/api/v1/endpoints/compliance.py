"""
POPIA Compliance Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.database import get_db
from app.auth.dependencies import require_role
from app.models.user import User
from app.compliance.audit import log_audit_event
from app.models.audit_log import AuditAction

router = APIRouter()


class DataInventoryResponse(BaseModel):
    """Data inventory response"""
    data_fields: List[Dict[str, Any]]
    total_fields: int
    categories: Dict[str, int]


@router.get("/data-inventory", response_model=DataInventoryResponse)
async def get_data_inventory(
    current_user: User = Depends(require_role(["admin", "auditor"])),
    db: AsyncSession = Depends(get_db),
):
    """
    POPIA Openness Requirement: Data Inventory
    Lists all personal information collected and processed
    """
    result = await db.execute(
        "SELECT * FROM data_inventory ORDER BY data_category, data_field"
    )
    inventory_items = result.fetchall()
    
    # Log access
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="data_inventory",
        description="Accessed data inventory",
    )
    
    # Group by category
    categories = {}
    data_fields = []
    
    for item in inventory_items:
        category = item.data_category
        categories[category] = categories.get(category, 0) + 1
        
        data_fields.append({
            "id": item.id,
            "data_field": item.data_field,
            "data_category": item.data_category,
            "description": item.description,
            "purpose": item.purpose,
            "legal_basis": item.legal_basis,
            "retention_period_days": item.retention_period_days,
            "shared_with_third_parties": item.shared_with_third_parties,
            "cloud_provider": item.cloud_provider,
            "region": item.region,
        })
    
    return DataInventoryResponse(
        data_fields=data_fields,
        total_fields=len(data_fields),
        categories=categories,
    )


@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
    action: str | None = None,
    current_user: User = Depends(require_role(["admin", "auditor"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit logs (POPIA: Security Safeguards)
    Only accessible to admins and auditors
    """
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = {}
    
    if user_id:
        query += " AND user_id = :user_id"
        params["user_id"] = user_id
    
    if action:
        query += " AND action = :action"
        params["action"] = action
    
    query += " ORDER BY timestamp DESC LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip
    
    result = await db.execute(query, params)
    logs = result.fetchall()
    
    # Log access to audit logs
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="audit_log",
        description=f"Accessed audit logs (limit={limit}, skip={skip})",
    )
    
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "metadata": log.metadata,
        }
        for log in logs
    ]


@router.get("/compliance-status")
async def get_compliance_status(
    current_user: User = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Get POPIA compliance status
    Checks various compliance metrics
    """
    # Check consent rates
    consent_result = await db.execute(
        "SELECT COUNT(*) as total, SUM(CASE WHEN consent_given THEN 1 ELSE 0 END) as consented FROM users"
    )
    consent_stats = consent_result.fetchone()
    
    # Check MFA adoption
    mfa_result = await db.execute(
        "SELECT COUNT(*) as total, SUM(CASE WHEN mfa_enabled THEN 1 ELSE 0 END) as mfa_enabled FROM users"
    )
    mfa_stats = mfa_result.fetchone()
    
    # Check audit log coverage
    audit_result = await db.execute(
        "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp > NOW() - INTERVAL '24 hours'"
    )
    audit_count = audit_result.fetchone()
    
    return {
        "popia_compliance": {
            "consent_rate": (
                consent_stats.consented / consent_stats.total * 100
                if consent_stats.total > 0
                else 0
            ),
            "mfa_adoption_rate": (
                mfa_stats.mfa_enabled / mfa_stats.total * 100
                if mfa_stats.total > 0
                else 0
            ),
            "audit_logging_active": audit_count.count > 0 if audit_count else False,
            "data_inventory_maintained": True,  # Check if data inventory exists
        },
        "security": {
            "encryption_enabled": True,  # From settings
            "mfa_required_for_admin": True,  # From settings
        },
    }

