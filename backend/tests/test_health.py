"""
SmartArena AI — Health Endpoint Tests
=======================================

Tests for /health and /health/ready endpoints.
"""


def test_health_check_returns_200(client):
    """Health check should return 200 with status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["service"] == "SmartArena AI"


def test_health_check_has_version(client):
    """Health check should include version information."""
    response = client.get("/health")
    data = response.get_json()
    assert "version" in data["data"]
    assert data["data"]["version"] == "1.0.0"


def test_readiness_check_returns_status(client):
    """Readiness check should return check results."""
    response = client.get("/health/ready")
    data = response.get_json()
    assert "checks" in data["data"]
    assert "flask" in data["data"]["checks"]
    assert data["data"]["checks"]["flask"] is True


def test_api_root_returns_endpoints(client):
    """API root should list available endpoints."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "endpoints" in data["data"]


def test_404_returns_json(client):
    """Non-existent routes should return JSON error."""
    response = client.get("/nonexistent-route")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == 404
