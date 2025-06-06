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

api_key = "-oZ7Dhbq-GyYWA-ZSMP9BXNxQjRJpER0lsXqYSh98CE"

API_VERSION = "3.0.0"

# Create directory for generated project descriptions
PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "generated_projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Action verbs for validation
ACTION_VERBS = [
    "developed", "built", "created", "implemented", 
    "designed", "architected", "engineered", "constructed",
    "established", "launched", "led", "managed", "orchestrated"
]


@pytest.fixture
def valid_payload():
    """Test payload for project description"""
    return {
        "project_name": "E-commerce Website",
        "skills": "React, Firebase, Stripe"
    }

def validate_project_description(description: str, payload: dict) -> dict:
    """
    Comprehensive project description validation
    """
    # Count words in description
    word_count = len(description.split())
    
    # Required checks
    required_validations = {
        "Word Count": (
            15 <= word_count <= 50,
            f"Word count ({word_count}) outside range 15-50 words"
        ),
        "Project Name": (
            any(term.lower() in description.lower() for term in payload["project_name"].split()),
            "Project name not mentioned"
        ),
        "Skills": (
            any(skill.lower() in description.lower() for skill in payload["skills"].split(", ")),
            "Skills not included"
        ),
    }

    # Best practices checks
    best_practices = {
        "Action Verb Start": (
            any(description.lower().startswith(verb) for verb in ACTION_VERBS),
            "Consider starting with an action verb"
        ),
        "Technical Terms": (
            bool(re.search(r'(app|application|website|platform|system|software)', description.lower())),
            "Consider including technical terms"
        ),
        "Achievement Focus": (
            any(word in description.lower() for word in ["improved", "optimized", "enhanced", "increased", "reduced"]),
            "Consider mentioning achievements or improvements"
        ),
        "Specificity": (
            bool(re.search(r'(\d+%|\d+ times|\d+ users)', description.lower())),
            "Consider adding specific metrics or numbers"
        )
    }

    return {
        "required": required_validations,
        "best_practices": best_practices
    }

def save_test_report(description: str, payload: dict, 
                   validations: dict, metadata: dict) -> str:
    """Save complete test report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5((description + timestamp).encode()).hexdigest()[:8]
    filename = f"project_description_report_{timestamp}_{content_hash}.txt"
    filepath = os.path.join(PROJECTS_DIR, filename)
    
    with open(filepath, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("PROJECT DESCRIPTION GENERATION REPORT\n")
        f.write("="*80 + "\n\n")

        # Metadata
        f.write("TEST METADATA:\n")
        f.write("-"*40 + "\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
        
        # Input Data
        f.write("\nINPUT PARAMETERS:\n")
        f.write("-"*40 + "\n")
        for key, value in payload.items():
            f.write(f"{key}: {value}\n")

        # Generated Project Description
        f.write("\n" + "="*80 + "\n")
        f.write("GENERATED PROJECT DESCRIPTION:\n")
        f.write("="*80 + "\n\n")
        f.write(description)
        
        # Statistics
        f.write("\n\n" + "="*80 + "\n")
        f.write("STATISTICS:\n")
        f.write("-"*40 + "\n")
        f.write(f"Word Count: {len(description.split())}\n")
        
        # Validation Results
        f.write("\nVALIDATION RESULTS:\n")
        f.write("="*80 + "\n")
        
        # Required Criteria
        f.write("\nRequired Criteria:\n")
        f.write("-"*40 + "\n")
        for criterion, (passed, message) in validations["required"].items():
            f.write(f"{criterion:20}: {'✓' if passed else '✗'}\n")
        
        # Best Practices
        f.write("\nBest Practices:\n")
        f.write("-"*40 + "\n")
        for criterion, (passed, message) in validations["best_practices"].items():
            f.write(f"{criterion:20}: {'✓' if passed else '○'}\n")
        
        # Failed Validations
        failed_required = [(c, m) for c, (p, m) in validations["required"].items() if not p]
        missed_practices = [(c, m) for c, (p, m) in validations["best_practices"].items() if not p]
        
        if failed_required:
            f.write("\nFAILED REQUIRED CRITERIA:\n")
            f.write("-"*40 + "\n")
            for criterion, message in failed_required:
                f.write(f"- {criterion}: {message}\n")
        
        if missed_practices:
            f.write("\nBEST PRACTICE SUGGESTIONS:\n")
            f.write("-"*40 + "\n")
            for criterion, message in missed_practices:
                f.write(f"- {criterion}: {message}\n")
        
        # Summary
        f.write("\nSUMMARY:\n")
        f.write("-"*40 + "\n")
        f.write(f"Required Criteria Met: {len(validations['required']) - len(failed_required)}/{len(validations['required'])}\n")
        f.write(f"Best Practices Met: {len(validations['best_practices']) - len(missed_practices)}/{len(validations['best_practices'])}\n")
    
    return filename

def test_project_description_generation(valid_payload):
    """Test project description generation"""
    print("\nTesting Project Description Generation")
    print("="*80)
    
    # Generate project description
    start_time = time.time()
    response = client.post(
        "/api/resume-flow/generate-project-description",
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    generation_time = time.time() - start_time
    
    # Check response
    assert response.status_code == 200, f"API call failed: {response.text}"
    
    # Extract description
    result = response.json()
    assert "project_description" in result, "No project_description in response"
    description = result["project_description"]
    
    # Run validations
    validations = validate_project_description(description, valid_payload)
    
    # Save comprehensive report
    filename = save_test_report(
        description=description,
        payload=valid_payload,
        validations=validations,
        metadata={
            "Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Response Time": f"{generation_time:.2f} seconds",
            "API Version": API_VERSION,
            "Model": "Gemini Pro"        }
    )
    
    # Print summary
    print(f"\nReport saved to: {filename}")
    print("\nValidation Summary:")
    print("-"*40)
    
    failed_required = [(c, m) for c, (p, m) in validations["required"].items() if not p]
    missed_practices = [(c, m) for c, (p, m) in validations["best_practices"].items() if not p]
    
    print(f"Required Criteria Met: {len(validations['required']) - len(failed_required)}/{len(validations['required'])}")
    print(f"Best Practices Met: {len(validations['best_practices']) - len(missed_practices)}/{len(validations['best_practices'])}")
    
    # Assert only required validations
    assert len(failed_required) == 0, "\n".join(f"- {c}: {m}" for c, m in failed_required)

def test_invalid_api_key(valid_payload):
    """Test with invalid API key"""
    response = client.post(
        "/api/resume-flow/generate-project-description",
        json=valid_payload,
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 403, "Expected forbidden access with invalid API key"

def test_missing_fields():
    """Test missing required fields"""
    test_cases = [
        ({"project_name": "Test Project"}, "Missing skills"),
        ({"skills": "Python, FastAPI"}, "Missing project name"),
        ({}, "Empty payload")
    ]
    
    for payload, case in test_cases:
        print(f"\nTesting: {case}")
        response = client.post(
            "/api/resume-flow/generate-project-description",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 422, \
            f"Expected 422 for {case}, got {response.status_code}"

def test_response_time(valid_payload):
    """Test response time"""
    print("\nTesting Response Time")
    print("="*80)
    
    start_time = time.time()
    response = client.post(
        "/api/resume-flow/generate-project-description",
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    end_time = time.time()
    
    response_time = end_time - start_time
    
    assert response.status_code == 200, "API call failed during performance test"
    assert response_time < 10, f"Response took {response_time:.2f} seconds (limit: 10s)"
    
    print(f"Response time: {response_time:.2f} seconds")
    print("✓ Performance test passed")

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/resume-flow/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}