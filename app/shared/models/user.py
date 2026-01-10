"""
User model - kept for database schema compatibility
Note: Authentication now uses Keycloak. These models remain for data migration.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.shared.models.api_key import ApiKey


class User(Base):
    """User model - kept for database schema compatibility"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationship to API keys
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

