"""Interviews Feature - Pydantic Models"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class InterviewRoomCreate(BaseModel):
    """Request model for creating an interview room"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "job_role": "Senior Software Engineer",
            "difficulty": "intermediate"
        }
    })
    
    job_role: Optional[str] = Field(None, description="Job role for the interview (optional)")
    difficulty: Optional[str] = Field(None, description="Interview difficulty level (optional)")


class InterviewRoomResponse(BaseModel):
    """Response model for interview room"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "room_123e4567-e89b-12d3-a456-426614174000",
            "room_name": "interview_user123_20240101_120000",
            "token": "eyJhbGc...",
            "websocket_url": "wss://resume-flow.livekit.cloud",
            "status": "active",
            "created_at": "2024-01-01T12:00:00Z"
        }
    })
    
    id: str = Field(..., description="Unique identifier for the room")
    room_name: str = Field(..., description="Name of the created room")
    token: str = Field(..., description="Access token for the room")
    websocket_url: str = Field(..., description="WebSocket URL for LiveKit connection")
    status: str = Field(default="active", description="Room status (active, ended)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class StartInterviewerRequest(BaseModel):
    """Request model for starting AI interviewer"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "resume": "John Doe\nSenior Software Engineer...",
            "job_description": "We are looking for a Senior Software Engineer..."
        }
    })
    
    resume: str = Field(..., description="Candidate's resume text")
    job_description: str = Field(..., description="Job description for the interview")
    room_name: str | None = Field(None, description="[DEPRECATED] Room name - use room_id in URL path instead")


class StartInterviewerResponse(BaseModel):
    """Response model for starting interviewer"""
    message: str = Field(..., description="Success message")
    room_id: str = Field(..., description="Room ID where interviewer was started")
    room_name: str = Field(..., description="Room name where interviewer was started")


class InterviewRoomListResponse(BaseModel):
    """Response model for listing interview rooms"""
    data: list[InterviewRoomResponse]
    total: int
    limit: int = 10
    offset: int = 0


# Backward compatibility - need separate class for old response format
class StartRoomResponse(BaseModel):
    """[DEPRECATED] Old response model for room creation"""
    room_name: str = Field(..., description="Name of the created room")
    token: str = Field(..., description="Access token for the room")
    websocket_url: str = Field(..., description="WebSocket URL for LiveKit connection")
    message: str = Field(..., description="Success message")


# Backward compatibility alias
StartRoomRequest = InterviewRoomCreate
