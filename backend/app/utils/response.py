"""
SmartArena AI — Standardized API Response Helpers
===================================================

Provides consistent JSON response formatting across all API endpoints.
"""

from typing import Any, Optional

from flask import jsonify
from flask.wrappers import Response


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
) -> tuple[Response, int]:
    """Build a standardized success response.

    Args:
        data: Response payload data.
        message: Human-readable success message.
        status_code: HTTP status code (default 200).

    Returns:
        Tuple of (JSON response, status code).
    """
    body: dict[str, Any] = {
        "success": True,
        "message": message,
    }
    if data is not None:
        body["data"] = data

    return jsonify(body), status_code


def error_response(
    message: str = "An error occurred",
    error_type: str = "Error",
    status_code: int = 400,
    details: Optional[Any] = None,
) -> tuple[Response, int]:
    """Build a standardized error response.

    Args:
        message: Human-readable error message.
        error_type: Short error classification.
        status_code: HTTP status code (default 400).
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
