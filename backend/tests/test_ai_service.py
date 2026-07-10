import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_process_incident():
    with (
        patch("app.services.ai_service.classify_incident") as mock_classify,
        patch("app.services.ai_service.get_firestore_client") as mock_fs,
    ):
        mock_classify.return_value = {"category": "Medical"}
        mock_db = MagicMock()
        mock_fs.return_value = mock_db

        res = await AIService.process_incident("Someone fainted", "uid123")
        assert res["category"] == "Medical"
        mock_db.collection.assert_called_with("incidents")


@pytest.mark.asyncio
async def test_process_crowd_analysis():
    with (
        patch("app.services.ai_service.analyze_crowd_data") as mock_analyze,
        patch("app.services.ai_service.get_firestore_client") as mock_fs,
    ):
        mock_analyze.return_value = {"global_status": "Normal"}
        mock_db = MagicMock()
        mock_fs.return_value = mock_db

        res = await AIService.process_crowd_analysis([{"zone": "A"}], "uid123")
        assert res["global_status"] == "Normal"
        mock_db.collection.assert_called_with("crowd_data")


@pytest.mark.asyncio
async def test_process_volunteer_assignment():
    with (
        patch("app.services.ai_service.assign_volunteer_task") as mock_assign,
        patch("app.services.ai_service.get_firestore_client") as mock_fs,
    ):
        mock_assign.return_value = {"task": "Clean"}
        mock_db = MagicMock()
        mock_fs.return_value = mock_db

        res = await AIService.process_volunteer_assignment("Gate A", "uid123")
        assert res["task"] == "Clean"
        mock_db.collection.assert_called_with("volunteers")


@pytest.mark.asyncio
async def test_process_sustainability():
    with (
        patch("app.services.ai_service.optimize_sustainability") as mock_opt,
        patch("app.services.ai_service.get_firestore_client") as mock_fs,
    ):
        mock_opt.return_value = {"status": "Good"}
        mock_db = MagicMock()
        mock_fs.return_value = mock_db

        res = await AIService.process_sustainability({"energy": 100}, "uid123")
        assert res["status"] == "Good"
        mock_db.collection.assert_called_with("sustainability")


@pytest.mark.asyncio
async def test_process_transport_suggestion():
    with patch("app.services.ai_service.suggest_transport") as mock_suggest:
        mock_suggest.return_value = {"recommended_mode": "Transit"}

        res = await AIService.process_transport_suggestion("Gate A", "3:00 PM")
        assert res["recommended_mode"] == "Transit"
