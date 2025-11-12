"""
Security Utilities: Encryption, Hashing, Token Management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("Token verification failed", error=str(e))
        return None


class EncryptionService:
    """Service for encrypting/decrypting sensitive data (POPIA requirement)"""
    
    def __init__(self):
        if not settings.ENCRYPTION_KEY:
            logger.warning("ENCRYPTION_KEY not set, encryption disabled")
            self.fernet = None
        else:
            # Derive Fernet key from encryption key
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fintech_salt_2024',  # In production, use unique salt per record
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY.encode()))
            self.fernet = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data"""
        if not self.fernet or not settings.USE_ENCRYPTION:
            return plaintext  # Return as-is if encryption disabled
        try:
            encrypted = self.fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error("Encryption failed", error=str(e))
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt sensitive data"""
        if not self.fernet or not settings.USE_ENCRYPTION:
            return ciphertext  # Return as-is if encryption disabled
        try:
            decoded = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error("Decryption failed", error=str(e))
            raise


# Global encryption service instance
encryption_service = EncryptionService()

