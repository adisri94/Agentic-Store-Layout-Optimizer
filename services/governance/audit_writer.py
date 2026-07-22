"""Append-only audit log writer (US-1.6).

This is the **only** module permitted to write ``data/audit.jsonl`` (architecture.md
§6.3). Every governed recommendation results in exactly one appended JSONL line
conforming to :class:`~api.schemas.AuditEntry`. Lines are never modified or removed.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from api.schemas import AuditEntry, PolicyResult, Recommendation
from platform_services.config import settings


def _audit_path(data_dir: Path | None = None) -> Path:
    """Return the audit-log path, ensuring its parent directory exists."""
    root = data_dir or settings.data_dir
    root.mkdir(parents=True, exist_ok=True)
    return root / "audit.jsonl"


def write_audit_entry(
    recommendation: Recommendation,
    policy_results: list[PolicyResult],
    user_id: str | None = None,
    data_dir: Path | None = None,
) -> AuditEntry:
    """Append one audit entry for a governed recommendation and return it.

    Args:
        recommendation: The recommendation being audited.
        policy_results: Per-policy outcomes from the policy engine.
        user_id: Optional acting user.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        The :class:`AuditEntry` that was appended.
    """
    passed = all(result.status != "fail" for result in policy_results)
    entry = AuditEntry(
        audit_id=f"aud-{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(UTC),
        recommendation_id=recommendation.recommendation_id,
        user_id=user_id,
        policy_result={
            "passed": passed,
            "results": [result.model_dump() for result in policy_results],
        },
        evidence={
            "lift": recommendation.lift,
            "confidence": recommendation.confidence,
            "support": recommendation.support,
            "contributing_baskets": recommendation.contributing_baskets,
        },
    )
    with _audit_path(data_dir).open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json() + "\n")
    return entry


def read_audit_entries(
    limit: int = 100, data_dir: Path | None = None
) -> list[AuditEntry]:
    """Read audit entries, newest first.

    Args:
        limit: Maximum number of entries to return.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        Up to ``limit`` :class:`AuditEntry` objects, newest first (empty if none).
    """
    path = _audit_path(data_dir)
    if not path.exists():
        return []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    entries = [AuditEntry.model_validate_json(line) for line in lines]
    entries.reverse()
    return entries[:limit]
