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
| `FLASK_ENV` | Environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `FIREBASE_PROJECT_ID` | Firebase project ID | Yes |
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON | Dev only |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `CORS_ORIGINS` | Comma-separated allowed origins | Yes |
