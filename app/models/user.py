"""
User Model - POPIA Compliant
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC (Role-Based Access Control)"""
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"  # POPIA: Can view audit logs but not modify data


class User(Base):
    """
    User model with POPIA compliance features:
    - Data minimization: Only essential fields
    - Encryption: Sensitive fields encrypted
    - Audit trail: All changes logged
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information (POPIA: minimal data collection)
    first_name = Column(String(100), nullable=True)  # Optional for data minimization
    last_name = Column(String(100), nullable=True)  # Optional for data minimization
    phone_number = Column(String(20), nullable=True)  # Encrypted in application layer
    
    # Authentication
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Email verification
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)  # TOTP secret (encrypted)
    
    # POPIA Compliance
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(DateTime, nullable=True)
    data_retention_until = Column(DateTime, nullable=True)  # When to delete data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

