# AI-Powered Cover Letter Generator

## Overview

This project is an advanced AI-powered Cover Letter Generator built using FastAPI and Google's Gemini AI. It helps job seekers create personalized, professional cover letters tailored to specific job postings.

## 🚀 Features

- 🤖 AI-driven cover letter generation
- 📝 Personalized content based on user profile
- 🎯 Tailored to specific job descriptions
- 🔒 Secure API endpoint
- 📊 Supports various professional backgrounds

## 🛠 Technologies Used

- Python
- FastAPI
- Google Generative AI (Gemini)
- Pydantic
- Pytest

## 📦 Prerequisites

- Python 3.8+
- Google Generative AI API Key

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cover-letter-generator.git
cd cover-letter-generator
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API Key:
Create a file `API_KEYS.py` in the project root:
```python
GEMINI_API_KEY = 'your_google_generative_ai_api_key'
```

## 🚀 Running the Application

### Development Server
```bash
uvicorn main:app --reload
```

### API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🧪 Running Tests
```bash
pytest tests/test_api.py
```

## 📝 Example Usage

### API Request Payload
```json

{
    "job_post": "Senior .NET Developer job description...",
    "user_name": "John Doe",
    "user_degree": "Bachelor of Science in Computer Science",
    "user_title": "Software Engineer",
    "user_experience": "5 years of .NET development",
    "user_skills": "C#, .NET Core, Azure, SQL Server"
}
```
## 🔒 Security
- Secure API key management
- Input validation
- Error handling

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Contact
Your Name - [Zeyad](mailto:shadodiss@gmail.com)


## Acknowledgements
- FastAPI
- Google Generative AI
- Pydantic

### Additional Files to Include

1. `requirements.txt`:
    ```
    fastapi
    uvicorn
    google-generativeai
    pydantic
    pytest
    httpx
    ```

2. `.gitignore`:
    ```
    # Virtual Environment
    venv/
    .env

    # Python cache files
    __pycache__/
    *.py[cod]

    # API Keys
    API_KEYS.py

    # IDE files
    .vscode/
    .idea/

    # Pytest
    .pytest_cache/

    # Snapshots (optional)
    tests/snapshots/
    ```

3. `LICENSE` (MIT License):
    ```
    MIT License
    ```

