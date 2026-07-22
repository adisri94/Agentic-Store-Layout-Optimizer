"""Unit tests for UI display-formatting helpers (TC-1.10.2, TC-1.11.2)."""

from __future__ import annotations

from ui.formatting import (
    ALL_CATEGORIES,
    audit_display_row,
    category_options,
    name_map,
    recommendation_display_row,
    sku_label,
)

_PRODUCTS = [
    {"sku_id": "SKU-1", "product_name": "Running Shoes", "category_l1": "Footwear"},
    {"sku_id": "SKU-2", "product_name": "Sports Socks", "category_l1": "Accessories"},
    {"sku_id": "SKU-3", "product_name": "Yoga Mat", "category_l1": "Equipment"},
    {"sku_id": "SKU-4", "product_name": "Trail Shoes", "category_l1": "Footwear"},
]


def test_category_options_sorted_distinct_with_all_first():
    """TC-1.13.2 — options are 'All categories' then sorted distinct category_l1."""
    assert category_options(_PRODUCTS) == [
        ALL_CATEGORIES,
        "Accessories",
        "Equipment",
        "Footwear",
    ]


def test_sku_label_with_and_without_name():
    """TC-1.14.1 / TC-1.14.2 — 'CODE — Name' when known, code alone otherwise."""
    names = name_map(_PRODUCTS)
    assert sku_label("SKU-1", names) == "SKU-1 — Running Shoes"
    assert sku_label("SKU-999", names) == "SKU-999"


def test_recommendation_row_uses_names():
    """US-1.14 — the results row shows CODE — Name for both SKUs."""
    names = name_map(_PRODUCTS)
    row = recommendation_display_row(
        {
            "sku_a": "SKU-1",
            "sku_b": "SKU-2",
            "placement_type": "adjacency",
            "lift": 2.0,
            "confidence": 0.4,
            "support": 0.05,
            "policy_warnings": [],
        },
        names,
    )
    assert row["Product A"] == "SKU-1 — Running Shoes"
    assert row["Product B"] == "SKU-2 — Sports Socks"


def test_recommendation_display_row():
    """TC-1.10.2 — a governed recommendation payload formats into a display row."""
    payload = {
        "sku_a": "SKU-A",
        "sku_b": "SKU-B",
        "placement_type": "adjacency",
        "lift": 2.134,
        "confidence": 0.35,
        "support": 0.081,
        "policy_warnings": ["POL-005: flagged"],
        "rationale": "because ...",
        "audit_id": "aud-1",
    }
    row = recommendation_display_row(payload)
    assert row["Product A"] == "SKU-A"  # code alone when no name map is supplied
    assert row["Product B"] == "SKU-B"
    assert row["Lift"] == 2.13
    assert row["Confidence"] == "35%"
    assert row["Support"] == "8.1%"
    assert row["Warnings"] == 1


def test_audit_display_row():
    """TC-1.11.2 — an audit-entry payload formats into a display row."""
    payload = {
        "audit_id": "aud-abc",
        "timestamp": "2026-07-22T10:00:00+00:00",
        "recommendation_id": "rec-A-B",
        "policy_result": {"passed": True, "results": []},
        "evidence": {"lift": 2.13456, "confidence": 0.35, "support": 0.08},
    }
    row = audit_display_row(payload)
    assert row["Audit ID"] == "aud-abc"
    assert row["Recommendation"] == "rec-A-B"
    assert row["Passed"] is True
    assert row["Lift"] == 2.13
