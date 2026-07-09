# SmartArena AI — API Documentation

## Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://smartarena-api-<hash>.run.app`

## API Version

All versioned endpoints are prefixed with `/api/v1/`.

---

## Health & Status

### GET `/health`

Basic health check.

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

Readiness probe with dependency checks.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ready",
    "checks": {
      "flask": true,
      "firebase": true
    },
    "timestamp": "2026-07-09T12:00:00Z"
  }
}
```

### GET `/api/v1/`

API root with endpoint listing.

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
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

---

*More endpoints will be documented as features are implemented in subsequent phases.*
