"""Basket context enrichment (Sprint 2A, US-2A.2).

Derives the contextual features used for context-aware affinity mining:
``hour_band`` and ``day_type`` from the transaction timestamp, ``promo_flag`` from
the promotion id, and ``weather_bucket`` from a :class:`~platform_services.weather.WeatherProvider`.

Functions are pure and degrade gracefully: unparseable timestamps yield ``"unknown"``
rather than raising.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from platform_services.weather import SyntheticWeatherProvider, WeatherProvider

UNKNOWN = "unknown"


def hour_band(moment: datetime) -> str:
    """Map a timestamp to a coarse time-of-day band.

    Args:
        moment: The transaction datetime.

    Returns:
        One of ``morning`` (05–10), ``afternoon`` (11–16), ``evening`` (17–21),
        or ``night`` (22–04).
    """
    hour = moment.hour
    if 5 <= hour <= 10:
        return "morning"
    if 11 <= hour <= 16:
        return "afternoon"
    if 17 <= hour <= 21:
        return "evening"
    return "night"


def day_type(moment: datetime) -> str:
    """Return ``weekend`` for Saturday/Sunday, else ``weekday``."""
    return "weekend" if moment.weekday() >= 5 else "weekday"


def promo_flag(promotion_id: object) -> bool:
    """Return True when a non-empty promotion id is present."""
    return pd.notna(promotion_id) and str(promotion_id).strip() != ""


def enrich_context(
    transactions: pd.DataFrame, weather_provider: WeatherProvider | None = None
) -> pd.DataFrame:
    """Add ``hour_band``, ``day_type``, ``promo_flag``, ``weather_bucket`` columns.

    Args:
        transactions: POS transactions (uses ``transaction_datetime``, ``store_id``,
            and optionally ``promotion_id``).
        weather_provider: Provider for the weather bucket (defaults to synthetic).

    Returns:
        A copy of ``transactions`` with the four context columns added.
    """
    provider = weather_provider or SyntheticWeatherProvider()
    enriched = transactions.copy()
    moments = pd.to_datetime(enriched["transaction_datetime"], errors="coerce")

    enriched["hour_band"] = moments.apply(lambda m: hour_band(m) if pd.notna(m) else UNKNOWN)
    enriched["day_type"] = moments.apply(lambda m: day_type(m) if pd.notna(m) else UNKNOWN)

    if "promotion_id" in enriched.columns:
        enriched["promo_flag"] = enriched["promotion_id"].apply(promo_flag)
    else:
        enriched["promo_flag"] = False

    enriched["weather_bucket"] = [
        provider.get_weather(store_id, moment.date()) if pd.notna(moment) else UNKNOWN
        for store_id, moment in zip(enriched["store_id"], moments, strict=True)
    ]
    return enriched
