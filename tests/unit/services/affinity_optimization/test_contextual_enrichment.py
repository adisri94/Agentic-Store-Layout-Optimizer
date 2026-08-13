"""Unit tests for basket context enrichment (US-2A.2)."""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from services.affinity_optimization.contextual import (
    day_type,
    enrich_context,
    hour_band,
    promo_flag,
)


def test_hour_band_and_day_type():
    """TC-2A.2.1 — a known timestamp maps to the expected band and day type."""
    saturday_morning = datetime(2026, 6, 6, 9, 30)  # 2026-06-06 is a Saturday
    assert hour_band(saturday_morning) == "morning"
    assert day_type(saturday_morning) == "weekend"

    tuesday_evening = datetime(2026, 6, 2, 19, 0)  # Tuesday
    assert hour_band(tuesday_evening) == "evening"
    assert day_type(tuesday_evening) == "weekday"


def test_promo_flag():
    """TC-2A.2.2 — a promotion id sets promo_flag True; missing/blank is False."""
    assert promo_flag("PROMO-SUM26-01") is True
    assert promo_flag(None) is False
    assert promo_flag("") is False


def test_enrich_context_adds_columns():
    """US-2A.2 — enrich_context adds all four context columns with valid values."""
    df = pd.DataFrame(
        {
            "transaction_datetime": ["2026-06-06T09:30:00", "2026-06-02T19:00:00"],
            "store_id": ["STR-0001", "STR-0002"],
            "promotion_id": ["PROMO-1", None],
        }
    )
    out = enrich_context(df)
    assert list(out["hour_band"]) == ["morning", "evening"]
    assert list(out["day_type"]) == ["weekend", "weekday"]
    assert list(out["promo_flag"]) == [True, False]
    assert out["weather_bucket"].notna().all()


def test_enrich_context_handles_bad_timestamp():
    """AC2 — an unparseable timestamp degrades to 'unknown' rather than raising."""
    df = pd.DataFrame(
        {
            "transaction_datetime": ["not-a-date"],
            "store_id": ["STR-0001"],
            "promotion_id": [None],
        }
    )
    out = enrich_context(df)
    assert out["hour_band"].iloc[0] == "unknown"
    assert out["day_type"].iloc[0] == "unknown"
    assert out["weather_bucket"].iloc[0] == "unknown"
