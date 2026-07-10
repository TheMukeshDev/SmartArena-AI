import json
import logging
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

STADIUM_LAT = 25.9542
STADIUM_LON = -80.2391


@dataclass
class WeatherData:
    temperature_c: float
    precipitation_mm: float
    weather_code: int
    wind_speed_kmh: float
    summary: str = ""
    operational_note: str = ""


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


async def fetch_weather(
    lat: float = STADIUM_LAT, lon: float = STADIUM_LON
) -> Optional[WeatherData]:
    try:
        url = (
            f"{OPEN_METEO_URL}?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,precipitation,weather_code,wind_speed_10m"
            f"&timezone=auto"
        )
        if not url.startswith("https://"):
            raise ValueError(f"Refusing non-HTTPS request: {url!r}")
        req = urllib.request.Request(url, headers={"User-Agent": "SmartArenaAI/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            body = json.loads(resp.read().decode())

        current = body.get("current", {})
        code = current.get("weather_code", 0)
        temp = current.get("temperature_2m", 20.0)
        precip = current.get("precipitation", 0.0)
        wind = current.get("wind_speed_10m", 0.0)
        condition = WEATHER_CODES.get(code, "Unknown")

        w = WeatherData(
            temperature_c=temp,
            precipitation_mm=precip,
            weather_code=code,
            wind_speed_kmh=wind,
            summary=f"{temp}°C, {condition}, {precip}mm precipitation",
        )
        w.operational_note = _generate_operational_note(temp, precip, wind, condition)
        return w
    except Exception as e:
        logger.warning("Weather fetch failed: %s", str(e))
        return None


def _generate_operational_note(
    temp: float, precip: float, wind: float, condition: str
) -> str:
    notes = []
    if precip > 5:
        notes.append(
            "Rain may cause fans to cluster under covered areas. "
            "Ensure covered walkways and concourses are staffed."
        )
    elif precip > 1:
        notes.append("Light rain expected. Advise fans to use covered routes.")

    if temp > 35:
        notes.append(
            "High heat — expect increased cooling energy load. "
            "Ensure water stations are stocked and medical teams are aware."
        )
    elif temp < 10:
        notes.append(
            "Cold weather — advise fans to dress warmly. Check heating systems."
        )

    if wind > 40:
        notes.append(
            "Strong winds detected. Secure loose signage and "
            "advise against outdoor gatherings in exposed areas."
        )

    if not notes:
        notes.append(
            "Weather conditions are favorable. No operational adjustments needed."
        )

    return " ".join(notes)
