"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "resume_flow"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    
    # Keycloak
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "resume-flow"
    keycloak_client_id: str = "resume-flow-api"
    keycloak_client_secret: Optional[str] = None
    
    # Gemini AI
    gemini_api_key: str
    
    # LiveKit
    livekit_url: Optional[str] = None
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # Dynu DNS
    dynu_pass: Optional[str] = None
    
    # Coolify Sentinel
    sentinel_token: str = ""
    
    # Application
    api_version: str = "5.0.0"
    environment: str = "development"
    api_port: int = 8000
    
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix=""
    )
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def keycloak_issuer(self) -> str:
        """Get Keycloak issuer URL"""
        return f"{self.keycloak_url}/realms/{self.keycloak_realm}"
    
    @property
    def keycloak_token_url(self) -> str:
        """Get Keycloak token endpoint URL"""
        return f"{self.keycloak_issuer}/protocol/openid-connect/token"
    
    @property
    def keycloak_userinfo_url(self) -> str:
        """Get Keycloak userinfo endpoint URL"""
        return f"{self.keycloak_issuer}/protocol/openid-connect/userinfo"
    
    @property
    def keycloak_jwks_url(self) -> str:
        """Get Keycloak JWKS endpoint URL"""
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"


# Global settings instance
settings = Settings()

