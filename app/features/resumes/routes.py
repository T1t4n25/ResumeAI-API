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
    result = resume_service.create_resume(data, username=username)
    
    # Service now returns CreateResumeResponse with id and base64-encoded pdf_file
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
    "/{id}/pdf",
    summary="Download resume PDF",
    description="Download the PDF version of a specific resume"
)
@limiter.limit("10/minute")
async def download_resume_pdf(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Response:
    """
    Download the PDF version of a specific resume.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup and file serving
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resume PDF with id {id} not found"
    )


@router.get(
    "/{id}/latex",
    summary="Get resume LaTeX source",
    description="Retrieve the LaTeX source code of a specific resume"
)
@limiter.limit("10/minute")
async def get_resume_latex(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get the LaTeX source code of a specific resume.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Resume LaTeX source with id {id} not found"
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
    format: str | None = None,
    user: Dict[str, Any] = Depends(get_current_user)
) -> ResumeListResponse:
    """
    List all resumes for the current user.
    
    Query parameters:
    - limit: Maximum number of results (default: 10)
    - offset: Number of results to skip (default: 0)
    - format: Filter by output format (pdf, tex, both) - optional
    
    NOTE: Currently returns empty list. Persistence layer needs to be implemented.
    """
    # TODO: Implement database query with filtering
    return ResumeListResponse(
        data=[],
        total=0,
        limit=limit,
        offset=offset
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


# ============================================================================
# DEPRECATED ENDPOINTS - Backward compatibility
# ============================================================================

@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateResumeResponse,
    summary="[DEPRECATED] Create complete resume",
    description="⚠️ DEPRECATED: Use POST /resumes instead. This endpoint will be removed in a future version.",
    deprecated=True
)
@limiter.limit("5/minute")
async def create_resume_deprecated(
    request: Request,
    data: CreateResumeRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CreateResumeResponse:
    """
    [DEPRECATED] Generate a complete resume using LaTeX.
    
    This endpoint is deprecated. Please use POST /resumes instead.
    """
    return await create_resume(request, data, user)
