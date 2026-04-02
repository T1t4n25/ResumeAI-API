"""Health Feature - API Routes"""
from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.limiter import limiter

# Create router
router = APIRouter(tags=["Health"])


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
            "auth": {
                "GET /auth/me": "Get current user information",
                "POST /auth/refresh": "Refresh access token",
                "GET /auth/tokens/info": "Get token information"
            },
            "cover_letters": {
                "POST /cover-letters": "Create a new cover letter",
                "GET /cover-letters": "List all cover letters",
                "GET /cover-letters/:id": "Get specific cover letter",
                "DELETE /cover-letters/:id": "Delete cover letter"
            },
            "project_descriptions": {
                "POST /project-descriptions": "Create a new project description",
                "GET /project-descriptions": "List all project descriptions",
                "GET /project-descriptions/:id": "Get specific project description"
            },
            "summaries": {
                "POST /summaries": "Create a new professional summary",
                "GET /summaries": "List all summaries",
                "GET /summaries/:id": "Get specific summary"
            },
            "interviews": {
                "POST /interviews/rooms": "Create interview room",
                "GET /interviews/rooms": "List all interview rooms",
                "GET /interviews/rooms/:id": "Get specific interview room",
                "POST /interviews/rooms/:id/start": "Start AI interviewer",
                "DELETE /interviews/rooms/:id": "End interview session"
            },
            "public": {
                "GET /health": "Health check",
                "GET /": "API information"
            },
            "docs": {
                "GET /docs": "Interactive API documentation (Swagger UI)",
                "GET /redoc": "Alternative API documentation (ReDoc)",
                "GET /openapi.json": "OpenAPI schema"
            }
        },
        "architecture": {
            "style": "RESTful",
            "authentication": "Keycloak JWT (Bearer token)",
            "response_format": "JSON",
            "status_codes": {
                "200": "OK (successful GET, PATCH)",
                "201": "Created (successful POST)",
                "204": "No Content (successful DELETE)",
                "400": "Bad Request (invalid input)",
                "401": "Unauthorized (missing/invalid auth)",
                "403": "Forbidden (insufficient permissions)",
                "404": "Not Found (resource doesn't exist)",
                "429": "Too Many Requests (rate limit exceeded)",
                "500": "Internal Server Error"
            }
        }
    }
