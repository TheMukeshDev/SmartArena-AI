"""
SmartArena AI — Gunicorn Configuration
========================================

Production WSGI server configuration for Cloud Run deployment.
Cloud Run provides PORT via environment variable.
"""

import os
import multiprocessing

# ── Server Socket ───────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# ── Worker Processes ────────────────────────────────────────────────────
# Cloud Run: Use 1 worker per vCPU, minimum 2
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
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
