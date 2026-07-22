"""Cross-layer Pydantic models (architecture.md §9).

These models are the shared contract between the services, API, and UI layers.
Sprint 1 defines :class:`Recommendation`; governance and audit models are added by
their respective stories (US-1.4–1.7).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PlacementType = Literal["adjacency", "endcap", "aisle_entry", "checkout"]


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
