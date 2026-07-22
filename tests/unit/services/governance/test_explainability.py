"""Unit tests for explainability narrative generation (US-1.4)."""

from __future__ import annotations

from api.schemas import Recommendation
from services.governance.explainability import generate_narrative


def _rec() -> Recommendation:
    return Recommendation(
        recommendation_id="rec-SKU-A-SKU-B",
        sku_a="SKU-A",
        sku_b="SKU-B",
        lift=2.1,
        confidence=0.35,
        support=0.08,
        contributing_baskets=3200,
    )


def test_rationale_contains_names_and_lift():
    """TC-1.4.1 — rationale names both SKUs, the lift, and the basket count."""
    context = {"product_names": {"SKU-A": "Running Shoes", "SKU-B": "Sports Socks"}}
    text = generate_narrative(_rec(), context)
    assert "Running Shoes" in text
    assert "Sports Socks" in text
    assert "2.1x" in text
    assert "3,200" in text


def test_rationale_is_deterministic():
    """TC-1.4.2 — the template rationale is deterministic for identical input."""
    context = {"product_names": {"SKU-A": "Running Shoes", "SKU-B": "Sports Socks"}}
    assert generate_narrative(_rec(), context) == generate_narrative(_rec(), context)


def test_rationale_falls_back_to_sku_ids_without_names():
    """Robustness — missing product names still yields a non-empty rationale."""
    text = generate_narrative(_rec(), {})
    assert text
    assert "SKU-A" in text and "SKU-B" in text
