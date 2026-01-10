"""
API Key model - kept for database schema compatibility
Note: Authentication now uses Keycloak. These models remain for data migration.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ApiKey(Base):
    """API Key model - kept for database schema compatibility"""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationship to user
    user = relationship("User", back_populates="api_keys")
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

