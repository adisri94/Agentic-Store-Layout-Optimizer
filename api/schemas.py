"""Cross-layer Pydantic models (architecture.md §9).

These models are the shared contract between the services, API, and UI layers.
Sprint 1 defines :class:`Recommendation`; governance and audit models are added by
their respective stories (US-1.4–1.7).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

PlacementType = Literal["adjacency", "endcap", "aisle_entry", "checkout"]
PolicyStatus = Literal["pass", "fail", "warning", "not_evaluated"]


class Recommendation(BaseModel):
    """A raw (pre-governance) product-placement recommendation.

    Attributes:
        recommendation_id: Stable identifier for the SKU pair + placement.
        sku_a: The antecedent SKU ("customers who buy A ...").
        sku_b: The consequent SKU ("... also buy B").
        placement_type: How the pair should be co-placed. Sprint 1 uses ``adjacency``.
        lift: How much more likely the pair sells together vs. chance (1.0 = independent).
        confidence: P(buy B | buy A).
        support: Fraction of baskets containing both SKUs.
        contributing_baskets: Number of baskets backing the rule (evidence for #9).
        context: Optional contextual signals (unused in Sprint 1; reserved for #1).
    """

    recommendation_id: str
    sku_a: str
    sku_b: str
    placement_type: PlacementType = "adjacency"
    lift: float
    confidence: float
    support: float
    contributing_baskets: int = 0
    context: dict = Field(default_factory=dict)


class RecommendationRequest(BaseModel):
    """Request body for ``POST /api/v1/recommendations``.

    Attributes:
        store_id: Store to scope transactions to (required).
        category: Optional category filter (matched against the merch hierarchy).
        top_k: Maximum number of recommendations to return.
    """

    store_id: str
    category: str | None = None
    top_k: int = 20


class PolicyResult(BaseModel):
    """Outcome of a single governance policy check (POL-001–005).

    Attributes:
        rule_id: Policy identifier, e.g. ``"POL-002"``.
        status: ``pass`` | ``fail`` | ``warning`` | ``not_evaluated``.
        message: Human-readable explanation of the outcome.
    """

    rule_id: str
    status: PolicyStatus
    message: str


class GovernedRecommendation(Recommendation):
    """A recommendation after passing through governance (#9).

    Extends :class:`Recommendation` with the explainability narrative, policy
    warnings, an optional fairness score, and the audit entry id.

    Attributes:
        rationale: Plain-English reason a category manager can act on.
        policy_warnings: Human-readable warnings for any triggered policy.
        fairness_score: Optional fairness metric (unused in Sprint 1).
        audit_id: Id of the audit-log entry written for this recommendation.
    """

    rationale: str
    policy_warnings: list[str] = Field(default_factory=list)
    fairness_score: float | None = None
    audit_id: str


class AuditEntry(BaseModel):
    """An append-only governance audit record (architecture.md §9, §10.2).

    Attributes:
        audit_id: Unique audit entry id.
        timestamp: When the recommendation was governed (ISO-8601 UTC).
        recommendation_id: The governed recommendation's id.
        user_id: Optional acting user.
        policy_result: Aggregate policy outcome (passed flag + per-rule results).
        evidence: Evidence bundle (lift, confidence, support, contributing baskets).
    """

    audit_id: str
    timestamp: datetime
    recommendation_id: str
    user_id: str | None = None
    policy_result: dict = Field(default_factory=dict)
    evidence: dict = Field(default_factory=dict)
