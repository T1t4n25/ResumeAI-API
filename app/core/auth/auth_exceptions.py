"""
Custom exceptions for authentication and authorization
"""
from fastapi import HTTPException, status
from typing import Optional


class AuthException(HTTPException):
    """Base authentication exception"""
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = "Authentication failed",
        headers: Optional[dict] = None,
        error_id: Optional[str] = None
    ):
        if error_id:
            detail = f"[{error_id}] {detail}"
        super().__init__(status_code=status_code, detail=detail, headers=headers or {})


class AuthServerUnavailableException(AuthException):
    """Keycloak server is unavailable"""
    def __init__(self, detail: str = "Authentication server unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class AuthTokenExpiredException(AuthException):
    """JWT token has expired"""
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthForbiddenException(AuthException):
    """User does not have required permissions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class AuthInvalidSessionException(AuthException):
    """Invalid or malformed JWT token"""
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthInvalidAudienceException(AuthException):
    """Token audience doesn't match expected client"""
    def __init__(self, detail: str = "Invalid token audience"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

