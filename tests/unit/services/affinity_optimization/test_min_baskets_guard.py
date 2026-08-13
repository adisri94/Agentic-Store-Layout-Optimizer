"""Tests for the minimum-supporting-baskets guard (US-2A.5 / T-014)."""

from __future__ import annotations

import pandas as pd

from services.affinity_optimization.mba_core import mine_recommendations
from services.affinity_optimization.mba_core.engine import effective_min_baskets


def _txn(basket: str, sku: str) -> dict:
    return {"basket_id": basket, "sku_id": sku}


def _fixture() -> pd.DataFrame:
    rows = []
    for i in range(6):  # well-supported pair A+B (6 baskets)
        rows += [_txn(f"AB-{i}", "A"), _txn(f"AB-{i}", "B")]
    rows += [_txn("CD-0", "C"), _txn("CD-0", "D")]  # thin pair C+D (1 basket)
    return pd.DataFrame(rows)


def _pairs(recs) -> set[tuple[str, str]]:
    return {(r.sku_a, r.sku_b) for r in recs}


def test_guard_excludes_thin_evidence():
    """TC-2A.5.1 — a 1-basket pair is dropped at threshold 5; well-supported stays."""
    df = _fixture()
    recs = mine_recommendations(
        df, min_support=0.1, min_confidence=0.1, min_supporting_baskets=5
    )
    pairs = _pairs(recs)
    assert ("A", "B") in pairs
    assert ("C", "D") not in pairs and ("D", "C") not in pairs
    assert all(r.contributing_baskets >= 5 for r in recs)


def test_threshold_one_reproduces_pre_guard():
    """TC-2A.5.2 — threshold 1 keeps the thin pair (pre-guard behaviour)."""
    df = _fixture()
    recs = mine_recommendations(
        df, min_support=0.1, min_confidence=0.1, min_supporting_baskets=1
    )
    pairs = _pairs(recs)
    assert ("C", "D") in pairs or ("D", "C") in pairs


def test_effective_min_baskets_scales_with_slice():
    """D-040 — the guard eases to the floor on small slices, holds at configured on large."""
    assert effective_min_baskets(300, 5) == 5   # large slice: full guard
    assert effective_min_baskets(58, 5) == 2    # small slice: floor
    assert effective_min_baskets(20, 5) == 2
    assert effective_min_baskets(1000, 5) == 5
    assert effective_min_baskets(300, 5) >= 2   # never below the floor


def test_adaptive_guard_keeps_floor_but_eases_small_slice():
    """D-040 — a 2-basket pair survives the adaptive guard; a 1-basket pair does not."""
    rows = []
    for i in range(2):  # 2-basket pair E+F
        rows += [_txn(f"EF-{i}", "E"), _txn(f"EF-{i}", "F")]
    rows += [_txn("GH-0", "G"), _txn("GH-0", "H")]  # 1-basket pair G+H
    df = pd.DataFrame(rows)

    recs = mine_recommendations(
        df, min_support=0.1, min_confidence=0.1, min_supporting_baskets=5, adaptive_guard=True
    )
    pairs = _pairs(recs)
    assert ("E", "F") in pairs or ("F", "E") in pairs   # 2 baskets survive (floor 2)
    assert ("G", "H") not in pairs and ("H", "G") not in pairs  # 1 basket still excluded
