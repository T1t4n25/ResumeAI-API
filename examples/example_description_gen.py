import requests

# Replace with your API endpoint URL
API_URL = ""  # or your production URL

def test_generate_project_description():
    # If your API requires an API key, obtain it here
    try:
        # Uncomment and modify the following if your API provides an endpoint to generate an API key
        api_key_response = requests.get(f"{API_URL}/generate-api-key")
        if api_key_response.status_code != 200:
            print("Failed to get API key:", api_key_response.text)
            return
        api_key = api_key_response.json()["api_key"]
        print("Got API key:", api_key)

        # Test payload
        payload = {
            "project_name": "AI-Powered Data Analysis Platform",
            "skills": "Python, Machine Learning, Data Visualization, Pandas, NumPy",
            "project_description": "Developed to process large datasets and generate insightful visualizations, reducing data processing time by 50%."
        }

        print("\nSending request to:", API_URL)

        # Headers for the request (include API key if required)
        headers = {
            "X-API-Key": api_key,  # Uncomment if your API requires an API key
            "Content-Type": "application/json"
        }

        # Make request to the API endpoint
        response = requests.post(
            f"{API_URL}/generate-project-description",
            json=payload,
            headers=headers
        )

        print("\nStatus Code:", response.status_code)

        if response.status_code == 200:
            result = response.json()
            print("\nGenerated Project Description:")
            print("="*80)
            print(result["project_description"])
            print("="*80)
        else:
            print("Error:", response.text)

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    test_generate_project_description()