<div align="center">

# 🏟️ SmartArena AI

### AI-Powered Smart Stadium Operations Platform

[![CI](https://github.com/yourusername/smartarena-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/smartarena-ai/actions)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-ffca28?logo=firebase&logoColor=black)](https://firebase.google.com)
[![Gemini](https://img.shields.io/badge/Gemini-AI-4285f4?logo=google&logoColor=white)](https://ai.google.dev)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-06b6d4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Real-time crowd intelligence • AI incident management • Sustainability tracking**

[Live Demo](#) · [Documentation](docs/) · [Architecture](docs/architecture.md) · [API Docs](docs/api.md)

</div>

---

## 🎯 Overview

SmartArena AI is an intelligent stadium operations platform that leverages **Google Gemini AI** to provide real-time crowd management, predictive analytics, incident response, volunteer coordination, and sustainability monitoring for modern sports venues.

### Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Crowd Intelligence** | Gemini-powered crowd density analysis, congestion prediction, and gate routing |
| 🚨 **Incident Management** | Auto-classification, prioritization, volunteer dispatch, and AI announcements |
| 🗺️ **Interactive Stadium Map** | SVG-based live heatmap with clickable zones and occupancy data |
| 🤝 **Volunteer Management** | Real-time location tracking, AI-optimized task assignment |
| 🌱 **Sustainability Dashboard** | Energy, water, waste, and carbon tracking with AI optimization |
| 🤖 **AI Assistant** | Natural language queries, report generation, PDF/CSV export |
| 📊 **Analytics Dashboard** | Chart.js powered real-time statistics and trend analysis |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + TailwindCSS + JavaScript |
| Backend | Python Flask (Blueprints) |
| Database | Firebase Firestore |
| Auth | Firebase Authentication |
| AI | Google Gemini API |
| Charts | Chart.js |
| Maps | SVG Stadium Map |
| Animation | GSAP + Lottie |
| Hosting | Firebase Hosting + Cloud Run |
| CI/CD | GitHub Actions |

---

## 📁 Project Structure

```
smartarena-ai/
├── backend/
│   ├── app/
│   │   ├── config/          # Settings, Firebase, Logging
│   │   ├── routes/          # Flask Blueprints
│   │   ├── services/        # Business logic
│   │   ├── ai/              # Gemini integration
│   │   ├── middleware/       # CORS, Auth, Rate limiting
│   │   ├── models/          # Data models
│   │   ├── utils/           # Response helpers
│   │   └── templates/       # Jinja2 templates
│   ├── tests/               # Pytest test suite
│   ├── app.py               # Entry point
│   ├── gunicorn.conf.py     # Production WSGI config
│   ├── Dockerfile           # Container image
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── css/                 # TailwindCSS source & output
│   ├── js/                  # Application logic
│   ├── assets/              # Static assets
│   ├── pages/               # HTML pages
│   ├── components/          # Reusable partials
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

## 🚀 Quick Start

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

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 🐳 Docker

```bash
cd backend
docker build -t smartarena-ai .
docker run -p 8080:8080 --env-file .env smartarena-ai
```

---

## 📦 Deployment

See [Deployment Guide](docs/deployment.md) for full instructions on deploying to:
- **Firebase Hosting** (Frontend)
- **Google Cloud Run** (Backend)

---

## 🛣️ Roadmap

- [x] Phase 1 — Foundation & Architecture
- [ ] Phase 2 — Authentication (Firebase Auth + JWT + RBAC)
- [ ] Phase 3 — AI Dashboard
- [ ] Phase 4 — Interactive Stadium Map
- [ ] Phase 5 — AI Crowd Intelligence
- [ ] Phase 6 — Incident Management
- [ ] Phase 7 — Volunteer Management
- [ ] Phase 8 — Sustainability Dashboard
- [ ] Phase 9 — Reports & AI Assistant
- [ ] Phase 10 — Production Audit & Deployment

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built with ❤️ using Gemini AI, Flask, and Firebase**

</div>
