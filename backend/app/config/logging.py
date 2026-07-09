"""
SmartArena AI — Logging Configuration
======================================

Configures structured JSON logging for production and readable
console logging for development.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any

from flask import Flask, has_request_context, request


class JSONFormatter(logging.Formatter):
    """Produces structured JSON log lines for production environments.

    Each log entry includes timestamp, level, message, module,
    and optional HTTP request context when available.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted log string.
        """
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach HTTP request context if available
        if has_request_context():
            log_entry["request"] = {
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
            }

        # Attach exception info if present
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "",
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_entry, default=str)


class ConsoleFormatter(logging.Formatter):
    """Human-readable colored console formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with color codes.

        Args:
            record: The log record to format.

        Returns:
            Color-formatted log string.
        """
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%H:%M:%S")
        return (
            f"{color}[{timestamp}] {record.levelname:8s}{self.RESET} "
            f"{record.name}: {record.getMessage()}"
        )


def setup_logging(app: Flask) -> None:
    """Configure application-wide logging.

    Uses JSON formatter in production and colored console
    formatter in development.

    Args:
        app: Flask application instance.
    """
    log_level_name: str = app.config.get("LOG_LEVEL", "INFO")
    log_format: str = app.config.get("LOG_FORMAT", "json")
    log_level: int = getattr(logging, log_level_name.upper(), logging.INFO)

    # Remove default Flask handlers
    app.logger.handlers.clear()
    logging.root.handlers.clear()

    # Create stream handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())

    # Configure root logger
    logging.root.setLevel(log_level)
    logging.root.addHandler(handler)

    # Configure Flask logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(handler)
    app.logger.propagate = False

    app.logger.debug("Logging configured: level=%s, format=%s", log_level_name, log_format)
