"""
SmartArena AI — WSGI Entry Point
=================================

Used by Render (and any host that expects a standard wsgi.py shim).
For direct Gunicorn invocation: gunicorn -c gunicorn.conf.py app:app
"""

from app import create_app

app = create_app()
