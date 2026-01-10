"""
Handles verification of JWT tokens
Adapted from Eldawood E-commerce project
"""
import jwt
from async_lru import alru_cache
import aiohttp
from typing import Dict, Any, Optional
from logging import Logger, getLogger
import uuid

# Local imports
from app.core.keycloak_config import KeycloakConfig
from app.shared.auth_exceptions import (
    AuthException,
    AUTH_SERVER_UNAVAILABLE,
    AUTH_TOKEN_EXPIRED,
    AUTH_FORBIDDEN,
    AUTH_INVALID_SESSION,
    AUTH_INVALID_AUDIENCE,
    UNEXPECTED_ERROR
)


class KeycloakJWTHandler:
    """Handles verification of JWT tokens"""
    
    def __init__(
        self, 
        config: Optional[KeycloakConfig] = None,
        logger: Optional[Logger] = None
    ):
        self.config = config or KeycloakConfig()
        self._public_keys = None
        self._last_keys_fetch = 0
        
        if logger:
            self.logger = getLogger(f"{logger.name}.KeycloakJWTHandler")
            self.logger.setLevel(logger.level)
        else:
            self.logger = getLogger("KeycloakJWTHandler")
    
    @alru_cache(maxsize=1)  # Cache the public keys preventing frequent network calls
    async def __get_public_keys(self) -> Dict[str, Any]:
        """Fetch and cache Keycloak public keys"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.jwks_url, timeout=10) as response:
                    response.raise_for_status()
                    jwks = await response.json()
            
            public_keys = {}
            
            for key in jwks.get('keys', []):
                kid = key.get('kid')
                if kid:
                    public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            
            self.logger.info(f"Fetched {len(public_keys)} public keys from Keycloak")
            return public_keys
        
        except Exception as e:
            self.logger.error(f"Failed to fetch public keys: {e}")
            raise AuthException(error_code=AUTH_SERVER_UNAVAILABLE)
    
    async def verify_token(
        self, 
        token: str, 
        roles: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Verify JWT token, with optional role verification.
        If any role from the list is present in the user roles, verification passes.
        
        Args:
            token: JWT token string
            roles: Optional list of role names to check
            
        Returns:
            Decoded token payload
            
        Raises:
            AuthException: If token is invalid or user doesn't have required roles
        """
        try:
            # Decode header to get public key id to verify the JWT token integrity
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                self.logger.debug("No kid in token header")
                raise AuthException(AUTH_INVALID_SESSION)
            
            # Get public keys
            public_keys = await self.__get_public_keys()
            
            if kid not in public_keys:
                # Clear cache and try again, maybe the keys have rotated or updated
                self.__get_public_keys.cache_clear()
                public_keys = await self.__get_public_keys()
                
                if kid not in public_keys:
                    raise AuthException(AUTH_INVALID_SESSION)
            
            # Verify token
            payload = jwt.decode(
                token,
                public_keys[kid],
                algorithms=["RS256"],
                audience=[self.config.client_id],
            )
            
            # Role-Based Access Control (RBAC)
            if roles:
                # Check resource_access for client-specific roles
                user_roles = (
                    payload.get("resource_access", {})
                    .get(self.config.client_id, {})
                    .get("roles", [])
                )
                
                # Also check realm-level roles
                realm_roles = payload.get("realm_access", {}).get("roles", [])
                all_user_roles = user_roles + realm_roles
                
                if not any(role in all_user_roles for role in roles):
                    self.logger.warning(
                        f"User {payload.get('preferred_username', 'unknown')} "
                        f"missing required roles. Has: {all_user_roles}, Needs one of: {roles}"
                    )
                    raise AuthException(AUTH_FORBIDDEN)
            
            self.logger.info(
                f"Token verified for user {payload.get('preferred_username', 'unknown')}"
            )
            return payload
        
        except jwt.ExpiredSignatureError as e:
            self.logger.debug(f"Token expired: {e}")
            raise AuthException(AUTH_TOKEN_EXPIRED)
        
        except jwt.InvalidTokenError as e:
            if "Audience doesn't match" in str(e):
                raise AuthException(AUTH_INVALID_AUDIENCE)
            self.logger.debug(f"Invalid token: {e}")
            raise AuthException(AUTH_INVALID_SESSION)
        
        except IndexError as e:
            self.logger.debug(f"Token format error: {e}")
            raise AuthException(AUTH_INVALID_SESSION)
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error during token verification: {e}")
            raise AuthException(error_code=UNEXPECTED_ERROR, error_id=error_id)
    
    def clear_cache(self):
        """Clear the public keys cache (useful for key rotation or testing)"""
        self.__get_public_keys.cache_clear()
        self.logger.info("Public keys cache cleared")
