# =============================================================================
# SmartArena AI — Production Docker Image
# =============================================================================
# Multi-stage build for minimal image size

FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN useradd -m appuser && chown -R appuser /app
USER appuser

# ── Install Dependencies ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Code ──────────────────────────────────────────────
COPY . .

# ── Expose Port ─────────────────────────────────────────────────────────
# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

# ── Health Check ─────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# ── Run with Gunicorn ────────────────────────────────────────────────────
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
