"""Interviews Feature - API Routes (RESTful)"""
from fastapi import APIRouter, Depends, Request, status, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict, Any

from app.features.interviews.models import (
    InterviewRoomCreate,
    InterviewRoomResponse,
    InterviewRoomListResponse,
    StartInterviewerRequest,
    StartInterviewerResponse,
    # Backward compatibility
    StartRoomRequest,
    StartRoomResponse
)
from app.features.interviews.service import interview_service
from app.core.security import get_current_user

# Create router
router = APIRouter(prefix="/interviews", tags=["AI Interview"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/rooms",
    status_code=status.HTTP_201_CREATED,
    response_model=InterviewRoomResponse,
    summary="Create interview room",
    description="Create a new LiveKit room for AI-powered interview session"
)
@limiter.limit("3/hour")
async def create_room(
    request: Request,
    data: InterviewRoomCreate | None = None,
    user: Dict[str, Any] = Depends(get_current_user)
) -> InterviewRoomResponse:
    """
    Create a new interview room.
    
    Requires Keycloak JWT token in Authorization header.
    """
    user_id = user.get("sub", "unknown")
    username = user.get("preferred_username", "unknown")
    
    result = await interview_service.create_room(user_id, username)
    return result


@router.post(
    "/rooms/{room_id}/start",
    status_code=status.HTTP_200_OK,
    response_model=StartInterviewerResponse,
    summary="Start AI interviewer",
    description="Start an AI interviewer agent in the specified room"
)
@limiter.limit("3/hour")
async def start_interviewer(
    request: Request,
    room_id: str,
    data: StartInterviewerRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> StartInterviewerResponse:
    """
    Start an AI interviewer in the specified room.
    
    Requires Keycloak JWT token in Authorization header.
    """
    result = await interview_service.start_interviewer(
        room_id,  # Use room_id from path
        data.resume,
        data.job_description
    )
    
    return StartInterviewerResponse(
        message=result.message,
        room_id=room_id,
        room_name=result.room_name
    )


@router.get(
    "/rooms/{room_id}",
    response_model=InterviewRoomResponse,
    summary="Get interview room",
    description="Retrieve details of a specific interview room"
)
@limiter.limit("10/minute")
async def get_room(
    request: Request,
    room_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> InterviewRoomResponse:
    """
    Get a specific interview room by ID.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement database lookup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview room with id {room_id} not found"
    )


@router.get(
    "/rooms",
    response_model=InterviewRoomListResponse,
    summary="List interview rooms",
    description="List all interview rooms for the current user"
)
@limiter.limit("10/minute")
async def list_rooms(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    status_filter: str | None = None,
    user: Dict[str, Any] = Depends(get_current_user)
) -> InterviewRoomListResponse:
    """
    List all interview rooms for the current user.
    
    Query parameters:
    - limit: Maximum number of results (default: 10)
    - offset: Number of results to skip (default: 0)
    - status: Filter by status (active, ended) - optional
    
    NOTE: Currently returns empty list. Persistence layer needs to be implemented.
    """
    # TODO: Implement database query with filtering
    return InterviewRoomListResponse(
        data=[],
        total=0,
        limit=limit,
        offset=offset
    )


@router.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End interview session",
    description="End an interview session and clean up resources"
)
@limiter.limit("10/minute")
async def delete_room(
    request: Request,
    room_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    End an interview session and delete the room.
    
    NOTE: Currently returns 404. Persistence layer needs to be implemented.
    """
    # TODO: Implement room deletion and cleanup
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Interview room with id {room_id} not found"
    )


# ============================================================================
# DEPRECATED ENDPOINTS - Backward compatibility
# ============================================================================

@router.post(
    "/start-room",
    status_code=status.HTTP_201_CREATED,
    response_model=StartRoomResponse,  # Using old response model
    summary="[DEPRECATED] Create interview room",
    description="⚠️ DEPRECATED: Use POST /interviews/rooms instead. This endpoint will be removed in a future version.",
    deprecated=True
)
@limiter.limit("3/hour")
async def start_room_deprecated(
    request: Request,
    user: Dict[str, Any] = Depends(get_current_user)
) -> StartRoomResponse:
    """
    [DEPRECATED] Create a room for AI interview and return room details.
    
    This endpoint is deprecated. Please use POST /interviews/rooms instead.
    """
    result = await create_room(request, None, user)
    # Convert new response format to old format
    return StartRoomResponse(
        room_name=result.room_name,
        token=result.token,
        websocket_url=result.websocket_url,
        message="Room created successfully. Use the token to join the room."
    )


@router.post(
    "/start-interviewer",
    status_code=status.HTTP_200_OK,
    response_model=StartInterviewerResponse,
    summary="[DEPRECATED] Start AI interviewer",
    description="⚠️ DEPRECATED: Use POST /interviews/rooms/:room_id/start instead. This endpoint will be removed in a future version.",
    deprecated=True
)
@limiter.limit("3/hour")
async def start_interviewer_deprecated(
    request: Request,
    data: StartInterviewerRequest,
    user: Dict[str, Any] = Depends(get_current_user)
) -> StartInterviewerResponse:
    """
    [DEPRECATED] Start an AI interviewer in the specified room.
    
    This endpoint is deprecated. Please use POST /interviews/rooms/:room_id/start instead.
    
    Note: This endpoint requires room_name in the request body, but the new endpoint uses room_id in the URL path.
    """
    if not data.room_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="room_name is required in request body for this deprecated endpoint. Please use POST /interviews/rooms/:room_id/start instead, with room_id in the URL path."
        )
    
    result = await interview_service.start_interviewer(
        data.room_name,
        data.resume,
        data.job_description
    )
    
    return StartInterviewerResponse(
        message=result.message,
        room_id=data.room_name,
        room_name=result.room_name
    )