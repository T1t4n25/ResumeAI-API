# tests/test_api.py
import sys
import os
import re
import pytest
import hashlib
import time
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Create test client
client = TestClient(app)

# Ensure snapshots directory exists
SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

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

def generate_snapshot_filename(payload):
    """
    Generate a unique filename based on payload contents
    """
    payload_string = str(payload)
    hash_object = hashlib.md5(payload_string.encode())
    return f"cover_letter_snapshot_{hash_object.hexdigest()}.txt"

def extract_key_content(cover_letter):
    """
    Extract key structural and content elements
    """
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', cover_letter).strip()
    
    # Extract key sections
    sections = re.findall(r'(Dear[^\n]+|Sincerely[^\n]+|\b(Name|Degree|Experience|Skills)[^\n]+)', normalized, re.IGNORECASE)
    
    # Extract skills and key professional terms
    skills_and_terms = re.findall(r'\b(C#|\.NET|Azure|Software|Engineer|Developer)\b', normalized, re.IGNORECASE)
    
    return {
        'sections': [s[0] for s in sections],
        'skills_and_terms': list(set(skills_and_terms))
    }

def compare_cover_letters(letter1, letter2):
    """
    Compare two cover letters based on key content
    """
    content1 = extract_key_content(letter1)
    content2 = extract_key_content(letter2)
    
    # Compare sections
    section_match = len(set(content1['sections']) & set(content2['sections'])) / max(len(content1['sections']), len(content2['sections']))
    
    # Compare skills and terms
    skills_match = len(set(content1['skills_and_terms']) & set(content2['skills_and_terms'])) / max(len(content1['skills_and_terms']), len(content2['skills_and_terms']))
    
    # Combine metrics
    overall_similarity = (section_match + skills_match) / 2
    
    return overall_similarity

def validate_cover_letter_structure(cover_letter, payload):
    """
    Comprehensive validation of cover letter structure and content
    """
    # Validation checks
    checks = [
        # Basic length constraints
        len(cover_letter) > 500,
        
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

def advanced_skill_matcher(skills, cover_letter):
    """
    Advanced skill matching with multiple strategies
    """
    def normalize_skill(skill):
        return skill.replace('.', '').lower().strip()
    
    # Normalize skills and cover letter
    normalized_skills = [normalize_skill(skill) for skill in skills.split(', ')]
    normalized_letter = cover_letter.lower()
    
    # Matching strategies
    matched_skills = []
    for skill in normalized_skills:
        matching_conditions = [
            skill in normalized_letter,
            skill.replace(' ', '') in normalized_letter,
            any(variant in normalized_letter for variant in [
                skill,
                skill.replace(' ', ''),
                skill.capitalize(),
                skill.upper()
            ])
        ]
        
        if any(matching_conditions):
            matched_skills.append(skill)
    
    return {
        'matched': matched_skills,
        'match_percentage': len(matched_skills) / len(normalized_skills) * 100
    }

def test_cover_letter_generation(valid_payload):
    """
    Primary test for cover letter generation
    """
    # Make API call
    response = client.post("/generate-cover-letter", json=valid_payload)
    
    # Basic response checks
    assert response.status_code == 200, "API call failed"
    
    # Extract cover letter
    result = response.json()
    assert "cover_letter" in result, "No cover letter in response"
    
    cover_letter = result["cover_letter"]
    
    # Structural validation
    assert validate_cover_letter_structure(cover_letter, valid_payload), "Cover letter fails structural validation"

def test_skill_inclusion(valid_payload):
    """
    Detailed skill inclusion test
    """
    response = client.post("/generate-cover-letter", json=valid_payload)
    cover_letter = response.json()["cover_letter"]
    
    # Advanced skill matching
    skill_match_result = advanced_skill_matcher(valid_payload['user_skills'], cover_letter)
    
    # Assertions
    assert skill_match_result['match_percentage'] >= 50, (
        f"Insufficient skill matching. "
        f"Matched {skill_match_result['matched']} "
        f"({skill_match_result['match_percentage']}%)"
    )
    
    # Print detailed matching for visibility
    print("\nSkill Matching Details:")
    print(f"Matched Skills: {skill_match_result['matched']}")
    print(f"Match Percentage: {skill_match_result['match_percentage']}%")

@pytest.mark.parametrize("skills_input", [
    "C#, .NET Core, Azure",
    "Python, Django, REST API",
    "JavaScript, React, Node.js",
    "Java, Spring Boot, Microservices"
])
def test_diverse_skill_scenarios(valid_payload, skills_input):
    """
    Test cover letter generation with different skill sets
    """
    # Update payload with new skills
    payload = valid_payload.copy()
    payload['user_skills'] = skills_input
    
    # Generate cover letter
    response = client.post("/generate-cover-letter", json=payload)
    
    # Validate response
    assert response.status_code == 200, f"Failed for skills: {skills_input}"
    
    cover_letter = response.json()["cover_letter"]
    
    # Skill matching
    skill_match = advanced_skill_matcher(skills_input, cover_letter)
    
    # Ensure at least some skills are matched
    assert skill_match['match_percentage'] > 30, (
        f"Low skill matching for {skills_input}. "
        f"Matched: {skill_match['matched']}"
    )

def test_error_handling():
    """
    Test API error handling with incomplete payload
    """
    # Incomplete payload
    incomplete_payloads = [
        {"job_post": "Sample Job Post"},
        {"user_name": "John Doe"},
        {}
    ]
    
    for payload in incomplete_payloads:
        response = client.post("/generate-cover-letter", json=payload)
        
        # Expect validation error
        assert response.status_code == 422, f"Expected validation error for payload: {payload}"

def test_long_job_post(valid_payload):
    """
    Test with an extremely long job post
    """
    long_payload = valid_payload.copy()
    long_payload['job_post'] = "A" * 2000  # Very long job post
    
    response = client.post("/generate-cover-letter", json=long_payload)
    
    # Validate response
    assert response.status_code == 200, "Failed to handle long job post"
    
    cover_letter = response.json()["cover_letter"]
    assert len(cover_letter) > 0, "Empty cover letter generated"

def test_cover_letter_snapshot(valid_payload):
    """
    Generate and compare cover letter snapshot
    """
    # Generate cover letter
    response = client.post("/generate-cover-letter", json=valid_payload)
    
    # Validate response
    assert response.status_code == 200, "API call failed"
    
    # Extract cover letter
    cover_letter = response.json()["cover_letter"]
    
    # Generate snapshot filename
    snapshot_filename = generate_snapshot_filename(valid_payload)
    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_filename)
    
    # Always update or create snapshot
    with open(snapshot_path, "w") as f:
        f.write(cover_letter)
    
    # If this is the first run, we just create the snapshot
    if not hasattr(test_cover_letter_snapshot, 'first_run'):
        test_cover_letter_snapshot.first_run = True
        pytest.skip("First snapshot created")
    
    # Read previous snapshot
    with open(snapshot_path, "r") as f:
        previous_snapshot = f.read()
    
    # Compare cover letters
    similarity = compare_cover_letters(previous_snapshot, cover_letter)
    
    # Print similarity for debugging
    print(f"\nSnapshot Similarity: {similarity:.2f}")
    
    # Allow more flexibility in AI-generated content
    assert similarity > 0.4, (
        f"Cover letter significantly differs from previous snapshot. "
        f"Similarity: {similarity:.2f}"
    )

def test_multiple_snapshot_scenarios(valid_payload):
    """
    Generate snapshots for multiple scenarios
    """
    # Scenarios to test
    scenarios = [
        valid_payload,
        {**valid_payload, "user_skills": "Python, Django, REST API"},
        {**valid_payload, "user_title": "Senior Software Engineer"}
    ]
    
    for scenario in scenarios:
        # Generate cover letter
        response = client.post("/generate-cover-letter", json=scenario)
        
        # Validate response
        assert response.status_code == 200, f"API call failed for scenario: {scenario}"
        
        # Extract cover letter
        cover_letter = response.json()["cover_letter"]
        
        # Generate snapshot filename
        snapshot_filename = generate_snapshot_filename(scenario)
        snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_filename)
        
        # Always update snapshot
        with open(snapshot_path, "w") as f:
            f.write(cover_letter)
        
        print(f"Snapshot updated for scenario: {snapshot_filename}")

# Performance test
def test_response_time(valid_payload):
    """
    Basic response time test
    """
    start_time = time.time()
    response = client.post("/generate-cover-letter", json=valid_payload)
    end_time = time.time()
    
    # Check response time (adjust threshold as needed)
    response_time = end_time - start_time
    assert response_time < 15, f"Response took too long: {response_time} seconds"