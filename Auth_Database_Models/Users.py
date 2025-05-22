from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text
from sqlalchemy.orm import relationship
from Auth_Database_Models.Base import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,nullable=False)
    username = Column(String(255),unique=True,nullable=False)
    password_hash = Column(String(255),unique=True,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    api_keys = relationship("ApiKey", back_populates="user")
