"""Unit tests for the append-only audit writer and govern() (US-1.6, US-1.4 AC3)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from api.schemas import AuditEntry, GovernedRecommendation, Recommendation
from services.governance import govern
from services.governance.audit_writer import write_audit_entry
from services.governance.policy_engine import run_policies


def _rec(rec_id: str = "rec-A-B") -> Recommendation:
    return Recommendation(
        recommendation_id=rec_id,
        sku_a="SKU-A",
        sku_b="SKU-B",
        lift=1.5,
        confidence=0.5,
        support=0.05,
        contributing_baskets=10,
    )


def test_single_audit_line_matches_schema(tmp_path: Path):
    """TC-1.6.1 — one govern-equivalent write yields one AuditEntry-shaped line."""
    rec = _rec()
    write_audit_entry(rec, run_policies(rec, {}), data_dir=tmp_path)

    lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = AuditEntry.model_validate_json(lines[0])
    assert entry.recommendation_id == "rec-A-B"
    assert "lift" in entry.evidence


def test_audit_log_is_append_only(tmp_path: Path):
    """TC-1.6.2 — a second write adds a line and never mutates the first."""
    audit_file = tmp_path / "audit.jsonl"

    write_audit_entry(_rec("rec-1"), run_policies(_rec("rec-1"), {}), data_dir=tmp_path)
    first_line_before = audit_file.read_text(encoding="utf-8").splitlines()[0]

    write_audit_entry(_rec("rec-2"), run_policies(_rec("rec-2"), {}), data_dir=tmp_path)
    lines_after = audit_file.read_text(encoding="utf-8").splitlines()

    assert len(lines_after) == 2
    assert lines_after[0] == first_line_before  # first line byte-identical


def test_audit_timestamp_is_iso_utc(tmp_path: Path):
    """TC-1.6.3 — the timestamp parses as ISO-8601 with a UTC offset."""
    rec = _rec()
    write_audit_entry(rec, run_policies(rec, {}), data_dir=tmp_path)
    raw = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()[0])
    parsed = datetime.fromisoformat(raw["timestamp"])
    assert parsed.utcoffset() is not None
    assert parsed.utcoffset().total_seconds() == 0


def test_govern_returns_governed_recommendation_and_audits(tmp_path: Path):
    """TC-1.4.3 / US-1.6 AC5 — govern wraps the rec and the audit_id matches."""
    context = {"product_names": {"SKU-A": "Shoes", "SKU-B": "Socks"}}
    governed = govern(_rec(), context, data_dir=tmp_path)

    assert isinstance(governed, GovernedRecommendation)
    assert governed.rationale
    assert governed.audit_id

    entry = AuditEntry.model_validate_json(
        (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    )
    assert entry.audit_id == governed.audit_id
