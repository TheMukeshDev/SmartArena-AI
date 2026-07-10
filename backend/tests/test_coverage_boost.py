"""
Coverage-boost tests — hit every uncovered branch across the codebase.
"""

import json
import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock

import pytest


# ── weather.py: light rain, cold, strong wind notes ───────────────────────


def test_operational_note_light_rain():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(20.0, 3.0, 5.0, "Moderate drizzle")
    assert "light rain" in note.lower() or "covered routes" in note.lower()


def test_operational_note_cold():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(5.0, 0.0, 5.0, "Clear sky")
    assert "cold" in note.lower() or "dress warmly" in note.lower()


def test_operational_note_strong_wind():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(20.0, 0.0, 50.0, "Clear sky")
    assert "wind" in note.lower() or "signage" in note.lower()


# ── navigation.py: BFS exhaustive queue via inaccessible edges ─────────────


def test_find_accessible_path_inaccessible_edges():
    """BFS exhausts queue when all paths need inaccessible edges."""
    from app.services.navigation import find_accessible_path

    with patch("app.services.navigation.ACCESSIBLE_EDGES", {}):
        path = find_accessible_path("North Stand", "West Stand")
        assert path == []


# ── gemini.py: exception branches in volunteer + sustainability ────────────


@pytest.mark.asyncio
async def test_assign_volunteer_task_exception():
    from app.ai.gemini import assign_volunteer_task

    with (
        patch("app.ai.gemini._init_gemini", return_value=True),
        patch("app.ai.gemini.genai.GenerativeModel") as mock_model,
    ):
        mock_model.return_value.generate_content_async = AsyncMock(
            side_effect=Exception("Gemini API error")
        )
        result = await assign_volunteer_task("Gate A")
        assert result["task"] == "Monitor designated area"


@pytest.mark.asyncio
async def test_optimize_sustainability_exception():
    from app.ai.gemini import optimize_sustainability

    with (
        patch("app.ai.gemini._init_gemini", return_value=True),
        patch("app.ai.gemini.genai.GenerativeModel") as mock_model,
    ):
        mock_model.return_value.generate_content_async = AsyncMock(
            side_effect=Exception("Gemini API error")
        )
        result = await optimize_sustainability({"energy": 100})
        assert result["status"] == "Optimization Failed"


# ── ai_service.py: cache key, crowd history overflow, process_chat ─────────


def test_cache_key_deterministic():
    from app.services.ai_service import _cache_key

    key1 = _cache_key("hello", {"a": 1}, "en")
    key2 = _cache_key("hello", {"a": 1}, "en")
    assert key1 == key2

    key3 = _cache_key("hello", {"a": 2}, "en")
    assert key1 != key3

    key4 = _cache_key("hello", {"a": 1}, "es")
    assert key1 != key4


@pytest.mark.asyncio
async def test_crowd_history_overflow():
    from app.services import ai_service
    from app.services.ai_service import AIService, CROWD_HISTORY_MAX

    original = ai_service._crowd_history.copy()
    try:
        ai_service._crowd_history.clear()

        with (
            patch("app.services.ai_service.analyze_crowd_data") as mock_analyze,
            patch("app.services.ai_service.get_firestore_client") as mock_fs,
            patch("app.services.ai_service.fetch_weather", new_callable=AsyncMock),
        ):
            mock_analyze.return_value = {"global_status": "Normal"}
            mock_fs.return_value = None

            for i in range(CROWD_HISTORY_MAX + 3):
                await AIService.process_crowd_analysis([{"zone": f"Zone {i}"}], "uid")

            assert len(ai_service._crowd_history) <= CROWD_HISTORY_MAX
    finally:
        ai_service._crowd_history.clear()
        ai_service._crowd_history.extend(original)


@pytest.mark.asyncio
async def test_process_chat_cache_hit():
    from app.services.ai_service import AIService

    with (
        patch("app.services.ai_service.ask_assistant", new_callable=AsyncMock),
        patch("app.services.ai_service._cache") as mock_cache,
    ):
        mock_cache.get.return_value = "Cached response"

        result = await AIService.process_chat("hello", {}, language="en")
        assert result == "Cached response"


@pytest.mark.asyncio
async def test_process_chat_unknown_language():
    from app.services.ai_service import AIService

    with (
        patch(
            "app.services.ai_service.ask_assistant", new_callable=AsyncMock
        ) as mock_ask,
        patch("app.services.ai_service._cache") as mock_cache,
    ):
        mock_ask.return_value = "Response"
        mock_cache.get.return_value = None

        await AIService.process_chat("hi", {}, language="xx")
        call_args = mock_ask.call_args
        assert call_args[1]["language"] == "English"


# ── ai_ops.py: weather 503, accessible path not found + success ───────────


def test_weather_returns_503_when_none(app, client):
    with (
        patch("app.routes.ai_ops.fetch_weather", new_callable=AsyncMock) as mock_fetch,
        patch(
            "app.middleware.auth.auth.verify_session_cookie",
            return_value={"uid": "123"},
        ),
    ):
        mock_fetch.return_value = None
        client.set_cookie("session", "fake")
        res = client.get("/api/v1/ai/weather")
        assert res.status_code == 503


def test_accessible_path_not_found(app, client):
    with patch(
        "app.middleware.auth.auth.verify_session_cookie",
        return_value={"uid": "123"},
    ):
        client.set_cookie("session", "fake")
        res = client.get(
            "/api/v1/ai/navigation/path/accessible",
            query_string={"start": "North Stand", "end": "Nonexistent"},
        )
        assert res.status_code == 404


def test_accessible_path_missing_params(app, client):
    with patch(
        "app.middleware.auth.auth.verify_session_cookie",
        return_value={"uid": "123"},
    ):
        client.set_cookie("session", "fake")
        res = client.get("/api/v1/ai/navigation/path/accessible")
        assert res.status_code == 400


def test_accessible_path_success(app, client):
    with patch(
        "app.middleware.auth.auth.verify_session_cookie",
        return_value={"uid": "123"},
    ):
        client.set_cookie("session", "fake")
        res = client.get(
            "/api/v1/ai/navigation/path/accessible",
            query_string={
                "start": "North Stand",
                "end": "VIP Lounge",
            },
        )
        assert res.status_code == 200
        data = json.loads(res.data)
        assert data["data"]["path"][0] == "North Stand"
        assert data["data"]["path"][-1] == "VIP Lounge"


# ── cache.py: delete and clear ────────────────────────────────────────────


def _close_cache(cache):
    conn = getattr(cache._local, "conn", None)
    if conn is not None:
        conn.close()
        cache._local.conn = None


def test_cache_delete():
    from app.services.cache import SQLiteCache

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_cache.db")
        cache = SQLiteCache(db_path=db_path, ttl_seconds=60)
        cache.set("k", "v")
        assert cache.get("k") == "v"
        cache.delete("k")
        assert cache.get("k") is None
        _close_cache(cache)


def test_cache_clear():
    from app.services.cache import SQLiteCache

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_cache.db")
        cache = SQLiteCache(db_path=db_path, ttl_seconds=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        _close_cache(cache)


def test_cache_cleanup_error():
    from app.services.cache import SQLiteCache

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_cache.db")
        cache = SQLiteCache(db_path=db_path, ttl_seconds=60)
        with patch.object(cache, "_get_conn") as mock_conn:
            mock_conn.return_value.execute.side_effect = Exception("db error")
            cache._cleanup_expired()
        _close_cache(cache)


def test_cache_get_non_json_value():
    from app.services.cache import SQLiteCache

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_cache.db")
        cache = SQLiteCache(db_path=db_path, ttl_seconds=60)
        conn = cache._get_conn()
        conn.execute(
            "INSERT INTO response_cache (cache_key, value, expires_at) "
            "VALUES (?, ?, ?)",
            ("bad", "not-json-at-all", 9999999999),
        )
        conn.commit()
        result = cache.get("bad")
        assert result == "not-json-at-all"
        _close_cache(cache)


# ── response.py: details branch ───────────────────────────────────────────


def test_error_response_with_details(app):
    from app.utils.response import error_response

    with app.app_context():
        resp, code = error_response(
            message="Bad",
            error_type="Validation",
            status_code=422,
            details={"field": "name"},
        )
        assert code == 422
        body = json.loads(resp.get_data(as_text=True))
        assert body["error"]["details"]["field"] == "name"
