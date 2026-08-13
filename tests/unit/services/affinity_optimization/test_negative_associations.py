"""Tests for negative-association (cannibalization) detection (US-2A.4)."""

from __future__ import annotations

import pandas as pd

from api.schemas import Recommendation
from services.affinity_optimization.mba_core import mine_negative_associations
from services.governance.explainability import generate_narrative


def _txn(basket: str, sku: str) -> dict:
    return {"basket_id": basket, "sku_id": sku}


def _anticorrelated_fixture() -> pd.DataFrame:
    # A and B each frequent but rarely together (lift < 1); C co-occurs with A (lift > 1).
    rows = []
    for i in range(10):
        rows += [_txn(f"A-{i}", "A"), _txn(f"A-{i}", "C")]   # A with C
    for i in range(10):
        rows.append(_txn(f"B-{i}", "B"))                      # B alone
    for i in range(2):
        rows += [_txn(f"AB-{i}", "A"), _txn(f"AB-{i}", "B")]  # A+B rarely
    return pd.DataFrame(rows)


def _pairs(recs) -> set[tuple[str, str]]:
    return {(r.sku_a, r.sku_b) for r in recs}


def test_negative_pair_detected_positive_excluded():
    """TC-2A.4.1 — an anti-correlated pair is returned; a correlated pair is not."""
    df = _anticorrelated_fixture()
    negatives = mine_negative_associations(df, min_support=0.05, max_lift=0.9)
    pairs = _pairs(negatives)

    assert ("A", "B") in pairs or ("B", "A") in pairs
    assert all(r.lift < 0.9 for r in negatives)
    # The correlated A→C pair must not appear among negatives.
    assert ("A", "C") not in pairs
    # Tagged as a negative association.
    assert all(r.context.get("association") == "negative" for r in negatives)


def test_negative_rationale_reads_as_avoid():
    """TC-2A.4.2 — a negative association's rationale is an avoid/cannibalization message."""
    rec = Recommendation(
        recommendation_id="neg-A-B",
        sku_a="SKU-A",
        sku_b="SKU-B",
        lift=0.3,
        confidence=0.05,
        support=0.02,
        contributing_baskets=4,
        context={"association": "negative"},
    )
    text = generate_narrative(rec, {"product_names": {"SKU-A": "Coffee", "SKU-B": "Tea"}})
    assert "Avoid co-placing" in text
    assert "Coffee" in text and "Tea" in text
