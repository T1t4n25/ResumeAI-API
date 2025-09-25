import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from dotenv import load_dotenv
from os import getenv
from fastapi.security import APIKeyHeader
from fastapi import Security

# Constants
load_dotenv()

SECRET_KEY =  getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 20

# Header scheme
header_scheme = APIKeyHeader(name="Authorization", auto_error=False)


class JWTManager:
    """
    JWT Manager for handling JWT tokens and password hashing.
    """
    def __init__(self, logger=None):
        self.logger = logger

    def create_jwt_token(self, user_id: int, full_name: str) -> str:
        """
        Create a JWT token with the given payload.
        """
        issued_at = datetime.now(tz=timezone.utc)
        payload = {
            "user_id": user_id,
            "username": full_name,
            "exp": issued_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": issued_at,
            "nbf": issued_at  
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def decode_jwt_token(self, token: str) -> dict:
        """
        Decode a JWT token and return the payload.
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Define JWT dependency function
    async def check_jwt(self, token: str = Security(header_scheme)):
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            # token = token.split(" ")[1]  # Commented for swagger testing, must be un-commented for production use
            decoded = self.decode_jwt_token(token)
            
            return decoded["user_id"]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid token format")
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
