"""Pure display-formatting helpers for the UI (US-1.10 / US-1.11).

These functions turn API JSON payloads into display rows. They are deliberately
free of Streamlit imports so they can be unit-tested in isolation.
"""

from __future__ import annotations


def recommendation_display_row(recommendation: dict) -> dict:
    """Format a governed recommendation payload into a display row.

    Args:
        recommendation: A ``GovernedRecommendation`` as returned by the API.

    Returns:
        A dict of human-readable columns for tabular display.
    """
    return {
        "SKU A": recommendation["sku_a"],
        "SKU B": recommendation["sku_b"],
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
