"""Resumes Feature - API Routes"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.resumes.models import CreateResumeRequest, CreateResumeResponse
from app.features.resumes.service import resume_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/resumes", tags=["Content Generation"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/create",
    response_model=CreateResumeResponse,
    summary="Create complete resume",
    description="Generate a complete professional resume using LaTeX (PDF and/or source)"
)
@limiter.limit("5/minute")
async def create_resume(
    request: Request,
    data: CreateResumeRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> CreateResumeResponse:
    """
    Generate a complete resume using LaTeX.
    
    Requires Keycloak JWT token in Authorization header.
    """
    username = user.get("preferred_username", "unknown")
    return resume_service.create_resume(data, username=username)
