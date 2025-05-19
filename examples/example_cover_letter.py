import requests

# Replace with your API endpoint URL
PROD_URL = ""

def test_simple_request():
    # First, get an API key
    try:
        api_key_response = requests.get(f"{PROD_URL}/generate-api-key")
        if api_key_response.status_code != 200:
            print("Failed to get API key:", api_key_response.text)
            return

        api_key = api_key_response.json()["api_key"]
        print("Got API key:", api_key)

        # Test payload
        payload = {
            "job_post": """About the job
e.construct

We are an engineering firm that specializes in providing elegant engineering solutions for complex challenges. e.construct is a fast-growing firm with 7 offices around the world. At our core, we question how the very nature of how to evolve the structures that we inhabit to increase their performance and value.

we design structures such as bridges, high-rise design, precast concrete engineering and post-tensioning design. The firm's core work is structural engineering; however, e.construct is increasingly holistic at its approach to buildings and it has divisions in MEP, Geotechnical and emerging construction technology such as 3D printing of concrete, technology and 3D laser scanning.

VAES.ai

We are a tech startup that is being incubated in the technology lab of e.construct and we employ technology to empower and eventually transform engineering. VAES’s mission is to reduce the amount of raw materials we design in our buildings and bridges by using optimization algorithms and machine learning.

VAES consists of a team of software developers, civil engineers, machine learning experts, architects and graphic designers that builds tools that engineers can use to design and manufacture the next generation of cities.

Primary Responsibilities:

Collaborate with a team to develop and maintain software for structural optimization
Manage the development process from initial idea to final release
Collaborate with stakeholders to gather requirements and test software components
Design and implement scalable software solutions


Qualifications & Skills:

Required:
Bachelor's degree in computer science or a related field
1-6 years of software development experience
Proficiency in Python, JavaScript and SQL
Experience with scalable software development
Desirable:
Knowledge of PySide6, Shapely, numpy and any python scientific libraries
Experience with C# or similar .NET frameworks
Soft Skills:
Ownership – responsibility for your work and projects
Problem-solving ability – ability to address and overcome challenges
Communication skills – work well with team members, stakeholders, and clients
Attention to detail
""",
            "user_name": "Zeyad Hemeda",
            "user_degree": "Bachelor of Computer Science",
            "user_title": "Software Engineer",
            "user_experience": "5 years of professional python development experience",
            "user_skills": "python, api, numpy, matplotlib, c#, .net core, open cv"
        }

        print("\nSending request to:", PROD_URL)

        # Make request with API key in header
        response = requests.post(
            f"{PROD_URL}/generate-cover-letter",
            json=payload,
            headers={"X-API-Key": api_key}
        )

        print("\nStatus Code:", response.status_code)

        if response.status_code == 200:
            result = response.json()
            print("\nGenerated Cover Letter:")
            print("="*80)
            print(result["cover_letter"])
            print("="*80)
        else:
            print("Error:", response.text)

    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_simple_request()