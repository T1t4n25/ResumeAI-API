from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text, ForeignKey
from sqlalchemy.orm import relationship
from Auth_Database_Models.Base import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    
    # Relationship to user
    user = relationship("User", back_populates="api_keys")