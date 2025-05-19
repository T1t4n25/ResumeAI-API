import requests

# Replace with your API endpoint URL
API_URL = "http://0.0.0.0:8000"  # or your production URL

api_key_response = requests.get(f"{API_URL}/generate-api-key")
print("API Key Response:", api_key_response.text)