"""
Authentication feature - Pydantic models
"""
from pydantic import BaseModel, Field, ConfigDict


class UserInfoResponse(BaseModel):
    """User information response from Keycloak"""
    sub: str = Field(..., description="User ID (subject)")
    preferred_username: str = Field(..., description="Username")
    email: str | None = Field(None, description="Email address")
    email_verified: bool | None = Field(None, description="Email verification status")
    realm_access: dict = Field(default_factory=dict, description="Realm roles")
    resource_access: dict = Field(default_factory=dict, description="Resource roles")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "123e4567-e89b-12d3-a456-426614174000",
                "preferred_username": "johndoe",
                "email": "john@example.com",
                "email_verified": True,
                "realm_access": {"roles": ["user", "admin"]},
                "resource_access": {}
            }
        }
    )


class TokenInfoResponse(BaseModel):
    """Token information response"""
    access_token: str = Field(..., description="Access token")
    refresh_token: str | None = Field(None, description="Refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGc...",
                "refresh_token": "eyJhbGc...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }
    )

