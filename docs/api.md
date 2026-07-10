# SmartArena AI — API Documentation

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://smartarena-api-<hash>.run.app`

## API Version

All versioned endpoints are prefixed with `/api/v1/`.

---

## Authentication

SmartArena AI uses **Firebase Authentication** with two credential types:

1. **ID Token** — Sent via `Authorization: Bearer <token>` header
2. **Session Cookie** — Set automatically after `sessionLogin`, sent via `Cookie: session=<cookie>`

All protected endpoints require at least one of these credentials. Some admin endpoints additionally require the `admin` role via Firebase Custom Claims.

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "type": "Not Found",
    "code": 404,
    "message": "Resource not found: /api/v1/unknown"
  }
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request / Validation Error |
| 401 | Unauthorized (missing/invalid credentials) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## Rate Limiting

All non-health endpoints are rate-limited per IP. Response headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Requests remaining in current window |

---

## Health & Status

### GET `/health`

Basic health check (exempt from rate limiting).

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "SmartArena AI",
    "version": "1.0.0",
    "timestamp": "2026-07-09T12:00:00Z"
  }
}
```

### GET `/health/ready`

Readiness probe with dependency checks (Firebase).

**Response (200 or 503):**
```json
{
  "success": true,
  "data": {
    "status": "ready",
    "checks": { "flask": true, "firebase": true },
    "timestamp": "2026-07-09T12:00:00Z"
  }
}
```

### GET `/api/v1/`

API root with endpoint listing.

---

## Authentication Endpoints

### POST `/api/v1/auth/sessionLogin`

Create a server-side session from a Firebase ID token.

**Request Body:**
```json
{ "idToken": "<firebase-id-token>" }
```

**Response (200):**
```json
{ "success": true, "data": { "message": "Session created" } }
```

### POST `/api/v1/auth/sessionLogout`

Destroy the current session.

**Response (200):**
```json
{ "success": true, "data": { "message": "Logged out" } }
```

### POST `/api/v1/auth/register`

Register a new user. Sets a session cookie on success.

**Request Body:**
```json
{
  "uid": "firebase-uid",
  "email": "user@example.com",
  "name": "Jane Doe",
  "role": "fan"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": { "uid": "...", "email": "...", "name": "...", "role": "fan" },
  "message": "User registered."
}
```

### GET `/api/v1/auth/me`

Get current authenticated user's profile.

**Response (200):**
```json
{
  "success": true,
  "data": { "uid": "...", "email": "...", "name": "...", "role": "admin" }
}
```

### GET `/api/v1/csrf-token`

Get a CSRF token for form submissions.

**Response (200):**
```json
{ "csrf_token": "a1b2c3d4..." }
```

---

## AI Operations

All AI endpoints require authentication.

### POST `/api/v1/ai/incident`

Classify and prioritize an incident report.

**Request Body:**
```json
{ "description": "Fan spilled drink in Section 12" }
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "original_description": "...",
    "classification": {
      "category": "Cleanliness",
      "priority": "Low",
      "action": "Send cleaning crew",
      "announcement": "Please be careful in Section 12."
    }
  }
}
```

### POST `/api/v1/ai/crowd/analyze`

Analyze crowd density for specified zones.

**Request Body:**
```json
{ "zones": ["North Stand", "South Concourse"] }
```

**Response (200):**
```json
{ "success": true, "data": { "analysis": "..." }, "message": "Crowd analysis complete." }
```

### POST `/api/v1/ai/volunteer/assign`

Assign a volunteer task at a location.

**Request Body:**
```json
{ "location": "North Stand Gate A" }
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "task": "Guide crowd at Gate A",
    "description": "Help direct incoming fans...",
    "priority": "High"
  },
  "message": "Task assigned."
}
```

### POST `/api/v1/ai/sustainability/optimize`

Run the AI eco-optimizer with current metrics.

**Request Body:**
```json
{
  "metrics": {
    "energy_kwh": 45000,
    "water_liters": 120000,
    "waste_kg": 8000
  }
}
```

### POST `/api/v1/ai/assistant/chat`

Chat with ArenaBot (supports context and multi-language).

**Request Body:**
```json
{
  "query": "Where is the nearest food court?",
  "context": { "current_zone": "North Stand" },
  "preferred_language": "en",
  "previous_interaction_id": "optional-id"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "reply": "The nearest food court is in the Concourse North zone...",
    "interaction_id": "abc123"
  }
}
```

### POST `/api/v1/ai/transport/suggest`

Get transport directions to a gate.

**Request Body:**
```json
{ "gate": "Gate C", "arrival_time": "18:00" }
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "recommended_mode": "Metro",
    "estimated_travel_time_minutes": 25,
    "directions": "Take Line 2 to Stadium Station...",
    "alternative": "Rideshare via Gate B entrance"
  }
}
```

### GET `/api/v1/ai/navigation/zones`

Return the full zone map with adjacency graph.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "zones": ["North Stand", "South Stand", "West VIP", "East Concourse", ...],
    "adjacency": { "North Stand": ["East Concourse", "Concourse North"], ... },
    "sensory_friendly_zones": ["Quiet Zone A"]
  }
}
```

### GET `/api/v1/ai/navigation/path?start=X&end=Y`

Find the shortest path between two zones.

### GET `/api/v1/ai/navigation/path/accessible?start=X&end=Y`

Find an accessible path (avoids stairs).

### GET `/api/v1/ai/weather`

Fetch current weather data for the venue.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "temperature_c": 28,
    "precipitation_mm": 0,
    "wind_speed_kmh": 12,
    "weather_code": 1,
    "summary": "Partly cloudy",
    "operational_note": "No weather disruptions expected."
  }
}
```

---

## Admin Endpoints

All admin endpoints require authentication with the `admin` role.

### GET `/api/v1/admin/gates`

List all stadium gates with capacity and status.

### POST `/api/v1/admin/gates`

Update a gate's status and/or capacity.

**Request Body:**
```json
{ "name": "Gate A", "status": "open", "capacity": 5000 }
```

### GET `/api/v1/admin/announcements`

List all announcements.

### POST `/api/v1/admin/announcements`

Create a new announcement.

**Request Body:**
```json
{
  "title": "Severe Weather Warning",
  "message": "Please proceed to nearest indoor shelter.",
  "priority": "urgent",
  "target_zones": ["North Stand", "South Stand"]
}
```

### DELETE `/api/v1/admin/announcements/<id>`

Delete an announcement by ID.

### GET `/api/v1/admin/security/logs`

List security audit logs (admin actions, auth events).

### GET `/api/v1/admin/users`

List all registered users (limited to 500).

---

## Events (Server-Sent Events)

### GET `/api/v1/events/incidents`

Real-time SSE stream of classified incidents.

**Response:** `text/event-stream`

Events are pushed as:
```
event: incident
data: {"incident": { "description": "...", "classification": {...} }}
```

Includes a keepalive heartbeat comment (`: heartbeat`) every 15 seconds.
