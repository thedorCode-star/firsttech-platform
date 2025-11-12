"""
Consent Model - POPIA Compliance Requirement
Track user consent for data processing
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ConsentPurpose(str, enum.Enum):
    """Purposes for which consent is given"""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"
    DATA_PROCESSING = "data_processing"  # General processing consent


class Consent(Base):
    """
    Consent management for POPIA compliance
    Tracks when, why, and how consent was given/withdrawn
    """
    __tablename__ = "consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Consent Details
    purpose = Column(SQLEnum(ConsentPurpose), nullable=False, index=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    
    # POPIA: Explicit consent
    consent_method = Column(String(50), nullable=True)  # "email", "web_form", "api", etc.
    consent_text = Column(Text, nullable=True)  # What the user consented to
    
    # Timestamps
    given_at = Column(DateTime(timezone=True), nullable=True)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="consents")
    
    def __repr__(self):
        return f"<Consent(id={self.id}, user={self.user_id}, purpose={self.purpose}, given={self.consent_given})>"

