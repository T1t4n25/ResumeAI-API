from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv
import os

from Auth_Database_Models import *


class AuthDatabase:
    """
    Class to handle the database connection and session management with optimized connection pooling.
    """

    def __init__(self):
        load_dotenv()

        # Configure connection pool explicitly for better control
        self.engine = create_engine(
            os.getenv('DATABASE_URL'),
            # Connection pool settings
            pool_size=10,          # Number of connections to maintain in pool
            max_overflow=20,       # Additional connections beyond pool_size
            pool_timeout=30,       # Seconds to wait for connection from pool
            pool_recycle=3600,     # Seconds before recreating connections (prevents stale connections)
            pool_pre_ping=True,    # Validate connections before use
            echo=False             # Set to True for SQL debugging
        )

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create all tables if they don't exist
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_db_session(self):
        """
        Context manager for database sessions - preferred method for most operations.
        Automatically handles session cleanup and error rollback.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()  # Auto-commit if no exceptions
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_db(self):
        """
        Dependency generator for frameworks like FastAPI.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def check_api_key(self, api_key: str) -> bool:
        """
        Check if the provided API key is valid.
        """
        with self.get_db_session() as db:
            api_key_entry = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
            api_key = True if api_key_entry != None else False
            return api_key

    def get_user_by_api_key(self, api_key: str):
        """
        Get the user associated with the provided API key.
        """
        with self.get_db_session() as db:
            user_obj = db.query(User).join(ApiKey).filter(ApiKey.api_key == api_key).first()
            user = user_obj.to_dict() if user_obj else None
            return user

    def get_user_api_keys(self, user_id: int):
        """
        Get all API keys associated with the provided user ID.
        """
        with self.get_db_session() as db:
            api_keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
            if not api_keys:
                return None
            #serialize the objects to dictionary containing all data
            api_keys = [api_key.to_dict() for api_key in api_keys]
            
                
            return api_keys

    def create_user(self, username: str, password_hash: str):
        """
        Create a new user.
        """
        with self.get_db_session() as db:
            user = User(username=username, password_hash=password_hash)
            db.add(user)
            db.flush()
            db.refresh(user)
            user_id= user.id

            return user_id

    def create_api_key(self, user_id: int, api_key: str):
        """
        Create a new API key for a user.
        """
        with self.get_db_session() as db:
            api_key_obj = ApiKey(user_id=user_id, api_key=api_key)
            db.add(api_key_obj)
            db.flush()
            db.refresh(api_key_obj)
            
            return api_key

    def get_user_by_username(self, username: str):
        """
        Get user by username.
        """
        with self.get_db_session() as db:
            user_obj = db.query(User).filter(User.username == username).first()
            user = {
                "id": user_obj.id,
                "username": user_obj.username,
                "password_hash": user_obj.password_hash
            } if user_obj else None
            return user
            

    def delete_api_key(self, api_key: str) -> bool:
        """
        Delete/revoke an API key.
        """
        with self.get_db_session() as db:
            api_key_obj = db.query(ApiKey).filter(ApiKey.api_key == api_key).first()
            if api_key_obj:
                db.delete(api_key_obj)
                return True
            return False

    def get_api_key_with_user(self, api_key: str):
        """
        Get API key object with associated user information.
        """
        with self.get_db_session() as db:
            return db.query(ApiKey).join(User).filter(ApiKey.api_key == api_key).first()

    def close_all_connections(self):
        """
        Close all connections in the pool. Call this when shutting down the server.
        """
        self.engine.dispose()

    def get_pool_status(self):
        """
        Get current connection pool status for monitoring.
        """
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
