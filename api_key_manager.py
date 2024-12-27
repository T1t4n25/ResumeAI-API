import os
import secrets
import logging
from typing import List

class APIKeyManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.valid_api_keys: List[str] = self.load_or_generate_api_keys()

    def load_or_generate_api_keys(self) -> List[str]:
        """
        Load existing API keys or generate new ones
        """
        # Check if API keys exist in environment or file
        stored_keys = os.getenv('API_KEYS', '').split(',')
        
        # If no keys, generate a new one
        if not stored_keys or stored_keys == ['']:
            new_key = secrets.token_urlsafe(32)
            print(f"🔑 New API Key Generated: {new_key}")
            os.environ['API_KEYS'] = new_key
            return [new_key]
        
        return [key.strip() for key in stored_keys if key.strip()]

    def generate_new_api_key(self) -> str:
        """
        Generate and store a new API key
        """
        new_key = secrets.token_urlsafe(32)
        
        # Add to existing keys
        self.valid_api_keys.append(new_key)
        
        # Update environment variable
        os.environ['API_KEYS'] = ','.join(self.valid_api_keys)
        
        return new_key