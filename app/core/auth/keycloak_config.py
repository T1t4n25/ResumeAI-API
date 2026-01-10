"""
Handles configuration for Keycloak integration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class KeycloakConfig:
    """Contains important Keycloak endpoints ready for use"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(KeycloakConfig, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
        self.realm = os.getenv("KEYCLOAK_REALM", "resume-flow")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "resume-flow-api")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
    
    @property
    def jwks_url(self) -> str:
        """Get the JWKS URL for public key verification"""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
    
    @property
    def token_url(self) -> str:
        """OpenID Connect token endpoint for authentication workflow.
        POST to retrieve access token, refresh token, etc.
        """
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
    
    @property
    def userinfo_url(self) -> str:
        """Userinfo endpoint to get user information from JWT token"""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
    
    @property
    def issuer(self) -> str:
        """Keycloak issuer URL"""
        return f"{self.keycloak_url}/realms/{self.realm}"
    
    @property
    def realm_roles_url(self) -> str:
        """GET for all realm roles, POST to create a realm role"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/roles"
    
    def realm_role_url(self, role_name: str) -> str:
        """GET to fetch realm role details, PUT to update, DELETE to remove"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/roles/{role_name}"
    
    def realm_role_mapping_url(self, user_id: str) -> str:
        """GET/POST to fetch or assign realm-level roles for user, DELETE to remove"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/realm"
    
    def user_url(self, user_id: str) -> str:
        """PUT to update the user, GET to get user representation, DELETE to delete user"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}"
    
    def available_client_user_role_url(self, user_id: str, client_id: str) -> str:
        """GET to get available client-level roles that can be mapped to user"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/clients/{client_id}/available"
    
    def client_role_mapping_url(self, user_id: str, client_id: str) -> str:
        """POST to attach role to user, DELETE to remove role from user"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users/{user_id}/role-mappings/clients/{client_id}"
    
    def client_roles_url(self, client_id: str) -> str:
        """GET all client-level roles, POST to create one for a client"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/clients/{client_id}/roles"
    
    def client_role_detail_url(self, client_id: str, role_name: str) -> str:
        """GET, PUT, DELETE a specific client-level role"""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/clients/{client_id}/roles/{role_name}"

