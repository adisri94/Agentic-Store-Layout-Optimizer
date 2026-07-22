"""Unit tests for UI display-formatting helpers (TC-1.10.2, TC-1.11.2)."""

from __future__ import annotations

from ui.formatting import audit_display_row, recommendation_display_row


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
    assert row["SKU A"] == "SKU-A"
    assert row["SKU B"] == "SKU-B"
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
