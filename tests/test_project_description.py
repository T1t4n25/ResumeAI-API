# tests/test_project_description.py
"""
Tests for the project descriptions feature.

Endpoints tested (new RESTful path — was /api/resume-flow/generate-project-description):
  POST /project-descriptions        → 201 { id, project_description, project_name, skills, ... }
  GET  /project-descriptions        → 200 { data: [], total: 0, ... }
  GET  /project-descriptions/{id}   → 404 (persistence not yet implemented)

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
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "generated_projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Action verbs used in CV project descriptions
CV_ACTION_VERBS = [
    "developed", "built", "created", "implemented", "designed", "architected",
    "engineered", "constructed", "established", "launched", "led", "managed",
    "delivered", "deployed", "integrated", "optimized",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_payload():
    """Standard project description request payload"""
    return {
        "project_name": "E-commerce Platform",
        "skills": "React, Firebase, Stripe, REST APIs",
        "project_description": "An online store for small businesses with real-time inventory",
    }


@pytest.fixture
def minimal_payload():
    """Minimal payload — only required fields"""
    return {
        "project_name": "Portfolio Website",
        "skills": "HTML, CSS, JavaScript",
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_project_description(description: str, payload: dict) -> dict:
    """Run required and best-practice validations on a generated project description."""
    words = description.split()
    word_count = len(words)

    required = {
        "word_count_in_range": {
            "passed": 15 <= word_count <= 60,
            "detail": f"Word count {word_count} (expected 15–60)",
        },
        "mentions_project_name": {
            "passed": any(
                term.lower() in description.lower()
                for term in payload["project_name"].split()
            ),
            "detail": f"Should mention project name '{payload['project_name']}'",
        },
        "mentions_at_least_one_skill": {
            "passed": any(
                skill.strip().lower() in description.lower()
                for skill in payload["skills"].split(",")
            ),
            "detail": "Should mention at least one skill from the skills list",
        },
    }

    best_practices = {
        "starts_with_action_verb": {
            "passed": any(
                description.lower().startswith(verb)
                for verb in CV_ACTION_VERBS
            ),
            "detail": f"Ideally starts with an action verb like: {', '.join(CV_ACTION_VERBS[:5])}...",
        },
        "uses_technical_term": {
            "passed": bool(
                re.search(
                    r"\b(app|application|website|platform|system|software|service|api)\b",
                    description.lower(),
                )
            ),
            "detail": "Should include technical terminology",
        },
        "has_impact_or_achievement": {
            "passed": any(
                word in description.lower()
                for word in ["improved", "optimized", "enhanced", "increased", "reduced", "scalable", "efficient"]
            ),
            "detail": "Should mention impact or achievement",
        },
    }

    return {"required": required, "best_practices": best_practices}


def save_json_report(description: str, payload: dict, validations: dict, metadata: dict) -> str:
    """Save test results as a JSON file for automation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5((description + timestamp).encode()).hexdigest()[:8]
    filename = f"project_desc_{timestamp}_{content_hash}.json"
    filepath = os.path.join(PROJECTS_DIR, filename)

    report = {
        "metadata": metadata,
        "input": payload,
        "output": {
            "project_description": description,
            "word_count": len(description.split()),
        },
        "validations": validations,
        "summary": {
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
class TestCreateProjectDescription:
    """Tests for POST /project-descriptions"""

    async def test_create_returns_201(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /project-descriptions returns HTTP 201 Created"""
        response = await async_client.post(
            "/project-descriptions",
            json=valid_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

    async def test_create_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /project-descriptions response contains required fields"""
        response = await async_client.post(
            "/project-descriptions",
            json=valid_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        for field in ("id", "project_description", "project_name", "skills", "created_at"):
            assert field in data, f"Response missing required field: '{field}'"
        assert isinstance(data["project_description"], str)
        assert len(data["project_description"]) > 0
        assert data["project_name"] == valid_payload["project_name"]
        assert data["skills"] == valid_payload["skills"]

    async def test_create_content_quality(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        valid_payload: dict,
    ):
        """POST /project-descriptions returns a valid CV-ready project description"""
        start = time.time()
        response = await async_client.post(
            "/project-descriptions",
            json=valid_payload,
            headers=auth_headers,
        )
        elapsed = time.time() - start
        assert response.status_code == 201

        description = response.json()["project_description"]
        validations = validate_project_description(description, valid_payload)

        report_file = save_json_report(
            description=description,
            payload=valid_payload,
            validations=validations,
            metadata={
                "test": "test_create_content_quality",
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

    async def test_create_with_minimal_payload(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
        minimal_payload: dict,
    ):
        """POST /project-descriptions works with only required fields (no description)"""
        response = await async_client.post(
            "/project-descriptions",
            json=minimal_payload,
            headers=auth_headers,
        )
        assert response.status_code == 201

    async def test_create_no_auth_returns_403(
        self,
        async_client: httpx.AsyncClient,
        valid_payload: dict,
    ):
        """POST /project-descriptions without Authorization header returns 403"""
        response = await async_client.post("/project-descriptions", json=valid_payload)
        assert response.status_code == 403

    async def test_create_missing_required_fields(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """POST /project-descriptions with missing required fields returns 422"""
        for bad_payload, description in [
            ({"project_name": "Test"}, "missing skills"),
            ({"skills": "Python"}, "missing project_name"),
            ({}, "empty payload"),
        ]:
            response = await async_client.post(
                "/project-descriptions",
                json=bad_payload,
                headers=auth_headers,
            )
            assert response.status_code == 422, (
                f"Expected 422 for {description}, got {response.status_code}"
            )


@pytest.mark.unit
class TestListProjectDescriptions:
    """Tests for GET /project-descriptions"""

    async def test_list_returns_200(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /project-descriptions returns HTTP 200"""
        response = await async_client.get("/project-descriptions", headers=auth_headers)
        assert response.status_code == 200

    async def test_list_response_shape(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /project-descriptions response has pagination fields"""
        response = await async_client.get("/project-descriptions", headers=auth_headers)
        data = response.json()
        for field in ("data", "total", "limit", "offset"):
            assert field in data, f"Response missing field: '{field}'"
        assert isinstance(data["data"], list)

    async def test_list_no_auth_returns_403(self, async_client: httpx.AsyncClient):
        """GET /project-descriptions without auth returns 403"""
        response = await async_client.get("/project-descriptions")
        assert response.status_code == 403


@pytest.mark.unit
class TestGetProjectDescriptionById:
    """Tests for GET /project-descriptions/{id}"""

    async def test_get_by_id_returns_404(
        self,
        async_client: httpx.AsyncClient,
        auth_headers: dict,
        mock_auth: dict,
    ):
        """GET /project-descriptions/{id} returns 404 (persistence not yet implemented)"""
        response = await async_client.get(
            "/project-descriptions/nonexistent-id-123",
            headers=auth_headers,
        )
        assert response.status_code == 404