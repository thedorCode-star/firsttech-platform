"""
Transaction Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.core.database import get_db
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.transaction import TransactionType, TransactionStatus
from app.compliance.audit import log_audit_event
from app.models.audit_log import AuditAction

router = APIRouter()


class TransactionCreate(BaseModel):
    """Create transaction request"""
    transaction_type: TransactionType
    amount: Decimal
    currency: str = "ZAR"
    description: Optional[str] = None
    recipient_account: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: int
    user_id: int
    transaction_type: str
    status: str
    amount: Decimal
    currency: str
    reference: str
    description: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new transaction
    POPIA: Only stores necessary transaction data
    """
    import uuid
    
    # Generate unique reference
    reference = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    # Create transaction
    result = await db.execute(
        """
        INSERT INTO transactions (user_id, transaction_type, status, amount, currency, 
                                 reference, description, recipient_account, created_at)
        VALUES (:user_id, :transaction_type, :status, :amount, :currency, :reference,
                :description, :recipient_account, NOW())
        RETURNING id, created_at
        """,
        {
            "user_id": current_user.id,
            "transaction_type": transaction_data.transaction_type.value,
            "status": TransactionStatus.PENDING.value,
            "amount": transaction_data.amount,
            "currency": transaction_data.currency,
            "reference": reference,
            "description": transaction_data.description,
            "recipient_account": transaction_data.recipient_account,
        }
    )
    transaction = result.fetchone()
    await db.commit()
    
    # Log creation
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        resource_type="transaction",
        resource_id=transaction.id,
        description=f"Created transaction {reference}",
        metadata={"amount": str(transaction_data.amount), "type": transaction_data.transaction_type.value},
    )
    
    return TransactionResponse(
        id=transaction.id,
        user_id=current_user.id,
        transaction_type=transaction_data.transaction_type.value,
        status=TransactionStatus.PENDING.value,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        reference=reference,
        description=transaction_data.description,
        created_at=transaction.created_at,
        completed_at=None,
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's transactions"""
    # Only return user's own transactions (unless admin)
    if current_user.role.value == "admin":
        result = await db.execute(
            """
            SELECT * FROM transactions
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
            """,
            {"limit": limit, "skip": skip}
        )
    else:
        result = await db.execute(
            """
            SELECT * FROM transactions
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
            """,
            {"user_id": current_user.id, "limit": limit, "skip": skip}
        )
    
    transactions = result.fetchall()
    
    # Log access
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="transaction",
        description=f"Listed transactions (limit={limit}, skip={skip})",
    )
    
    return [
        TransactionResponse(
            id=t.id,
            user_id=t.user_id,
            transaction_type=t.transaction_type,
            status=t.status,
            amount=t.amount,
            currency=t.currency,
            reference=t.reference,
            description=t.description,
            created_at=t.created_at,
            completed_at=t.completed_at,
        )
        for t in transactions
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transaction by ID"""
    result = await db.execute(
        "SELECT * FROM transactions WHERE id = :transaction_id",
        {"transaction_id": transaction_id}
    )
    transaction = result.fetchone()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    
    # Check access (user can only see own transactions, unless admin)
    if current_user.role.value != "admin" and transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )
    
    # Log access
    await log_audit_event(
        db=db,
        user_id=current_user.id,
        action=AuditAction.READ,
        resource_type="transaction",
        resource_id=transaction_id,
        description=f"Accessed transaction {transaction.reference}",
    )
    
    return TransactionResponse(
        id=transaction.id,
        user_id=transaction.user_id,
        transaction_type=transaction.transaction_type,
        status=transaction.status,
        amount=transaction.amount,
        currency=transaction.currency,
        reference=transaction.reference,
        description=transaction.description,
        created_at=transaction.created_at,
        completed_at=transaction.completed_at,
    )

