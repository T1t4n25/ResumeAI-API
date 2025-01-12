# tests/test_project_description.py
import sys
import os
import re
import pytest
import time
import hashlib
from datetime import datetime
from fastapi.testclient import TestClient
from typing import List, Dict

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Create test client
client = TestClient(app)

# Create directory for generated project descriptions
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "generated_projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Action verbs for validation
ACTION_VERBS = [
    "developed", "built", "created", "implemented", 
    "designed", "architected", "engineered", "constructed",
    "established", "launched", "led", "managed", "orchestrated"
]

def save_project_description(description: str, metadata: dict) -> str:
    """Save generated project description with metadata"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5((description + timestamp).encode()).hexdigest()[:8]
        filename = f"project_{timestamp}_{content_hash}.txt"
        filepath = os.path.join(PROJECTS_DIR, filename)
        
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
    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return None

@pytest.fixture
def api_key():
    """Get API key for testing"""
    response = client.get("/generate-api-key")
    assert response.status_code == 200, "Failed to generate API key"
    return response.json()["api_key"]

@pytest.fixture
def test_payload():
    """Test payload for project description"""
    return {
        "project_name": "E-commerce Website",
        "skills": "React, Firebase, Stripe"
    }

def test_project_description_generation(api_key, test_payload):
    """Test project description generation"""
    print("\nTesting Project Description Generation")
    print("="*80)
    
    # Generate project description
    response = client.post(
        "/generate-project-description",
        json=test_payload,
        headers={"X-API-Key": api_key}
    )
    
    # Print response for debugging
    print("\nAPI Response:", response.text)
    
    # Check response status
    assert response.status_code == 200, f"API call failed with status {response.status_code}: {response.text}"
    
    # Extract description
    result = response.json()
    assert "project_description" in result, "Response missing 'project_description' field"
    
    description = result["project_description"]
    word_count = len(description.split())
    
    print("\nGenerated Description:")
    print("-"*80)
    print(description)
    print("-"*80)
    print(f"Word Count: {word_count}")
    
    # Basic validations
    assert 15 <= word_count <= 50, f"Word count {word_count} outside range 15-50"
    
    # Save the description
    filename = save_project_description(
        description,
        {
            "Project Name": test_payload["project_name"],
            "Skills": test_payload["skills"],
            "Word Count": word_count
        }
    )
    
    assert filename is not None, "Failed to save project description"
    print(f"\nSaved to: {filename}")
    
    # Content validations
    validations = {
        "Project Name": any(term.lower() in description.lower() 
                          for term in test_payload["project_name"].split()),
        "Skills": any(skill.lower() in description.lower() 
                     for skill in test_payload["skills"].split(", ")),
        "Action Verb": any(description.lower().startswith(verb) 
                          for verb in ACTION_VERBS)
    }
    
    print("\nValidation Results:")
    print("-"*80)
    for criterion, passed in validations.items():
        print(f"{criterion:15}: {'✓' if passed else '✗'}")
        assert passed, f"Validation failed for {criterion}"

def test_invalid_api_key(test_payload):
    """Test with invalid API key"""
    print("\nTesting Invalid API Key")
    print("="*80)
    
    response = client.post(
        "/generate-project-description",
        json=test_payload,
        headers={"X-API-Key": "invalid_key"}
    )
    
    assert response.status_code == 403, \
        f"Expected 403 status code for invalid API key, got {response.status_code}"
    print("✓ Invalid API key test passed")

def test_missing_fields(api_key):
    """Test missing required fields"""
    print("\nTesting Missing Fields")
    print("="*80)
    
    test_cases = [
        ({"project_name": "Test Project"}, "Missing skills"),
        ({"skills": "Python, FastAPI"}, "Missing project name"),
        ({}, "Empty payload")
    ]
    
    for payload, case in test_cases:
        print(f"\nTesting: {case}")
        response = client.post(
            "/generate-project-description",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 422, \
            f"Expected 422 for {case}, got {response.status_code}"
        print(f"✓ Correctly failed with 422")

def test_response_time(api_key, test_payload):
    """Test response time"""
    print("\nTesting Response Time")
    print("="*80)
    
    start_time = time.time()
    response = client.post(
        "/generate-project-description",
        json=test_payload,
        headers={"X-API-Key": api_key}
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200, "API call failed during performance test"
    assert response_time < 10, f"Response took {response_time:.2f} seconds (limit: 10s)"
    
    print(f"Response time: {response_time:.2f} seconds")
    print("✓ Performance test passed")