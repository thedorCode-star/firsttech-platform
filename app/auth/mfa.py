"""
Multi-Factor Authentication (MFA) Implementation
TOTP-based MFA for enhanced security (POPIA requirement)
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class MFAService:
    """Service for MFA operations"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret for a user"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, email: str) -> str:
        """
        Generate QR code for MFA setup
        Returns base64-encoded PNG image
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=settings.MFA_ISSUER_NAME,
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Return base64-encoded image
        return base64.b64encode(buffer.read()).decode()
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify a TOTP token
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 1 time step tolerance
    
    @staticmethod
    def get_current_token(secret: str) -> str:
        """Get current TOTP token (for testing)"""
        totp = pyotp.TOTP(secret)
        return totp.now()


mfa_service = MFAService()

