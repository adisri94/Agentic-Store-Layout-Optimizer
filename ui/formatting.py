"""Pure display-formatting helpers for the UI (US-1.10 / US-1.11).

These functions turn API JSON payloads into display rows. They are deliberately
free of Streamlit imports so they can be unit-tested in isolation.
"""

from __future__ import annotations

ALL_CATEGORIES = "All categories"


def category_options(products: list[dict]) -> list[str]:
    """Build the category dropdown options from the product catalog (US-1.13).

    Args:
        products: Product-catalog entries (each with ``category_l1``).

    Returns:
        ``["All categories", <sorted distinct category_l1>...]``.
    """
    categories = sorted({p["category_l1"] for p in products if p.get("category_l1")})
    return [ALL_CATEGORIES, *categories]


def name_map(products: list[dict]) -> dict[str, str]:
    """Build a ``sku_id -> product_name`` lookup from the product catalog (US-1.14)."""
    return {p["sku_id"]: p["product_name"] for p in products}


def sku_label(sku_id: str, names: dict[str, str]) -> str:
    """Render ``CODE — Name`` for a SKU, or just the code if no name is known (US-1.14)."""
    name = names.get(sku_id)
    return f"{sku_id} — {name}" if name else sku_id


def recommendation_display_row(recommendation: dict, names: dict[str, str] | None = None) -> dict:
    """Format a governed recommendation payload into a display row.

    Args:
        recommendation: A ``GovernedRecommendation`` as returned by the API.
        names: Optional ``sku_id -> product_name`` map for display (US-1.14).

    Returns:
        A dict of human-readable columns for tabular display.
    """
    names = names or {}
    return {
        "Product A": sku_label(recommendation["sku_a"], names),
        "Product B": sku_label(recommendation["sku_b"], names),
        "Placement": recommendation["placement_type"],
        "Lift": round(recommendation["lift"], 2),
        "Confidence": f"{recommendation['confidence'] * 100:.0f}%",
        "Support": f"{recommendation['support'] * 100:.1f}%",
        "Warnings": len(recommendation.get("policy_warnings", [])),
    }


def audit_display_row(entry: dict) -> dict:
    """Format an audit-log entry payload into a display row.

    Args:
        entry: An ``AuditEntry`` as returned by the API.

    Returns:
        A dict of human-readable columns for tabular display.
    """
    policy_result = entry.get("policy_result", {})
    evidence = entry.get("evidence", {})
    return {
        "Audit ID": entry["audit_id"],
        "Timestamp": entry["timestamp"],
        "Recommendation": entry["recommendation_id"],
        "Passed": policy_result.get("passed"),
        "Lift": round(evidence.get("lift", 0.0), 2),
        "Confidence": evidence.get("confidence"),
        "Support": evidence.get("support"),
    }
