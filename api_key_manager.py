# api_key_manager.py
import os
import secrets
import hashlib
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from Auth_DataBase.auth_database import AuthDatabase

class APIKeyManager:
    def __init__(self, logger=None):
        self.logger = logger
        self.auth_db = AuthDatabase()
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def generate_new_api_key(self, user_id: int):
        """
        Generate and store a new API key for a specific user
        """
        new_key = secrets.token_urlsafe(32)
        try:
            api_key_obj = self.auth_db.create_api_key(user_id, new_key)
            if self.logger:
                self.logger.info(f"New API key generated for user {user_id}")
            return new_key
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create API key for user {user_id}: {str(e)}")
            raise e

    async def validate_api_key(self, api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False))):
        """
        Validate the API key from the request header
        """
        if not api_key:
            if self.logger:
                self.logger.error("No API key provided")
            raise HTTPException(
                status_code=403,
                detail="API key required"
            )
        
        is_valid = self.auth_db.check_api_key(api_key)
        if not is_valid:
            if self.logger:
                self.logger.error(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        
        if self.logger:
            self.logger.info(f"Valid API key used: {api_key[:8]}...")
        return api_key

    def get_user_from_api_key(self, api_key: str):
        """
        Get the user associated with the provided API key
        """
        try:
            user_obj = self.auth_db.get_user_by_api_key(api_key)
            user = {
                "id": user_obj['id'],
                "username": user_obj['username'],
            }
            return user
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting user for API key: {str(e)}")
            return None

    def revoke_api_key(self, api_key: str):
        """
        Revoke/delete an API key (you'll need to implement this in AuthDatabase)
        """
        # You can implement this method in AuthDatabase if needed
        pass