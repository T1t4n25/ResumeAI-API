"""
Handles verification of JWT tokens
"""
import jwt
from async_lru import alru_cache
import aiohttp
from typing import Dict, Any, Optional, List
from logging import Logger, getLogger
import uuid

from app.core.auth.keycloak_config import KeycloakConfig
from app.core.auth.auth_exceptions import (
    AuthException,
    AuthServerUnavailableException,
    AuthTokenExpiredException,
    AuthForbiddenException,
    AuthInvalidSessionException,
    AuthInvalidAudienceException
)


class KeycloakJWTHandler:
    """Handles verification of JWT tokens"""
    
    def __init__(
        self,
        config: Optional[KeycloakConfig] = None,
        logger: Optional[Logger] = None
    ):
        self.config = config or KeycloakConfig()
        self.logger = logger or getLogger("KeycloakJWTHandler")
        
    @alru_cache(maxsize=1)
    async def _get_public_keys(self) -> Dict[str, Any]:
        """Fetch and cache Keycloak public keys"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.config.jwks_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
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
            raise AuthServerUnavailableException(f"Failed to fetch Keycloak public keys: {str(e)}")
    
    async def verify_token(
        self,
        token: str,
        roles: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verify JWT token, with optional role verification.
        
        Args:
            token: JWT token string (without "Bearer " prefix)
            roles: Optional list of roles to check. If any role is present, verification passes.
        
        Returns:
            Decoded token payload
        
        Raises:
            AuthException: Various auth-related exceptions on failure
        """
        try:
            # Decode header to get public key id
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                self.logger.debug("Token missing key ID (kid)")
                raise AuthInvalidSessionException("Token missing key ID")
            
            # Get public keys
            public_keys = await self._get_public_keys()
            
            if kid not in public_keys:
                # Clear cache and try again, maybe the keys have rotated
                self._get_public_keys.cache_clear()
                public_keys = await self._get_public_keys()
                
                if kid not in public_keys:
                    self.logger.warning(f"Public key not found for kid: {kid}")
                    raise AuthInvalidSessionException("Public key not found for token")
            
            # Verify token
            payload = jwt.decode(
                token,
                public_keys[kid],
                algorithms=["RS256"],
                audience=[self.config.client_id],
                issuer=self.config.issuer,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                }
            )
            
            # Role-based access control (RBAC)
            if roles:
                user_roles = []
                # Get realm roles
                realm_roles = payload.get("realm_access", {}).get("roles", [])
                user_roles.extend(realm_roles)
                
                # Get resource/client roles
                resource_access = payload.get("resource_access", {})
                for client_name, client_data in resource_access.items():
                    client_roles = client_data.get("roles", [])
                    user_roles.extend(client_roles)
                
                # Check if user has any of the required roles
                if not any(role in user_roles for role in roles):
                    self.logger.warning(f"User does not have required roles. Required: {roles}, Has: {user_roles}")
                    raise AuthForbiddenException(f"Required role(s): {', '.join(roles)}")
            
            username = payload.get("preferred_username") or payload.get("name") or "unknown"
            self.logger.info(f"Token verified for user: {username}, roles: {roles or 'none'}")
            return payload
        
        except jwt.ExpiredSignatureError as e:
            self.logger.debug(f"Token expired: {str(e)}")
            raise AuthTokenExpiredException()
        except jwt.InvalidAudienceError as e:
            self.logger.debug(f"Invalid audience: {str(e)}")
            raise AuthInvalidAudienceException(f"Token audience does not match client: {self.config.client_id}")
        except jwt.InvalidIssuerError as e:
            self.logger.debug(f"Invalid issuer: {str(e)}")
            raise AuthInvalidSessionException("Token issuer is invalid")
        except jwt.InvalidTokenError as e:
            self.logger.debug(f"Invalid token: {str(e)}")
            raise AuthInvalidSessionException(f"Invalid token: {str(e)}")
        except AuthException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid4())
            self.logger.exception(f"[{error_id}] Unexpected error verifying token: {str(e)}")
            raise AuthException(
                status_code=500,
                detail=f"Unexpected error during token verification",
                error_id=error_id
            )

