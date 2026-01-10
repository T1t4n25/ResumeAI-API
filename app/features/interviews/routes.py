"""Interviews Feature - API Routes"""
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.interviews.models import (
    StartRoomResponse,
    StartInterviewerRequest,
    StartInterviewerResponse
)
from app.features.interviews.service import interview_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/interviews", tags=["AI Interview"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/start-room",
    response_model=StartRoomResponse,
    summary="Create interview room",
    description="Create a LiveKit room for AI-powered interview session"
)
# @limiter.limit("3/hour")  # Uncomment to enable rate limiting
async def start_room(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user)
) -> StartRoomResponse:
    """
    Create a room for AI interview and return room details.
    
    Requires Keycloak JWT token in Authorization header.
    """
    user_id = user.get("sub", "unknown")
    username = user.get("preferred_username", "unknown")
    return await interview_service.create_room(user_id, username)


@router.post(
    "/start-interviewer",
    response_model=StartInterviewerResponse,
    summary="Start AI interviewer",
    description="Start an AI interviewer agent in the specified room"
)
# @limiter.limit("3/hour")  # Uncomment to enable rate limiting
async def start_interviewer(
    request: Request,
    data: StartInterviewerRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> StartInterviewerResponse:
    """
    Start an AI interviewer in the specified room.
    
    Requires Keycloak JWT token in Authorization header.
    """
    return await interview_service.start_interviewer(
        data.room_name,
        data.resume,
        data.job_description
    )
