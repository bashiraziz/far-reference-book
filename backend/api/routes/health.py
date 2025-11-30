"""
Health check endpoint.
"""

from fastapi import APIRouter
from datetime import datetime
from backend.config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns basic service information and status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "FAR Reference Book API",
        "config": {
            "embedding_dimensions": settings.embedding_dimensions,
            "embedding_model": settings.embedding_model
        }
    }
