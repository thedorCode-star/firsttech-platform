"""
Audit Log Model - POPIA Compliance Requirement
All data access and modifications must be logged
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AuditAction(str, enum.Enum):
    """Types of actions to audit"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"
    DATA_EXPORT = "data_export"  # POPIA: Right to data portability
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"


class AuditLog(Base):
    """
    Audit log for POPIA compliance
    Immutable record of all data access and modifications
    Retention: 7 years (2555 days)
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # Store email even if user deleted
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    
    # What
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # e.g., "user", "transaction"
    resource_id = Column(Integer, nullable=True, index=True)
    
    # Details
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # Store before/after values for updates
    metadata = Column(JSON, nullable=True)  # Additional context
    
    # When
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Where (POPIA: Data location)
    cloud_provider = Column(String(50), nullable=True)  # aws, azure, gcp
    region = Column(String(50), nullable=True)
    availability_zone = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type}, user={self.user_id})>"

