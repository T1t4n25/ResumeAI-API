"""
Responsible for all Keycloak admin functions like user management
Adapted from Eldawood E-commerce project
"""
import asyncio
import aiohttp
import logging
import uuid
from typing import Optional, Dict, Any
from async_lru import alru_cache

# Local imports
from app.core.keycloak_config import KeycloakConfig
from app.shared.auth_exceptions import (
    AuthException,
    AUTH_SERVER_UNAVAILABLE,
    AUTH_TOKEN_EXPIRED,
    USER_NOT_FOUND,
    UNEXPECTED_ERROR,
    ROLE_REVOCATION_FAILED
)


class KeycloakAdmin:
    """Singleton class for Keycloak admin operations"""
    _instance: Optional['KeycloakAdmin'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeycloakAdmin, cls).__new__(cls)
        return cls._instance
    
    def __init__(
        self, 
        main_logger: Optional[logging.Logger] = None,
        config: Optional[KeycloakConfig] = None
    ):
        if not hasattr(self, '_initialized'):
            self.config = config or KeycloakConfig()
            self.max_retries = 3
            self.retry_delay = 1  # seconds
            self._initialized = True
        
        # Initialize logger
        if main_logger:
            self.logger = logging.getLogger(f"{main_logger.name}.KeycloakAdmin")
            self.logger.setLevel(main_logger.level)
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
        token_url: str = self.config.token_url
        data: dict = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                response.raise_for_status()
                token_data = await response.json()
                return token_data["access_token"]
    
    def _clear_token_cache(self):
        """Clear the cached token to force a new token request."""
        self._get_admin_token.cache_clear()
    
    async def _make_request_with_retry(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry mechanism for connection failures and token invalidation.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            url: The URL to make the request to.
            **kwargs: Additional arguments to pass to aiohttp.
            
        Returns:
            dict: Response data and status code.
            
        Raises:
            AuthException: If all retries are exhausted or specific errors occur.
        """
        for attempt in range(self.max_retries):
            try:
                # Ensure we have headers with a fresh token for each attempt
                if 'headers' not in kwargs:
                    kwargs['headers'] = await self._headers()
                else:
                    # Update the token in existing headers
                    kwargs['headers']['Authorization'] = f"Bearer {await self._get_admin_token()}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(method, url, **kwargs) as response:
                        response.raise_for_status()
                        data = await response.json() if response.content_type == 'application/json' else None
                        return {
                            'status': response.status,
                            'data': data,
                            'response': response
                        }
            
            except aiohttp.ClientResponseError as e:
                # Log the error for developers
                self.logger.error(f"Keycloak API error: {method} {url} - Status: {e.status}, Message: {e.message}")
                
                # Handle token invalidation (401/403) by clearing cache and retrying
                if e.status in [401, 403]:
                    if attempt < self.max_retries - 1:
                        # Clear token cache and retry with fresh token
                        self.logger.warning(f"Token expired, clearing cache and retrying. Attempt {attempt + 1}/{self.max_retries}")
                        self._clear_token_cache()
                        continue
                    else:
                        # Last attempt failed, raise AuthException
                        self.logger.error("Token refresh failed after all retries")
                        raise AuthException(AUTH_TOKEN_EXPIRED)
                
                elif e.status == 404:
                    # Not found errors
                    self.logger.error(f"Resource not found: {method} {url}")
                    if 'user' in url.lower():
                        raise AuthException(USER_NOT_FOUND)
                    else:
                        self.logger.error(f"Keycloak resource not found: {url}")
                        raise AuthException(UNEXPECTED_ERROR)
                
                elif e.status >= 500:
                    # Server errors
                    self.logger.error(f"Keycloak server error: {e.status} - {e.message}")
                    raise AuthException(AUTH_SERVER_UNAVAILABLE)
                
                else:
                    # Other client errors
                    self.logger.error(f"Keycloak client error: {e.status} - {e.message}")
                    raise AuthException(UNEXPECTED_ERROR)
            
            except (aiohttp.ClientConnectionError, aiohttp.ClientTimeout) as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    break
            
            except aiohttp.ClientError as e:
                # Other aiohttp errors
                self.logger.error(f"Keycloak connection error: {str(e)}")
                raise AuthException(AUTH_SERVER_UNAVAILABLE)
        
        # If we get here, all retries failed
        self.logger.error(f"All retry attempts failed for {method} {url}")
        raise AuthException(AUTH_SERVER_UNAVAILABLE)
    
    async def _headers(self) -> dict:
        """
        Construct the authorization and content-type headers for Keycloak requests.
        
        Returns:
            dict: Headers including the bearer token and content type.
        """
        return {
            "Authorization": f"Bearer {await self._get_admin_token()}",
            "Content-Type": "application/json"
        }
    
    async def add_user_attribute(
        self, 
        user_id: str, 
        attribute_name: str, 
        attribute_value: str
    ) -> bool:
        """
        Add or update a custom attribute for a specific Keycloak user.
        
        Args:
            user_id: The Keycloak user ID.
            attribute_name: The name of the attribute to set.
            attribute_value: The value to set for the attribute.
        
        Returns:
            bool: True if the attribute was updated successfully.
            
        Raises:
            AuthException: If user not found or update fails.
        """
        try:
            self.logger.info(f"Updating user {user_id} with {attribute_name}: {attribute_value}")
            user_url: str = self.config.user_url(user_id=user_id)
            resp = await self._make_request_with_retry('GET', user_url)
            user = resp['data']
            attributes = user.get('attributes', {})
            attributes[attribute_name] = [attribute_value]
            user["attributes"] = attributes
            
            put_resp = await self._make_request_with_retry('PUT', user_url, json=user)
            if put_resp['status'] != 204:
                self.logger.error(f"Failed to update user {user_id}: HTTP {put_resp['status']}")
                raise AuthException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully updated user {user_id} with {attribute_name}: {attribute_value}")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error updating user {user_id}: {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
    
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
            user_id: The Keycloak user ID.
            first_name: New first name (optional).
            last_name: New last name (optional).
            email: New email (optional).
            phone_number: New phone number (optional).
        
        Returns:
            bool: True if update successful.
        
        Raises:
            AuthException: If user not found or update fails.
        """
        try:
            self.logger.info(f"Updating user info for user {user_id}")
            user_url: str = self.config.user_url(user_id)
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
                return True  # Nothing to update
            
            put_resp = await self._make_request_with_retry('PUT', user_url, json=payload)
            if put_resp['status'] != 204:
                self.logger.error(f"Failed to update user {user_id}: HTTP {put_resp['status']}")
                raise AuthException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully updated user {user_id} info in Keycloak.")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error updating user info for {user_id}: {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
    
    async def assign_role_to_user(
        self, 
        user_id: str, 
        role_name: str,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Assign a realm-level or client-level role to a user.
        
        Args:
            user_id: The Keycloak user ID.
            role_name: The name of the role to assign.
            client_id: The client ID for client-level roles (optional).
        
        Returns:
            bool: True if the role was assigned successfully.
            
        Raises:
            AuthException: If role not found or assignment fails.
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
                raise AuthException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully assigned role '{role_name}' to user {user_id}")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error assigning role '{role_name}' to user {user_id}: {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
    
    async def revoke_role_from_user(
        self, 
        user_id: str, 
        role_id: int,
        client_id: Optional[str] = None
    ) -> bool:
        """
        Revoke a realm-level or client-level role from a user.
        
        Args:
            user_id: The Keycloak user ID.
            role_id: The ID of the role to revoke.
            client_id: The client ID for client-level roles (optional).
        
        Returns:
            bool: True if the role was revoked successfully.
            
        Raises:
            AuthException: If role not found or revocation fails.
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Revoking {role_type} role '{role_id}' from user {user_id}")
            
            # Revoke Role
            role_revoke_resp = await self._make_request_with_retry(
                'DELETE',
                self.config.client_role_mapping_url(user_id, client_id),
                json=[role_id]
            )
            if role_revoke_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to revoke role '{role_id}' from user {user_id}: HTTP {role_revoke_resp['status']}")
                raise AuthException(ROLE_REVOCATION_FAILED)
            
            self.logger.info(f"Successfully revoked role '{role_id}' from user {user_id}")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error revoking role '{role_id}' from user {user_id}: {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
    
    async def delete_user_from_keycloak(self, user_id: str) -> bool:
        """
        Delete a user from Keycloak.
        
        Args:
            user_id: The Keycloak user ID.
        
        Returns:
            bool: True if the user was deleted successfully.
            
        Raises:
            AuthException: If user not found or deletion fails.
        """
        try:
            self.logger.info(f"Deleting user {user_id} from Keycloak")
            user_url: str = self.config.user_url(user_id=user_id)
            
            delete_resp = await self._make_request_with_retry('DELETE', user_url)
            if delete_resp['status'] not in (200, 204):
                self.logger.error(f"Failed to delete user {user_id} from Keycloak: HTTP {delete_resp['status']}")
                raise AuthException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully deleted user {user_id} from Keycloak")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error deleting user {user_id} from Keycloak: {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
    
    async def add_role(
        self, 
        role_name: str, 
        description: str = "",
        client_id: Optional[str] = None
    ) -> bool:
        """
        Add a realm-level or client-level role in Keycloak.
        
        Args:
            role_name: The name of the role to add.
            description: A description for the role (optional).
            client_id: The client ID for client roles (optional).
        
        Returns:
            bool: True if the role was added successfully.
            
        Raises:
            AuthException: If role creation fails.
        """
        try:
            role_type = "realm-level" if client_id is None else f"client-level (client: {client_id})"
            self.logger.info(f"Creating {role_type} role '{role_name}' with description: '{description}'")
            
            payload = {
                "name": role_name,
                "description": description,
                "composite": False
            }
            
            if client_id is None:
                # Add realm role
                roles_url = self.config.realm_roles_url
            else:
                # Add client role
                roles_url = self.config.client_roles_url(client_id)
            
            resp = await self._make_request_with_retry('POST', roles_url, json=payload)
            if resp['status'] not in (201, 204):
                self.logger.error(f"Failed to create role '{role_name}': HTTP {resp['status']}")
                raise AuthException(UNEXPECTED_ERROR)
            
            self.logger.info(f"Successfully created role '{role_name}'")
            return True
        
        except AuthException:
            raise
        
        except Exception as e:
            error_id = str(uuid.uuid1())
            self.logger.exception(f"[{error_id}] Unexpected error creating role '{role_name}': {str(e)}")
            raise AuthException(UNEXPECTED_ERROR, error_id=error_id)
