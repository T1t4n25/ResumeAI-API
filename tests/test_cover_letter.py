# tests/test_cover_letter.py
"""
Tests for the cover letters feature.

Endpoints tested (new RESTful path — was /api/resume-flow/generate-cover-letter):
  POST   /cover-letters       → 201 { id, cover_letter, tokens_used, created_at }
  GET    /cover-letters       → 200 { data: [], total: 0, ... }
  GET    /cover-letters/{id}  → 404 (persistence not yet implemented)
  DELETE /cover-letters/{id}  → 404 (persistence not yet implemented)

Auth: Bearer token header (Keycloak JWT — mocked in unit tests via dependency override)
"""
import re
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
COVER_LETTERS_DIR = os.path.join(os.path.dirname(__file__), "generated_cover_letters")
os.makedirs(COVER_LETTERS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_payload():
    """Standard cover letter request payload"""
    return {
        "job_post": (
            "Senior .NET Developer at TechInnovate Solutions. We are seeking an experienced "
            ".NET professional with strong skills in C#, .NET Core, and cloud technologies. "
            "Responsibilities include developing scalable web applications, implementing "
            "microservices architecture, and collaborating with cross-functional teams."
        ),
        "user_name": "John Doe",
        "user_degree": "Bachelor of Science in Computer Science",
        "user_title": "Software Engineer",
        "user_experience": "5 years of professional .NET development experience",
        "user_skills": "C#, .NET Core, Azure, SQL Server, RESTful APIs",
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_cover_letter(cover_letter: str, payload: dict) -> dict:
    """
    Run required and best-practice validations on generated cover letter content.
    Returns a results dict suitable for saving as JSON.
    """
    words = cover_letter.split()
    word_count = len(words)
    experience_numbers = re.findall(r"\d+", payload.get("user_experience", ""))
    experience_num = experience_numbers[0] if experience_numbers else None

    required = {
        "word_count_in_range": {
            "passed": 200 <= word_count <= 450,
            "detail": f"Word count {word_count} (expected 200–450)",
        },
        "has_salutation": {
            "passed": "Dear" in cover_letter,
            "detail": "Cover letter must contain 'Dear'",
        },
        "has_closing": {
            "passed": "Sincerely" in cover_letter or "Regards" in cover_letter,
            "detail": "Cover letter must contain 'Sincerely' or 'Regards'",
        },
        "contains_name": {
            "passed": payload["user_name"] in cover_letter,
            "detail": f"Name '{payload['user_name']}' not found in cover letter",
        },
    }

    best_practices = {
        "mentions_title_or_degree": {
            "passed": (
                payload.get("user_title", "") in cover_letter
                or payload.get("user_degree", "") in cover_letter
            ),
            "detail": "Should mention applicant title or degree",
        },
        "mentions_skills": {
            "passed": any(
                skill.strip() in cover_letter
                for skill in payload.get("user_skills", "").split(",")
            ),
            "detail": "Should mention at least one skill from user_skills",
        },
        "mentions_experience_years": {
            "passed": bool(experience_num and experience_num in cover_letter),
            "detail": f"Should mention {experience_num} years of experience",
        },
        "references_position": {
            "passed": any(word in cover_letter.lower() for word in ["position", "role", "opportunity"]),
            "detail": "Should reference the position or role",
        },
        "uses_achievement_words": {
            "passed": any(
                word in cover_letter.lower()
                for word in ["achieved", "developed", "improved", "led", "managed", "delivered"]
            ),
            "detail": "Should use action/achievement words",
        },
    }

    return {"required": required, "best_practices": best_practices}


def save_json_report(cover_letter: str, payload: dict, validations: dict, metadata: dict) -> str:
    """Save test results as a JSON file for automation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5((cover_letter + timestamp).encode()).hexdigest()[:8]
    filename = f"cover_letter_{timestamp}_{content_hash}.json"
    filepath = os.path.join(COVER_LETTERS_DIR, filename)

    report = {
        "metadata": metadata,
        "input": payload,
        "output": {
            "cover_letter": cover_letter,
            "word_count": len(cover_letter.split()),
        },
        "validations": validations,
        "summary": {
            "required_passed": sum(
                1 for v in validations["required"].values() if v["passed"]
            ),
            "required_total": len(validations["required"]),
            "best_practices_passed": sum(
                1 for v in validations["best_practices"].values() if v["passed"]
            ),
            "best_practices_total": len(validations["best_practices"]),
        },
    }

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2, default=str)

    return filename


# ---------------------------------------------------------------------------
# Unit tests (fast — mock auth, real AI)
# ---------------------------------------------------------------------------

@pytest.mark.slow
class TestCreateCoverLetter:
    """Tests for POST /cover-letters (creates cover letter via Gemini AI)"""

    async def test_create_cover_letter_returns_201(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /cover-letters returns HTTP 201 Created"""
        start = time.time()
        response = await async_client.post(
            "/cover-letters",
            json=valid_payload,
            headers=auth_headers,
        )
        elapsed = time.time() - start
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )
        print(f"\n  Response time: {elapsed:.2f}s")

    async def test_create_cover_letter_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /cover-letters response contains required fields"""
        response = await async_client.post(
            "/cover-letters",
            json=valid_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        for field in ("id", "cover_letter", "created_at"):
            assert field in data, f"Response missing required field: '{field}'"
        assert isinstance(data["cover_letter"], str)
        assert len(data["cover_letter"]) > 0

    async def test_create_cover_letter_content_quality(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /cover-letters returns a valid, high-quality cover letter"""
        start = time.time()
        response = await async_client.post(
            "/cover-letters",
            json=valid_payload,
            headers=auth_headers,
        )
        elapsed = time.time() - start
        assert response.status_code == 201
        cover_letter = response.json()["cover_letter"]

        validations = validate_cover_letter(cover_letter, valid_payload)

        report_file = save_json_report(
            cover_letter=cover_letter,
            payload=valid_payload,
            validations=validations,
            metadata={
                "test": "test_create_cover_letter_content_quality",
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

    async def test_create_cover_letter_no_auth_returns_403(
        self,
        async_client: httpx.AsyncClient,
        valid_payload: dict,
    ):
        """POST /cover-letters without Authorization header returns 403"""
        response = await async_client.post("/cover-letters", json=valid_payload)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    async def test_create_cover_letter_missing_required_fields(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /cover-letters with missing required fields returns 422"""
        for required_field in ("job_post", "user_name"):
            payload = valid_payload.copy()
            del payload[required_field]
            response = await async_client.post(
                "/cover-letters",
                json=payload,
                headers=auth_headers,
            )
            assert response.status_code == 422, (
                f"Expected 422 when '{required_field}' is missing, got {response.status_code}"
            )


@pytest.mark.unit
class TestListCoverLetters:
    """Tests for GET /cover-letters"""

    async def test_list_cover_letters_returns_200(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /cover-letters returns HTTP 200"""
        response = await async_client.get("/cover-letters", headers=auth_headers)
        assert response.status_code == 200

    async def test_list_cover_letters_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /cover-letters response has pagination fields"""
        response = await async_client.get("/cover-letters", headers=auth_headers)
        data = response.json()
        for field in ("data", "total", "limit", "offset"):
            assert field in data, f"Response missing field: '{field}'"
        assert isinstance(data["data"], list)

    async def test_list_cover_letters_no_auth_returns_403(
        self,
        async_client: httpx.AsyncClient,
    ):
        """GET /cover-letters without auth returns 403"""
        response = await async_client.get("/cover-letters")
        assert response.status_code == 403


@pytest.mark.unit
class TestGetCoverLetterById:
    """Tests for GET /cover-letters/{id}"""

    async def test_get_cover_letter_by_id_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /cover-letters/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.get(
            "/cover-letters/nonexistent-id-123",
            headers=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.unit
class TestDeleteCoverLetter:
    """Tests for DELETE /cover-letters/{id}"""

    async def test_delete_cover_letter_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """DELETE /cover-letters/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.delete(
            "/cover-letters/nonexistent-id-123",
            headers=auth_headers,
        )
        assert response.status_code == 404