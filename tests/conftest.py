# tests/conftest.py
import os
import sys
import pytest

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def set_test_environment():
    """
    Set up test environment variables
    """
    # Set test-specific environment variables
    os.environ['GEMINI_API_KEY'] = 'test_api_key'