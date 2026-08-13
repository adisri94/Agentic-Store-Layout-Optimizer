"""Weather provider seam (Sprint 2A, US-2A.1, D-037).

Weather is a contextual signal for affinity mining. It is served through a
`WeatherProvider` interface with two implementations:

* :class:`SyntheticWeatherProvider` — the default. Deterministic weather bucket per
  store × day, fully local and demo-controllable.
* :class:`LiveWeatherProvider` — opt-in. Calls the free, key-less Open-Meteo API and
  **falls back to the synthetic provider on any failure** (offline, proxy block,
  timeout, parse error), so the demo never breaks.

The live provider trusts the OS certificate store (via ``truststore``) so corporate
TLS interception (e.g. Zscaler) works without disabling verification.
"""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Protocol, runtime_checkable

import structlog

from platform_services.config import settings

logger = structlog.get_logger(__name__)

# The known weather buckets used as a categorical context signal.
WEATHER_BUCKETS: tuple[str, ...] = ("sunny", "rainy", "cold", "hot", "mild")

_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_HOT_TEMP_C = 30.0
_COLD_TEMP_C = 5.0


@runtime_checkable
class WeatherProvider(Protocol):
    """Returns a weather bucket for a given store and day."""

    def get_weather(self, store_id: str, day: date) -> str:
        """Return a bucket from :data:`WEATHER_BUCKETS` for ``store_id`` on ``day``."""
        ...


class SyntheticWeatherProvider:
    """Deterministic, offline weather derived from a stable hash of (store, day).

    Uses a content hash (not Python's salted ``hash()``) so results are identical
    across processes and runs.
    """

    def get_weather(self, store_id: str, day: date) -> str:
        """Return a deterministic bucket for the store/day."""
        key = f"{store_id}|{day.isoformat()}".encode()
        digest = int(hashlib.md5(key).hexdigest(), 16)
        return WEATHER_BUCKETS[digest % len(WEATHER_BUCKETS)]


class LiveWeatherProvider:
    """Open-Meteo-backed provider with graceful fallback to synthetic.

    Args:
        latitude: Latitude to query.
        longitude: Longitude to query.
        fallback: Provider used when the live call fails (defaults to synthetic).
        timeout: HTTP timeout in seconds.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        fallback: WeatherProvider | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._latitude = latitude
        self._longitude = longitude
        self._fallback: WeatherProvider = fallback or SyntheticWeatherProvider()
        self._timeout = timeout
        # Trust the OS certificate store so corporate-CA TLS interception works.
        try:
            import truststore

            truststore.inject_into_ssl()
        except Exception as exc:  # noqa: BLE001 - trust setup is best-effort
            logger.warning("weather.truststore_unavailable", error=str(exc))

    def get_weather(self, store_id: str, day: date) -> str:
        """Return the live bucket, falling back to synthetic on any failure."""
        try:
            code, temperature_c = self._fetch_current()
            return self._to_bucket(code, temperature_c)
        except Exception as exc:  # noqa: BLE001 - any failure must fall back, never raise
            logger.warning("weather.live_fallback", store_id=store_id, error=str(exc))
            return self._fallback.get_weather(store_id, day)

    def _fetch_current(self) -> tuple[int, float]:
        """Fetch the current WMO weather code and temperature from Open-Meteo."""
        import requests

        response = requests.get(
            _OPEN_METEO_URL,
            params={
                "latitude": self._latitude,
                "longitude": self._longitude,
                "current": "weather_code,temperature_2m",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        current = response.json()["current"]
        return int(current["weather_code"]), float(current["temperature_2m"])

    @staticmethod
    def _to_bucket(weather_code: int, temperature_c: float) -> str:
        """Map a WMO weather code + temperature to a bucket."""
        # Precipitation-type codes take priority, then temperature, then sky state.
        if weather_code in {71, 73, 75, 77, 85, 86}:  # snow
            return "cold"
        if weather_code >= 51:  # drizzle / rain / showers / thunderstorm
            return "rainy"
        if temperature_c >= _HOT_TEMP_C:
            return "hot"
        if temperature_c <= _COLD_TEMP_C:
            return "cold"
        if weather_code == 0:  # clear sky
            return "sunny"
        return "mild"


def get_weather_provider() -> WeatherProvider:
    """Return the configured provider: live when opted in, else synthetic (D-037)."""
    if settings.enable_live_weather:
        return LiveWeatherProvider(settings.weather_latitude, settings.weather_longitude)
    return SyntheticWeatherProvider()
