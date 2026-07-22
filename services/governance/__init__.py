"""Service 3 — Governance (#9): explainability, policy checks, audit logging.

Public interface (architecture.md §4.3): :func:`govern` and :func:`get_audit_log`.
Every recommendation-producing function in the other services must pass its output
through :func:`govern` before returning to any caller (principle #5, US-1.7).
"""

from __future__ import annotations

from pathlib import Path

import structlog

from api.schemas import AuditEntry, GovernedRecommendation, Recommendation
from services.governance.audit_writer import read_audit_entries, write_audit_entry
from services.governance.explainability import generate_narrative
from services.governance.policy_engine import run_policies

logger = structlog.get_logger(__name__)

__all__ = ["govern", "get_audit_log"]


def govern(
    recommendation: Recommendation,
    context: dict,
    user_id: str | None = None,
    data_dir: Path | None = None,
) -> GovernedRecommendation:
    """Intercept a recommendation: explain it, check policy, audit it, wrap it.

    This is the governance-in-path entry point. It attaches a plain-English
    rationale, runs all policy checks, writes an audit entry, and returns the
    recommendation wrapped as a :class:`GovernedRecommendation`. The result is
    returned transparently even when a policy warns/fails — the warning travels
    with it rather than being hidden (governance_charter.md §3, §7).

    Args:
        recommendation: The raw recommendation to govern.
        context: Governance/explainability context (product names, categories, etc.).
        user_id: Optional acting user, recorded in the audit entry.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        The governed recommendation, including rationale, warnings, and audit id.
    """
    rationale = generate_narrative(recommendation, context)
    policy_results = run_policies(recommendation, context)
    warnings = [
        f"{r.rule_id}: {r.message}"
        for r in policy_results
        if r.status in ("fail", "warning")
    ]
    audit_entry = write_audit_entry(
        recommendation, policy_results, user_id=user_id, data_dir=data_dir
    )
    logger.info(
        "governance.governed",
        recommendation_id=recommendation.recommendation_id,
        audit_id=audit_entry.audit_id,
        warnings=len(warnings),
    )
    return GovernedRecommendation(
        **recommendation.model_dump(),
        rationale=rationale,
        policy_warnings=warnings,
        fairness_score=None,
        audit_id=audit_entry.audit_id,
    )


def get_audit_log(
    limit: int = 100,
    filters: dict | None = None,
    data_dir: Path | None = None,
) -> list[AuditEntry]:
    """Return recent audit entries, newest first.

    Args:
        limit: Maximum number of entries to return.
        filters: Reserved for future filtering (unused in Sprint 1).
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        Up to ``limit`` audit entries, newest first.
    """
    return read_audit_entries(limit=limit, data_dir=data_dir)
