"""Summaries Feature - API Routes (RESTful)"""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any
import uuid
from datetime import datetime
from app.features.summaries.models import (
    SummaryCreate,
    SummaryResponse,
    SummaryListResponse,
)
from app.features.summaries.service import summary_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/summaries", tags=["Summaries"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SummaryResponse,
    summary="Create professional summary",
    description="Generate a new professional summary for your resume"
)
@limiter.limit("5/minute")
async def create_summary(
    request: Request,
    data: SummaryCreate,
    user: Dict[str, Any] = Depends(get_current_user)
) -> SummaryResponse:
    """
    Create a new professional summary.
    
    Requires Keycloak JWT token in Authorization header.
    """
    result = summary_service.generate_summary(data)
    return SummaryResponse(
        id=str(uuid.uuid7()),
        summary=result.summary,
        current_title=data.current_title,
        years_experience=data.years_experience,
        skills=data.skills,
        achievements=data.achievements,
        created_at=datetime.now(datetime.UTC),
        updated_at=datetime.now(datetime.UTC)
    )


@router.get(
    "/{id}",
    response_model=SummaryResponse,
    summary="Get summary",
    description="Retrieve a specific summary by ID"
)
@limiter.limit("10/minute")
async def get_summary(
    request: Request,
    id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> SummaryResponse:
    """
    Get a specific summary by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Summary with id {id} not found"
    )


@router.get(
    "",
    response_model=SummaryListResponse,
    summary="List summaries",
    description="List all summaries for the current user"
)
@limiter.limit("10/minute")
async def list_summaries(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user: Dict[str, Any] = Depends(get_current_user)
) -> SummaryListResponse:
    """
    List all summaries for the current user.
    
    NOTE: Currently returns empty list. Persistence layer needs to be implemented.
    """
    # TODO: Implement database query
    return SummaryListResponse(
        data=[],
        total=0,
        limit=limit,
        offset=offset
    )
