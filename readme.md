# Resume Flow API: Enterprise-Grade AI Career Assistant

A comprehensive, AI-powered backend service that orchestrates the generation of professional career materials and simulates technical interviews. Built to demonstrate advanced backend architecture, secure identity management, and generative AI orchestration, this service provides a complete solution for job seekers to create compelling application materials.

---

## 🌟 Business Value & Key Features
*(A high-level overview of what this product solves)*

- **AI-Powered Technical Interviews**: Simulates interactive technical and behavioral interviews using Google's Gemini AI, providing immediate, actionable feedback to candidates.
- **Automated Career Material Generation**: Crafts highly tailored cover letters, quantifiable project descriptions, and impactful professional summaries tuned to specific job descriptions.
- **End-to-End Resume Compilation**: Takes structured candidate data and generates pixel-perfect, ATS-compliant resumes in PDF format using LaTeX.
- **Enterprise Security Model**: Secured via **Keycloak** Identity and Access Management (IAM), utilizing OAuth2 and JWTs for robust authentication and endpoint protection.
- **Scalable Architecture Design**: Built using a Vertical Slice Architecture, ensuring high maintainability, feature encapsulation, and dynamic routing for rapid iteration.

---

## 🛠️ Technical Overview
*(For developers, engineers, and technical recruiters)*

### Tech Stack
- **Core Framework**: FastAPI (Python 3.8+)
- **AI Integration**: Google Gemini AI (2.0 Flash Lite via `google-genai` SDK)
- **Identity Provider**: Keycloak (OAuth2 / OpenID Connect)
- **Database**: PostgreSQL with Async SQLAlchemy ORM
- **Document Processing**: LaTeX compilation (latexmk) and TexSoup
- **Rate Limiting**: `slowapi`
- **Testing**: `pytest`

### Architectural Highlights
- **Vertical Slicing**: Code is organized strictly by domain features (`auth`, `cover_letters`, `interviews`, `resumes`, etc.) rather than technical concerns (like grouping all routes or all models together). This vastly improves domain cohesion.
- **Dynamic Router Discovery**: The FastAPI application dynamically scans the `features` directory at startup to automatically discover and register `APIRouter` instances. This drastically reduces boilerplate and decouples the core application from its feature modules.
- **Connection Pool Management**: Optimized asynchronous database connections with automatic lifespan handling to prevent connection leaks under load.

## 📋 Prerequisites
- Python 3.8+
- PostgreSQL database
- Keycloak Server (locally or cloud-hosted)
- LaTeX distribution (for PDF compilation)
- Google Cloud Project with Gemini API access

## 🔧 Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/T1t4n25/ResumeAI-API.git
cd ResumeAI-API
```

2. **Environment Setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install LaTeX Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full latexmk

# macOS
brew install --cask mactex
```

4. **Environment Variables:**
Create a `.env` file based on the provided `.env.example`:
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/resume_db
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=resume-flow
KEYCLOAK_CLIENT_ID=resume-api
```

## 🚀 Running the Application

1. **Start the server:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Access API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

*(Note: Protected endpoints require a valid JWT token obtained from Keycloak. Use the "Authorize" button in Swagger UI to inject your Bearer token).*

## 📝 Key Domains & Endpoints

Explore the full interactive documentation at `/docs` once the server is running. The API encompasses the following domains:

| Domain | Description | Auth Required |
|----------|-------------|---------------|
| **Auth** | User identity verification and Keycloak integration | No / Yes |
| **Cover Letters** | AI-driven generation of cover letters | Yes (JWT) |
| **Resumes** | LaTeX compilation orchestration of resumes | Yes (JWT) |
| **Interviews** | Dynamic AI interview simulation engine | Yes (JWT) |
| **Summaries** | Professional summary and project description generation | Yes (JWT) |
| **Health & Sentinel**| Application health checks and telemetry | No / Admin |

## 🏗️ Project Structure
```text
app/
├── core/                  # Core configurations (config, database, limiter)
├── features/              # Vertical slices
│   ├── auth/              # Keycloak integration and user identity checks
│   ├── cover_letters/     # AI cover letter generation pipelines
│   ├── health/            # Application health and DB checks
│   ├── interviews/        # AI interview simulation engine
│   ├── project_descriptions/
│   ├── resumes/           # LaTeX compilation orchestration
│   ├── sentinel/          # Admin/Monitoring capabilities
│   └── summaries/         # Professional summary generation
└── main.py                # FastAPI app entry point & dynamic router discovery
```

## 🧪 Testing

Execute the comprehensive test suite using `pytest`:
```bash
pytest tests/ -v
```

## 🔒 Security & Load Management

- **Identity & Access Management:** Delegated entirely to Keycloak. Services do not store passwords; they authenticate with the IdP and verify JWT signatures and claims.
- **Rate Limiting:** IP-based and user-based request throttling using `slowapi` to protect expensive AI token generation endpoints from abuse.
- **Environment Protection:** Sensitive secrets are managed via `pydantic-settings`, supporting strict type validation, variable overrides, and preventing credential leakage.

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

Contact **Zeyad Hemeda (@T1t4n25)** for commercial licensing:
- **Email**: [zeyad.mohammedwork@gmail.com](mailto:zeyad.mohammedwork@gmail.com)
- **GitHub**: [@T1t4n25](https://github.com/T1t4n25)

**Unauthorized commercial use constitutes copyright infringement and will be prosecuted.**

See `COMMERCIAL_LICENSE.md` for full terms.

## 👥 Author

- Zeyad Hemeda (@T1t4n25)
