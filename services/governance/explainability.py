"""Explainability narrative generation (US-1.4).

Sprint 1 builds the rationale from a **template** — no LLM call, fully offline and
deterministic (principle #7, mock-first). The single public entry point
:func:`generate_narrative` leaves a flag-gated seam so an LLM-authored narrative can
be slotted in at Sprint 4 (#3) without changing any caller.
"""

from __future__ import annotations

from api.schemas import Recommendation


def _build_template_rationale(recommendation: Recommendation, context: dict) -> str:
    """Compose the plain-English rationale from the evidence bundle.

    Args:
        recommendation: The raw recommendation being explained.
        context: May contain ``product_names`` (sku_id -> display name).

    Returns:
        A one-sentence, category-manager-readable rationale.
    """
    names: dict[str, str] = context.get("product_names", {})
    name_a = names.get(recommendation.sku_a, recommendation.sku_a)
    name_b = names.get(recommendation.sku_b, recommendation.sku_b)
    return (
        f"Recommended because customers who buy {name_a} are "
        f"{recommendation.lift:.1f}x more likely to also buy {name_b}, "
        f"based on {recommendation.contributing_baskets:,} comparable transactions."
    )


def generate_narrative(recommendation: Recommendation, context: dict) -> str:
    """Return the explainability narrative for a recommendation.

    In Sprint 1 this always uses the deterministic template. The seam below is
    where an LLM narrative is added later (guarded by a feature flag); callers do
    not change.

    Args:
        recommendation: The raw recommendation being explained.
        context: Explainability context (e.g. ``product_names``).

    Returns:
        A non-empty plain-English rationale string.
    """
    # Sprint 4 seam:
    #   if settings.enable_llm_narrative:
    #       return llm_client.complete(...)   # llm_client falls back to mock w/o key
    return _build_template_rationale(recommendation, context)
