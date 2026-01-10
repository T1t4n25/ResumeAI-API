"""
Authentication feature - Dependencies
"""
from fastapi import Depends
from typing import Dict, Any

from app.core.security import get_current_user, require_role


async def get_authenticated_user(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency that ensures user is authenticated.
    Returns user information from Keycloak token.
    """
    return user


async def require_admin_role(user: Dict[str, Any] = Depends(require_role("admin"))) -> Dict[str, Any]:
    """
    Dependency that requires admin role.
    Use this for admin-only endpoints.
    """
    return user

