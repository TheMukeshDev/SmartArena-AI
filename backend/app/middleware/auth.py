"""
SmartArena AI — Authentication & Authorization Middleware
==========================================================

Provides Flask decorators for Firebase Authentication (ID tokens and session
cookies) and role-based access control (RBAC) via Firebase Custom Claims.
"""

import asyncio
import functools
import logging
from typing import Any, Callable

from firebase_admin import auth
from flask import request, g

from app.utils.response import error_response

logger = logging.getLogger(__name__)


def _authenticate_request() -> tuple[dict | None, Any]:
    session_cookie = request.cookies.get("session")
    auth_header = request.headers.get("Authorization")
    bearer_token = None
    if auth_header and auth_header.startswith("Bearer "):
        bearer_token = auth_header.split("Bearer ")[1]

    try:
        if bearer_token:
            return auth.verify_id_token(bearer_token, check_revoked=True), None
        elif session_cookie:
            return auth.verify_session_cookie(session_cookie, check_revoked=True), None
        else:
            return None, error_response(
                message="Authentication required. No token or session cookie provided.",
                error_type="Unauthorized",
                status_code=401,
            )
    except auth.RevokedIdTokenError:
        logger.warning("Revoked token used")
        return None, error_response(
            message="Session has been revoked. Please log in again.",
            error_type="Unauthorized",
            status_code=401,
        )
    except auth.InvalidSessionCookieError:
        logger.warning("Invalid session cookie")
        return None, error_response(
            message="Invalid session. Please log in again.",
            error_type="Unauthorized",
            status_code=401,
        )
    except Exception as e:
        logger.error("Auth error: %s", str(e))
        return None, error_response(
            message="Authentication failed",
            error_type="Unauthorized",
            status_code=401,
        )


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to require a valid Firebase session cookie or ID token.

    Sets g.user with the decoded token payload.
    """
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            decoded_claims, err = _authenticate_request()
            if err:
                return err
            g.user = decoded_claims
            return await func(*args, **kwargs)

        return async_wrapper
    else:

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            decoded_claims, err = _authenticate_request()
            if err:
                return err
            g.user = decoded_claims
            return func(*args, **kwargs)

        return wrapper


def require_role(allowed_roles: list[str]) -> Callable[..., Any]:
    """Decorator to enforce RBAC based on Firebase Custom Claims.

    Must be used AFTER @require_auth.

    Args:
        allowed_roles: List of role strings (e.g., ['admin', 'volunteer'])
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def _check_role() -> Any:
            user = getattr(g, "user", None)
            if not user:
                return error_response(
                    message="Authentication required for role check.",
                    error_type="Unauthorized",
                    status_code=401,
                )

            user_role = user.get("role")
            if not user_role or user_role not in allowed_roles:
                logger.warning(
                    "Access denied for user %s. Role '%s' not in %s",
                    user.get("uid"),
                    user_role,
                    allowed_roles,
                )
                return error_response(
                    message="You do not have permission to access this resource.",
                    error_type="Forbidden",
                    status_code=403,
                )
            return None

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                err = _check_role()
                if err:
                    return err
                return await func(*args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                err = _check_role()
                if err:
                    return err
                return func(*args, **kwargs)

            return wrapper

    return decorator
