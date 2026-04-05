# tests/test_summary.py
"""
Tests for the summaries feature.

Endpoints tested (new RESTful path — was /api/resume-flow/generate-summary):
  POST /summaries        → 201 { id, summary, current_title, years_experience, skills, ... }
  GET  /summaries        → 200 { data: [], total: 0, ... }
  GET  /summaries/{id}   → 404 (persistence not yet implemented)

Auth: Bearer token header (Keycloak JWT — mocked in unit tests via dependency override)
"""
import os
import json
import time
import pytest
import hashlib
import httpx
from datetime import datetime

# ---------------------------------------------------------------------------
# Output directory for generated content
# ---------------------------------------------------------------------------
SUMMARIES_DIR = os.path.join(os.path.dirname(__file__), "generated_summaries")
os.makedirs(SUMMARIES_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_payload():
    """Standard summary creation request payload"""
    return {
        "current_title": "Senior Software Engineer",
        "years_experience": "5+ years",
        "skills": "Python, React, AWS, Microservices",
        "achievements": "Led team of 5, Reduced system latency by 40%",
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_summary(summary: str, payload: dict) -> dict:
    """Run required and best-practice validations on generated summary text."""
    words = summary.split()
    word_count = len(words)

    required = {
        "word_count_in_range": {
            "passed": 40 <= word_count <= 100,
            "detail": f"Word count {word_count} (expected 40–100)",
        },
        "mentions_title": {
            "passed": payload["current_title"].lower() in summary.lower(),
            "detail": f"Summary should mention title '{payload['current_title']}'",
        },
        "mentions_experience": {
            "passed": any(
                part in summary.lower()
                for part in payload["years_experience"].lower().split()
                if part.isdigit() or "+" in part
            ) or payload["years_experience"].lower() in summary.lower(),
            "detail": f"Summary should mention '{payload['years_experience']}'",
        },
        "mentions_at_least_one_skill": {
            "passed": any(
                skill.strip().lower() in summary.lower()
                for skill in payload["skills"].split(",")
            ),
            "detail": "Summary should mention at least one skill",
        },
    }

    best_practices = {
        "mentions_multiple_skills": {
            "passed": sum(
                1 for skill in payload["skills"].split(",")
                if skill.strip().lower() in summary.lower()
            ) >= 2,
            "detail": "Ideally mentions 2+ skills",
        },
        "uses_achievement_language": {
            "passed": any(
                word in summary.lower()
                for word in ["achieved", "reduced", "improved", "led", "developed", "delivered", "optimized"]
            ),
            "detail": "Should use achievement-focused language",
        },
        "has_value_proposition": {
            "passed": any(
                phrase in summary.lower()
                for phrase in ["expertise", "specialized", "proven", "experienced", "skilled", "accomplished"]
            ),
            "detail": "Should contain a value proposition phrase",
        },
        "has_metrics": {
            "passed": any(char.isdigit() for char in summary),
            "detail": "Should contain numerical metrics",
        },
    }

    return {"required": required, "best_practices": best_practices}


def save_json_report(summary: str, payload: dict, validations: dict, metadata: dict) -> str:
    """Save test results as a JSON file for automation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5((summary + timestamp).encode()).hexdigest()[:8]
    filename = f"summary_{timestamp}_{content_hash}.json"
    filepath = os.path.join(SUMMARIES_DIR, filename)

    report = {
        "metadata": metadata,
        "input": payload,
        "output": {
            "summary": summary,
            "word_count": len(summary.split()),
        },
        "validations": validations,
        "summary_stats": {
            "required_passed": sum(1 for v in validations["required"].values() if v["passed"]),
            "required_total": len(validations["required"]),
            "best_practices_passed": sum(1 for v in validations["best_practices"].values() if v["passed"]),
            "best_practices_total": len(validations["best_practices"]),
        },
    }

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return filename


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestCreateSummary:
    """Tests for POST /summaries"""

    async def test_create_summary_returns_201(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /summaries returns HTTP 201 Created"""
        response = await async_client.post(
            "/summaries",
            json=valid_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

    async def test_create_summary_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /summaries response contains required fields"""
        response = await async_client.post(
            "/summaries",
            json=valid_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        for field in ("id", "summary", "current_title", "years_experience", "skills", "created_at"):
            assert field in data, f"Response missing required field: '{field}'"
        assert isinstance(data["summary"], str)
        assert len(data["summary"]) > 0
        assert data["current_title"] == valid_payload["current_title"]

    async def test_create_summary_content_quality(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /summaries returns a well-written professional summary"""
        start = time.time()
        response = await async_client.post(
            "/summaries",
            json=valid_payload,
            headers=auth_headers,
        )
        elapsed = time.time() - start
        assert response.status_code == 201

        summary = response.json()["summary"]
        validations = validate_summary(summary, valid_payload)

        report_file = save_json_report(
            summary=summary,
            payload=valid_payload,
            validations=validations,
            metadata={
                "test": "test_create_summary_content_quality",
                "generated_at": datetime.now().isoformat(),
                "response_time_seconds": round(elapsed, 2),
                "api_version": "5.0.0",
            },
        )
        print(f"\n  Report saved: {report_file}")

        failed = [k for k, v in validations["required"].items() if not v["passed"]]
        assert not failed, "Required validations failed:\n" + "\n".join(
            f"  - {k}: {validations['required'][k]['detail']}" for k in failed
        )

    async def test_create_summary_no_auth_returns_403(
        self,
        async_client: httpx.AsyncClient,
        valid_payload: dict,
    ):
        """POST /summaries without Authorization header returns 403"""
        response = await async_client.post("/summaries", json=valid_payload)
        assert response.status_code == 403

    async def test_create_summary_missing_required_fields(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /summaries with missing required fields returns 422"""
        for required_field in ("current_title", "years_experience", "skills"):
            payload = valid_payload.copy()
            del payload[required_field]
            response = await async_client.post(
                "/summaries",
                json=payload,
                headers=auth_headers,
            )
            assert response.status_code == 422, (
                f"Expected 422 when '{required_field}' is missing, got {response.status_code}"
            )


@pytest.mark.unit
class TestListSummaries:
    """Tests for GET /summaries"""

    async def test_list_summaries_returns_200(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /summaries returns HTTP 200"""
        response = await async_client.get("/summaries", headers=auth_headers)
        assert response.status_code == 200

    async def test_list_summaries_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /summaries response has pagination fields"""
        response = await async_client.get("/summaries", headers=auth_headers)
        data = response.json()
        for field in ("data", "total", "limit", "offset"):
            assert field in data, f"Response missing field: '{field}'"
        assert isinstance(data["data"], list)

    async def test_list_summaries_no_auth_returns_403(
        self,
        async_client: httpx.AsyncClient,
    ):
        """GET /summaries without auth returns 403"""
        response = await async_client.get("/summaries")
        assert response.status_code == 403


@pytest.mark.unit
class TestGetSummaryById:
    """Tests for GET /summaries/{id}"""

    async def test_get_summary_by_id_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /summaries/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.get(
            "/summaries/nonexistent-id-123",
            headers=auth_headers,
        )
        assert response.status_code == 404