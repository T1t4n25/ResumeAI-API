# tests/test_interviews.py
"""
Tests for the interviews feature.

Endpoints tested:
  POST   /interviews/rooms              → SKIPPED (requires LiveKit)
  GET    /interviews/rooms              → 200 { data: [], total: 0, ... }
  GET    /interviews/rooms/{room_id}    → 404 (persistence not yet implemented)
  POST   /interviews/rooms/{id}/start   → SKIPPED (requires LiveKit)
  DELETE /interviews/rooms/{room_id}    → 404 (persistence not yet implemented)

Note: Any test that touches LiveKit (create room, start interviewer) is intentionally
      skipped in the local test suite. These require a real LiveKit connection.
"""
import pytest
import httpx


SKIP_LIVEKIT = pytest.mark.skip(reason="Skipped: requires LiveKit connection (not available in local tests)")


@pytest.mark.unit
class TestListInterviewRooms:
    """Tests for GET /interviews/rooms (stub — always returns empty list)"""

    async def test_list_rooms_returns_200(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /interviews/rooms returns HTTP 200"""
        response = await async_client.get("/interviews/rooms", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    async def test_list_rooms_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /interviews/rooms response has pagination structure"""
        response = await async_client.get("/interviews/rooms", headers=auth_headers)
        data = response.json()
        for field in ("data", "total", "limit", "offset"):
            assert field in data, f"Response missing field: '{field}'"
        assert isinstance(data["data"], list)

    async def test_list_rooms_no_auth_returns_403(self, async_client: httpx.AsyncClient):
        """GET /interviews/rooms without auth returns 403"""
        response = await async_client.get("/interviews/rooms")
        assert response.status_code == 403


@pytest.mark.unit
class TestGetInterviewRoom:
    """Tests for GET /interviews/rooms/{room_id} (stub — returns 404)"""

    async def test_get_room_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /interviews/rooms/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.get(
            "/interviews/rooms/nonexistent-room-id",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.unit
class TestDeleteInterviewRoom:
    """Tests for DELETE /interviews/rooms/{room_id} (stub — returns 404)"""

    async def test_delete_room_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """DELETE /interviews/rooms/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.delete(
            "/interviews/rooms/nonexistent-room-id",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestCreateInterviewRoom:
    """Tests for POST /interviews/rooms — SKIPPED: requires LiveKit"""

    @SKIP_LIVEKIT
    async def test_create_room_returns_201(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """POST /interviews/rooms returns 201 with room details"""
        response = await async_client.post("/interviews/rooms", headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        for field in ("id", "room_name", "token", "websocket_url", "status"):
            assert field in data

    @SKIP_LIVEKIT
    async def test_create_room_no_auth_returns_403(self, async_client: httpx.AsyncClient):
        """POST /interviews/rooms without auth returns 403"""
        response = await async_client.post("/interviews/rooms")
        assert response.status_code == 403


class TestStartInterviewer:
    """Tests for POST /interviews/rooms/{id}/start — SKIPPED: requires LiveKit"""

    @SKIP_LIVEKIT
    async def test_start_interviewer_returns_200(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """POST /interviews/rooms/{id}/start returns 200"""
        response = await async_client.post(
            "/interviews/rooms/some-room-id/start",
            json={"resume": "My resume text", "job_description": "Software Engineer role"},
            headers=auth_headers,
        )
        assert response.status_code == 200
