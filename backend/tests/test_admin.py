"""
SmartArena AI — Admin Route Tests
==================================

Tests for admin panel endpoints: gates, announcements,
security logs, and user management.
"""

from unittest.mock import patch, MagicMock


def test_list_gates(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/gates")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            assert len(data["data"]["gates"]) > 0


def test_list_gates_with_firestore(app, client):
    mock_doc = MagicMock()
    mock_doc.id = "Gate A"
    mock_doc.to_dict.return_value = {"status": "closed", "capacity": 3000}
    mock_db = MagicMock()
    mock_db.collection.return_value.stream.return_value = [mock_doc]
    with patch("app.routes.admin._get_db", return_value=mock_db):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/gates")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True


def test_update_gate(app, client):
    mock_db = MagicMock()
    mock_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_ref
    with patch("app.routes.admin._get_db", return_value=mock_db):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.post(
                "/api/v1/admin/gates",
                json={"name": "Gate A", "status": "closed", "capacity": 2000},
            )
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            mock_ref.set.assert_called_once()


def test_update_gate_validation_error(app, client):
    decoded = {"uid": "admin-123", "role": "admin"}
    with patch(
        "app.middleware.auth._authenticate_request", return_value=(decoded, None)
    ):
        resp = client.post("/api/v1/admin/gates", json={})
        assert resp.status_code == 400


def test_update_gate_db_unavailable(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.post(
                "/api/v1/admin/gates",
                json={"name": "Gate A", "status": "closed"},
            )
            assert resp.status_code == 503


def test_list_announcements(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/announcements")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            assert isinstance(data["data"]["announcements"], list)


def test_create_announcement(app, client):
    mock_db = MagicMock()
    mock_ref = MagicMock()
    mock_ref.id = "ann-001"
    mock_db.collection.return_value.document.return_value = mock_ref
    with patch("app.routes.admin._get_db", return_value=mock_db):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.post(
                "/api/v1/admin/announcements",
                json={"title": "Test", "message": "Hello", "priority": "urgent"},
            )
            data = resp.get_json()
            assert resp.status_code == 201
            assert data["success"] is True


def test_create_announcement_validation_error(app, client):
    decoded = {"uid": "admin-123", "role": "admin"}
    with patch(
        "app.middleware.auth._authenticate_request", return_value=(decoded, None)
    ):
        resp = client.post("/api/v1/admin/announcements", json={"title": ""})
        assert resp.status_code == 400


def test_delete_announcement(app, client):
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_ref = MagicMock()
    mock_ref.get.return_value = mock_doc
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_ref
    with patch("app.routes.admin._get_db", return_value=mock_db):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.delete("/api/v1/admin/announcements/ann-001")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            mock_ref.delete.assert_called_once()


def test_delete_announcement_not_found(app, client):
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_ref = MagicMock()
    mock_ref.get.return_value = mock_doc
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_ref
    with patch("app.routes.admin._get_db", return_value=mock_db):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.delete("/api/v1/admin/announcements/missing")
            assert resp.status_code == 404


def test_list_security_logs(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/security/logs")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            assert isinstance(data["data"]["logs"], list)


def test_list_users(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/users")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
            assert isinstance(data["data"]["users"], list)


def test_admin_role_required(app, client):
    decoded = {"uid": "vol-123", "role": "volunteer"}
    with patch(
        "app.middleware.auth._authenticate_request", return_value=(decoded, None)
    ):
        resp = client.get("/api/v1/admin/gates")
        assert resp.status_code == 403


def test_unauthenticated_admin_access(app, client):
    resp = client.get("/api/v1/admin/gates")
    assert resp.status_code == 401


def test_security_logs_with_limit(app, client):
    with patch("app.routes.admin._get_db", return_value=None):
        decoded = {"uid": "admin-123", "role": "admin"}
        with patch(
            "app.middleware.auth._authenticate_request", return_value=(decoded, None)
        ):
            resp = client.get("/api/v1/admin/security/logs?limit=10")
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["success"] is True
