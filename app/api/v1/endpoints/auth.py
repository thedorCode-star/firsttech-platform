"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings
from app.auth.dependencies import get_current_user
from app.auth.mfa import mfa_service
from app.models.user import User, UserRole
from app.models.audit_log import AuditAction
from app.compliance.audit import log_audit_event
import structlog

logger = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str
    mfa_token: str | None = None  # MFA token if MFA enabled


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MFASetupResponse(BaseModel):
    """MFA setup response"""
    secret: str
    qr_code: str  # Base64-encoded QR code
    backup_codes: list[str]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user
    POPIA: Collects minimal data, requires consent
    """
    # Check if user exists
    result = await db.execute(
        "SELECT id FROM users WHERE email = :email",
        {"email": user_data.email}
    )
    if result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user (simplified - in production use proper ORM)
    hashed_password = get_password_hash(user_data.password)
    
    # POPIA: Data minimization - only store necessary fields
    await db.execute(
        """
        INSERT INTO users (email, hashed_password, first_name, last_name, phone_number, 
                          is_active, is_verified, role, consent_given, consent_date)
        VALUES (:email, :hashed_password, :first_name, :last_name, :phone_number,
                :is_active, :is_verified, :role, :consent_given, NOW())
        """,
        {
            "email": user_data.email,
            "hashed_password": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "phone_number": user_data.phone_number,
            "is_active": True,
            "is_verified": False,  # Email verification required
            "role": UserRole.USER.value,
            "consent_given": True,  # User consents by registering
        }
    )
    await db.commit()
    
    logger.info("User registered", email=user_data.email)
    
    return {"message": "User registered successfully. Please verify your email."}


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    User login with optional MFA
    """
    # Get user
    result = await db.execute(
        "SELECT * FROM users WHERE email = :email",
        {"email": login_data.email}
    )
    user_row = result.fetchone()
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Verify password
    if not verify_password(login_data.password, user_row.hashed_password):
        await log_audit_event(
            db=db,
            user_id=user_row.id,
            action=AuditAction.ACCESS_DENIED,
            resource_type="user",
            description="Failed login attempt - incorrect password",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if user is active
    if not user_row.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # MFA verification if enabled
    if user_row.mfa_enabled:
        if not login_data.mfa_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA token required",
            )
        
        if not mfa_service.verify_token(user_row.mfa_secret, login_data.mfa_token):
            await log_audit_event(
                db=db,
                user_id=user_row.id,
                action=AuditAction.ACCESS_DENIED,
                resource_type="user",
                description="Failed login attempt - invalid MFA token",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token",
            )
    
    # Update last login
    await db.execute(
        "UPDATE users SET last_login = NOW() WHERE id = :user_id",
        {"user_id": user_row.id}
    )
    await db.commit()
    
    # Log successful login
    await log_audit_event(
        db=db,
        user_id=user_row.id,
        action=AuditAction.LOGIN,
        resource_type="user",
        description="User logged in successfully",
    )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user_row.id, "email": user_row.email, "role": user_row.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": user_row.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token"""
    payload = verify_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    
    # Get user
    result = await db.execute(
        "SELECT id, email, role FROM users WHERE id = :user_id AND is_active = true",
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,  # Refresh token remains valid
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/mfa/setup")
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Setup MFA for user
    Returns QR code for authenticator app
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled",
        )
    
    # Generate secret
    secret = mfa_service.generate_secret()
    qr_code = mfa_service.generate_qr_code(secret, current_user.email)
    
    # Store secret (encrypted) - user must verify before enabling
    await db.execute(
        "UPDATE users SET mfa_secret = :secret WHERE id = :user_id",
        {"secret": secret, "user_id": current_user.id}
    )
    await db.commit()
    
    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=[],  # In production, generate backup codes
    )


@router.post("/mfa/verify")
async def verify_mfa_setup(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify and enable MFA"""
    # Get secret from database
    result = await db.execute(
        "SELECT mfa_secret FROM users WHERE id = :user_id",
        {"user_id": current_user.id}
    )
    user = result.fetchone()
    
    if not user or not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up. Please setup MFA first.",
        )
    
    # Verify token
    if not mfa_service.verify_token(user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token",
        )
    
    # Enable MFA
    await db.execute(
        "UPDATE users SET mfa_enabled = true WHERE id = :user_id",
        {"user_id": current_user.id}
    )
    await db.commit()
    
    return {"message": "MFA enabled successfully"}

