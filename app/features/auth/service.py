"""
Authentication feature - Business logic
"""
import httpx
from typing import Dict, Any
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import keycloak_jwt_handler


class AuthService:
    """Authentication service for Keycloak operations"""
    
    async def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Get user information from Keycloak token.
        
        Args:
            token: JWT access token
            
        Returns:
            User information dictionary
        """
        try:
            # Verify token and get user info
            user_info = await keycloak_jwt_handler.verify_token(token)
            return user_info
        except HTTPException:
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
            payload = await keycloak_jwt_handler.verify_token(token)
            return payload
        except HTTPException:
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
            async with httpx.AsyncClient(timeout=10.0) as client:
                data = {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.keycloak_client_id,
                }
                
                if settings.keycloak_client_secret:
                    data["client_secret"] = settings.keycloak_client_secret
                
                response = await client.post(
                    settings.keycloak_token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to refresh token"
                    )
                
                return response.json()
        except httpx.RequestError as e:
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

