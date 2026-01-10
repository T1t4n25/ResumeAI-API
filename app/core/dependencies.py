"""
Shared FastAPI dependencies
"""
import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_id
from app.core.auth import KeycloakAdmin

logger = logging.getLogger("resume_flow")


# Re-export commonly used dependencies for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
    "get_keycloak_admin",
]


async def get_authenticated_user_with_db(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> tuple[Dict[str, Any], AsyncSession]:
    """
    Combined dependency that provides both authenticated user and database session.
    Useful for routes that need both.
    """
    return user, db


def get_keycloak_admin(logger_instance: logging.Logger = None) -> KeycloakAdmin:
    """
    Dependency to get KeycloakAdmin instance.
    Useful for admin endpoints that need to manage users/roles.
    """
    return KeycloakAdmin(logger=logger_instance or logger)

