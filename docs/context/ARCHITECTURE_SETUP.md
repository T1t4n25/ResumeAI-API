# Architecture Setup Guide

This document explains how to set up and run the Resume Flow API with the new vertical slicing architecture and Keycloak authentication.

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Access to Google Gemini API (for AI generation features)

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `KEYCLOAK_URL`: Keycloak server URL (http://localhost:8080 for local)
- `KEYCLOAK_REALM`: Keycloak realm name (default: resume-flow)
- `KEYCLOAK_CLIENT_ID`: Keycloak client ID (default: resume-flow-api)
- `GEMINI_API_KEY`: Your Google Gemini API key

### 3. Start Services with Docker Compose

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL**: Database for the application
- **Keycloak Database**: Separate database for Keycloak
- **Keycloak**: Authentication server on port 8080
- **FastAPI API**: Application server on port 8000

### 4. Keycloak Setup

After Keycloak starts (wait ~60 seconds for initialization):

1. Access Keycloak Admin Console: http://localhost:8080
   - Username: `admin` (default)
   - Password: `admin` (from .env)

2. Create a Realm:
   - Click "Create Realm" or select existing
   - Name: `resume-flow` (or match your KEYCLOAK_REALM)

3. Create a Client:
   - Go to "Clients" → "Create client"
   - Client ID: `resume-flow-api` (match KEYCLOAK_CLIENT_ID)
   - Client authentication: **ON** (confidential client)
   - Authorization: **OFF** (can enable later)
   - Valid redirect URIs: `http://localhost:8000/*`
   - Web origins: `http://localhost:8000`
   - Save

4. Get Client Secret:
   - Open the client → "Credentials" tab
   - Copy the "Client secret"
   - Update `KEYCLOAK_CLIENT_SECRET` in `.env`

5. Create a User:
   - Go to "Users" → "Create new user"
   - Set username, email, first name, last name
   - Go to "Credentials" tab
   - Set password and disable "Temporary"
   - Save

### 5. Get Access Token

#### Using Keycloak Admin Console:
1. Go to your realm → "Test" → "Token generation"
2. Select the user
3. Click "Generate"
4. Copy the "Access token"

#### Using curl:
```bash
curl -X POST http://localhost:8080/realms/resume-flow/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=resume-flow-api" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "username=your_username" \
  -d "password=your_password" \
  -d "grant_type=password"
```

#### Using Python:
```python
import httpx

response = httpx.post(
    "http://localhost:8080/realms/resume-flow/protocol/openid-connect/token",
    data={
        "client_id": "resume-flow-api",
        "client_secret": "YOUR_CLIENT_SECRET",
        "username": "your_username",
        "password": "your_password",
        "grant_type": "password"
    }
)
token = response.json()["access_token"]
print(token)
```

### 6. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get current user info (requires token)
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/auth/me

# Get token info
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/auth/token-info
```

## Architecture Overview

### Directory Structure

```
app/
├── core/                    # Shared infrastructure
│   ├── config.py           # Pydantic Settings configuration
│   ├── database.py         # Async SQLAlchemy setup
│   ├── security.py         # Keycloak authentication
│   └── dependencies.py     # Shared FastAPI dependencies
│
├── features/               # Feature slices (vertical architecture)
│   └── auth/              # Authentication feature
│       ├── models.py      # Pydantic request/response models
│       ├── routes.py      # API endpoints
│       ├── service.py     # Business logic
│       └── dependencies.py # Feature-specific dependencies
│
├── shared/                # Shared domain models & utilities
│   ├── models/           # SQLAlchemy models
│   ├── utils/            # Utility functions
│   └── exceptions.py     # Custom exceptions
│
└── main.py               # FastAPI app initialization
```

### Vertical Slicing Principles

1. **Feature Independence**: Each feature is self-contained
2. **No Cross-Feature Imports**: Features communicate through shared interfaces
3. **Feature-Specific Dependencies**: Each feature can have its own DI
4. **Self-Contained Testing**: Each feature is testable in isolation

### Keycloak Integration

The authentication system uses:
- **OAuth2/OIDC** protocol with JWT tokens
- **RS256** algorithm for token signing
- **JWKS** endpoint for public key discovery
- **Token caching** for performance
- **Userinfo endpoint** for user information

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Keycloak (still use Docker)
docker-compose up keycloak -d

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest tests/
```

## Migration Notes

### From Old Architecture

The old architecture used:
- Custom API key authentication
- Synchronous database operations
- Monolithic structure

The new architecture:
- Keycloak OAuth2/OIDC authentication
- Async database operations
- Vertical slicing by feature

### Backward Compatibility

During migration:
- Old API key authentication is still available (legacy support)
- Both authentication methods can coexist
- Gradually migrate endpoints to use Keycloak

## Troubleshooting

### Keycloak Not Starting

- Check logs: `docker-compose logs keycloak`
- Wait at least 60 seconds for initialization
- Verify database connection

### Token Verification Fails

- Check `KEYCLOAK_URL` and `KEYCLOAK_REALM` in `.env`
- Verify client secret is correct
- Ensure token hasn't expired
- Check Keycloak logs for errors

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify network connectivity between services

## Next Steps

1. Migrate remaining features to vertical slices:
   - `cover_letters/`
   - `project_descriptions/`
   - `summaries/`
   - `resumes/`
   - `interviews/`

2. Add comprehensive tests for each feature

3. Set up CI/CD pipeline

4. Configure production Keycloak instance

5. Set up monitoring and logging

