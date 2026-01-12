"""
Authentication feature - API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer
from typing import Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.features.auth.models import UserInfoResponse, TokenInfoResponse
from app.features.auth.service import auth_service
from app.features.auth.dependencies import get_authenticated_user

# Create router for auth feature
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for bearer tokens
security = HTTPBearer()


@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="Get current user information",
    description="Returns information about the currently authenticated user from Keycloak"
)
async def get_current_user_info(
    user: Dict[str, Any] = Depends(get_authenticated_user)
) -> UserInfoResponse:
    """
    Get current authenticated user information.
    Requires valid Keycloak JWT token in Authorization header.
    """
    return UserInfoResponse(**user)


@router.post(
    "/refresh",
    response_model=TokenInfoResponse,
    summary="Refresh access token",
    description="Refresh access token using refresh token from Keycloak"
)
async def refresh_access_token(
    refresh_token: str
) -> TokenInfoResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token from Keycloak
        
    Returns:
        New access token information
    """
    token_info = await auth_service.refresh_token(refresh_token)
    
    return TokenInfoResponse(
        access_token=token_info.get("access_token"),
        refresh_token=token_info.get("refresh_token"),
        token_type=token_info.get("token_type", "Bearer"),
        expires_in=token_info.get("expires_in", 3600)
    )


@router.get(
    "/tokens/info",
    summary="Get token information",
    description="Decode and return token payload information (for debugging)"
)
async def get_token_info(
    credentials = Security(security)
) -> Dict[str, Any]:
    """
    Get token information by decoding the JWT token.
    Useful for debugging and understanding token claims.
    """
    token = credentials.credentials
    token_info = await auth_service.get_token_info(token)
    return token_info


# ============================================================================
# DEPRECATED ENDPOINTS - Backward compatibility
# ============================================================================

@router.get(
    "/token-info",
    summary="[DEPRECATED] Get token information",
    description="⚠️ DEPRECATED: Use GET /auth/tokens/info instead. This endpoint will be removed in a future version.",
    deprecated=True
)
async def get_token_info_deprecated(
    credentials = Security(security)
) -> Dict[str, Any]:
    """
    [DEPRECATED] Get token information by decoding the JWT token.
    
    This endpoint is deprecated. Please use GET /auth/tokens/info instead.
    """
    return await get_token_info(credentials)

