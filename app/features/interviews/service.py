"""Interviews Feature - Business Logic Service"""
import logging
import os
import datetime
from typing import Dict, Any

from app.features.interviews.models import (
    InterviewRoomResponse,
    StartRoomResponse,  # Backward compatibility
    StartInterviewerResponse
)
from app.features.interviews.livekit_manager import LiveKitManager
from app.features.interviews.agent_manager import AgentManager


logger = logging.getLogger("resume_flow")


class InterviewService:
    """Service for AI interview management"""
    
    def __init__(self):
        self.livekit_manager = LiveKitManager(logger=logger)
        self.agent_manager = AgentManager(logger=logger, livekit_manager=self.livekit_manager)
    
    async def create_room(self, user_id: str, username: str) -> InterviewRoomResponse:
        """
        Create a LiveKit room for AI interview.
        
        Args:
            user_id: User ID from Keycloak
            username: Username from Keycloak
            
        Returns:
            Room details and access token
        """
        room_name = f"interview_{user_id}_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        room_name = await self.livekit_manager.create_room(room_name)
        user_token = await self.livekit_manager.generate_token(room_name, username)
        
        logger.info(f"Created interview room {room_name} for user {username}")
        
        from datetime import datetime
        return InterviewRoomResponse(
            id=room_name,  # Use room_name as ID
            room_name=room_name,
            token=user_token,
            websocket_url=os.getenv("LIVEKIT_URL", ""),
            status="active",
            created_at=datetime.utcnow()
        )
    
    async def start_interviewer(
        self,
        room_name: str,
        resume: str,
        job_description: str
    ) -> StartInterviewerResponse:
        """
        Start AI interviewer in the specified room.
        
        Args:
            room_name: Name of the room
            resume: Candidate's resume text
            job_description: Job description for the interview
            
        Returns:
            Confirmation of interviewer start
        """
        await self.agent_manager.start_agent_in_room(room_name, resume, job_description)
        
        logger.info(f"Started AI interviewer in room {room_name}")
        
        return StartInterviewerResponse(
            message=f"AI interviewer started in room {room_name}.",
            room_id=room_name,
            room_name=room_name
        )


# Global service instance
interview_service = InterviewService()
