"""Contextual affinity (#1): context enrichment, context-aware mining, negatives."""

from services.affinity_optimization.contextual.enrichment import (
    apply_context_filter,
    day_type,
    enrich_context,
    hour_band,
    promo_flag,
)

__all__ = ["apply_context_filter", "day_type", "enrich_context", "hour_band", "promo_flag"]
