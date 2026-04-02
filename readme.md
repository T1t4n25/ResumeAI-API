# SAFEER API — سفير

**Your AI Ambassador to Your Next Career.**

The intelligent backend powering [SAFEER](https://github.com/T1t4n25), an AI-driven SaaS platform that acts as a user's **Professional Ambassador** — crafting persuasive career materials with dual AI personas and conducting real-time audio mock interviews.

---

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| **Framework** | FastAPI (Python 3.11+, fully async) |
| **AI Engine** | Google Gemini 2.0 Flash Lite (`google-genai` SDK) |
| **Identity & Access** | Keycloak (OAuth2 / OIDC, RS256 JWT, JWKS) |
| **Database** | PostgreSQL + AsyncPG + SQLAlchemy 2.0 (async ORM) |
| **Real-Time Interviews** | LiveKit (WebRTC rooms + server-side AI agents) |
| **Document Compilation** | LaTeX (`latexmk` + `TexSoup` AST manipulation) |
| **Rate Limiting** | `slowapi` (IP-based and per-endpoint) |
| **Infrastructure Monitoring** | Coolify Sentinel integration |
| **Containerisation** | Docker Compose (postgres, keycloak, api) |

### Vertical Slice Architecture

Code is organised strictly by **feature domain**, not by technical layer. Each slice is self-contained with its own `models.py`, `routes.py`, `service.py`, and `generator.py`. The FastAPI application uses **dynamic router discovery** — it scans the `features/` directory at startup and auto-registers every `APIRouter` it finds, eliminating boilerplate and decoupling core from features.

```
app/
├── core/                          # Shared infrastructure
│   ├── auth/                     # Keycloak auth sub-package
│   │   ├── keycloak_config.py    # Keycloak connection settings
│   │   ├── keycloak_jwt_handler.py  # JWT verification (RS256/JWKS)
│   │   ├── keycloak_admin.py     # Admin API (user/role management)
│   │   └── auth_exceptions.py    # Auth-specific error codes
│   ├── config.py                 # Pydantic Settings (env-validated)
│   ├── database.py               # Async engine, session factory, pool mgmt
│   ├── security.py               # FastAPI auth dependencies
│   ├── dependencies.py           # Shared DI (user + db combos)
│   └── limiter.py                # Rate limiter instance
│
├── features/                      # Vertical slices
│   ├── auth/                     # Keycloak identity verification
│   ├── cover_letters/            # AI cover letter generation
│   ├── project_descriptions/     # AI project description generation
│   ├── summaries/                # AI professional summary generation
│   ├── resumes/                  # LaTeX resume compilation pipeline
│   ├── interviews/               # LiveKit AI interview rooms & agents
│   ├── health/                   # Health checks & API info
│   └── sentinel/                 # Coolify Sentinel metrics receiver
│
├── shared/                        # Cross-cutting utilities
│   ├── models/                   # SQLAlchemy ORM models
│   ├── utils/text_utils.py       # Token reduction for prompts
│   └── exceptions.py             # Base exception hierarchy
│
└── main.py                        # App init, CORS, lifespan, router discovery
```

### Keycloak Integration

- **RS256 JWT verification** using JWKS public key discovery (cached)
- **Role-based access control** via `require_role()` / `require_any_role()` dependency factories
- **Admin API** wrapper for user attribute management, role assignment/revocation
- **Token refresh** and **introspection** endpoints

---

## 📡 RESTful API

All endpoints follow REST conventions with proper HTTP status codes (`201 Created`, `204 No Content`, etc.) and paginated list responses.

### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/auth/me` | Current user info from token | JWT |
| `POST` | `/auth/refresh` | Refresh access token | Refresh Token |
| `GET` | `/auth/tokens/info` | Decode and inspect JWT claims | JWT |

### Cover Letters (Al-Wazir powered)
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/cover-letters` | Generate a tailored cover letter | JWT |
| `GET` | `/cover-letters` | List user's cover letters | JWT |
| `GET` | `/cover-letters/{id}` | Get specific cover letter | JWT |
| `DELETE` | `/cover-letters/{id}` | Delete cover letter | JWT |

### Project Descriptions
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/project-descriptions` | Generate project description | JWT |
| `GET` | `/project-descriptions` | List project descriptions | JWT |
| `GET` | `/project-descriptions/{id}` | Get specific description | JWT |

### Professional Summaries
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/summaries` | Generate professional summary | JWT |
| `GET` | `/summaries` | List summaries | JWT |
| `GET` | `/summaries/{id}` | Get specific summary | JWT |

### Resumes (LaTeX Pipeline)
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/resumes` | Compile LaTeX resume from structured data | JWT |
| `GET` | `/resumes` | List resumes | JWT |
| `GET` | `/resumes/{id}` | Get specific resume | JWT |
| `PATCH` | `/resumes/{id}` | Update resume metadata | JWT |
| `DELETE` | `/resumes/{id}` | Delete resume | JWT |

### AI Interviews (Al-Qadi powered — LiveKit)
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/interviews/rooms` | Create a LiveKit interview room | JWT |
| `GET` | `/interviews/rooms` | List interview rooms | JWT |
| `GET` | `/interviews/rooms/{id}` | Get interview room details | JWT |
| `POST` | `/interviews/rooms/{id}/start` | Start AI interviewer agent | JWT |
| `DELETE` | `/interviews/rooms/{id}` | End interview session | JWT |

### Infrastructure
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/` | API information and endpoint directory | — |
| `GET` | `/health` | Health check | — |
| `POST` | `/api/v1/sentinel/push` | Receive Coolify Sentinel metrics | Bearer Token |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Google Cloud project with Gemini API access
- LaTeX distribution (`texlive-full`, `latexmk`)

### 1. Clone & configure
```bash
git clone https://github.com/T1t4n25/ResumeAI-API.git
cd ResumeAI-API
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run with Docker Compose
```bash
docker-compose up -d
```
This starts **PostgreSQL**, **Keycloak** (port 8080), and the **API** (port 8000).

### 3. Run locally (development)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Keycloak separately
docker-compose up keycloak -d

# Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Keycloak Setup
1. Access admin console at `http://localhost:8080` (`admin/admin`)
2. Create realm: `resume-flow`
3. Create confidential client: `resume-flow-api`
4. Copy client secret → `.env` → `KEYCLOAK_CLIENT_SECRET`
5. Create a test user with credentials

### 5. Explore the API
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- Use the "Authorize" button with `Bearer <your_jwt_token>`

---

## ⚙️ Environment Variables

| Variable | Description | Required |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database credentials | ✅ |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Database connection | ✅ |
| `KEYCLOAK_URL` | Keycloak server URL | ✅ |
| `KEYCLOAK_REALM` | Keycloak realm name | ✅ |
| `KEYCLOAK_CLIENT_ID` | OIDC client ID | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | OIDC client secret | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET` | LiveKit credentials | For interviews |
| `SENTINEL_TOKEN` | Coolify Sentinel auth token | For monitoring |
| `ENVIRONMENT` | `development` / `production` | ❌ (default: dev) |
| `LOG_LEVEL` | Logging level | ❌ (default: INFO) |

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🔒 Security & Load Management

- **Identity & Access**: Delegated entirely to Keycloak. The API verifies JWT signatures using cached RS256 public keys — no passwords stored.
- **Rate Limiting**: Per-endpoint throttling via `slowapi` to protect expensive AI generation endpoints.
- **Environment Protection**: Secrets managed via `pydantic-settings` with strict type validation.
- **Connection Pooling**: Async engine with `pool_pre_ping`, configurable pool size and overflow.

---

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
