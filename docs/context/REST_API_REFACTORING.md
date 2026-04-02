# REST API Endpoint Reference

## Current Endpoints (RESTful)

All endpoints follow REST conventions with proper HTTP status codes and resource-based URIs.

### Authentication

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `GET` | `/auth/me` | 200 | Get current user info from Keycloak token |
| `POST` | `/auth/refresh` | 200 | Refresh access token |
| `GET` | `/auth/tokens/info` | 200 | Decode and inspect JWT claims |

### Cover Letters

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/cover-letters` | 201 | Generate a new cover letter |
| `GET` | `/cover-letters` | 200 | List all cover letters (paginated) |
| `GET` | `/cover-letters/{id}` | 200 | Get specific cover letter |
| `DELETE` | `/cover-letters/{id}` | 204 | Delete cover letter |

### Project Descriptions

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/project-descriptions` | 201 | Generate project description |
| `GET` | `/project-descriptions` | 200 | List project descriptions (paginated) |
| `GET` | `/project-descriptions/{id}` | 200 | Get specific description |

### Summaries

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/summaries` | 201 | Generate professional summary |
| `GET` | `/summaries` | 200 | List summaries (paginated) |
| `GET` | `/summaries/{id}` | 200 | Get specific summary |

### Resumes

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/resumes` | 201 | Compile LaTeX resume |
| `GET` | `/resumes` | 200 | List resumes (paginated) |
| `GET` | `/resumes/{id}` | 200 | Get specific resume |
| `PATCH` | `/resumes/{id}` | 200 | Update resume metadata |
| `DELETE` | `/resumes/{id}` | 204 | Delete resume |

### Interviews

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/interviews/rooms` | 201 | Create LiveKit interview room |
| `GET` | `/interviews/rooms` | 200 | List interview rooms (paginated) |
| `GET` | `/interviews/rooms/{id}` | 200 | Get room details |
| `POST` | `/interviews/rooms/{id}/start` | 200 | Start AI interviewer agent |
| `DELETE` | `/interviews/rooms/{id}` | 204 | End interview session |

### Infrastructure

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `GET` | `/` | 200 | API information and endpoint directory |
| `GET` | `/health` | 200 | Health check |
| `POST` | `/api/v1/sentinel/push` | 200 | Receive Coolify Sentinel metrics |

## Response Conventions

### Create Responses (POST → 201)
All creation endpoints return the generated resource with:
- `id`: UUID identifier
- `created_at` / `updated_at`: ISO 8601 timestamps

### List Responses (GET → 200)
All list endpoints return paginated responses:
```json
{
  "data": [...],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

### Standard Status Codes
| Code | Meaning |
|---|---|
| `200 OK` | Successful GET, PATCH |
| `201 Created` | Successful POST (new resource) |
| `204 No Content` | Successful DELETE |
| `400 Bad Request` | Invalid input |
| `401 Unauthorized` | Missing/invalid auth |
| `403 Forbidden` | Insufficient permissions |
| `404 Not Found` | Resource doesn't exist |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Server error |

## Implementation Notes

### Fully Functional Endpoints
- All `POST` creation endpoints (cover letters, summaries, project descriptions, resumes, interview rooms/start)
- All auth endpoints
- Health and sentinel endpoints

### Stub Endpoints (Awaiting Persistence Layer)
- `GET /{resource}/{id}` — Returns 404 (needs database lookup)
- `GET /{resource}` — Returns empty list (needs database query)
- `DELETE /{resource}/{id}` — Returns 404 (needs database deletion)
- `PATCH /resumes/{id}` — Returns 404 (needs database update)

These stubs have correct request/response models and status codes — they just need the persistence layer wired in.
