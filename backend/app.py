"""
SmartArena AI — Application Entry Point
=========================================

Starts the Flask development server.
For production, use Gunicorn: gunicorn -c gunicorn.conf.py app:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=int(app.config.get("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
