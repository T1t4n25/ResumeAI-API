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
        # Create timestamp and hash for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5((summary + timestamp).encode()).hexdigest()[:8]
        filename = f"summary_{timestamp}_{content_hash}.txt"
        filepath = os.path.join(SUMMARIES_DIR, filename)
        
        # Save with formatted content
        with open(filepath, 'w') as f:
            # Header
            f.write("="*80 + "\n")
            f.write("RESUME SUMMARY METADATA:\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Metadata
            f.write("Input Parameters:\n")
            f.write("-"*40 + "\n")
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
            
            # Summary
            f.write("\n" + "="*80 + "\n")
            f.write("GENERATED SUMMARY:\n")
            f.write("="*80 + "\n\n")
            f.write(summary)
            
            # Statistics
            f.write("\n\n" + "="*80 + "\n")
            f.write("STATISTICS:\n")
            f.write("-"*40 + "\n")
            f.write(f"Word Count: {len(summary.split())}\n")
            f.write(f"Character Count: {len(summary)}\n")
            
            # Validation Results
            f.write("\nValidation Results:\n")
            f.write("-"*40 + "\n")
            validations = {
                "Word Count": 50 <= len(summary.split()) <= 75,
                "Professional Title": metadata["Title"].lower() in summary.lower(),
                "Experience": metadata["Experience"].lower() in summary.lower(),
                "Skills": any(skill.lower() in summary.lower() 
                            for skill in metadata["Skills"].split(", "))
            }
            for criterion, passed in validations.items():
                f.write(f"{criterion:15}: {'✓' if passed else '✗'}\n")
            
            f.write("\n" + "="*80 + "\n")
        
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
    
    # Check response status
    assert response.status_code == 200, f"API call failed with status {response.status_code}: {response.text}"
    
    # Extract summary
    result = response.json()
    assert "summary" in result, "Response missing 'summary' field"
    
    summary = result["summary"]
    word_count = len(summary.split())
    
    # Display generated summary
    print("\nGenerated Summary:")
    print("-"*80)
    print(summary)
    print("-"*80)
    print(f"Word Count: {word_count}")
    
    # Save the summary first (before any validations)
    filename = save_summary(
        summary,
        {
            "Title": test_payload["current_title"],
            "Experience": test_payload["years_experience"],
            "Skills": test_payload["skills"],
            "Achievements": test_payload.get("achievements", "Not provided"),
            "Word Count": word_count,
            "Generation Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "Generated - Pending Validation"
        }
    )
    
    assert filename is not None, "Failed to save summary"
    print(f"\nSaved to: {filename}")
    
 # Split validations into required and best practices
    required_validations = {
        "Word Count": (40 <= word_count <= 75, f"Word count {word_count} outside range 40-75"),
        "Professional Identity": (
            test_payload["current_title"].lower() in summary.lower(),
            "Missing professional title"
        ),
        "Experience": (
            test_payload["years_experience"].lower() in summary.lower(),
            "Missing experience information"
        ),
        "Technical Skills": (
            any(skill.lower() in summary.lower() for skill in test_payload["skills"].split(", ")),
            "Missing technical skills"
        ),
        "Metrics Present": (
            any(char.isdigit() for char in summary),
            "Missing numerical metrics"
        )
    }

    best_practices = {
        "Action Verb Start": (
            summary.lower().split()[0] in [
                "developed", "implemented", "led", "spearheaded", "orchestrated",
                "delivered", "designed", "architected", "engineered", "managed",
                "experienced", "skilled", "seasoned", "accomplished",
                "results-oriented", "results-driven", "innovative"
            ],
            "Consider starting with strong action verb"
        ),
        "Achievement Focus": (
            any(achievement_word in summary.lower() for achievement_word in [
                "achieved", "reduced", "improved", "led", "developed",
                "increased", "delivered", "implemented", "spearheaded",
                "orchestrated", "optimized", "enhanced", "streamlined"
            ]),
            "Consider including achievement-focused language"
        ),
        "Value Proposition": (
            any(phrase.lower() in summary.lower() for phrase in [
                "expertise in", "specialized in", "proven track record", 
                "demonstrated success", "proven ability", "expertise",
                "successfully", "effectively", "consistently"
            ]),
            "Consider adding clear value proposition"
        ),
        "Length Optimization": (
            50 <= word_count <= 75,
            "Consider expanding to 50-75 words for optimal detail"
        ),
        "Skills Integration": (
            sum(1 for skill in test_payload["skills"].split(", ") 
                if skill.lower() in summary.lower()) >= 2,
            "Consider mentioning more technical skills"
        )
    }
    
    # Print and save validation results
    print("\nRequired Criteria:")
    print("-"*80)
    failed_required = []
    for criterion, (passed, error_msg) in required_validations.items():
        status = "✓" if passed else "✗"
        print(f"{criterion:20}: {status}")
        if not passed:
            failed_required.append(f"{criterion}: {error_msg}")

    print("\nBest Practices:")
    print("-"*80)
    best_practices_met = []
    best_practices_missed = []
    for criterion, (passed, suggestion) in best_practices.items():
        status = "✓" if passed else "○"  # Using ○ instead of ✗ for best practices
        print(f"{criterion:20}: {status}")
        if passed:
            best_practices_met.append(criterion)
        else:
            best_practices_missed.append(f"{criterion}: {suggestion}")

    # Save results to file
    if os.path.exists(os.path.join(SUMMARIES_DIR, filename)):
        with open(os.path.join(SUMMARIES_DIR, filename), 'a') as f:
            f.write("\nVALIDATION RESULTS:\n")
            f.write("="*80 + "\n")
            
            f.write("\nREQUIRED CRITERIA:\n")
            f.write("-"*80 + "\n")
            for criterion, (passed, _) in required_validations.items():
                f.write(f"{criterion:20}: {'Passed' if passed else 'Failed'}\n")
            
            f.write("\nBEST PRACTICES:\n")
            f.write("-"*80 + "\n")
            for criterion, (passed, suggestion) in best_practices.items():
                f.write(f"{criterion:20}: {'Met' if passed else 'Consider'}\n")
            
            if failed_required:
                f.write("\nFAILED REQUIRED CRITERIA:\n")
                f.write("-"*80 + "\n")
                for failure in failed_required:
                    f.write(f"- {failure}\n")
            
            if best_practices_missed:
                f.write("\nBEST PRACTICE SUGGESTIONS:\n")
                f.write("-"*80 + "\n")
                for suggestion in best_practices_missed:
                    f.write(f"- {suggestion}\n")
            
            # Add summary statistics
            f.write("\nSUMMARY:\n")
            f.write("-"*80 + "\n")
            f.write(f"Required Criteria Met: {len(required_validations) - len(failed_required)}/{len(required_validations)}\n")
            f.write(f"Best Practices Met: {len(best_practices_met)}/{len(best_practices)}\n")
    
    # Assert only required validations
    assert all(passed for passed, _ in required_validations.values()), \
        "Failed required criteria:\n" + "\n".join(failed_required)

    # Print summary statistics
    print(f"\nSummary Statistics:")
    print(f"Required Criteria Met: {len(required_validations) - len(failed_required)}/{len(required_validations)}")
    print(f"Best Practices Met: {len(best_practices_met)}/{len(best_practices)}")
    
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