"""
Authentication feature - Business logic
"""
import aiohttp
from typing import Dict, Any
from fastapi import HTTPException, status

from app.core.auth import KeycloakJWTHandler, KeycloakConfig
from app.core.auth.auth_exceptions import AuthException


class AuthService:
    """Authentication service for Keycloak operations"""
    
    def __init__(self):
        self.config = KeycloakConfig()
        self.jwt_handler = KeycloakJWTHandler(config=self.config)
    
    async def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Get user information from Keycloak token.
        
        Args:
            token: JWT access token
            
        Returns:
            User information dictionary from token payload
        """
        try:
            # Verify token and get payload
            payload = await self.jwt_handler.verify_token(token)
            
            # Return user info from token payload
            return {
                "sub": payload.get("sub"),
                "preferred_username": payload.get("preferred_username"),
                "email": payload.get("email"),
                "email_verified": payload.get("email_verified"),
                "name": payload.get("name"),
                "given_name": payload.get("given_name"),
                "family_name": payload.get("family_name"),
                "realm_access": payload.get("realm_access", {}),
                "resource_access": payload.get("resource_access", {}),
            }
        except AuthException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user information: {str(e)}"
            )
    
    async def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get token information (decode and verify token).
        
        Args:
            token: JWT access token
            
        Returns:
            Token payload dictionary
        """
        try:
            payload = await self.jwt_handler.verify_token(token)
            return payload
        except AuthException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from Keycloak
            
        Returns:
            New token information
        """
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.config.client_id,
                }
                
                if self.config.client_secret:
                    data["client_secret"] = self.config.client_secret
                
                async with session.post(
                    self.config.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Failed to refresh token"
                        )
                    
                    return await response.json()
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Keycloak service unavailable: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token refresh failed: {str(e)}"
            )


# Global service instance
auth_service = AuthService()

