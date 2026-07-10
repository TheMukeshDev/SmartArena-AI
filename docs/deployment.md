# SmartArena AI — Deployment Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker
- Firebase CLI (`npm i -g firebase-tools`)
- Google Cloud CLI (`gcloud`)

---

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your Firebase credentials and API keys

# Run development server
python app.py
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Watch mode (auto-compile Tailwind)
npm run dev

# Production build
npm run build
```

---

## Docker

```bash
cd backend

# Build
docker build -t smartarena-ai-backend .

# Run
docker run -p 8080:8080 --env-file .env smartarena-ai-backend
```

---

## Google Cloud Run Deployment

```bash
# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Build and deploy
gcloud run deploy smartarena-api \
  --source ./backend \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars "FLASK_ENV=production"
```

---

## Firebase Hosting Deployment

```bash
# Login to Firebase
firebase login

# Deploy frontend
firebase deploy --only hosting
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Environment (development/production/testing) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes |
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON | Dev only |
| `FIREBASE_CLIENT_EMAIL` | Service account email (env-based auth) | Dev only |
| `FIREBASE_PRIVATE_KEY` | Service account private key (env-based auth) | Dev only |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | Yes |
| `RATE_LIMIT_DEFAULT` | Max requests per window (int) | No (default: 100) |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window in seconds | No (default: 3600) |
| `RATE_LIMIT_DB_PATH` | SQLite path for rate limiter | No (default: ratelimit.db) |
| `CACHE_DB_PATH` | SQLite path for response cache | No (default: cache.db) |
| `CACHE_TTL_SECONDS` | Cache TTL in seconds | No (default: 3600) |
| `FORCE_HTTPS` | Force HTTPS redirect (0/1) | No (default: 1 in prod, 0 in dev) |

---

## Architecture Notes

### Rate Limiting (SQLite-backed)
The app uses a fixed-window SQLite rate limiter (no Redis needed). Each client IP gets a configurable number of requests per window. Rate limit data persists in `ratelimit.db`.

### Caching (SQLite-backed)
AI responses are cached in `cache.db` using SHA-256 keyed hashes. Cache entries have a configurable TTL and expired rows are cleaned opportunistically on writes.

### Security Headers
Flask-Talisman applies CSP, HSTS, X-Content-Type-Options, frame-options, and referrer-policy. Force HTTPS can be disabled via `FORCE_HTTPS=0` for local development.

### i18n
The frontend supports English, Spanish, French, Arabic, and Hindi for FIFA World Cup 2026. Language preference is stored in `localStorage` and sent to the AI backend for multilingual responses.
