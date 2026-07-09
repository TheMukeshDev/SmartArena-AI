"""
SmartArena AI — Global Error Handlers
=======================================

Registers centralized error handlers for consistent error
responses across the entire application.
"""

import logging
import traceback
from typing import Any

from flask import Flask, jsonify, request
from flask.wrappers import Response
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """Register global error handlers on the Flask application.

    Args:
        app: Flask application instance.
    """

    @app.errorhandler(400)
    def bad_request(error: HTTPException) -> tuple[Response, int]:
        """Handle 400 Bad Request errors."""
        return _error_response(
            status_code=400,
            error_type="Bad Request",
            message=str(error.description) if error.description else "Invalid request data",
        )

    @app.errorhandler(401)
    def unauthorized(error: HTTPException) -> tuple[Response, int]:
        """Handle 401 Unauthorized errors."""
        return _error_response(
            status_code=401,
            error_type="Unauthorized",
            message="Authentication required",
        )

    @app.errorhandler(403)
    def forbidden(error: HTTPException) -> tuple[Response, int]:
        """Handle 403 Forbidden errors."""
        return _error_response(
            status_code=403,
            error_type="Forbidden",
            message="You do not have permission to access this resource",
        )

    @app.errorhandler(404)
    def not_found(error: HTTPException) -> tuple[Response, int]:
        """Handle 404 Not Found errors."""
        return _error_response(
            status_code=404,
            error_type="Not Found",
            message=f"Resource not found: {request.path}",
        )

    @app.errorhandler(405)
    def method_not_allowed(error: HTTPException) -> tuple[Response, int]:
        """Handle 405 Method Not Allowed errors."""
        return _error_response(
            status_code=405,
            error_type="Method Not Allowed",
            message=f"Method {request.method} is not allowed for {request.path}",
        )

    @app.errorhandler(429)
    def rate_limited(error: HTTPException) -> tuple[Response, int]:
        """Handle 429 Too Many Requests errors."""
        return _error_response(
            status_code=429,
            error_type="Rate Limited",
            message="Too many requests. Please try again later.",
        )

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[Response, int]:
        """Handle 500 Internal Server errors."""
        logger.error(
            "Internal server error: %s\n%s",
            str(error),
            traceback.format_exc(),
        )
        return _error_response(
            status_code=500,
            error_type="Internal Server Error",
            message="An unexpected error occurred. Please try again later.",
        )

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception) -> tuple[Response, int]:
        """Catch-all handler for unhandled exceptions."""
        if isinstance(error, HTTPException):
            return _error_response(
                status_code=error.code or 500,
                error_type=error.name,
                message=str(error.description),
            )

        logger.critical(
            "Unhandled exception: %s\n%s",
            str(error),
            traceback.format_exc(),
        )
        return _error_response(
            status_code=500,
            error_type="Internal Server Error",
            message="An unexpected error occurred",
        )


def _error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Any = None,
) -> tuple[Response, int]:
    """Build a standardized error response.

    Args:
        status_code: HTTP status code.
        error_type: Short error classification.
        message: Human-readable error message.
        details: Optional additional error details.

    Returns:
        Tuple of (JSON response, status code).
    """
    body: dict[str, Any] = {
        "success": False,
        "error": {
            "type": error_type,
            "code": status_code,
            "message": message,
        },
    }
    if details is not None:
        body["error"]["details"] = details

    return jsonify(body), status_code
