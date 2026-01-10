"""Cover Letters Feature - API Routes"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.cover_letters.models import CoverLetterRequest, CoverLetterResponse
from app.features.cover_letters.service import cover_letter_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/cover-letters", tags=["Content Generation"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/generate",
    response_model=CoverLetterResponse,
    summary="Generate cover letter",
    description="Generate a personalized cover letter based on job posting and user profile"
)
@limiter.limit("5/minute")
async def generate_cover_letter(
    request: Request,
    data: CoverLetterRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CoverLetterResponse:
    """
    Generate a personalized cover letter.
    
    Requires Keycloak JWT token in Authorization header.
    """
    return cover_letter_service.generate_cover_letter(data)
