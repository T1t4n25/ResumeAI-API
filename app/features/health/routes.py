"""Health Feature - API Routes"""
from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Create router
router = APIRouter(tags=["Health"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint to verify API is running"
)
@limiter.limit("6/minute")
async def health_check(request: Request):
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.api_version,
        "environment": settings.environment
    }


@router.get(
    "/",
    summary="API information",
    description="Root endpoint with API version and available endpoints"
)
@limiter.limit("6/minute")
async def root(request: Request):
    """Root endpoint with API information"""
    return {
        "message": "Resume Flow API",
        "version": settings.api_version,
        "environment": settings.environment,
        "endpoints": {
            "auth": ["/auth/me", "/auth/refresh", "/auth/token-info"],
            "generation": [
                "/cover-letters/generate",
                "/project-descriptions/generate",
                "/summaries/generate",
                "/resumes/create"
            ],
            "interviews": ["/interviews/start-room", "/interviews/start-interviewer"],
            "public": ["/health", "/"],
            "docs": ["/docs", "/redoc", "/openapi.json"]
        }
    }
