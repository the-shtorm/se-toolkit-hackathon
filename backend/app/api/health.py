from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
