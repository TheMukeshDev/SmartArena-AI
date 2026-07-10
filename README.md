<div align="center">

# 🏟️ SmartArena AI

### AI-Powered Smart Stadium Operations Platform — FIFA World Cup 2026

[![CI](https://github.com/themukeshdev/smartarena-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/themukeshdev/smartarena-ai/actions)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-ffca28?logo=firebase&logoColor=black)](https://firebase.google.com)
[![Gemini](https://img.shields.io/badge/Gemini-AI-4285f4?logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Real-time crowd intelligence • AI incident management • Sustainability tracking • Multilingual (EN/ES/FR/AR)**

[Live Demo](#) · [Documentation](docs/) · [Architecture](docs/architecture.md) · [API Docs](docs/api.md)

</div>

---

## Problem Statement

FIFA World Cup 2026 Challenge 4 — Develop an AI-powered platform for smart stadium operations at scale, handling crowd management, incident response, volunteer coordination, sustainability tracking, and multilingual support for diverse audiences across USA, Mexico, and Canada.

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Crowd Intelligence** | Gemini-powered crowd density analysis, congestion prediction, and gate routing |
| 🚨 **Incident Management** | Auto-classification, prioritization, volunteer dispatch, and AI announcements |
| 🗺️ **Interactive Stadium Map** | SVG-based live heatmap with clickable zones, keyboard navigation, and ARIA support |
| 🤝 **Volunteer Management** | Real-time location tracking, AI-optimized task assignment |
| 🌱 **Sustainability Dashboard** | Energy, water, waste, and carbon tracking with AI optimization |
| 🤖 **AI Assistant** | Natural language queries with zone-aware navigation context |
| 🚗 **Transportation Advisor** | AI-powered gate routing with parking, transit, rideshare, and walking suggestions |
| 🌐 **Multilingual** | Full UI and AI responses in English, Spanish, French, and Arabic |
| ♿ **Accessible** | Skip-to-content, keyboard navigation, ARIA labels, screen reader support |
| 🛡️ **Secure** | SQLite rate limiting, CSP headers, prompt injection defense, CSRF protection |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + TailwindCSS + JavaScript |
| Backend | Python Flask (Blueprints + Factory Pattern) |
| Database | Firebase Firestore |
| Cache | SQLite (SHA-256 keyed, TTL-based) |
| Rate Limiting | SQLite (fixed-window, per-IP) |
| Auth | Firebase Authentication |
| AI | Google Gemini 1.5 Flash API |
| Security | Flask-Talisman (CSP, HSTS, frame-options) |
| Charts | Chart.js |
| Maps | SVG Stadium Map (accessible) |
| i18n | Custom JS i18n (EN, ES, FR, AR) |
| Hosting | Firebase Hosting + Cloud Run |
| CI/CD | GitHub Actions |

---

## Project Structure

```
smartarena-ai/
├── backend/
│   ├── app/
│   │   ├── config/          # Settings, Firebase, Logging, Prompts
│   │   ├── routes/          # Flask Blueprints (auth, ai_ops, health, navigation)
│   │   ├── services/        # AI service, cache, navigation graph
│   │   ├── ai/              # Gemini integration + prompt injection defense
│   │   ├── middleware/       # CORS, Auth, Rate limiting (SQLite), Security headers
│   │   ├── models/          # Pydantic schemas
│   │   ├── utils/           # Response helpers
│   │   └── templates/       # Jinja2 templates
│   ├── tests/               # Pytest test suite
│   ├── app.py               # Entry point
│   ├── gunicorn.conf.py     # Production WSGI config
│   ├── Dockerfile           # Container image
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── css/                 # TailwindCSS source & output
│   ├── js/                  # Config, auth, i18n, map, dashboard, sustainability
│   ├── assets/              # Static assets
│   ├── pages/               # HTML pages
│   ├── index.html           # Landing page
│   ├── tailwind.config.js   # Tailwind configuration
│   └── package.json         # Node dependencies
├── firebase/
│   ├── firebase.json        # Hosting config
│   ├── firestore.rules      # Security rules
│   └── firestore.indexes.json
├── docs/
│   ├── architecture.md      # System architecture
│   ├── api.md               # API documentation
│   └── deployment.md        # Deployment guide
├── .github/workflows/
│   └── ci.yml               # CI pipeline
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
pip install -r requirements.txt
cp .env.example .env           # Edit with your credentials
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev                    # Watch mode
```

Visit `http://localhost:5000/health` to verify the backend is running.

---

## Testing

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
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
- **Firebase Hosting** (Frontend)
- **Google Cloud Run** (Backend)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/incident` | Classify and prioritize an incident |
| POST | `/api/v1/ai/crowd/analyze` | Analyze crowd density data |
| POST | `/api/v1/ai/volunteer/assign` | Assign task to volunteer |
| POST | `/api/v1/ai/sustainability/optimize` | Run AI eco-optimizer |
| POST | `/api/v1/ai/assistant/chat` | Chat with ArenaBot (supports preferred_language) |
| POST | `/api/v1/ai/transport/suggest` | Get transport directions to a gate |
| GET | `/api/v1/ai/navigation/zones` | List all zones with adjacency graph |
| GET | `/api/v1/ai/navigation/path?start=X&end=Y` | Find shortest path between zones |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/csrf-token` | Get CSRF token |

---

## License

This project is licensed under the MIT License.

---

<div align="center">

**Built with ❤️ using Gemini AI, Flask, and Firebase — FIFA World Cup 2026 Challenge 4**

</div>
