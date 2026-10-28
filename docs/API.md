# Arambh API Documentation

Base URL: `http://localhost:8000/api`
Interactive Docs: `http://localhost:8000/api/docs`

---

## Authentication

### POST /auth/register
Register a new user.
```json
{ "name": "string", "email": "string", "password": "string (min 8 chars)" }
```
Returns: `{ access_token, refresh_token, user }`

### POST /auth/login
Login (OAuth2 form).
```
username=email&password=pass
```
Returns: `{ access_token, refresh_token, token_type, user }`

### POST /auth/refresh
Refresh access token.
Query param: `?refresh_token=<token>`

### GET /auth/me
Get current user profile. Requires Bearer token.

---

## Chat

### POST /chat/message
Send a message (streaming SSE by default).
```json
{
  "message": "What are COEP fees?",
  "session_id": "uuid",
  "language": "en",
  "college_filter": null,
  "stream": true
}
```
SSE events:
- `data: {"type":"sources","sources":[...]}`
- `data: {"type":"token","content":"..."}`
- `data: {"type":"metadata","confidence":0.9}`
- `data: [DONE]`

### GET /chat/sessions
Get all conversation sessions for current user.

### GET /chat/history/{session_id}
Get full chat history for a session.

### DELETE /chat/session/{session_id}
Delete a conversation session.

### POST /chat/feedback
```json
{ "session_id": "uuid", "message_index": 1, "was_helpful": true }
```

---

## Colleges

### GET /colleges/
List colleges. Query params: `search`, `college_type`, `city`, `skip`, `limit`

### GET /colleges/{id}
Get a college by ID.

### POST /colleges/ (Admin)
Create a college.

### PUT /colleges/{id} (Admin)
Update a college.

---

## Documents (Admin)

### POST /documents/upload
Upload a PDF/DOCX for indexing.
Form data: `file`, `college_id`, `document_type`

### GET /documents/
List all uploaded documents.

### GET /documents/{id}/status
Get document indexing status.

---

## Crawler (Admin)

### POST /crawler/start
Start a web crawl job.
```json
{ "url": "https://college-website.com", "college_id": "optional", "max_depth": 3 }
```

### GET /crawler/jobs
List all crawl jobs.

---

## Analytics (Admin)

### GET /analytics/stats
Returns: total_queries, helpful_responses, total_users, total_colleges, top_queries
