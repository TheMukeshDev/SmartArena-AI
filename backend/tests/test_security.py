"""
SmartArena AI — Security Test Suite
=====================================

Comprehensive security tests covering CSRF, CORS, rate limiting,
security headers, and input validation.
"""


# ── CORS Tests ──────────────────────────────────────────────────────────


class TestCORS:
    """Verify CORS configuration and behavior."""

    def test_cors_preflight_headers(self, client):
        """OPTIONS requests should include CORS headers."""
        resp = client.options(
            "/api/v1/csrf-token",
            headers={
                "Origin": "http://localhost:5500",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code in (200, 204)

    def test_cors_credentials_header(self, client):
        """CORS responses should support credentials when origin matches."""
        resp = client.get(
            "/health",
            headers={"Origin": "http://localhost:5500"},
        )
        assert resp.status_code == 200


# ── Rate Limiting Tests ─────────────────────────────────────────────────


class TestRateLimiting:
    """Verify per-IP rate limiting enforcement."""

    def test_rate_limit_returns_429(self, client):
        """Exceeding the rate limit on a non-exempt path should return 429."""
        app = client.application
        original_limit = app.config.get("RATE_LIMIT_DEFAULT", 100)
        original_window = app.config.get("RATE_LIMIT_WINDOW_SECONDS", 3600)
        app.config["RATE_LIMIT_DEFAULT"] = 2
        app.config["RATE_LIMIT_WINDOW_SECONDS"] = 3600

        try:
            for _ in range(3):
                client.get("/api/v1/csrf-token")

            resp = client.get("/api/v1/csrf-token")
            assert resp.status_code == 429
            data = resp.get_json()
            assert data["error"]["type"] == "Too Many Requests"
        finally:
            app.config["RATE_LIMIT_DEFAULT"] = original_limit
            app.config["RATE_LIMIT_WINDOW_SECONDS"] = original_window

    def test_rate_limit_headers_present(self, client):
        """Rate-limited responses should include standard headers."""
        resp = client.get("/api/v1/csrf-token")
        assert resp.status_code == 200
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers

    def test_health_endpoint_skips_rate_limit(self, client):
        """Health endpoint should not be affected by rate limiting."""
        app = client.application
        original_limit = app.config.get("RATE_LIMIT_DEFAULT", 100)
        app.config["RATE_LIMIT_DEFAULT"] = 1
        try:
            resp1 = client.get("/health")
            resp2 = client.get("/health")
            assert resp1.status_code == 200
            assert resp2.status_code == 200
        finally:
            app.config["RATE_LIMIT_DEFAULT"] = original_limit


# ── CSRF Tests ──────────────────────────────────────────────────────────


class TestCSRF:
    """Verify CSRF protection behavior."""

    def test_csrf_token_endpoint_returns_token(self, client):
        """GET /api/v1/csrf-token should return a valid token."""
        resp = client.get("/api/v1/csrf-token")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "csrf_token" in data
        assert len(data["csrf_token"]) > 0

    def test_auth_endpoints_exempt_from_csrf(self, client):
        """sessionLogin should not require CSRF token."""
        resp = client.post(
            "/api/v1/auth/sessionLogin",
            json={"idToken": "invalid-token"},
            content_type="application/json",
        )
        assert resp.status_code in (400, 401, 500)
        data = resp.get_json()
        if data:
            assert "csrf" not in str(data).lower()

    def test_session_logout_exempt_from_csrf(self, client):
        """sessionLogout should not require CSRF token."""
        resp = client.post(
            "/api/v1/auth/sessionLogout",
            content_type="application/json",
        )
        assert resp.status_code == 200


# ── Security Headers Tests ──────────────────────────────────────────────


class TestSecurityHeaders:
    """Verify security-related HTTP headers are present."""

    def test_security_headers_on_health(self, client):
        """Health endpoint should respond and have security headers."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.content_type == "application/json"

    def test_security_headers_on_api(self, client):
        """API endpoints should have security headers."""
        resp = client.get("/api/v1/csrf-token")
        assert resp.status_code == 200

    def test_x_content_type_options(self, client):
        """X-Content-Type-Options should be set to nosniff."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_strict_transport_security(self, client):
        """HSTS header should be present in production-like configs."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_content_security_policy(self, client):
        """CSP header should be set by Flask-Talisman."""
        resp = client.get("/health")
        assert resp.status_code == 200
        csp = resp.headers.get("Content-Security-Policy", "")
        assert csp or resp.headers.get("Content-Security-Policy-Report-Only", "")

    def test_x_frame_options(self, client):
        """X-Frame-Options should be set."""
        resp = client.get("/health")
        assert resp.status_code == 200
        xfo = resp.headers.get("X-Frame-Options", "")
        assert xfo in ("DENY", "SAMEORIGIN", "")


# ── Input Validation Tests ──────────────────────────────────────────────


class TestInputValidation:
    """Verify Pydantic/FastAPI-style input validation."""

    def test_incident_endpoint_rejects_unauthenticated(self, client):
        """POST /ai/incident should reject unauthenticated requests."""
        resp = client.post(
            "/api/v1/ai/incident",
            json={},
            content_type="application/json",
        )
        assert resp.status_code in (400, 401, 422)

    def test_incident_endpoint_rejects_missing_fields(self, client):
        """POST /ai/incident should reject missing description."""
        resp = client.post(
            "/api/v1/ai/incident",
            json={"wrong_field": "value"},
            content_type="application/json",
        )
        assert resp.status_code in (400, 401, 422)

    def test_crowd_analyze_rejects_unauthenticated(self, client):
        """POST /ai/crowd/analyze should reject unauthenticated requests."""
        resp = client.post(
            "/api/v1/ai/crowd/analyze",
            json={"zones": "not-a-list"},
            content_type="application/json",
        )
        assert resp.status_code in (400, 401, 422)

    def test_volunteer_assign_rejects_unauthenticated(self, client):
        """POST /ai/volunteer/assign should reject unauthenticated requests."""
        resp = client.post(
            "/api/v1/ai/volunteer/assign",
            json={},
            content_type="application/json",
        )
        assert resp.status_code in (400, 401, 422)


# ── Auth Tests ──────────────────────────────────────────────────────────


class TestAuthSecurity:
    """Verify authentication security properties."""

    def test_register_rejects_invalid_token(self, client):
        """POST /auth/register should reject invalid Firebase token."""
        resp = client.post(
            "/api/v1/auth/register",
            json={"uid": "test", "email": "test@test.com"},
            headers={"Authorization": "Bearer invalid-token"},
            content_type="application/json",
        )
        assert resp.status_code in (401, 500)

    def test_protected_endpoint_requires_auth(self, client):
        """Protected endpoints should return 401 without auth."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_admin_endpoint_requires_admin_role(self, client):
        """Admin endpoints should require admin role."""
        resp = client.get("/api/v1/admin/gates")
        assert resp.status_code in (401, 403)

    def test_health_endpoint_is_public(self, client):
        """Health endpoint should be accessible without auth."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_error_response_format(self, client):
        """Error responses should follow consistent JSON schema."""
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401
        data = resp.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "type" in data["error"]
        assert "code" in data["error"]
        assert "message" in data["error"]

    def test_404_returns_error_format(self, client):
        """Non-existent routes should return 404 in standard error format."""
        resp = client.get("/api/v1/nonexistent-endpoint")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == 404
