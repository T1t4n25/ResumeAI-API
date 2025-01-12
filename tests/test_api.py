# tests/test_api.py
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
from api_key_manager import APIKeyManager

# Create test client
client = TestClient(app)

# Initialize API Key Manager for testing
api_key_manager = APIKeyManager()

# Create directory for generated cover letters if it doesn't exist
COVER_LETTERS_DIR = os.path.join(os.path.dirname(__file__), "generated_cover_letters")
os.makedirs(COVER_LETTERS_DIR, exist_ok=True)

@pytest.fixture
def valid_payload():
    """
    Comprehensive test payload covering various scenarios
    """
    return {
        "job_post": "Senior .NET Developer at TechInnovate Solutions. We are seeking an experienced .NET professional with strong skills in C#, .NET Core, and cloud technologies. Responsibilities include developing scalable web applications, implementing microservices architecture, and collaborating with cross-functional teams.",
        "user_name": "John Doe",
        "user_degree": "Bachelor of Science in Computer Science",
        "user_title": "Software Engineer",
        "user_experience": "5 years of professional .NET development experience",
        "user_skills": "C#, .NET Core, Azure, SQL Server, RESTful APIs"
    }

def save_cover_letter(cover_letter: str, payload: dict) -> str:
    """
    Save cover letter to a unique file with timestamp and hash
    Returns the filename
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create hash from content and timestamp
    content_hash = hashlib.md5(
        (cover_letter + timestamp).encode()
    ).hexdigest()[:8]
    
    # Create filename with timestamp and hash
    filename = f"cover_letter_{timestamp}_{content_hash}.txt"
    filepath = os.path.join(COVER_LETTERS_DIR, filename)
    
    # Save cover letter with metadata
    with open(filepath, 'w') as f:
        f.write("="*80 + "\n")
        f.write("COVER LETTER METADATA:\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Job Post: {payload['job_post'][:100]}...\n")
        f.write(f"Candidate: {payload['user_name']}\n")
        f.write(f"Skills: {payload['user_skills']}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("GENERATED COVER LETTER:\n")
        f.write("="*80 + "\n\n")
        f.write(cover_letter)
        f.write("\n\n" + "="*80 + "\n")
        f.write(f"Character Count: {len(cover_letter)}\n")
        f.write("="*80 + "\n")
    
    return filename

def validate_cover_letter_structure(cover_letter, payload):
    """
    Comprehensive validation of cover letter structure and content
    """
    # Validation checks
    checks = [
        # Basic length constraints
        len(cover_letter) > 1000,
        # Professional salutation check
        re.search(r'\b(Dear|To)\b', cover_letter, re.IGNORECASE) is not None,
        
        # Closing check
        re.search(r'\b(Sincerely|Regards|Best regards)\b', cover_letter, re.IGNORECASE) is not None,
        
        # User name inclusion
        payload['user_name'] in cover_letter,
        
        # Job-related content checks
        any(keyword in cover_letter for keyword in [
            payload['user_title'], 
            payload['user_degree'].split()[-1]  # Last word of degree
        ])
    ]
    
    return all(checks)

def test_generate_api_key():
    """
    Test API key generation endpoint
    """
    response = client.get("/generate-api-key")
    
    assert response.status_code == 200
    assert "api_key" in response.json()
    assert len(response.json()["api_key"]) > 0

def test_cover_letter_generation(valid_payload):
    """
    Primary test for cover letter generation
    """
    # Generate an API key to use
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    # Make API call with generated API key
    response = client.post(
        "/generate-cover-letter", 
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    
    # Basic response checks
    assert response.status_code == 200, f"API call failed: {response.text}"
    
    # Extract cover letter
    result = response.json()
    assert "cover_letter" in result, "No cover letter in response"
    
    cover_letter = result["cover_letter"]
    
    # Structural validation
    assert validate_cover_letter_structure(cover_letter, valid_payload), "Cover letter fails structural validation"
    
    # Save cover letter and get filename
    filename = save_cover_letter(cover_letter, valid_payload)
    
    # Print information about saved file
    print("\n" + "="*80)
    print(f"Cover letter saved to: {filename}")
    print("="*80)
    
    # Print cover letter for immediate viewing
    print("\nGENERATED COVER LETTER:")
    print("="*80)
    print(cover_letter)
    print("="*80)
    print(f"\nCharacter Count: {len(cover_letter)}")
    print("="*80 + "\n")

def test_cover_letter_skill_inclusion(valid_payload):
    """
    Detailed skill inclusion test
    """
    # Generate an API key to use
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    response = client.post(
        "/generate-cover-letter", 
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    
    # Ensure successful response
    assert response.status_code == 200, f"API call failed: {response.text}"
    
    # Extract cover letter
    result = response.json()
    cover_letter = result["cover_letter"]
    
    # Save cover letter
    filename = save_cover_letter(cover_letter, valid_payload)
    
    # Check skill inclusion
    skills = valid_payload['user_skills'].split(", ")
    matched_skills = [
        skill for skill in skills 
        if skill in cover_letter
    ]
    
    # Print skills analysis
    print("\n" + "="*80)
    print("SKILLS ANALYSIS:")
    print("="*80)
    print(f"Cover letter saved to: {filename}")
    print(f"Total Skills: {len(skills)}")
    print(f"Matched Skills: {len(matched_skills)}")
    print("\nMatched Skills List:")
    for skill in matched_skills:
        print(f"✓ {skill}")
    print("\nUnmatched Skills:")
    for skill in set(skills) - set(matched_skills):
        print(f"✗ {skill}")
    print("="*80 + "\n")
    
    # Assert that at least half the skills are mentioned
    assert len(matched_skills) >= len(skills) // 2, (
        f"Insufficient skill matching. "
        f"Matched skills: {matched_skills}"
    )

def test_invalid_api_key(valid_payload):
    """
    Test API endpoint with invalid API key
    """
    response = client.post(
        "/generate-cover-letter", 
        json=valid_payload,
        headers={"X-API-Key": "invalid_key"}
    )
    
    # Expect forbidden status
    assert response.status_code == 403, "Expected forbidden access with invalid API key"

@pytest.mark.parametrize("missing_field", [
    "job_post", "user_name", "user_degree", 
    "user_title", "user_experience", "user_skills"
])
def test_missing_fields(valid_payload, missing_field):
    """
    Test handling of missing fields
    """
    # Generate an API key to use
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    # Create payload with one field removed
    incomplete_payload = valid_payload.copy()
    del incomplete_payload[missing_field]
    
    response = client.post(
        "/generate-cover-letter", 
        json=incomplete_payload,
        headers={"X-API-Key": api_key}
    )
    
    # Expect validation error
    assert response.status_code == 422, f"Expected validation error when {missing_field} is missing"

def test_health_endpoint():
    """
    Test health check endpoint
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_response_performance(valid_payload):
    """
    Basic performance test
    """
    # Generate an API key to use
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    start_time = time.time()
    response = client.post(
        "/generate-cover-letter", 
        json=valid_payload,
        headers={"X-API-Key": api_key}
    )
    end_time = time.time()
    
    # Check response time
    response_time = end_time - start_time
    assert response_time < 10, f"Response took too long: {response_time} seconds"
    
    # Ensure successful response
    assert response.status_code == 200, f"API call failed: {response.text}"

    # If successful, save the cover letter
    if response.status_code == 200:
        cover_letter = response.json()["cover_letter"]
        filename = save_cover_letter(cover_letter, valid_payload)
        print(f"\nPerformance test cover letter saved to: {filename}")
        print(f"Response time: {response_time:.2f} seconds")

# Add to .gitignore
gitignore_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.gitignore')
if os.path.exists(gitignore_path):
    with open(gitignore_path, 'a') as f:
        f.write('\ntests/generated_cover_letters/\n')
# Project Description Generator Tests ==========================================================================
@pytest.fixture
def project_description_payloads():
    """
    Multiple test payloads for different scenarios
    """
    return [
        {
            "project_name": "E-commerce Website",
            "skills": "React, Firebase, Stripe, REST APIs",
            "project_description": "Built a website for an online store. Users can browse products, add to cart, and checkout."
        },
        {
            "project_name": "Task Management System",
            "skills": "Python, Django, PostgreSQL, Docker",
            # No description provided
        }
    ]

def test_project_description_generation(project_description_payloads):
    """
    Test project description generation with different payloads
    """
    # Generate an API key
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    for payload in project_description_payloads:
        # Generate project description
        response = client.post(
            "/generate-project-description",
            json=payload,
            headers={"X-API-Key": api_key}
        )
        
        # Basic response checks
        assert response.status_code == 200
        result = response.json()
        assert "project_description" in result
        
        description = result["project_description"]
        
        # Content validation
        validations = [
            # Length check (30-50 words)
            30 <= len(description.split()) <= 50,
            
            # Contains project name or key terms
            any(term.lower() in description.lower() 
                for term in payload["project_name"].split()),
            
            # Contains mentioned skills
            all(skill.lower() in description.lower() 
                for skill in payload["skills"].split(", ")),
            
            # Starts with action verb
            any(verb in description.lower().split()[0] 
                for verb in ["developed", "built", "created", "implemented", 
                           "designed", "architected", "engineered"])
        ]
        
        assert all(validations), "Project description validation failed"
        
        # Save to file for review
        filename = save_cover_letter(
            description, 
            {"type": "project_description", **payload}
        )
        
        print(f"\nTesting payload: {payload['project_name']}")
        print("\nGenerated Project Description:")
        print("="*80)
        print(description)
        print("="*80)
        print(f"Saved to: {filename}")
        print("\nSkills mentioned:", payload["skills"])
        print("="*80)

def test_missing_required_fields():
    """
    Test validation of required fields
    """
    api_key_response = client.get("/generate-api-key")
    api_key = api_key_response.json()["api_key"]
    
    # Test missing skills
    invalid_payload = {
        "project_name": "Test Project"
    }
    
    response = client.post(
        "/generate-project-description",
        json=invalid_payload,
        headers={"X-API-Key": api_key}
    )
    
    assert response.status_code == 422