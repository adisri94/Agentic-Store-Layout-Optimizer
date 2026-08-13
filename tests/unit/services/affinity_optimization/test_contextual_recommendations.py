"""Tests for context-aware recommendations (US-2A.3)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from api.schemas import GovernedRecommendation
from services.affinity_optimization import get_recommendations
from services.affinity_optimization.contextual import apply_context_filter
from services.affinity_optimization.mba_core import mine_recommendations


def _txn(basket: str, sku: str, dt: str) -> dict:
    return {
        "basket_id": basket,
        "sku_id": sku,
        "transaction_datetime": dt,
        "store_id": "STR-0001",
        "promotion_id": None,
    }


def _context_fixture() -> pd.DataFrame:
    # Weekend baskets pair A+B; weekday baskets pair A+C. (2026-06-06 = Sat, 06-02 = Tue)
    rows = []
    for i in range(4):
        rows += [_txn(f"WKND-{i}", "A", "2026-06-06T10:00:00"),
                 _txn(f"WKND-{i}", "B", "2026-06-06T10:00:00")]
    for i in range(4):
        rows += [_txn(f"WKDY-{i}", "A", "2026-06-02T10:00:00"),
                 _txn(f"WKDY-{i}", "C", "2026-06-02T10:00:00")]
    return pd.DataFrame(rows)


def _pairs(recs) -> set[tuple[str, str]]:
    return {(r.sku_a, r.sku_b) for r in recs}


def test_context_slice_changes_rules():
    """TC-2A.3.1 — filtering by day_type changes which pairs are mined."""
    df = _context_fixture()

    weekend, applied = apply_context_filter(df, {"day_type": "weekend"})
    assert applied == {"day_type": "weekend"}
    weekend_pairs = _pairs(mine_recommendations(weekend, min_support=0.3, min_confidence=0.1))

    weekday, _ = apply_context_filter(df, {"day_type": "weekday"})
    weekday_pairs = _pairs(mine_recommendations(weekday, min_support=0.3, min_confidence=0.1))

    assert ("A", "B") in weekend_pairs and ("A", "B") not in weekday_pairs
    assert ("A", "C") in weekday_pairs and ("A", "C") not in weekend_pairs


def test_context_recorded_and_governed(seeded_data_dir: Path):
    """TC-2A.3.2 / TC-2A.3.3 — context is recorded on results and they are governed."""
    recs = get_recommendations(
        top_k=10, context={"day_type": "weekend"}, data_dir=seeded_data_dir
    )
    for rec in recs:
        assert isinstance(rec, GovernedRecommendation)
        assert rec.context.get("day_type") == "weekend"


def test_no_context_is_backward_compatible(seeded_data_dir: Path):
    """TC-2A.3 AC4 — omitting context reproduces the Sprint 1 baseline (no context tag)."""
    recs = get_recommendations(top_k=5, data_dir=seeded_data_dir)
    assert recs
    assert all(r.context == {} for r in recs)
