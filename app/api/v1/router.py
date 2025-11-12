"""
API Router - Main API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, transactions, data_subject, compliance

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(data_subject.router, prefix="/data-subject", tags=["Data Subject Rights"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["POPIA Compliance"])

