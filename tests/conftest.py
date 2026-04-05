# tests/conftest.py
"""
Shared test fixtures for the Resume Flow API test suite.

Strategy:
  - All tests use `async_client` (httpx.AsyncClient via ASGITransport) — no server needed
  - Auth is mocked by default via `mock_auth` fixture which overrides `get_current_user`
  - Integration tests (requiring a real Keycloak token) are marked @pytest.mark.integration
"""
import os
import sys
from typing import AsyncGenerator, Dict, Any

import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport
import time

@pytest.fixture(autouse=True)
def rate_limit_sleep(request):
    """Sleep before slow tests to prevent Gemini 429 Resource Exhausted errors.
    Adjusted to 13 seconds for Gemini 2.5 Flash's 5 RPM limit."""
    if "slow" in request.node.keywords:
        time.sleep(13)


# ---------------------------------------------------------------------------
# Make `app` importable from `app.main` by prepending the project root to sys.path
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.core.security import get_current_user


# ---------------------------------------------------------------------------
# Mock authenticated user (mirrors what Keycloak JWT decoding returns)
# ---------------------------------------------------------------------------
MOCK_USER: Dict[str, Any] = {
    "sub": "test-user-id-12345",
    "preferred_username": "testuser",
    "email": "testuser@example.com",
    "email_verified": True,
    "name": "Test User",
    "given_name": "Test",
    "family_name": "User",
    "realm_access": {"roles": ["user"]},
    "resource_access": {},
}


from fastapi import Request, HTTPException, status

async def _mock_get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency override: bypass Keycloak and return a fake user, but demand auth header."""
    if "Authorization" not in request.headers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated"
        )
    return MOCK_USER


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def mock_auth():
    """
    Session-scoped fixture that overrides the `get_current_user` dependency
    with a fake user dict for the entire test session.

    This removes the need for a live Keycloak server during unit tests.
    """
    app.dependency_overrides[get_current_user] = _mock_get_current_user
    yield MOCK_USER
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture(scope="session")
async def async_client(mock_auth) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Session-scoped async HTTP client that talks directly to the ASGI app.
    Depends on `mock_auth` so that auth is always mocked.
    """
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """
    Authorization headers with a fake Bearer token.
    The token value is irrelevant because the dependency is overridden.
    """
    return {"Authorization": "Bearer mock-test-token"}