"""
Audit Logging Middleware - POPIA Compliance
Logs all API requests for compliance and security
"""
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog
from datetime import datetime
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.audit_log import AuditLog, AuditAction
import json

logger = structlog.get_logger()


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for POPIA compliance
    Creates immutable audit trail of all data access
    """
    
    # Endpoints to exclude from audit logging (health checks, etc.)
    EXCLUDED_PATHS = [
        "/health",
        "/health/ready",
        "/health/live",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
    ]
    
    # Read-only actions (GET, HEAD, OPTIONS)
    READ_ACTIONS = {"GET", "HEAD", "OPTIONS"}
    
    # Write actions
    WRITE_ACTIONS = {
        "POST": AuditAction.CREATE,
        "PUT": AuditAction.UPDATE,
        "PATCH": AuditAction.UPDATE,
        "DELETE": AuditAction.DELETE,
    }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and log audit trail"""
        
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)
        
        # Skip if audit logging disabled
        if not settings.ENABLE_AUDIT_LOGGING:
            return await call_next(request)
        
        # Extract user information
        user_id = None
        user_email = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("id")
            user_email = request.state.user.get("email")
        
        # Determine action type
        action = self._determine_action(request.method, request.url.path)
        
        # Extract resource information from path
        resource_type, resource_id = self._extract_resource_info(request.url.path)
        
        # Get client information
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # Read request body if available (for POST/PUT)
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = body.decode("utf-8")[:1000]  # Limit size
            except Exception:
                pass
        
        # Process request
        start_time = datetime.utcnow()
        response = await call_next(request)
        end_time = datetime.utcnow()
        
        # Log to database asynchronously (don't block response)
        try:
            await self._log_audit_event(
                user_id=user_id,
                user_email=user_email,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=client_ip,
                user_agent=user_agent,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                metadata={
                    "request_body_preview": request_body,
                    "response_time_ms": (end_time - start_time).total_seconds() * 1000,
                    "query_params": str(request.query_params),
                }
            )
        except Exception as e:
            # Don't fail the request if audit logging fails
            logger.error("Audit logging failed", error=str(e), path=request.url.path)
        
        return response
    
    def _determine_action(self, method: str, path: str) -> AuditAction:
        """Determine audit action from HTTP method and path"""
        if method in self.READ_ACTIONS:
            return AuditAction.READ
        elif method in self.WRITE_ACTIONS:
            return self.WRITE_ACTIONS[method]
        elif "login" in path.lower():
            return AuditAction.LOGIN
        elif "logout" in path.lower():
            return AuditAction.LOGOUT
        else:
            return AuditAction.READ
    
    def _extract_resource_info(self, path: str) -> tuple[str, int | None]:
        """Extract resource type and ID from URL path"""
        # Example: /api/v1/users/123 -> ("user", 123)
        parts = path.strip("/").split("/")
        resource_type = None
        resource_id = None
        
        # Look for common patterns
        if "users" in parts:
            resource_type = "user"
            idx = parts.index("users")
            if idx + 1 < len(parts) and parts[idx + 1].isdigit():
                resource_id = int(parts[idx + 1])
        elif "transactions" in parts:
            resource_type = "transaction"
            idx = parts.index("transactions")
            if idx + 1 < len(parts) and parts[idx + 1].isdigit():
                resource_id = int(parts[idx + 1])
        elif "data-subject" in parts:
            resource_type = "data_subject"
        
        return resource_type or "unknown", resource_id
    
    async def _log_audit_event(
        self,
        user_id: int | None,
        user_email: str | None,
        action: AuditAction,
        resource_type: str,
        resource_id: int | None,
        ip_address: str | None,
        user_agent: str,
        path: str,
        method: str,
        status_code: int,
        metadata: dict,
    ):
        """Log audit event to database"""
        async with AsyncSessionLocal() as session:
            audit_log = AuditLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent[:500],  # Limit length
                description=f"{method} {path} - Status: {status_code}",
                metadata=metadata,
                cloud_provider=settings.CLOUD_PROVIDER,
                region=settings.REGION,
                # Availability zone would be determined at runtime
            )
            session.add(audit_log)
            await session.commit()

