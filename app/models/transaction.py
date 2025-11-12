"""
Transaction Model - Financial Transaction Records
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TransactionType(str, enum.Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction(Base):
    """
    Financial transaction model
    POPIA: Financial records must be retained for 7 years (2555 days)
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction Details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)  # Decimal with 2 decimal places
    currency = Column(String(3), default="ZAR", nullable=False)  # South African Rand
    
    # Transaction Metadata
    reference = Column(String(100), unique=True, index=True, nullable=False)  # Unique transaction reference
    description = Column(Text, nullable=True)
    recipient_account = Column(String(50), nullable=True)  # For transfers/payments
    sender_account = Column(String(50), nullable=True)
    
    # POPIA: Minimal data - only necessary transaction data
    # No unnecessary personal information stored here
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount}, status={self.status})>"

