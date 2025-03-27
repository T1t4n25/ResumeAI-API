# api_key_manager.py
import os
import secrets
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
class APIKeyManager:
    def __init__(self, logger=None):
        self.logger = logger
        self.valid_api_keys = self.load_or_generate_api_keys()
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def load_or_generate_api_keys(self):
        """
        Load existing API keys or generate new ones
        """
        # Check if API keys exist in environment or file
        stored_keys = os.getenv('API_KEYS', '').split(',')
        
        # If no keys, generate a new one
        if not stored_keys or stored_keys == ['']:
            new_key = secrets.token_urlsafe(32)
            self.logger.info(f"🔑 New API Key Generated: {new_key}")
            os.environ['API_KEYS'] = new_key
            return [new_key]
        
        return [key.strip() for key in stored_keys if key.strip()]

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
        if api_key not in self.valid_api_keys:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        return api_key