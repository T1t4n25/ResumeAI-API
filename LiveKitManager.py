import os

from livekit import api
from fastapi import HTTPException
from dotenv import load_dotenv
load_dotenv()

class LiveKitManager:
    def __init__(self, logger):
        self.livekit_api = None
        self.active_sessions = {}
        self.logger = logger
        
    async def get_api(self):
        """Lazy initialization of LiveKit API client"""
        if self.livekit_api is None:
            self.livekit_api = api.LiveKitAPI()
        return self.livekit_api
    
    async def create_room(self, room_name: str) -> str:
        """Create a LiveKit room and return room info"""
        try:
            self.livekit_api = await self.get_api()
            room = await self.livekit_api.room.create_room(
                api.CreateRoomRequest(name=room_name)
            )
            self.logger.info(f"Room created: {room.name}")
            self.active_sessions[room_name] = room
            return room.name
        except Exception as e:
            self.logger.error(f"Error creating room: {e}")
            raise HTTPException(status_code=500, detail="Failed to create room.")
    
    async def generate_token(self, room_name: str, participant_name: str) -> str:
        """Generate access token for a participant"""
        try:
            token = api.AccessToken(
                api_key=os.getenv("LIVEKIT_API_KEY"),
                api_secret=os.getenv("LIVEKIT_API_SECRET")
            )
            token = token.with_identity(participant_name).with_name(participant_name)
            token = token.with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            return token.to_jwt()
        except Exception as e:
            self.logger.error(f"Error generating token: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate token.")
