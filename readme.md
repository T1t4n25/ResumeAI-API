# AI-Powered Resume Assistant API

A comprehensive FastAPI-based backend service that leverages Google's Gemini AI to generate professional cover letters, project descriptions, resume summaries, and complete LaTeX-compiled resumes. This service provides a complete solution for job seekers to create compelling application materials with secure API access and user authentication.

## 🚀 Features

- **Cover Letter Generation**: Creates tailored cover letters based on job descriptions and user profiles
- **Project Description Generation**: Crafts impactful project descriptions for resumes/CVs with quantifiable achievements
- **Professional Summary Generation**: Generates concise professional summaries with measurable results
- **Complete Resume Compilation**: Takes all your data and generates ATS-compliant resumes in PDF/LaTeX format
- **User Authentication System**: Complete user registration and API key management
- **Secure Database Integration**: SQLAlchemy-based user and API key management with PostgreSQL support
- **LaTeX Resume Compilation**: Professional resume generation using LaTeX templates
- **Comprehensive Testing**: Full pytest test suite with detailed validation
- **Automated Documentation**: FastAPI-generated OpenAPI documentation with security schemes
- **Dynamic DNS**: Using Dynu service for static domain access
- **Connection Pool Management**: Optimized database connections with automatic cleanup

## 🛠️ Tech Stack

- **Framework**: FastAPI 
- **AI Model**: Google Gemini AI (2.0 Flash Lite)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Custom API Key management with secure hashing
- **Resume Compilation**: LaTeX with TexSoup manipulation
- **Testing**: pytest with comprehensive test coverage
- **Documentation**: OpenAPI (Swagger UI)
- **Environment Management**: python-dotenv
- **Document Processing**: LaTeX compilation with latexmk

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- LaTeX distribution (for PDF compilation)
- Google Cloud Project with Gemini API access
- Environment variables setup

## 🔧 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/resume-assistant-api.git
cd resume-assistant-api
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

4. Install LaTeX (for resume compilation):

```bash
# Ubuntu/Debian
sudo apt-get install texlive-full latexmk

# macOS
brew install --cask mactex

# Windows
# Download and install MiKTeX or TeX Live
```

5. Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/resume_db
DYNU_PASS=your_dynu_password
```

## 🗄️ Database Setup

The application uses PostgreSQL with SQLAlchemy. The database schema includes:

- **Users**: Store user credentials and information
- **API Keys**: Manage authentication tokens linked to users

Tables are automatically created on startup via SQLAlchemy metadata.

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

## 🔑 Authentication System

The API uses a secure authentication system with user registration and API key management:

### 1. Register a new user:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 2. Generate additional API keys:

```bash
curl -X POST "http://localhost:8000/auth/generate-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### 3. View your API keys:

```bash
curl -H "X-API-Key: your_api_key" \
  "http://localhost:8000/auth/my-api-keys"
```

### 4. Use API key in protected requests:

```bash
curl -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -X POST "http://localhost:8000/generate-cover-letter" \
  -d '{"job_post": "...", "user_name": "..."}'
```

## 📝 API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/auth/register` | POST | Register new user account | No |
| `/auth/generate-api-key` | POST | Generate API key for existing user | No |
| `/auth/my-api-keys` | GET | List user's API keys | Yes |

### Content Generation Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/generate-cover-letter` | POST | Generate tailored cover letter | Yes |
| `/generate-project-description` | POST | Create impactful project descriptions | Yes |
| `/generate-summary` | POST | Generate professional summaries | Yes |
| `/create-resume` | POST | Compile complete resume (PDF/LaTeX) | Yes |

### Utility Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/health` | GET | Health check endpoint | No |
| `/` | GET | API information and endpoints | No |

## 📋 Request/Response Examples

### Cover Letter Generation

```json
{
  "job_post": "Senior Software Engineer position requiring Python, AWS, and team leadership experience...",
  "user_name": "John Doe",
  "user_title": "Senior Software Engineer",
  "user_degree": "B.S. Computer Science",
  "user_experience": "5+ years developing scalable web applications...",
  "user_skills": "Python, AWS, Docker, React, PostgreSQL"
}
```

### Resume Creation

```json
{
  "information": {
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe",
    "summary": "Professional summary text..."
  },
  "education": [
    {
      "school": "University Name",
      "degree": "B.S. Computer Science",
      "start_date": "2018",
      "end_date": "2022"
    }
  ],
  "experience": [...],
  "projects": [...],
  "technical_skills": {...},
  "soft_skills": [...],
  "output_format": "pdf"
}
```

## 🧪 Running Tests

Execute the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test categories
pytest tests/test_cover_letter.py
pytest tests/test_project_description.py
pytest tests/test_summary.py
pytest tests/test_resume_creation.py
```

Test outputs are generated in:
- `tests/generated_cover_letters/`
- `tests/generated_projects/`
- `tests/generated_summaries/`
- `tests/generated_resumes/`

## 🏗️ Project Structure

```
├── Auth_DataBase/
│   ├── auth_database.py          # Database operations
│   └── Auth_Database_Models/     # SQLAlchemy models
├── generation_endpoints/         # AI generation services
├── latex_templates/             # LaTeX resume templates
├── tests/                       # Comprehensive test suite
├── generated_resumes/           # Compiled resume output
├── logs/                        # Application logs
├── main.py                      # FastAPI application
├── models.py                    # Pydantic request/response models
├── api_key_manager.py           # API key management
├── resume_creator.py            # LaTeX resume generation
├── utility_func.py              # Helper functions
└── requirements.txt             # Python dependencies
```

## 🔒 Security Features

- **Secure Password Hashing**: SHA-256 password hashing
- **API Key Authentication**: Secure token-based access control
- **Database Connection Pooling**: Optimized and secure database connections
- **Input Validation**: Comprehensive request validation with Pydantic
- **Error Handling**: Secure error responses without information leakage
- **Environment Variable Protection**: Sensitive data stored in environment variables

## 🎯 AI Generation Features

### Cover Letter Generator
- Tailored content based on job postings
- Professional formatting and tone
- Integration of user experience and skills
- 250-300 word optimized length

### Project Description Generator
- Achievement-focused language
- Quantifiable results emphasis
- Technical skill highlighting
- 30-50 word concise format

### Summary Generator
- Professional identity emphasis
- Measurable achievements inclusion
- 50-75 word targeted length
- Action verb utilization

### Resume Compiler
- LaTeX-based professional formatting
- ATS-compliant design
- Multiple output formats (PDF/LaTeX/Both)
- Template-based consistency

## 🚀 Deployment

The application includes production-ready features:

- **Dynamic DNS**: Automatic IP address updates
- **Logging**: Comprehensive application and access logging  
- **Health Monitoring**: Connection pool status and health checks
- **Graceful Shutdown**: Proper resource cleanup on termination
- **CORS Support**: Cross-origin request handling


## 📄 License & Commercial Use

This project uses a **dual licensing model**:

### Non-Commercial Use (Free)
For personal, educational, research, or non-commercial purposes, this software is available under the [MIT License](LICENSE).

### Commercial Use (Requires License)
**⚠️ IMPORTANT**: Commercial use of this software requires a separate commercial license and revenue sharing agreement.

#### Commercial Use Includes:
- Using this software in business environments
- Generating revenue through this software
- Offering paid services based on this software
- Integration into commercial products
- Selling access to features or APIs

#### Commercial License Terms:
- to be negotiated with the author
#### Get Commercial License:
Contact **Zeyad Hemeda (@T1t4n25)** for commercial licensing:
- **Email**: [Email](mailto:zeyad.mohammedwork@gmail.com)
- **GitHub**: [@T1t4n25](https://github.com/T1t4n25)

**Unauthorized commercial use constitutes copyright infringement and will be prosecuted.**

See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for full terms.

## 👥 Author

- Zeyad Hemeda (@T1t4n25)

## 🙏 Acknowledgments

- Google Gemini AI team for the powerful language model
- FastAPI team for the excellent framework
- SQLAlchemy team for robust ORM capabilities
- LaTeX community for document preparation system
- Dynu for dynamic DNS services
- pytest team for comprehensive testing framework
