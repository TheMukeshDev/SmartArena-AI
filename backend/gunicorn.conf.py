"""
SmartArena AI — Gunicorn Configuration
=======================================

Production WSGI server configuration for Render / Cloud Run deployment.
Render provides PORT via environment variable (default 10000).
Cloud Run provides PORT via environment variable (default 8080).
"""

import os
import multiprocessing

# ── WSGI Application ─────────────────────────────────────────────────────
# Ensures gunicorn always finds the Flask app even when Render invokes
# gunicorn without an explicit app module argument (e.g. its default
# "gunicorn your_application.wsgi" start command).
# Note: app/__init__.py uses a factory (create_app), so "app:app" won't
# work — gunicorn needs the wsgi.py shim which exposes the created instance.
wsgi_app = "wsgi:app"

# ── Server Socket ───────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# ── Worker Processes ────────────────────────────────────────────────────
# Cloud Run: Use 1 worker per vCPU, minimum 2
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "gthread"
threads = int(os.getenv("MAX_THREADS", 8))
worker_connections = 1000
timeout = 120
keepalive = 5

# ── Logging ─────────────────────────────────────────────────────────────
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ── Process Naming ──────────────────────────────────────────────────────
proc_name = "smartarena-ai"


# ── Server Hooks ────────────────────────────────────────────────────────
def on_starting(server):
    """Log when Gunicorn starts."""
    pass


def on_exit(server):
    """Cleanup on shutdown."""
    pass
