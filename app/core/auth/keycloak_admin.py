"""
Keycloak admin operations (user management, role assignment, etc.)
"""
import asyncio
import aiohttp
import logging
import uuid
from typing import Optional, Dict, Any
from async_lru import alru_cache

from app.core.auth.keycloak_config import KeycloakConfig
from app.core.auth.auth_exceptions import (
    AuthException,
    AuthServerUnavailableException,
    AuthTokenExpiredException,
    AuthInvalidSessionException
)


class KeycloakAdmin:
    """Keycloak admin operations handler"""
    _instance: Optional['KeycloakAdmin'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeycloakAdmin, cls).__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        config: Optional[KeycloakConfig] = None,
        logger: Optional[logging.Logger] = None
    ):
        if not hasattr(self, '_initialized'):
            self.config = config or KeycloakConfig()
            self.max_retries = 3
            self.retry_delay = 1  # seconds
            self._initialized = True
            
        # Initialize logger
        if logger:
            self.logger = logging.getLogger(f"{logger.name}.KeycloakAdmin")
            self.logger.setLevel(logger.level)
        else:
            self.logger = logging.getLogger("KeycloakAdmin")
            self.logger.setLevel(logging.INFO)

    @alru_cache(maxsize=1)
    async def _get_admin_token(self) -> str:
        """
        Obtain an access token for the Keycloak admin client using client credentials.
        Uses LRU cache to avoid unnecessary token requests.
        
        Returns:
            str: The admin access token.
        """
        token_url = self.config.token_url
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                token_url,
                data=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                token_data = await response.json()
                return token_data["access_token"]

    def _clear_token_cache(self):
        """Clear the cached token to force a new token request"""
        self._get_admin_token.cache_clear()

    async def _headers(self) -> Dict[str, str]:
        """
        Construct the authorization and content-type headers for Keycloak requests.
        
        Returns:
            dict: Headers including the bearer token and content type.
        """
        return {
            "Authorization": f"Bearer {await self._get_admin_token()}",
            "Content-Type": "application/json"
        }

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry mechanism for connection failures and token invalidation.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: The URL to make the request to
            **kwargs: Additional arguments to pass to aiohttp
            
        Returns:
            dict: Response data and status code
            
        Raises:
            AuthException: If all retries are exhausted or specific errors occur
        """
        for attempt in range(self.max_retries):
            try:
                # Ensure we have headers with a fresh token for each attempt
                if 'headers' not in kwargs:
                    kwargs['headers'] = await self._headers()
                else:
                    kwargs['headers']['Authorization'] = f"Bearer {await self._get_admin_token()}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        timeout=aiohttp.ClientTimeout(total=10),
                        **kwargs
                    ) as response:
                        response.raise_for_status()
                        data = await response.json() if response.content_type == 'application/json' else None
                        return {
                            'status': response.status,
                            'data': data,
                            'response': response
                        }
                
            except aiohttp.ClientResponseError as e:
                self.logger.error(f"Keycloak API error: {method} {url} - Status: {e.status}, Message: {e.message}")
                
                # Handle token invalidation (401/403) by clearing cache and retrying
                if e.status in [401, 403]:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(f"Token expired, clearing cache and retrying. Attempt {attempt + 1}/{self.max_retries}")
                        self._clear_token_cache()
                        continue
                    else:
                        self.logger.error("Token refresh failed after all retries")
                        raise AuthTokenExpiredException()
                elif e.status == 404:
                    self.logger.error(f"Resource not found: {method} {url}")
                    raise AuthException(status_code=404, detail="Resource not found")
                elif e.status >= 500:
                    self.logger.error(f"Keycloak server error: {e.status} - {e.message}")
                    raise AuthServerUnavailableException()
                else:
                    self.logger.error(f"Keycloak client error: {e.status} - {e.message}")
                    raise AuthException(status_code=e.status, detail=f"Keycloak error: {e.message}")
                    
            except (aiohttp.ClientConnectionError, aiohttp.ClientTimeout) as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    break
            except aiohttp.ClientError as e:
                self.logger.error(f"Keycloak connection error: {str(e)}")
                raise AuthServerUnavailableException(f"Connection error: {str(e)}")
        
        # If we get here, all retries failed
        self.logger.error(f"All retry attempts failed for {method} {url}")
        raise AuthServerUnavailableException("All retry attempts failed")

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information from Keycloak.
        
        Args:
            user_id: The Keycloak user ID
            
        Returns:
            dict: User information
        """
        try:
            user_url = self.config.user_url(user_id=user_id)
            resp = await self._make_request_with_retry('GET', user_url)
            return resp['data']
        except AuthException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid4())
            self.logger.exception(f"[{error_id}] Unexpected error getting user info: {str(e)}")
            raise AuthException(status_code=500, detail="Unexpected error", error_id=error_id)

    async def update_user_info(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Update user's info in Keycloak.
        
        Args:
            user_id: The Keycloak user ID
            first_name: New first name
            last_name: New last name
            email: New email
            phone_number: New phone number
            
        Returns:
            bool: True if update successful
        """
        try:
            self.logger.info(f"Updating user info for user {user_id}")
            user_url = self.config.user_url(user_id)
            resp = await self._make_request_with_retry('GET', user_url)
            user = resp['data']

            # Prepare update payload
            payload = {}
            if first_name is not None:
                payload["firstName"] = first_name
            if last_name is not None:
                payload["lastName"] = last_name
            if email is not None:
                payload["email"] = email

            # Keycloak custom attribute for phone number
            attributes = user.get('attributes', {})
            if phone_number is not None:
                attributes['phone_number'] = [phone_number]
                payload["attributes"] = attributes
            elif attributes:
                payload["attributes"] = attributes

            if not payload:
                self.logger.warning(f"No update fields provided for user {user_id}")
                return True

            put_resp = await self._make_request_with_retry('PUT', user_url, json=payload)
            if put_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to update user {user_id}: HTTP {put_resp['status']}")
                raise AuthException(status_code=put_resp['status'], detail="Failed to update user")

            self.logger.info(f"Successfully updated user {user_id} info in Keycloak")
            return True
        except AuthException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid4())
            self.logger.exception(f"[{error_id}] Unexpected error updating user info: {str(e)}")
            raise AuthException(status_code=500, detail="Unexpected error", error_id=error_id)

    async def assign_role_to_user(
        self,
        user_id: str,
        role_name: str,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Assign a realm-level or client-level role to a user.
        
        Args:
            user_id: The Keycloak user ID
            role_name: The name of the role to assign
            client_id: Optional client ID for client-level roles
            
        Returns:
            bool: True if the role was assigned successfully
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Assigning {role_type} role '{role_name}' to user {user_id}")
            
            if client_id is None:
                # Realm-level role
                role_url = self.config.realm_role_url(role_name)
                mapping_url = self.config.realm_role_mapping_url(user_id)
            else:
                # Client-level role
                role_url = self.config.client_role_detail_url(client_id, role_name)
                mapping_url = self.config.client_role_mapping_url(user_id, client_id)

            # Get the Role dict
            role_resp = await self._make_request_with_retry('GET', role_url)
            role = role_resp['data']

            # Assign Role
            role_assign_resp = await self._make_request_with_retry('POST', mapping_url, json=[role])
            if role_assign_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to assign role '{role_name}' to user {user_id}: HTTP {role_assign_resp['status']}")
                raise AuthException(status_code=role_assign_resp['status'], detail="Failed to assign role")
            
            self.logger.info(f"Successfully assigned role '{role_name}' to user {user_id}")
            return True
        except AuthException:
            raise
        except Exception as e:
            error_id = str(uuid.uuid4())
            self.logger.exception(f"[{error_id}] Unexpected error assigning role: {str(e)}")
            raise AuthException(status_code=500, detail="Unexpected error", error_id=error_id)

