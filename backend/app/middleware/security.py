"""
SmartArena AI — Security Headers (Flask-Talisman)
===================================================

Applies Content-Security-Policy, HSTS, X-Content-Type-Options,
frame-options, and referrer-policy via Flask-Talisman.
"""

import logging
from flask import Flask
from flask_talisman import Talisman

logger = logging.getLogger(__name__)

CSP_POLICY = {
    "default-src": ["'self'"],
    "script-src": [
        "'self'",
        "https://www.gstatic.com",
        "https://cdn.jsdelivr.net",
        "https://fonts.googleapis.com",
        "https://apis.google.com",
        "https://maps.googleapis.com",
    ],
    "style-src": [
        "'self'",
        # 'unsafe-inline' is required for Tailwind CSS inline style attributes
        # (e.g. style="width: 75%" on progress bars). These are CSS-only and
        # non-executable — they cannot run JavaScript. This is the standard
        # approach for Tailwind-based projects.
        "'unsafe-inline'",
        "https://fonts.googleapis.com",
        "https://cdn.jsdelivr.net",
        "https://maps.googleapis.com",
    ],
    "font-src": [
        "'self'",
        "https://fonts.gstatic.com",
        "https://cdn.jsdelivr.net",
    ],
    "img-src": [
        "'self'",
        "data:",
        "https://www.gstatic.com",
        "https://apis.google.com",
        "https://maps.googleapis.com",
        "https://maps.gstatic.com",
    ],
    "connect-src": [
        "'self'",
        "https://www.gstatic.com",
        "https://identitytoolkit.googleapis.com",
        "https://securetoken.googleapis.com",
        "https://firestore.googleapis.com",
        "https://firebaseremoteconfig.googleapis.com",
        "https://generativelanguage.googleapis.com",
        "https://googleapis.com",
        "https://maps.googleapis.com",
    ],
    "frame-src": [
        "'self'",
        "https://apis.google.com",
        "https://maps.google.com",
    ],
    "object-src": ["'none'"],
    "base-uri": ["'self'"],
    "form-action": ["'self'"],
}


def init_security_headers(app: Flask) -> None:
    """Configure Flask-Talisman security headers on the given app.

    Sets Content-Security-Policy, HSTS, X-Content-Type-Options,
    frame-options, referrer-policy, Permissions-Policy, and
    session cookie attributes.
    """
    force_https = app.config.get("FORCE_HTTPS", True)
    Talisman(
        app,
        force_https=force_https,
        force_https_permanent=False,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,
        strict_transport_security_preload=True,
        content_security_policy=CSP_POLICY,
        content_security_policy_nonce_in=None,
        x_content_type_options="nosniff",
        frame_options="DENY",
        referrer_policy="strict-origin-when-cross-origin",
        session_cookie_secure=force_https,
        session_cookie_http_only=True,
        session_cookie_samesite="Lax",
        permissions_policy={
            "camera": "()",
            "microphone": "()",
            "geolocation": "()",
            "payment": "()",
        },
    )
    logger.info("Security headers initialized (force_https=%s)", force_https)
