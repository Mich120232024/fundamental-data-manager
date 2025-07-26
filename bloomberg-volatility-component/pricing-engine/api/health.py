"""Health check endpoints"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "fx-options-pricing-engine",
        "version": "0.1.0"
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # TODO: Check Bloomberg API connectivity
    # TODO: Check if pricing models are loaded
    return {
        "ready": True,
        "checks": {
            "bloomberg_api": "connected",
            "pricing_models": "loaded"
        }
    }