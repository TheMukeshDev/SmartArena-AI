import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_fetch_weather_returns_data():
    from app.services.weather import fetch_weather, WeatherData

    mock_data = {
        "current": {
            "temperature_2m": 28.5,
            "precipitation": 0.0,
            "weather_code": 0,
            "wind_speed_10m": 12.0,
        }
    }
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_data).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        w = await fetch_weather()
        assert w is not None
        assert isinstance(w, WeatherData)
        assert w.temperature_c == 28.5
        assert w.precipitation_mm == 0.0
        assert w.weather_code == 0
        assert "28.5" in w.summary


@pytest.mark.asyncio
async def test_fetch_weather_returns_none_on_error():
    from app.services.weather import fetch_weather

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("Network error")
        w = await fetch_weather()
        assert w is None


@pytest.mark.asyncio
async def test_fetch_weather_injects_into_crowd_prompt():
    from app.services.weather import fetch_weather, WeatherData
    from app.ai.gemini import analyze_crowd_data

    mock_data = {
        "current": {
            "temperature_2m": 32.0,
            "precipitation": 12.0,
            "weather_code": 65,
            "wind_speed_10m": 25.0,
        }
    }
    with (
        patch("urllib.request.urlopen") as mock_urlopen,
        patch("app.ai.gemini._init_gemini", return_value=True),
        patch("app.ai.gemini.genai.GenerativeModel") as mock_model,
    ):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_data).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        weather = await fetch_weather()
        assert weather is not None

        mock_instance = mock_model.return_value
        mock_response = AsyncMock()
        mock_response.text = json.dumps(
            {
                "global_status": "Optimal",
                "insights": ["Consider covered routes due to rain"],
                "routing_advice": "Use covered walkways",
                "predicted_status_15min": {},
                "recommended_action": "Staff covered areas",
            }
        )
        mock_instance.generate_content_async = AsyncMock(return_value=mock_response)

        res = await analyze_crowd_data(
            [{"zone": "North Stand", "occupancy": 50}],
            history=[{"zones": [], "timestamp": ""}],
            weather=weather.summary,
        )

        sent_prompt = mock_instance.generate_content_async.call_args[0][0]
        assert "32.0" in sent_prompt or "25.0" in sent_prompt
        assert res["global_status"] == "Optimal"


def test_operational_note_rain():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(20.0, 10.0, 5.0, "Heavy rain")
    assert "covered" in note.lower()
    assert "rain" in note.lower()


def test_operational_note_high_heat():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(38.0, 0.0, 5.0, "Clear sky")
    assert "heat" in note.lower() or "cooling" in note.lower()


def test_operational_note_favorable():
    from app.services.weather import _generate_operational_note

    note = _generate_operational_note(22.0, 0.0, 5.0, "Clear sky")
    assert "favorable" in note.lower()
