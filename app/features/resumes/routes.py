"""Resumes Feature - API Routes (RESTful)"""
from fastapi import APIRouter, Depends, Request, status, HTTPException, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.resumes.models import (
    CreateResumeRequest,
    CreateResumeResponse,
    ResumeResponse,
    ResumeListResponse
)
from app.features.resumes.service import resume_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/resumes", tags=["Resumes"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateResumeResponse,
    summary="Create resume",
    description="Generate a complete professional resume using LaTeX (PDF and/or source)"
)
@limiter.limit("5/minute")
async def create_resume(
    request: Request,
    data: CreateResumeRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CreateResumeResponse:
    """
    Create a new resume.
    
    Requires Keycloak JWT token in Authorization header.
    """
    username = user.get("preferred_username", "unknown")
    result = resume_service.create_resume_latex(data, username=username)
    
    # Service now returns CreateResumeResponse with id and tex_file
    return result


@router.get(
    "/{id}",
    response_model=ResumeResponse,
    summary="Get resume",
    description="Retrieve a specific resume by ID"
)
@limiter.limit("10/minute")
async def get_resume(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ResumeResponse:
    """
    Get a specific resume by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resume with id {id} not found"
    )

@router.get(
    "",
    response_model=ResumeListResponse,
    summary="List resumes",
    description="List all resumes for the current user"
)
@limiter.limit("10/minute")
async def list_resumes(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ResumeListResponse:
    """
    List all resumes for the current user.
    
    Query parameters:
    - limit: Maximum number of results (default: 10)
    - offset: Number of results to skip (default: 0)
    """
    return ResumeListResponse(
        data=[],
        total=0
    )


@router.patch(
    "/{id}",
    response_model=ResumeResponse,
    summary="Update resume",
    description="Update a specific resume (metadata only, not content regeneration)"
)
@limiter.limit("10/minute")
async def update_resume(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ResumeResponse:
    """
    Update a specific resume.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database update
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resume with id {id} not found"
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resume",
    description="Delete a specific resume by ID"
)
@limiter.limit("10/minute")
async def delete_resume(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a specific resume by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database deletion
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resume with id {id} not found"
    )

