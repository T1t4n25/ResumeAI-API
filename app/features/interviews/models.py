"""Interviews Feature - Pydantic Models"""
from pydantic import BaseModel, Field


class StartRoomRequest(BaseModel):
    """Request model for starting an interview room"""
    pass  # No additional data needed, user is extracted from JWT


class StartRoomResponse(BaseModel):
    """Response model for room creation"""
    room_name: str = Field(..., description="Name of the created room")
    token: str = Field(..., description="Access token for the room")
    websocket_url: str = Field(..., description="WebSocket URL for LiveKit connection")
    message: str = Field(..., description="Success message")


class StartInterviewerRequest(BaseModel):
    """Request model for starting AI interviewer"""
    room_name: str = Field(..., description="Room name where interviewer should join")
    resume: str = Field(..., description="Candidate's resume text")
    job_description: str = Field(..., description="Job description for the interview")


class StartInterviewerResponse(BaseModel):
    """Response model for starting interviewer"""
    message: str = Field(..., description="Success message")
    room_name: str = Field(..., description="Room name where interviewer was started")
