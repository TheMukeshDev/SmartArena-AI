# SmartArena AI — Architecture

## System Overview

SmartArena AI is an AI-powered smart stadium operations platform designed to manage real-time crowd intelligence, incident handling, volunteer coordination, and sustainability metrics using Google's Gemini AI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/JS)                     │
│              TailwindCSS + Chart.js + GSAP               │
│                  Firebase Hosting                         │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS / REST API
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask Backend (API)                      │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Routes   │  │ Services │  │   AI     │              │
│  │(Blueprints)│  │  Layer   │  │ (Gemini) │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                    │
│  ┌────┴──────────────┴──────────────┴─────┐             │
│  │          Middleware Layer               │             │
│  │   CORS │ Auth │ Rate Limit │ Logging   │             │
│  └────────────────────────────────────────┘             │
│                  Cloud Run / Render                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Firebase Services                            │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  Firestore   │  │  Firebase    │                     │
│  │  (Database)  │  │  Auth        │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **App Factory** | `create_app()` for testable Flask initialization |
| **Blueprint** | Modular route registration per feature |
| **Config Inheritance** | `BaseConfig` → `DevelopmentConfig` / `ProductionConfig` |
| **Singleton** | Firebase/Firestore client shared across app |
| **Service Layer** | Business logic separated from route handlers |
| **Repository Pattern** | Database access abstracted (future) |

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `app/config/` | Settings, Firebase init, logging setup |
| `app/routes/` | HTTP endpoint definitions (Blueprints) |
| `app/services/` | Business logic and data processing |
| `app/ai/` | Gemini AI integration and prompts |
| `app/models/` | Data models and validation schemas |
| `app/middleware/` | CORS, auth, rate limiting |
| `app/utils/` | Shared utilities and response helpers |

## Security Measures

- JWT-based authentication via Firebase Auth
- Role-based access control (Admin / Volunteer / Fan)
- CORS whitelisting
- Rate limiting on API endpoints
- CSRF protection
- Input validation via Pydantic schemas
- Firestore security rules enforce server-side authorization

## Deployment

- **Frontend**: Firebase Hosting with CDN
- **Backend**: Google Cloud Run (containerized)
- **CI/CD**: GitHub Actions for automated testing and deployment
