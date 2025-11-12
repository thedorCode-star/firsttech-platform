"""
Data Inventory Model - POPIA Compliance Requirement (Openness)
Catalog of all personal information processed
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DataCategory(str, enum.Enum):
    """Categories of personal information"""
    IDENTIFIERS = "identifiers"  # Name, ID number, email
    FINANCIAL = "financial"  # Bank accounts, transactions
    CONTACT = "contact"  # Address, phone
    BEHAVIORAL = "behavioral"  # Usage patterns, preferences
    SENSITIVE = "sensitive"  # Special category data


class DataInventory(Base):
    """
    Data inventory for POPIA compliance (Openness requirement)
    Documents what personal information is collected, why, and where
    """
    __tablename__ = "data_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # What data
    data_field = Column(String(200), nullable=False, index=True)  # e.g., "email", "phone_number"
    data_category = Column(SQLEnum(DataCategory), nullable=False, index=True)
    description = Column(Text, nullable=True)  # What this field is used for
    
    # Where stored
    table_name = Column(String(100), nullable=False)  # Database table
    column_name = Column(String(100), nullable=False)  # Database column
    
    # Why collected (POPIA: Purpose specification)
    purpose = Column(Text, nullable=False)  # Why this data is collected
    legal_basis = Column(String(100), nullable=True)  # Legal basis for processing
    
    # Data location (POPIA: Openness)
    cloud_provider = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True)
    availability_zone = Column(String(50), nullable=True)
    
    # Retention
    retention_period_days = Column(Integer, nullable=True)  # How long data is kept
    retention_reason = Column(Text, nullable=True)  # Why this retention period
    
    # Sharing
    shared_with_third_parties = Column(String(10), default="no", nullable=False)  # yes/no
    third_parties = Column(JSON, nullable=True)  # List of third parties if shared
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DataInventory(id={self.id}, field={self.data_field}, category={self.data_category})>"

