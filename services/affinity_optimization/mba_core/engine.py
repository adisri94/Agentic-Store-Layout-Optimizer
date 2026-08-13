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


_MIN_BASKETS_FLOOR = 2
_MIN_BASKETS_RATIO = 0.02


def effective_min_baskets(
    n_baskets: int,
    configured: int,
    floor: int = _MIN_BASKETS_FLOOR,
    ratio: float = _MIN_BASKETS_RATIO,
) -> int:
    """Scale the min-supporting-baskets guard to the slice size (T-014, D-040).

    On large slices the configured threshold applies; on small slices (few baskets,
    e.g. a single store × a narrow context) it eases down to ``floor`` so some
    evidence-backed rules can still surface — but never below ``floor``, so
    single-basket rules remain excluded.

    Args:
        n_baskets: Number of baskets in the (possibly sliced) data.
        configured: The configured maximum threshold.
        floor: The hard minimum (default 2 — blocks one-basket rules).
        ratio: Fraction of baskets used to scale (default 0.02).

    Returns:
        The effective threshold, in ``[floor, configured]``.
    """
    return max(floor, min(configured, round(ratio * n_baskets)))


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
    min_supporting_baskets: int = 1,
    adaptive_guard: bool = False,
) -> list[Recommendation]:
    """Mine ranked raw recommendations from POS transactions.

    Args:
        transactions: POS Transactions DataFrame.
        algorithm: Frequent-itemset algorithm (``"fpgrowth"`` default, or ``"apriori"``).
        top_k: Maximum number of recommendations to return.
        min_support: Minimum itemset support threshold.
        min_confidence: Minimum rule confidence threshold.
        min_supporting_baskets: Exclude rules backed by fewer than this many baskets
            (T-014 guard, US-2A.5). ``1`` disables the guard.
        adaptive_guard: When True, scale the guard to the slice size via
            :func:`effective_min_baskets` (D-040) so small slices still surface
            evidence-backed rules while one-basket rules stay excluded.

    Returns:
        Up to ``top_k`` :class:`Recommendation` objects, ranked by lift descending.
        These are raw and must still be governed before returning to a user.
    """
    baskets = baskets_from_transactions(transactions)
    n_baskets = len(baskets)
    rules = _mine_rules(baskets, algorithm, min_support, min_confidence)

    threshold = (
        effective_min_baskets(n_baskets, min_supporting_baskets)
        if adaptive_guard
        else min_supporting_baskets
    )

    recommendations: list[Recommendation] = []
    for _, rule in rules.iterrows():
        sku_a = next(iter(rule["antecedents"]))
        sku_b = next(iter(rule["consequents"]))
        support = float(rule["support"])
        contributing = round(support * n_baskets)
        if contributing < threshold:
            continue  # T-014: drop thin-evidence rules
        recommendations.append(
            Recommendation(
                recommendation_id=f"rec-{sku_a}-{sku_b}",
                sku_a=sku_a,
                sku_b=sku_b,
                placement_type="adjacency",
                lift=float(rule["lift"]),
                confidence=float(rule["confidence"]),
                support=support,
                contributing_baskets=contributing,
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


def mine_negative_associations(
    transactions: pd.DataFrame,
    algorithm: Algorithm = "fpgrowth",
    top_k: int = 20,
    min_support: float = 0.01,
    max_lift: float = 0.8,
) -> list[Recommendation]:
    """Mine negative associations (cannibalization): pairs bought together < chance.

    These are pairs that co-occur but with **lift below** ``max_lift`` (i.e. less
    often than independence would predict) — candidates to avoid co-placing.

    Args:
        transactions: POS Transactions DataFrame.
        algorithm: Frequent-itemset algorithm.
        top_k: Maximum number of negative associations to return.
        min_support: Minimum itemset support (they must still co-occur enough to score).
        max_lift: Upper lift bound; only pairs with ``lift < max_lift`` are returned.

    Returns:
        Up to ``top_k`` :class:`Recommendation` objects tagged ``context={"association":
        "negative"}``, ranked by lift ascending (most negative first). Raw — must be governed.
    """
    baskets = baskets_from_transactions(transactions)
    n_baskets = len(baskets)
    rules = _mine_rules(baskets, algorithm, min_support, min_confidence=0.0)

    negatives: list[Recommendation] = []
    for _, rule in rules.iterrows():
        lift = float(rule["lift"])
        if lift >= max_lift:
            continue
        sku_a = next(iter(rule["antecedents"]))
        sku_b = next(iter(rule["consequents"]))
        support = float(rule["support"])
        negatives.append(
            Recommendation(
                recommendation_id=f"neg-{sku_a}-{sku_b}",
                sku_a=sku_a,
                sku_b=sku_b,
                placement_type="adjacency",
                lift=lift,
                confidence=float(rule["confidence"]),
                support=support,
                contributing_baskets=round(support * n_baskets),
                context={"association": "negative"},
            )
        )

    negatives.sort(key=lambda rec: rec.lift)
    logger.info("mba.mined_negatives", n_baskets=n_baskets, returned=min(top_k, len(negatives)))
    return negatives[:top_k]
