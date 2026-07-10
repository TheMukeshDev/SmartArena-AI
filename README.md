<div align="center">

# 🏟️ SmartArena AI

### AI-Powered Volunteer Co-Pilot — FIFA World Cup 2026

[![CI](https://github.com/themukeshdev/smartarena-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/themukeshdev/smartarena-ai/actions)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-ffca28?logo=firebase&logoColor=black)](https://firebase.google.com)
[![Gemini](https://img.shields.io/badge/Gemini-AI-4285f4?logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Built for under-trained stadium volunteers managing multilingual crowds in real time — crowd intelligence, incident response, and sustainability tracking in 5 languages.**

[Live Demo](#) · [Documentation](docs/) · [Architecture](docs/architecture.md) · [API Docs](docs/api.md) · [PS Alignment](docs/ps-alignment.md)

</div>

---

## Problem Statement

FIFA World Cup 2026 Challenge 4 — An AI-powered platform built for **under-trained stadium volunteers** who must coordinate multilingual crowds in real time. The system provides a **Volunteer Co-Pilot** mode with live zone status, AI-generated recommended actions, and multilingual guidance across English, Spanish, French, Arabic, and Hindi — enabling volunteers to make confident decisions under pressure.

**Why depth over breadth:** Every feature exists to support one persona (the volunteer) in one vertical (crowd management + multilingual coordination). Navigation, transport, sustainability, and admin capabilities are secondary features that feed data back into the volunteer's real-time awareness.

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Crowd Intelligence** | Gemini-powered crowd density analysis, congestion prediction, and gate routing |
| 🚨 **Incident Management** | Auto-classification, prioritization, volunteer dispatch, and AI announcements |
| 🗺️ **Interactive Stadium Map** | SVG-based live heatmap with clickable zones, keyboard navigation, and ARIA support |
| 🤝 **Volunteer Management** | Real-time location tracking, AI-optimized task assignment, task history |
| 🌱 **Sustainability Dashboard** | Energy, water, waste, and carbon tracking with AI optimization and Chart.js visualizations |
| 🤖 **AI Assistant** | Natural language queries with zone-aware navigation context and text-to-speech |
| 🚗 **Transportation Advisor** | AI-powered gate routing with parking, transit, rideshare, and walking suggestions |
| 🌤️ **Weather Intelligence** | Real-time weather data with operational notes for stadium planning |
| 🗣️ **Speech & Text** | Web Speech API voice input/output for the AI Assistant, supporting multiple languages |
| 📡 **Live Event Stream** | Server-Sent Events (SSE) for real-time incident notifications |
| 🌐 **Multilingual** | Full UI and AI responses in English, Spanish, French, Arabic, and Hindi |
| ♿ **Accessible** | Skip-to-content, keyboard navigation, ARIA labels, focus management, screen reader support |
| 🛡️ **Secure** | SQLite rate limiting, CSP headers, CSRF protection, RBAC, prompt injection defense |
| 🔐 **Role-Based Access** | Admin, volunteer, and fan roles with Firebase Custom Claims |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + TailwindCSS + JavaScript (ES6+) |
| Backend | Python Flask (Blueprints + Factory Pattern) |
| Database | Firebase Firestore |
| Cache | SQLite (SHA-256 keyed, TTL-based, indexed expiry) |
| Rate Limiting | SQLite (fixed-window, per-IP, atomic upsert) |
| Auth | Firebase Authentication (ID tokens + session cookies) |
| AI | Google Gemini 1.5 Flash API |
| Security | Flask-Talisman (CSP, HSTS, frame-options, Permissions-Policy) |
| Charts | Chart.js |
| Maps | SVG Stadium Map (accessible, keyboard-navigable) |
| Speech | Web Speech API (recognition + synthesis) |
| Events | Server-Sent Events (SSE) with keepalive heartbeat |
| i18n | Custom JS i18n (EN, ES, FR, AR, HI) |
| Hosting | Firebase Hosting + Cloud Run |
| CI/CD | GitHub Actions |

---

## Project Structure

```
smartarena-ai/
├── backend/
│   ├── app/
│   │   ├── config/          # Settings, Firebase, Logging, Prompts
│   │   ├── routes/          # Flask Blueprints (auth, ai_ops, health, admin, events)
│   │   ├── services/        # AI service, cache, navigation graph, weather
│   │   ├── ai/              # Gemini integration + prompt injection defense
│   │   ├── middleware/       # CORS, Auth (RBAC), Rate limiting (SQLite), Security headers
│   │   ├── models/          # Pydantic schemas (validated input models)
│   │   └── utils/           # Response helpers
│   ├── tests/               # Pytest test suite (187 tests)
│   ├── app.py               # Entry point
│   ├── gunicorn.conf.py     # Production WSGI config
│   ├── Dockerfile           # Container image
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── css/                 # TailwindCSS source & output
│   ├── js/                  # Config, auth, i18n, map, dashboard, sustainability, toast, admin
│   ├── assets/              # Static assets (images, icons)
│   ├── pages/               # HTML pages (dashboard, volunteer, admin, auth, map)
│   ├── index.html           # Landing page
│   ├── tailwind.config.js   # Tailwind configuration
│   └── package.json         # Node dependencies + ESLint
├── firebase/
│   ├── firebase.json        # Hosting config
│   ├── firestore.rules      # Security rules (10 collections)
│   └── firestore.indexes.json
├── docs/
│   ├── architecture.md      # System architecture
│   ├── api.md               # Full API documentation (20+ endpoints)
│   └── deployment.md        # Deployment guide
├── .github/workflows/
│   └── ci.yml               # CI pipeline (backend tests + frontend lint)
├── LICENSE                   # MIT License
├── .gitignore
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Firebase Project with Firestore enabled
- Google Gemini API key

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
cp .env.example .env           # Edit with your credentials
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev                    # Watch mode with TailwindCSS
```

Visit `http://localhost:5000/health` to verify the backend is running.

---

## Testing

### Backend Tests (187 tests)
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Frontend Linting
```bash
cd frontend
npx eslint js/
```

### Firestore Rules Tests
The Firestore rules tests require the Firebase emulator and Java/JRE to be installed.
Run the emulator in one terminal:
```bash
npx firebase-tools emulators:start --project smartarena-test-rules --only firestore
```
Then run the tests in another terminal:
```bash
cd frontend
npm install
npm run test:rules
```

---

## Docker

```bash
cd backend
docker build -t smartarena-ai .
docker run -p 8080:8080 --env-file .env smartarena-ai
```

---

## Deployment

See [Deployment Guide](docs/deployment.md) for full instructions on deploying to:
- **Firebase Hosting** (Frontend) — `smartarena-ai-eaa94.web.app`
- **Render.com** (Backend) — `https://smartarena-ai.onrender.com`

---

## Test Credentials

For manual testing of Role-Based Access Control (RBAC) and dashboard panels, the following users have been seeded in Firebase Authentication and Firestore:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@smartarena.ai` | `Admin123!` |
| **Volunteer** | `volunteer@smartarena.ai` | `Volunteer123!` |
| **Fan** | `fan@smartarena.ai` | `Fan123!` |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness probe with dependency checks |
| GET | `/api/v1/` | API root with endpoint listing |
| GET | `/api/v1/csrf-token` | Get CSRF token |
| GET | `/api/v1/config/firebase` | Firebase client configuration (public) |
| POST | `/api/v1/auth/sessionLogin` | Create session from Firebase ID token |
| POST | `/api/v1/auth/sessionLogout` | Destroy session |
| POST | `/api/v1/auth/register` | Register new user |
| GET | `/api/v1/auth/me` | Get current user profile |
| POST | `/api/v1/ai/incident` | Classify and prioritize an incident |
| POST | `/api/v1/ai/crowd/analyze` | Analyze crowd density data |
| POST | `/api/v1/ai/volunteer/assign` | Assign task to volunteer |
| POST | `/api/v1/ai/sustainability/optimize` | Run AI eco-optimizer |
| POST | `/api/v1/ai/assistant/chat` | Chat with ArenaBot (supports preferred_language) |
| POST | `/api/v1/ai/transport/suggest` | Get transport directions to a gate |
| GET | `/api/v1/ai/navigation/zones` | List all zones with adjacency graph |
| GET | `/api/v1/ai/navigation/path` | Find shortest path between zones |
| GET | `/api/v1/ai/navigation/path/accessible` | Find accessible path (no stairs) |
| GET | `/api/v1/ai/weather` | Fetch current weather data |
| GET | `/api/v1/admin/gates` | List all stadium gates (admin) |
| POST | `/api/v1/admin/gates` | Update gate status/capacity (admin) |
| GET | `/api/v1/admin/announcements` | List announcements (admin) |
| POST | `/api/v1/admin/announcements` | Create announcement (admin) |
| DELETE | `/api/v1/admin/announcements/<id>` | Delete announcement (admin) |
| GET | `/api/v1/admin/security/logs` | List security audit logs (admin) |
| GET | `/api/v1/admin/users` | List all users (admin) |
| POST | `/api/v1/admin/import-dataset` | Import CSV/JSON stadium dataset (admin) |
| GET | `/api/v1/events/incidents` | SSE stream for real-time incidents |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ using Gemini AI, Flask, and Firebase — FIFA World Cup 2026 Challenge 4**

</div>
