"""Unit tests for the MBA engine (US-1.3).

Covers TC-1.3.1 (hand-computed metrics), TC-1.3.2 (independence -> lift 1.0),
TC-1.3.3 (Apriori == FP-Growth), TC-1.3.4 (top_k + ordering), TC-1.3.5 (support
threshold), TC-1.3.6 (Recommendation contract).
"""

from __future__ import annotations

import pandas as pd

from api.schemas import Recommendation
from data.seed import generate
from services.affinity_optimization.mba_core import mine_recommendations


def _transactions(baskets: list[list[str]]) -> pd.DataFrame:
    """Build a minimal POS DataFrame (basket_id, sku_id) from basket lists."""
    rows = []
    for i, basket in enumerate(baskets):
        for sku in basket:
            rows.append({"basket_id": f"BSK-{i:04d}", "sku_id": sku})
    return pd.DataFrame(rows)


def _find(recs: list[Recommendation], sku_a: str, sku_b: str) -> Recommendation:
    return next(r for r in recs if r.sku_a == sku_a and r.sku_b == sku_b)


def test_metrics_match_hand_computation():
    """TC-1.3.1 — support/confidence/lift equal manually computed values."""
    # 5 baskets: A,B / A,B / A,B / A / C
    txns = _transactions([["A", "B"], ["A", "B"], ["A", "B"], ["A"], ["C"]])
    recs = mine_recommendations(txns, min_support=0.5, min_confidence=0.1)

    rule = _find(recs, "A", "B")
    assert rule.support == round(0.6, 4) or abs(rule.support - 0.6) < 1e-6
    assert abs(rule.confidence - 0.75) < 1e-6  # 0.6 / 0.8
    assert abs(rule.lift - 1.25) < 1e-6        # 0.75 / 0.6
    assert rule.contributing_baskets == 3      # 0.6 * 5


def test_independent_pair_has_unit_lift():
    """TC-1.3.2 — an independent pair yields lift ~= 1.0."""
    # A in 2/4, B in 2/4, AB in 1/4 -> 0.25 == 0.5*0.5 (independent)
    txns = _transactions([["A", "B"], ["A"], ["B"], ["C"]])
    recs = mine_recommendations(txns, min_support=0.2, min_confidence=0.1)
    rule = _find(recs, "A", "B")
    assert abs(rule.lift - 1.0) < 1e-6


def test_apriori_and_fpgrowth_agree():
    """TC-1.3.3 — both algorithms return the same rule set on the same data."""
    txns = _transactions([["A", "B"], ["A", "B"], ["A", "B"], ["A"], ["C"]])
    fp = mine_recommendations(txns, algorithm="fpgrowth", min_support=0.4, min_confidence=0.1)
    ap = mine_recommendations(txns, algorithm="apriori", min_support=0.4, min_confidence=0.1)

    def key(recs):
        return sorted(
            (r.sku_a, r.sku_b, round(r.support, 6), round(r.confidence, 6), round(r.lift, 6))
            for r in recs
        )

    assert key(fp) == key(ap)


def test_top_k_limits_and_orders_by_lift():
    """TC-1.3.4 — top_k caps the count; results are sorted by lift descending."""
    txns = generate(profile="small", seed=42)["pos_transactions"]
    recs = mine_recommendations(txns, top_k=5, min_support=0.01, min_confidence=0.1)
    assert len(recs) == 5
    lifts = [r.lift for r in recs]
    assert lifts == sorted(lifts, reverse=True)


def test_support_threshold_excludes_low_support_rules():
    """TC-1.3.5 — no returned rule has support below min_support."""
    txns = _transactions([["A", "B"], ["A", "B"], ["A", "B"], ["A"], ["C"]])
    recs = mine_recommendations(txns, min_support=0.6, min_confidence=0.1)
    assert recs, "expected at least one rule at this threshold"
    assert all(r.support >= 0.6 - 1e-9 for r in recs)


def test_outputs_are_valid_recommendations():
    """TC-1.3.6 — every output is a Recommendation with the expected field types."""
    txns = generate(profile="small", seed=42)["pos_transactions"]
    recs = mine_recommendations(txns, top_k=10)
    assert recs
    for rec in recs:
        assert isinstance(rec, Recommendation)
        assert rec.placement_type == "adjacency"
        assert isinstance(rec.lift, float)
        assert rec.recommendation_id.startswith("rec-")
