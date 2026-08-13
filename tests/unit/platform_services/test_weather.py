"""Unit tests for the weather provider seam (US-2A.1)."""

from __future__ import annotations

from datetime import date

from platform_services.weather import (
    WEATHER_BUCKETS,
    LiveWeatherProvider,
    SyntheticWeatherProvider,
)


def test_synthetic_is_deterministic():
    """TC-2A.1.1 — same (store, day) yields the same bucket across instances."""
    a = SyntheticWeatherProvider()
    b = SyntheticWeatherProvider()
    day = date(2026, 6, 1)
    assert a.get_weather("STR-0001", day) == b.get_weather("STR-0001", day)


def test_synthetic_returns_known_buckets():
    """TC-2A.1.2 — the provider only returns buckets from the known set."""
    provider = SyntheticWeatherProvider()
    seen = {
        provider.get_weather(f"STR-{i:04d}", date(2026, 6, 1 + (i % 27))) for i in range(1, 40)
    }
    assert seen  # non-empty
    assert seen <= set(WEATHER_BUCKETS)


def test_live_falls_back_on_failure(monkeypatch):
    """TC-2A.1.3 — a failing live call falls back to synthetic (no exception)."""
    provider = LiveWeatherProvider(latitude=0.0, longitude=0.0)

    def _boom() -> tuple[int, float]:
        raise RuntimeError("network down")

    monkeypatch.setattr(provider, "_fetch_current", _boom)
    bucket = provider.get_weather("STR-0001", date(2026, 6, 1))
    assert bucket in WEATHER_BUCKETS
    # Matches what the synthetic fallback would produce for the same key.
    assert bucket == SyntheticWeatherProvider().get_weather("STR-0001", date(2026, 6, 1))


def test_live_code_mapping():
    """The WMO code + temperature mapping picks sensible buckets."""
    to_bucket = LiveWeatherProvider._to_bucket
    assert to_bucket(0, 22.0) == "sunny"      # clear sky
    assert to_bucket(61, 18.0) == "rainy"     # rain
    assert to_bucket(75, 1.0) == "cold"       # snow
    assert to_bucket(1, 34.0) == "hot"        # warm, mostly clear
    assert to_bucket(3, 20.0) == "mild"       # overcast, temperate
