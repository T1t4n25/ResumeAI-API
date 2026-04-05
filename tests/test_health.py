# tests/test_health.py
"""
Tests for public health endpoints.

Endpoints tested:
  GET /health  → 200 { status, version, environment }
  GET /        → 200 { message, version, endpoints, architecture }
"""
import pytest
import httpx


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for GET /health"""

    async def test_health_check_status_200(self, async_client: httpx.AsyncClient):
        """Health endpoint returns HTTP 200"""
        response = await async_client.get("/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    async def test_health_check_response_fields(self, async_client: httpx.AsyncClient):
        """Health endpoint returns required fields"""
        response = await async_client.get("/health")
        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert "version" in data, "Response missing 'version' field"
        assert "environment" in data, "Response missing 'environment' field"

    async def test_health_check_status_value(self, async_client: httpx.AsyncClient):
        """Health endpoint returns status: healthy"""
        response = await async_client.get("/health")
        assert response.json()["status"] == "healthy"

    async def test_health_no_auth_required(self, async_client: httpx.AsyncClient):
        """Health endpoint is publicly accessible — no auth header needed"""
        response = await async_client.get("/health")
        # Must NOT return 401 or 403
        assert response.status_code not in (401, 403), "Health endpoint should not require auth"


@pytest.mark.unit
class TestRootEndpoint:
    """Tests for GET /"""

    async def test_root_status_200(self, async_client: httpx.AsyncClient):
        """Root endpoint returns HTTP 200"""
        response = await async_client.get("/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    async def test_root_response_fields(self, async_client: httpx.AsyncClient):
        """Root endpoint returns required fields"""
        response = await async_client.get("/")
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data

    async def test_root_endpoints_includes_features(self, async_client: httpx.AsyncClient):
        """Root endpoint lists all feature groups"""
        response = await async_client.get("/")
        endpoints = response.json().get("endpoints", {})
        for group in ["cover_letters", "summaries", "project_descriptions", "interviews", "auth"]:
            assert group in endpoints, f"Missing endpoint group '{group}' in root response"
