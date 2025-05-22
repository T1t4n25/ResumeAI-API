# api_key_manager.py
import os
import secrets
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from Auth_DataBase.auth_database import AuthDatabase
class APIKeyManager:
    def __init__(self, logger=None):
        self.logger = logger
        self.auth_db = AuthDatabase()
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


    def generate_new_api_key(self):
        """
        Generate and store a new API key
        """
        new_key = secrets.token_urlsafe(32)
        self.valid_api_keys.append(new_key)
        os.environ['API_KEYS'] = ','.join(self.valid_api_keys)
        return new_key

    async def validate_api_key(self, api_key: str = Security(APIKeyHeader(name="X-API-Key"))):
        """
        Validate the API key from the request header
        """
        is_valid = self.auth_db.check_api_key(api_key)
        if not is_valid:
            self.logger.error(f"Invalid API key: {api_key}")
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        self.logger.info(f"API key {api_key} is valid")
        return api_key