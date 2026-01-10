"""
Custom exceptions for authentication and authorization
Simplified version adapted from Eldawood E-commerce project
"""
from fastapi import HTTPException
from typing import Optional
from dataclasses import dataclass


@dataclass
class ErrorCode:
    """Error code with status code and message"""
    status_code: int
    message: str


# Authentication Error Codes
AUTH_SERVER_UNAVAILABLE = ErrorCode(
    status_code=503,
    message="Authentication server is currently unavailable. Please try again later."
)

AUTH_TOKEN_EXPIRED = ErrorCode(
    status_code=401,
    message="Your session has expired. Please log in again."
)

AUTH_FORBIDDEN = ErrorCode(
    status_code=403,
    message="You do not have permission to access this resource."
)

AUTH_INVALID_SESSION = ErrorCode(
    status_code=401,
    message="Invalid or expired session. Please log in again."
)

AUTH_INVALID_AUDIENCE = ErrorCode(
    status_code=401,
    message="Token audience mismatch. Invalid authentication token."
)

USER_NOT_FOUND = ErrorCode(
    status_code=404,
    message="User not found."
)

ROLE_REVOCATION_FAILED = ErrorCode(
    status_code=500,
    message="Failed to revoke role from user."
)

UNEXPECTED_ERROR = ErrorCode(
    status_code=500,
    message="An unexpected error occurred. Please try again later."
)


class AuthException(HTTPException):
    """Base authentication exception"""
    
    def __init__(
        self, 
        error_code: ErrorCode, 
        headers: Optional[dict] = None,
        error_id: Optional[str] = None,
        **kwargs
    ):
        detail = error_code.message
        
        # If error_id is provided, append it to the message for debugging
        if error_id:
            detail = f"{detail} (Error ID: {error_id})"
        
        # If additional kwargs are provided, try to format the message
        if kwargs:
            try:
                detail = detail.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        super().__init__(
            status_code=error_code.status_code,
            detail=detail,
            headers=headers
        )
