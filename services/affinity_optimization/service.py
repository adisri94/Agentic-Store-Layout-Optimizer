"""Affinity & Optimization service — public recommendation entry point (US-1.7).

Ties the MBA core to governance: mines raw recommendations, then routes every one
through ``governance.govern()`` so no raw recommendation can escape to a caller
(principle #5, D-012, architecture.md §4.4).
"""

from __future__ import annotations

from pathlib import Path

import structlog

from api.schemas import GovernedRecommendation
from platform_services.data_access import load_parquet
from services.affinity_optimization.mba_core import mine_recommendations
from services.governance import govern

logger = structlog.get_logger(__name__)

# Category can be matched against any of the merch hierarchy levels.
_CATEGORY_COLUMNS = ["category_l1", "category_l2", "category_l3", "department"]


def _build_context(products) -> dict:
    """Build the governance/explainability context from the product master."""
    product_names = dict(zip(products["sku_id"], products["product_name"], strict=True))
    product_categories = dict(
        zip(products["sku_id"], products["category_l1"], strict=True)
    )
    return {
        "product_names": product_names,
        "product_categories": product_categories,
    }


def _skus_in_category(products, category: str) -> set[str]:
    """Return SKUs whose any hierarchy level matches ``category`` (case-insensitive)."""
    target = category.strip().lower()
    mask = None
    for column in _CATEGORY_COLUMNS:
        col_mask = products[column].str.lower() == target
        mask = col_mask if mask is None else (mask | col_mask)
    return set(products.loc[mask, "sku_id"]) if mask is not None else set()


def get_recommendations(
    store_id: str | None = None,
    category: str | None = None,
    top_k: int = 20,
    data_dir: Path | None = None,
) -> list[GovernedRecommendation]:
    """Return top-k governed placement recommendations.

    Mines association rules from POS baskets, optionally scoped to a store and/or
    category, then governs each recommendation before returning. The return type is
    intentionally ``list[GovernedRecommendation]`` — there is no code path that
    returns raw recommendations to a caller.

    Args:
        store_id: Restrict to a single store's transactions (``None`` = all stores).
        category: Restrict to pairs whose antecedent SKU is in this category.
        top_k: Maximum number of recommendations to return.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        Up to ``top_k`` governed recommendations, ranked by lift descending.
    """
    transactions = load_parquet("pos_transactions", data_dir=data_dir)
    products = load_parquet("product_master", data_dir=data_dir)

    if store_id is not None:
        transactions = transactions[transactions["store_id"] == store_id]

    raw = mine_recommendations(transactions, top_k=top_k)

    if category is not None:
        allowed = _skus_in_category(products, category)
        raw = [rec for rec in raw if rec.sku_a in allowed]

    context = _build_context(products)
    governed = [govern(rec, context, data_dir=data_dir) for rec in raw]
    logger.info(
        "affinity.get_recommendations",
        store_id=store_id,
        category=category,
        returned=len(governed),
    )
    return governed
