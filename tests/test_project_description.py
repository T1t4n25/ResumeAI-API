# tests/test_project_description.py
import sys
import os
import re
import pytest
import time
import hashlib
from datetime import datetime
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Create test client
client = TestClient(app)

# Create directory for generated project descriptions
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "generated_projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

def save_project_description(description: str, metadata: dict) -> str:
    """
    Save generated project description with metadata
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create hash from content
    content_hash = hashlib.md5(
        (description + timestamp).encode()
    ).hexdigest()[:8]
    
    # Create filename
    filename = f"project_{timestamp}_{content_hash}.txt"
    filepath = os.path.join(PROJECTS_DIR, filename)
    
    # Save content with metadata
    with open(filepath, 'w') as f:
        f.write("="*80 + "\n")
        f.write("PROJECT DESCRIPTION METADATA:\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("GENERATED DESCRIPTION:\n")
        f.write("="*80 + "\n\n")
        f.write(description)
        f.write("\n\n" + "="*80 + "\n")
        f.write(f"Word Count: {len(description.split())}\n")
        f.write("="*80 + "\n")
    
    return filename

@pytest.fixture
def api_key():
    """Get API key for testing"""
    response = client.get("/generate-api-key")
    assert response.status_code == 200
    return response.json()["api_key"]

@pytest.fixture
def project_payloads():
    """Different test payloads"""
    return [
        {
            "project_name": "E-commerce Website",
            "skills": "React, Firebase, Stripe, REST APIs",
            "project_description": "Built a website for an online store. Users can browse products, add to cart, and checkout."
        },
        {
            "project_name": "Task Manager",
            "skills": "Python, FastAPI, PostgreSQL",
            # No description provided
        },
        {
            "project_name": "Portfolio Site",
            "skills": "HTML, CSS, JavaScript",
            "project_description": "Personal portfolio showcasing my projects."
        }
    ]

def test_project_description_generation(api_key, project_payloads):
    """
    Test project description generation with various payloads
    """
    for payload in project_payloads:
        # Generate project description
        response = client.post(
            "/generate-project-description",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        # Basic response checks
        assert response.status_code == 200, f"API call failed: {response.text}"
        
        # Extract description
        result = response.json()
        assert "project_description" in result, "No project description in response"
        
        description = result["project_description"]
        
        # Word count validation
        word_count = len(description.split())
        assert 15 <= word_count <= 50, f"Description length ({word_count} words) outside allowed range (15-50 words)"
        
        # Content validation
        validations = [
            # Contains project name or key terms
            any(term.lower() in description.lower() 
                for term in payload["project_name"].split()),
            
            # Contains mentioned skills
            any(skill.lower() in description.lower() 
                for skill in payload["skills"].split(", ")),
            
            # Starts with action verb
            any(verb in description.lower().split()[0] 
                for verb in ["developed", "built", "created", "implemented", 
                            "designed", "architected", "engineered"])
        ]
        
        assert all(validations), "Project description validation failed"
        
        # Save to file
        filename = save_project_description(
            description,
            {
                "Project Name": payload["project_name"],
                "Skills": payload["skills"],
                "Description": payload.get("project_description", "Not provided")
            }
        )
        
        # Print results
        print(f"\nTesting Project: {payload['project_name']}")
        print("="*80)
        print("Generated Description:")
        print(description)
        print("-"*80)
        print(f"Word Count: {word_count}")
        print(f"Saved to: {filename}")
        print("="*80)

def test_invalid_api_key():
    """Test with invalid API key"""
    payload = {
        "project_name": "Test Project",
        "skills": "Python, FastAPI"
    }
    
    response = client.post(
        "/generate-project-description",
        json=payload,
        headers={"X-API-Key": "invalid_key"}
    )
    
    assert response.status_code == 403

def test_missing_required_fields(api_key):
    """Test validation of required fields"""
    invalid_payloads = [
        {"project_name": "Test Project"},  # Missing skills
        {"skills": "Python, FastAPI"},     # Missing project name
        {}                                 # Missing all fields
    ]
    
    for payload in invalid_payloads:
        response = client.post(
            "/generate-project-description",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 422, f"Expected validation error for payload: {payload}"

def test_response_time(api_key):
    """Test response time"""
    payload = {
        "project_name": "Performance Test Project",
        "skills": "Python, FastAPI",
        "project_description": "Testing response time."
    }
    
    start_time = time.time()
    response = client.post(
        "/generate-project-description",
        json=payload,
        headers={"X-API-Key": api_key}
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 10, f"Response took too long: {response_time} seconds"
    assert response.status_code == 200