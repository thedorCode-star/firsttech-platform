"""
User Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.auth.dependencies import get_current_active_user, require_role
from app.models.user import User, UserRole
from app.compliance.audit import log_audit_event
from app.models.audit_log import AuditAction

router = APIRouter()


class UserResponse(BaseModel):
    """User response model"""
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    role: str
    is_active: bool
    mfa_enabled: bool
    created_at: str


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information"""
    # Log access (POPIA: audit all data access)
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="user",
        resource_id=current_user.id,
        description="User accessed own profile",
    )
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        mfa_enabled=current_user.mfa_enabled,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(require_role(["admin", "auditor"])),
    db: AsyncSession = Depends(get_db),
):
    """Get user by ID (admin/auditor only)"""
    result = await db.execute(
        "SELECT * FROM users WHERE id = :user_id",
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Log access
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="user",
        resource_id=user_id,
        description=f"Admin accessed user {user_id}",
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

