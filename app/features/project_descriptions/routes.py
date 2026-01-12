"""Project Descriptions Feature - API Routes (RESTful)"""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.project_descriptions.models import (
    ProjectDescriptionCreate,
    ProjectDescriptionResponse,
    ProjectDescriptionListResponse,
    ProjectDescriptionRequest  # Backward compatibility
)
from app.features.project_descriptions.service import project_description_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/project-descriptions", tags=["Project Descriptions"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectDescriptionResponse,
    summary="Create project description",
    description="Generate a new professional project description for your CV/resume"
)
@limiter.limit("5/minute")
async def create_project_description(
    request: Request,
    data: ProjectDescriptionCreate,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ProjectDescriptionResponse:
    """
    Create a new project description.
    
    Requires Keycloak JWT token in Authorization header.
    """
    result = project_description_service.generate_description(data)
    # Generate ID (in real implementation, this would come from database)
    import uuid
    from datetime import datetime
    
    return ProjectDescriptionResponse(
        id=str(uuid.uuid4()),
        project_description=result.project_description,
        project_name=data.project_name,
        skills=data.skills,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.get(
    "/{id}",
    response_model=ProjectDescriptionResponse,
    summary="Get project description",
    description="Retrieve a specific project description by ID"
)
@limiter.limit("10/minute")
async def get_project_description(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ProjectDescriptionResponse:
    """
    Get a specific project description by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project description with id {id} not found"
    )


@router.get(
    "",
    response_model=ProjectDescriptionListResponse,
    summary="List project descriptions",
    description="List all project descriptions for the current user"
)
@limiter.limit("10/minute")
async def list_project_descriptions(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ProjectDescriptionListResponse:
    """
    List all project descriptions for the current user.
    
    NOTE: Currently returns empty list. Persistence layer needs to be implemented.
    """
    # TODO: Implement database query
    return ProjectDescriptionListResponse(
        data=[],
        total=0,
        limit=limit,
        offset=offset
    )


# ============================================================================
# DEPRECATED ENDPOINTS - Backward compatibility
# ============================================================================

@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectDescriptionResponse,
    summary="[DEPRECATED] Generate project description",
    description="⚠️ DEPRECATED: Use POST /project-descriptions instead. This endpoint will be removed in a future version.",
    deprecated=True
)
@limiter.limit("5/minute")
async def generate_project_description_deprecated(
    request: Request,
    data: ProjectDescriptionRequest,  # Using old name for compatibility
    user: Dict[str, Any] = Depends(get_current_user)
) -> ProjectDescriptionResponse:
    """
    [DEPRECATED] Generate a professional project description for CV.
    
    This endpoint is deprecated. Please use POST /project-descriptions instead.
    """
    # Convert old model to new model
    create_data = ProjectDescriptionCreate(**data.model_dump())
    return await create_project_description(request, create_data, user)
