# tests/test_cover_letter.py
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

# Create directory for generated cover letters
COVER_LETTERS_DIR = os.path.join(os.path.dirname(__file__), "generated_cover_letters")
os.makedirs(COVER_LETTERS_DIR, exist_ok=True)
api_key = "-oZ7Dhbq-GyYWA-ZSMP9BXNxQjRJpER0lsXqYSh98CE"

@pytest.fixture
def valid_payload():
    """Test payload for cover letter generation"""
    return {
        "job_post": "Senior .NET Developer at TechInnovate Solutions. We are seeking an experienced .NET professional with strong skills in C#, .NET Core, and cloud technologies. Responsibilities include developing scalable web applications, implementing microservices architecture, and collaborating with cross-functional teams.",
        "user_name": "John Doe",
        "user_degree": "Bachelor of Science in Computer Science",
        "user_title": "Software Engineer",
        "user_experience": "5 years of professional .NET development experience",
        "user_skills": "C#, .NET Core, Azure, SQL Server, RESTful APIs"
    }
    
def validate_cover_letter(cover_letter: str, payload: dict) -> dict:
    """
    Comprehensive cover letter validation
    """
    # Count words in cover letter
    word_count = len(cover_letter.split())
    
    # Get the experience number
    experience_text = payload['user_experience']
    numbers_found = re.findall(r'\d+', experience_text)
    experience_number = numbers_found[0] if numbers_found else None
    
    print(f"\nChecking experience number:")
    print(f"Found in input: {experience_number}")
    print(f"Found in cover letter: {experience_number in cover_letter}")
    
    # Required checks
    required_validations = {
        "Word Count": (
            200 <= word_count <= 400,
            f"Word count ({word_count}) outside range 200-400 words"
        ),
        "Salutation": (
            "Dear" in cover_letter,
            "Missing 'Dear' in salutation"
        ),
        "Closing": (
            "Sincerely" in cover_letter,
            "Missing 'Sincerely' in closing"
        ),
        "Name": (
            payload['user_name'] in cover_letter,
            "Name not included"
        ),
        "Professional Info": (
            payload['user_title'] in cover_letter or payload['user_degree'] in cover_letter,
            "Missing title or degree"
        )
    }

    # Best practices checks
    best_practices = {
        "Skills": (
            any(skill in cover_letter for skill in payload['user_skills'].split(", ")),
            "Consider mentioning skills"
        ),
        "Experience Number": (
            experience_number and experience_number in cover_letter,
            f"Consider mentioning {experience_number} years"
        ),
        "Position Reference": (
            any(word in cover_letter.lower() for word in ["position", "role", "opportunity"]),
            "Consider referencing the position"
        ),
        "Enthusiasm": (
            any(word in cover_letter.lower() for word in ["excited", "enthusiastic", "passionate", "eager"]),
            "Consider showing enthusiasm"
        ),
        "Achievement Words": (
            any(word in cover_letter.lower() for word in ["achieved", "developed", "improved", "led", "managed"]),
            "Consider using achievement words"
        )
    }

    return {
        "required": required_validations,
        "best_practices": best_practices
    }
    
def save_test_report(cover_letter: str, payload: dict, 
                    validations: dict, metadata: dict) -> str:
    """Save complete test report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_hash = hashlib.md5((cover_letter + timestamp).encode()).hexdigest()[:8]
    filename = f"cover_letter_report_{timestamp}_{content_hash}.txt"
    filepath = os.path.join(COVER_LETTERS_DIR, filename)
    
    with open(filepath, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("COVER LETTER GENERATION REPORT\n")
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

        # Generated Cover Letter
        f.write("\n" + "="*80 + "\n")
        f.write("GENERATED COVER LETTER:\n")
        f.write("="*80 + "\n\n")
        f.write(cover_letter)
        
        # Statistics
        f.write("\n\n" + "="*80 + "\n")
        f.write("STATISTICS:\n")
        f.write("-"*40 + "\n")
        f.write(f"Word Count: {len(cover_letter.split())}\n")
        
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

def test_cover_letter_generation(valid_payload):
    """Test cover letter generation"""
    print("\nTesting Cover Letter Generation")
    print("="*80)
    
    # Generate cover letter
    start_time = time.time()
    response = client.post(
        "/api/resume-flow/generate-cover-letter", 
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    generation_time = time.time() - start_time
    
    # Check response
    assert response.status_code == 200, f"API call failed: {response.text}"
    
    # Extract cover letter
    result = response.json()
    assert "cover_letter" in result, "No cover letter in response"
    cover_letter = result["cover_letter"]
    
    # Run validations
    validations = validate_cover_letter(cover_letter, valid_payload)
    
    # Save comprehensive report
    filename = save_test_report(
        cover_letter=cover_letter,
        payload=valid_payload,
        validations=validations,
        metadata={
            "Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Response Time": f"{generation_time:.2f} seconds",
            "API Version": "1.0.0"
        }
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
        "/api/resume-flow/generate-cover-letter",
        json=valid_payload,
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 403, "Expected forbidden access with invalid API key"

def test_missing_fields(valid_payload):
    """Test missing required fields"""

    required_fields = ["job_post", "user_name", "user_degree", 
                      "user_title", "user_experience", "user_skills"]
    
    for field in required_fields:
        incomplete_payload = valid_payload.copy()
        del incomplete_payload[field]
        
        response = client.post(
            "/api/resume-flow/generate-cover-letter",
            json=incomplete_payload,
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 422, f"Expected validation error when {field} is missing"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/resume-flow/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}