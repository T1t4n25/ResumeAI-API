"""
Keycloak authentication and authorization
Uses Keycloak modules from Eldawood-ecom architecture
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth import KeycloakConfig, KeycloakJWTHandler
from app.core.auth.auth_exceptions import AuthException

# HTTP Bearer token security scheme
security = HTTPBearer()

# Logger
logger = logging.getLogger("resume_flow")

# Initialize Keycloak components
keycloak_config = KeycloakConfig()
keycloak_jwt_handler = KeycloakJWTHandler(config=keycloak_config, logger=logger)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user from Keycloak token.
    Use this in route dependencies to require authentication.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        User information dict from decoded token
        
    Raises:
        AuthException: If token is invalid or verification fails
    """
    token = credentials.credentials
    try:
        # Verify token and get payload
        payload = await keycloak_jwt_handler.verify_token(token)
        
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
        # Re-raise auth exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


async def get_current_user_id(
    user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Extract user ID (sub claim) from current user info.
    
    Args:
        user: User info dict from get_current_user dependency
        
    Returns:
        User ID (Keycloak sub claim)
    """
    return user.get("sub")


async def get_current_username(
    user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """
    Extract username from current user info.
    
    Args:
        user: User info dict from get_current_user dependency
        
    Returns:
        Username (preferred_username claim)
    """
    return user.get("preferred_username", "unknown")


def require_role(required_role: str):
    """
    Factory function to create a dependency that requires a specific role.
    
    Usage in routes:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
        
    Or to get user info:
        @app.get("/admin")
        async def admin_route(user: Dict = Depends(require_role("admin"))):
            ...
    
    Args:
        required_role: The role name required to access the endpoint
        
    Returns:
        Dependency function that checks for the role
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Check if user has the required role"""
        token = credentials.credentials
        
        try:
            # Verify token WITH role check
            payload = await keycloak_jwt_handler.verify_token(
                token,
                roles=[required_role]
            )
            
            # Return user info
            return {
                "sub": payload.get("sub"),
                "preferred_username": payload.get("preferred_username"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "realm_access": payload.get("realm_access", {}),
                "resource_access": payload.get("resource_access", {}),
            }
        except AuthException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in require_role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization failed"
            )
    
    return role_checker


def require_any_role(*roles: str):
    """
    Factory function to create a dependency that requires ANY of the specified roles.
    
    Usage:
        @app.get("/moderator", dependencies=[Depends(require_any_role("admin", "moderator"))])
    
    Args:
        *roles: Variable number of role names (user needs at least one)
        
    Returns:
        Dependency function that checks for any of the roles
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Check if user has any of the required roles"""
        token = credentials.credentials
        
        try:
            # Verify token WITH role check (any role from the list)
            payload = await keycloak_jwt_handler.verify_token(
                token,
                roles=list(roles)
            )
            
            # Return user info
            return {
                "sub": payload.get("sub"),
                "preferred_username": payload.get("preferred_username"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "realm_access": payload.get("realm_access", {}),
                "resource_access": payload.get("resource_access", {}),
            }
        except AuthException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in require_any_role: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization failed"
            )
    
    return role_checker


# Optional: Export config and handler for direct use if needed
__all__ = [
    "security",
    "keycloak_config",
    "keycloak_jwt_handler",
    "get_current_user",
    "get_current_user_id",
    "get_current_username",
    "require_role",
    "require_any_role",
]
