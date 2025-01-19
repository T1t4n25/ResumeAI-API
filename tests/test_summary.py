# tests/test_summary.py
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

# Create directory for generated summaries
SUMMARIES_DIR = os.path.join(os.path.dirname(__file__), "generated_summaries")
os.makedirs(SUMMARIES_DIR, exist_ok=True)

def save_summary(summary: str, metadata: dict) -> str:
    """Save generated summary with metadata"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5((summary + timestamp).encode()).hexdigest()[:8]
        filename = f"summary_{timestamp}_{content_hash}.txt"
        filepath = os.path.join(SUMMARIES_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PROFESSIONAL SUMMARY METADATA:\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
            f.write("\n" + "="*80 + "\n")
            f.write("GENERATED SUMMARY:\n")
            f.write("="*80 + "\n\n")
            f.write(summary)
            f.write("\n\n" + "="*80 + "\n")
            f.write(f"Word Count: {len(summary.split())}\n")
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
    """Test payload for summary generation"""
    return {
        "current_title": "Senior Software Engineer",
        "years_experience": "5+ years",
        "skills": "Python, React, AWS, Microservices",
        "achievements": "Led team of 5, Reduced system latency by 40%"
    }

def test_summary_generation(api_key, test_payload):
    """Test summary generation"""
    print("\nTesting Summary Generation")
    print("="*80)
    
    # Generate summary
    response = client.post(
        "/generate-summary",
        json=test_payload,
        headers={"X-API-Key": api_key}
    )
    
    # Print response for debugging
    print("\nAPI Response:", response.text)
    
    # Check response status
    assert response.status_code == 200, f"API call failed with status {response.status_code}: {response.text}"
    
    # Extract summary
    result = response.json()
    assert "summary" in result, "Response missing 'summary' field"
    
    summary = result["summary"]
    word_count = len(summary.split())
    
    print("\nGenerated Summary:")
    print("-"*80)
    print(summary)
    print("-"*80)
    print(f"Word Count: {word_count}")
    
    # Word count validation
    assert 50 <= word_count <= 75, f"Word count {word_count} outside range 50-75"
    
    # Save the summary
    filename = save_summary(
        summary,
        {
            "Title": test_payload["current_title"],
            "Experience": test_payload["years_experience"],
            "Skills": test_payload["skills"],
            "Achievements": test_payload["achievements"],
            "Word Count": word_count
        }
    )
    
    assert filename is not None, "Failed to save summary"
    print(f"\nSaved to: {filename}")
    
    # Content validations
    validations = {
        "Professional Identity": test_payload["current_title"].lower() in summary.lower(),
        "Experience": test_payload["years_experience"].lower() in summary.lower(),
        "Technical Skills": any(skill.lower() in summary.lower() 
                              for skill in test_payload["skills"].split(", ")),
        "Achievement Focus": any(word in summary.lower() 
                               for word in ["achieved", "reduced", "improved", "led", "developed"]),
        "Action Language": any(word in summary.lower() 
                             for word in ["delivered", "implemented", "managed", "designed", "developed"]),
        "Value Proposition": any(phrase in summary.lower() 
                               for phrase in ["expertise in", "specialized in", "proven track record", 
                                            "demonstrated success", "brings"])
    }
    
    print("\nValidation Results:")
    print("-"*80)
    for criterion, passed in validations.items():
        print(f"{criterion:15}: {'✓' if passed else '✗'}")
        assert passed, f"Validation failed for {criterion}"
def test_missing_fields(api_key):
    """Test missing required fields"""
    print("\nTesting Missing Fields")
    print("="*80)
    
    test_cases = [
        ({"current_title": "Engineer"}, "Missing required fields"),
        ({"years_experience": "5 years"}, "Missing required fields"),
        ({}, "Empty payload")
    ]
    
    for payload, case in test_cases:
        print(f"\nTesting: {case}")
        response = client.post(
            "/generate-summary",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        assert response.status_code == 422, \
            f"Expected 422 for {case}, got {response.status_code}"
        print(f"✓ Correctly failed with 422")