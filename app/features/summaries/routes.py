"""Summaries Feature - API Routes"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.summaries.models import SummaryRequest, SummaryResponse
from app.features.summaries.service import summary_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/summaries", tags=["Content Generation"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/generate",
    response_model=SummaryResponse,
    summary="Generate professional summary",
    description="Generate a professional summary for your resume"
)
@limiter.limit("5/minute")
async def generate_summary(
    request: Request,
    data: SummaryRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> SummaryResponse:
    """
    Generate a professional summary for resume.
    
    Requires Keycloak JWT token in Authorization header.
    """
    return summary_service.generate_summary(data)
