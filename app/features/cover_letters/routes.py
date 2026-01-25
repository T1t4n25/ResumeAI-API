"""Cover Letters Feature - API Routes (RESTful)"""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any, List
import uuid
from datetime import datetime
from app.features.cover_letters.models import (
    CoverLetterCreate,
    CoverLetterResponse,
    CoverLetterListResponse,
)
from app.features.cover_letters.service import cover_letter_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/cover-letters", tags=["Cover Letters"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CoverLetterResponse,
    summary="Create cover letter",
    description="Generate a new personalized cover letter based on job posting and user profile"
)
@limiter.limit("5/minute")
async def create_cover_letter(
    request: Request,
    data: CoverLetterCreate,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CoverLetterResponse:
    """
    Create a new cover letter.
    
    Requires Keycloak JWT token in Authorization header.
    """
    result = cover_letter_service.generate_cover_letter(data)
    return CoverLetterResponse(
        id=str(uuid.uuid7()),
        cover_letter=result.cover_letter,
        tokens_used=result.tokens_used,
        created_at=datetime.now(datetime.UTC),
        updated_at=datetime.now(datetime.UTC)
    )


@router.get(
    "/{id}",
    response_model=CoverLetterResponse,
    summary="Get cover letter",
    description="Retrieve a specific cover letter by ID"
)
@limiter.limit("10/minute")
async def get_cover_letter(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CoverLetterResponse:
    """
    Get a specific cover letter by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cover letter with id {id} not found"
    )


@router.get(
    "",
    response_model=CoverLetterListResponse,
    summary="List cover letters",
    description="List all cover letters for the current user"
)
@limiter.limit("10/minute")
async def list_cover_letters(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CoverLetterListResponse:
    """
    List all cover letters for the current user.
    
    NOTE: Currently returns empty list. Persistence layer needs to be implemented.
    """
    # TODO: Implement database query
    return CoverLetterListResponse(
        data=[],
        total=0,
        limit=limit,
        offset=offset
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete cover letter",
    description="Delete a specific cover letter by ID"
)
@limiter.limit("10/minute")
async def delete_cover_letter(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a specific cover letter by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database deletion
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cover letter with id {id} not found"
    )

