from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from Auth_Database_Models import *


class AuthDatabase:
    """
    Class to handle the database connection and session management.
    """

    def __init__(self):
        load_dotenv()
        self.engine = create_engine(os.getenv('DATABASE_URL'))
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create all tables if they don't exist
        Base.metadata.create_all(bind=self.engine)

    def get_db(self):
        """
        Dependency to get the database session.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_session(self):
        """
        Get a database session for direct use (not generator)
        """
        return self.SessionLocal()
    
    def check_api_key(self, api_key: str):
        """
        Check if the provided API key is valid.
        """
        db = self.get_session()
        try:
            api_key_entry = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
            return api_key_entry is not None
        finally:
            db.close()
    
    def get_user_by_api_key(self, api_key: str):
        """
        Get the user associated with the provided API key.
        """
        db = self.get_session()
        try:
            # Using join for better performance
            result = db.query(User).join(ApiKey).filter(ApiKey.api_key == api_key).first()
            return result
        finally:
            db.close()
    
    def get_user_api_keys(self, user_id: int):
        """
        Get all API keys associated with the provided user ID.
        """
        db = self.get_session()
        try:
            return db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
        finally:
            db.close()
    
    def create_user(self, username: str, password_hash: str):
        """
        Create a new user.
        """
        db = self.get_session()
        try:
            user = User(username=username, password_hash=password_hash)
            db.add(user)
            db.commit()
            db.refresh(user)  # Get the ID from database
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_api_key(self, user_id: int, api_key: str):
        """
        Create a new API key for a user.
        """
        db = self.get_session()
        try:
            api_key_obj = ApiKey(user_id=user_id, api_key=api_key)
            db.add(api_key_obj)
            db.commit()
            db.refresh(api_key_obj)
            return api_key_obj
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

