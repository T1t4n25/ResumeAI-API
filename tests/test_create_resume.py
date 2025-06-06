import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

api_key = "-oZ7Dhbq-GyYWA-ZSMP9BXNxQjRJpER0lsXqYSh98CE"


@pytest.fixture
def auth_headers():
    """Create headers with API key"""
    return {"X-API-Key": api_key}

@pytest.fixture
def test_data():
    """Test data fixture matching the Pydantic models"""
    return {
        "information": {
            "name": "John Doe",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "address": "123 Main St",
            "linkedin": "linkedin.com/in/johndoe",
            "github": "github.com/johndoe",
            "summary": "Experienced software engineer"
        },
        "education": [
            {
                "degree": "BSc Computer Science",
                "school": "University",
                "start_date": "2016",
                "end_date": "2020",
                "location": "Tanta, Egypt",
                "gpa": "3.8"
            }
        ],
        "projects": [
            {
                "name": "Project A",
                "skills": "Python, FastAPI",
                "description": "Built scalable web application",
                "end_date": "2023"
            }
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "start_date": "2020",
                "end_date": "Present",
                "description": "Led development of key features"
            }
        ],
        "technical_skills": {
            "Programming Languages": ["Python", "FastAPI"],
            "Tools": ["Git", "Docker"]
        },
        "soft_skills": ["Leadership", "Communication"],
        "output_format": "pdf"
    }

@pytest.fixture
def cleanup_output():
    """Cleanup generated files after tests"""
    yield
    output_dir = "generated_resumes"
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))

def test_create_resume_pdf_success(test_data, auth_headers, cleanup_output):
    response = client.post("/api/resume-flow/create-resume", 
                          json=test_data,
                          headers=auth_headers)
    
    assert response.status_code == 200
    assert "pdf_file" in response.json()

def test_create_resume_tex_success(test_data, auth_headers, cleanup_output):
    test_data["output_format"] = "tex"
    response = client.post("/api/resume-flow/create-resume", 
                          json=test_data,
                          headers=auth_headers)
    
    assert response.status_code == 200
    assert "tex_file" in response.json()

def test_create_resume_unauthorized(test_data):
    response = client.post("/api/resume-flow/create-resume", 
                          json=test_data,
                          headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403

# def test_create_resume_invalid_data(auth_headers):
#     invalid_data = {
#         "information": {
#             "name": "John Doe"
#             # Missing required fields
#         },
#         "output_format": "pdf"
#     }
    
#     response = client.post("/api/resume-flow/create-resume", 
#                           json=invalid_data,
#                           headers=auth_headers)
#     assert response.status_code == 422