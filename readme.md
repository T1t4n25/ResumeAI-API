# AI-Powered Resume Assistant API

A FastAPI-based backend service that leverages Google's Gemini AI to generate professional cover letters, project descriptions, and resume summaries. This service is designed to help job seekers create compelling job application materials efficiently.

## 🚀 Features

- **Cover Letter Generation**: Creates tailored cover letters based on job descriptions and user profiles
- **Project Description Generation**: Crafts impactful project descriptions for resumes/CVs
- **Professional Summary Generation**: Generates concise professional summaries
- **Secure API Access**: Implementation of API key authentication
- **Comprehensive Testing**: Includes unit tests with detailed validation
- **Automated Documentation**: FastAPI-generated OpenAPI documentation

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **AI Model**: Google Gemini AI (1.5 Pro/Flash)
- **Testing**: pytest
- **Authentication**: Custom API Key management
- **Documentation**: OpenAPI (Swagger UI)
- **Environment Management**: python-dotenv

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Project with Gemini API access
- Environment variables setup

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/t1t4n25-generate-cover-letter-fast-api.git
cd t1t4n25-generate-cover-letter-fast-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key
API_KEYS=your_initial_api_key  # Optional
```

## 🚀 Running the Application

1. Start the server:
```bash
./start.sh
# Or manually:
uvicorn main:app --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔑 API Authentication

All endpoints (except `/generate-api-key` and `/health`) require API key authentication:

1. Generate an API key:
```bash
curl http://localhost:8000/generate-api-key
```

2. Use the API key in requests:
```bash
curl -H "X-API-Key: your_api_key" -X POST http://localhost:8000/endpoint
```

## 📝 API Endpoints

### Cover Letter Generation
```http
POST /generate-cover-letter
```
Generates a professional cover letter based on job posting and user profile.

### Project Description Generation
```http
POST /generate-project-description
```
Creates impactful project descriptions for resumes/CVs.

### Professional Summary Generation
```http
POST /generate-summary
```
Generates professional summaries for resumes.

### API Key Management
```http
GET /generate-api-key
```
Generates a new API key for authentication.

### Health Check
```http
GET /health
```
Simple health check endpoint.

## 🧪 Running Tests

Execute the test suite:
```bash
pytest tests/
```

The tests generate output files in:
- `tests/generated_cover_letters/`
- `tests/generated_projects/`
- `tests/generated_summaries/`

## 📁 Project Structure

```
t1t4n25-generate-cover-letter-fast-api/
├── api_key_manager.py      # API key management
├── cover_letter_generator.py # Cover letter generation logic
├── main.py                 # FastAPI application and routes
├── models.py              # Pydantic models for requests/responses
├── project_description_generator.py # Project description generation
├── summary_generator.py    # Professional summary generation
├── requirements.txt       # Project dependencies
├── start.sh              # Startup script
└── tests/                # Test suite
```

## 🔒 Security Considerations

- API keys are required for all main endpoints
- Keys are securely generated using `secrets` module
- Environment variables are used for sensitive data
- No user data is stored persistently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

[MIT License](LICENSE)

## 👥 Authors

- Your Name (@yourusername)

## 🙏 Acknowledgments

- Google Gemini AI team for the powerful language model
- FastAPI team for the excellent framework