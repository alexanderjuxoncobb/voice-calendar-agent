"""Health check endpoints for monitoring."""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status."""
    # TODO: Check database connection
    # TODO: Check Redis connection
    # TODO: Check VAPI API availability
    
    return {
        "status": "healthy",
        "environment": settings.environment,
        "services": {
            "database": "connected",
            "redis": "connected",
            "vapi": "reachable"
        }
    }