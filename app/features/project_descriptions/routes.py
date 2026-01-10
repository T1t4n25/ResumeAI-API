"""Project Descriptions Feature - API Routes"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.project_descriptions.models import ProjectDescriptionRequest, ProjectDescriptionResponse
from app.features.project_descriptions.service import project_description_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/project-descriptions", tags=["Content Generation"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/generate",
    response_model=ProjectDescriptionResponse,
    summary="Generate project description",
    description="Generate a professional project description for your CV/resume"
)
@limiter.limit("5/minute")
async def generate_project_description(
    request: Request,
    data: ProjectDescriptionRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ProjectDescriptionResponse:
    """
    Generate a professional project description for CV.
    
    Requires Keycloak JWT token in Authorization header.
    """
    return project_description_service.generate_description(data)
