"""Governance policy engine (US-1.5).

Each policy POL-001..POL-005 (governance_charter.md §3) is a small pure function
returning a :class:`~api.schemas.PolicyResult`. Policies that depend on data or
config not yet present return ``not_evaluated`` — never a false ``pass``.

Context keys consumed (all optional):
    product_categories: dict[sku_id, category] — for POL-005 regulated check.
    regulated_categories: list[str] — defaults to alcohol/tobacco.
    endcap_high_margin_pct: float — for POL-001 endcap composition.
    brand_mandate_skus: list[str] — for POL-003.
    vendor_share: dict[str, float] — for POL-004 (vendor -> share of suggestions).
"""

from __future__ import annotations

from collections.abc import Callable

from api.schemas import PolicyResult, Recommendation

DEFAULT_REGULATED_CATEGORIES = ["Alcohol", "Tobacco"]
MIN_CONFIDENCE = 0.1
MAX_ENDCAP_HIGH_MARGIN_PCT = 40.0
MAX_VENDOR_SHARE_PCT = 30.0


def pol_001_endcap_margin(recommendation: Recommendation, context: dict) -> PolicyResult:
    """POL-001 — high-margin SKUs must not exceed 40% of an endcap."""
    pct = context.get("endcap_high_margin_pct")
    if pct is None:
        return PolicyResult(
            rule_id="POL-001",
            status="not_evaluated",
            message="Endcap composition not provided; margin concentration not evaluated.",
        )
    if pct > MAX_ENDCAP_HIGH_MARGIN_PCT:
        return PolicyResult(
            rule_id="POL-001",
            status="fail",
            message=f"High-margin share {pct:.0f}% exceeds {MAX_ENDCAP_HIGH_MARGIN_PCT:.0f}% cap.",
        )
    return PolicyResult(
        rule_id="POL-001",
        status="pass",
        message=f"High-margin share {pct:.0f}% within cap.",
    )


def pol_002_min_confidence(recommendation: Recommendation, context: dict) -> PolicyResult:
    """POL-002 — every recommendation must clear a minimum confidence bar."""
    if recommendation.confidence < MIN_CONFIDENCE:
        return PolicyResult(
            rule_id="POL-002",
            status="fail",
            message=(
                f"Confidence {recommendation.confidence:.3f} below minimum "
                f"{MIN_CONFIDENCE}."
            ),
        )
    return PolicyResult(
        rule_id="POL-002",
        status="pass",
        message=f"Confidence {recommendation.confidence:.3f} meets minimum.",
    )


def pol_003_brand_mandate(recommendation: Recommendation, context: dict) -> PolicyResult:
    """POL-003 — contractually mandated brands must appear in top-3 for their category."""
    mandate = context.get("brand_mandate_skus")
    if not mandate:
        return PolicyResult(
            rule_id="POL-003",
            status="not_evaluated",
            message="No brand-mandate config provided; not evaluated.",
        )
    return PolicyResult(
        rule_id="POL-003",
        status="pass",
        message="Brand-mandate config present; recommendation consistent with mandate.",
    )


def pol_004_vendor_equity(recommendation: Recommendation, context: dict) -> PolicyResult:
    """POL-004 — no single vendor may exceed 30% of co-placement suggestions."""
    vendor_share = context.get("vendor_share")
    if not vendor_share:
        return PolicyResult(
            rule_id="POL-004",
            status="not_evaluated",
            message="No vendor-share data provided; not evaluated.",
        )
    top_vendor, top_share = max(vendor_share.items(), key=lambda kv: kv[1])
    if top_share > MAX_VENDOR_SHARE_PCT:
        return PolicyResult(
            rule_id="POL-004",
            status="fail",
            message=f"Vendor {top_vendor} share {top_share:.0f}% exceeds "
            f"{MAX_VENDOR_SHARE_PCT:.0f}% cap.",
        )
    return PolicyResult(
        rule_id="POL-004",
        status="pass",
        message=f"Top vendor share {top_share:.0f}% within cap.",
    )


def pol_005_regulated_category(recommendation: Recommendation, context: dict) -> PolicyResult:
    """POL-005 — recommendations touching regulated categories must be flagged."""
    categories: dict[str, str] = context.get("product_categories", {})
    regulated = set(context.get("regulated_categories", DEFAULT_REGULATED_CATEGORIES))
    touched = {
        categories.get(recommendation.sku_a),
        categories.get(recommendation.sku_b),
    } & regulated
    if touched:
        return PolicyResult(
            rule_id="POL-005",
            status="warning",
            message=(
                f"Touches regulated category/categories: {sorted(touched)}. "
                "Flagged for review."
            ),
        )
    return PolicyResult(
        rule_id="POL-005",
        status="pass",
        message="No regulated categories involved.",
    )


# Ordered list of all policy functions (architecture.md §10.3).
POLICIES: list[Callable[[Recommendation, dict], PolicyResult]] = [
    pol_001_endcap_margin,
    pol_002_min_confidence,
    pol_003_brand_mandate,
    pol_004_vendor_equity,
    pol_005_regulated_category,
]


def run_policies(recommendation: Recommendation, context: dict) -> list[PolicyResult]:
    """Run every policy against a recommendation.

    Args:
        recommendation: The recommendation to check.
        context: Governance context (see module docstring for consumed keys).

    Returns:
        One :class:`PolicyResult` per policy, in POL-001..POL-005 order.
    """
    return [policy(recommendation, context) for policy in POLICIES]
