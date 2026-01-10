"""
Custom exceptions for the application
"""
from fastapi import HTTPException, status


class ResumeFlowException(HTTPException):
    """Base exception for Resume Flow API"""
    pass


class AuthenticationError(ResumeFlowException):
    """Authentication related errors"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(ResumeFlowException):
    """Authorization related errors"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundError(ResumeFlowException):
    """Resource not found errors"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class ValidationError(ResumeFlowException):
    """Validation errors"""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class GenerationError(ResumeFlowException):
    """AI generation related errors"""
    def __init__(self, detail: str = "Content generation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

