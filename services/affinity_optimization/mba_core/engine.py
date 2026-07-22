"""Market Basket Analysis engine (US-1.3).

Mines association rules from POS baskets using ``mlxtend`` (Apriori or FP-Growth)
and maps them to :class:`~api.schemas.Recommendation` objects scored by lift,
confidence, and support.

These are **raw** recommendations. They must be passed through
``services.governance.govern()`` before reaching any caller (principle #5, US-1.7);
this module deliberately does not expose a user-facing entry point.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
import structlog
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

from api.schemas import Recommendation

logger = structlog.get_logger(__name__)

Algorithm = Literal["fpgrowth", "apriori"]


def baskets_from_transactions(transactions: pd.DataFrame) -> list[list[str]]:
    """Group POS line items into per-basket lists of unique SKUs.

    Args:
        transactions: POS Transactions with ``basket_id`` and ``sku_id`` columns.

    Returns:
        One list of unique SKU ids per basket, ordered by ``basket_id``.
    """
    grouped = transactions.groupby("basket_id")["sku_id"].apply(
        lambda skus: sorted(set(skus))
    )
    return [grouped[key] for key in sorted(grouped.index)]


def _mine_rules(
    baskets: list[list[str]],
    algorithm: Algorithm,
    min_support: float,
    min_confidence: float,
) -> pd.DataFrame:
    """Run the chosen frequent-itemset miner and derive 1:1 association rules.

    Args:
        baskets: Per-basket lists of SKU ids.
        algorithm: ``"fpgrowth"`` or ``"apriori"``.
        min_support: Minimum itemset support.
        min_confidence: Minimum rule confidence.

    Returns:
        A DataFrame of association rules restricted to single-SKU antecedent and
        single-SKU consequent (may be empty).
    """
    encoder = TransactionEncoder()
    encoded = encoder.fit(baskets).transform(baskets)
    frame = pd.DataFrame(encoded, columns=encoder.columns_)

    miner = fpgrowth if algorithm == "fpgrowth" else apriori
    itemsets = miner(frame, min_support=min_support, use_colnames=True)
    if itemsets.empty:
        return pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])

    rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)
    pairwise = rules[
        (rules["antecedents"].apply(len) == 1) & (rules["consequents"].apply(len) == 1)
    ]
    return pairwise


def mine_recommendations(
    transactions: pd.DataFrame,
    algorithm: Algorithm = "fpgrowth",
    top_k: int = 20,
    min_support: float = 0.01,
    min_confidence: float = 0.1,
) -> list[Recommendation]:
    """Mine ranked raw recommendations from POS transactions.

    Args:
        transactions: POS Transactions DataFrame.
        algorithm: Frequent-itemset algorithm (``"fpgrowth"`` default, or ``"apriori"``).
        top_k: Maximum number of recommendations to return.
        min_support: Minimum itemset support threshold.
        min_confidence: Minimum rule confidence threshold.

    Returns:
        Up to ``top_k`` :class:`Recommendation` objects, ranked by lift descending.
        These are raw and must still be governed before returning to a user.
    """
    baskets = baskets_from_transactions(transactions)
    n_baskets = len(baskets)
    rules = _mine_rules(baskets, algorithm, min_support, min_confidence)

    recommendations: list[Recommendation] = []
    for _, rule in rules.iterrows():
        sku_a = next(iter(rule["antecedents"]))
        sku_b = next(iter(rule["consequents"]))
        support = float(rule["support"])
        recommendations.append(
            Recommendation(
                recommendation_id=f"rec-{sku_a}-{sku_b}",
                sku_a=sku_a,
                sku_b=sku_b,
                placement_type="adjacency",
                lift=float(rule["lift"]),
                confidence=float(rule["confidence"]),
                support=support,
                contributing_baskets=round(support * n_baskets),
            )
        )

    recommendations.sort(key=lambda rec: rec.lift, reverse=True)
    logger.info(
        "mba.mined",
        algorithm=algorithm,
        n_baskets=n_baskets,
        n_rules=len(recommendations),
        returned=min(top_k, len(recommendations)),
    )
    return recommendations[:top_k]
