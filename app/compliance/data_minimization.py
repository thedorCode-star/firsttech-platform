"""
Data Minimization - POPIA Compliance
Ensures only necessary data is collected and stored
"""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
import structlog

logger = structlog.get_logger()


async def purge_expired_data(db: AsyncSession):
    """
    Purge data that has exceeded retention period
    POPIA: Data should not be kept longer than necessary
    """
    retention_days = settings.DATA_RETENTION_DAYS
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    
    # Find users marked for deletion past retention period
    result = await db.execute(
        """
        SELECT id FROM users 
        WHERE data_retention_until IS NOT NULL 
        AND data_retention_until < :cutoff_date
        """,
        {"cutoff_date": cutoff_date}
    )
    users_to_delete = result.fetchall()
    
    deleted_count = 0
    for user in users_to_delete:
        # Delete user and all associated data (cascade)
        await db.execute(
            "DELETE FROM users WHERE id = :user_id",
            {"user_id": user.id}
        )
        deleted_count += 1
    
    await db.commit()
    
    if deleted_count > 0:
        logger.info(
            "Purged expired data",
            deleted_users=deleted_count,
            retention_days=retention_days,
        )
    
    return deleted_count


async def anonymize_old_audit_logs(db: AsyncSession):
    """
    Anonymize old audit logs (keep for compliance but remove PII)
    """
    # Keep audit logs but anonymize user_email after 1 year
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    
    await db.execute(
        """
        UPDATE audit_logs 
        SET user_email = CONCAT('user_', user_id, '@anonymized.local')
        WHERE timestamp < :one_year_ago 
        AND user_email IS NOT NULL
        AND user_email NOT LIKE '%@anonymized.local'
        """,
        {"one_year_ago": one_year_ago}
    )
    await db.commit()
    
    logger.info("Anonymized old audit logs")

