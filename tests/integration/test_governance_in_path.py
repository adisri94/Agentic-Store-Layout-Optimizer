"""Integration tests for governance-in-path (US-1.7) and audit isolation (TC-1.6.4).

Exercises the end-to-end service flow: synthetic data -> MBA mining -> govern ->
governed recommendations + audit log, using a temp data dir and no live LLM.
"""

from __future__ import annotations

import typing
from pathlib import Path

from api.schemas import GovernedRecommendation
from services.affinity_optimization import get_recommendations
from services.affinity_optimization.service import (
    get_recommendations as get_recommendations_impl,
)
from services.governance import get_audit_log

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_get_recommendations_returns_only_governed(seeded_data_dir: Path):
    """TC-1.7.1 — every returned item is a GovernedRecommendation with rationale + audit."""
    recs = get_recommendations(top_k=10, data_dir=seeded_data_dir)
    assert recs, "expected at least one recommendation from the seeded data"
    for rec in recs:
        assert isinstance(rec, GovernedRecommendation)
        assert rec.rationale
        assert rec.audit_id


def test_audit_count_matches_recommendations(seeded_data_dir: Path):
    """TC-1.7.2 — exactly one audit entry is written per returned recommendation."""
    recs = get_recommendations(top_k=10, data_dir=seeded_data_dir)
    entries = get_audit_log(limit=1000, data_dir=seeded_data_dir)
    assert len(entries) == len(recs)
    # Every returned recommendation's audit_id is present in the log.
    logged_ids = {e.audit_id for e in entries}
    assert {r.audit_id for r in recs} <= logged_ids


def test_get_recommendations_return_annotation_is_governed():
    """TC-1.7.3 — the public signature returns list[GovernedRecommendation]."""
    hints = typing.get_type_hints(get_recommendations_impl)
    assert "GovernedRecommendation" in str(hints["return"])


def test_only_audit_writer_writes_audit_log():
    """TC-1.6.4 — no module except audit_writer.py references the audit log file."""
    services_dir = REPO_ROOT / "services"
    offenders: list[str] = []
    for py_file in services_dir.rglob("*.py"):
        if py_file.name == "audit_writer.py":
            continue
        if "audit.jsonl" in py_file.read_text(encoding="utf-8"):
            offenders.append(str(py_file.relative_to(REPO_ROOT)))
    assert not offenders, f"Only audit_writer.py may touch audit.jsonl; found: {offenders}"
