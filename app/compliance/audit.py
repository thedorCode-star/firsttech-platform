"""
Audit Logging Utilities - POPIA Compliance
Helper functions for logging audit events
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog, AuditAction
from app.core.config import settings
import structlog

logger = structlog.get_logger()


async def log_audit_event(
    db: AsyncSession,
    user_id: int | None,
    action: AuditAction,
    resource_type: str,
    resource_id: int | None = None,
    description: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
):
    """
    Log an audit event to the database
    Used throughout the application for POPIA compliance
    """
    try:
        # Get user email if user_id provided
        user_email = None
        if user_id:
            result = await db.execute(
                "SELECT email FROM users WHERE id = :user_id",
                {"user_id": user_id}
            )
            user = result.fetchone()
            if user:
                user_email = user.email
        
        audit_log = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            cloud_provider=settings.CLOUD_PROVIDER,
            region=settings.REGION,
        )
        
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        logger.error("Failed to log audit event", error=str(e), action=action.value)
        await db.rollback()

