"""Unit tests for the governance policy engine (US-1.5, POL-001..005)."""

from __future__ import annotations

from api.schemas import PolicyResult, Recommendation
from services.governance.policy_engine import (
    POLICIES,
    pol_001_endcap_margin,
    pol_002_min_confidence,
    pol_003_brand_mandate,
    pol_004_vendor_equity,
    pol_005_regulated_category,
    run_policies,
)


def _rec(confidence: float = 0.5) -> Recommendation:
    return Recommendation(
        recommendation_id="rec-A-B",
        sku_a="SKU-A",
        sku_b="SKU-B",
        lift=1.5,
        confidence=confidence,
        support=0.05,
    )


def test_pol_002_confidence_gate():
    """TC-1.5.1 — low confidence fails POL-002; adequate confidence passes."""
    assert pol_002_min_confidence(_rec(confidence=0.05), {}).status == "fail"
    assert pol_002_min_confidence(_rec(confidence=0.5), {}).status == "pass"


def test_pol_005_flags_regulated_category():
    """TC-1.5.2 — a SKU in a regulated category is flagged with a warning."""
    context = {
        "product_categories": {"SKU-A": "Alcohol", "SKU-B": "Apparel"},
        "regulated_categories": ["Alcohol", "Tobacco"],
    }
    result = pol_005_regulated_category(_rec(), context)
    assert result.status == "warning"
    assert "Alcohol" in result.message


def test_pol_001_endcap_margin_threshold():
    """TC-1.5.3 — endcap over 40% high-margin fails; under passes."""
    assert pol_001_endcap_margin(_rec(), {"endcap_high_margin_pct": 45}).status == "fail"
    assert pol_001_endcap_margin(_rec(), {"endcap_high_margin_pct": 35}).status == "pass"


def test_every_policy_returns_policy_result():
    """TC-1.5.4 — every policy function returns a well-formed PolicyResult."""
    results = run_policies(_rec(), {})
    assert len(results) == len(POLICIES) == 5
    for result in results:
        assert isinstance(result, PolicyResult)
        assert result.rule_id.startswith("POL-")
        assert result.status in {"pass", "fail", "warning", "not_evaluated"}


def test_pol_003_004_not_evaluated_without_config():
    """TC-1.5.5 — brand/vendor policies return not_evaluated (never a false pass)."""
    assert pol_003_brand_mandate(_rec(), {}).status == "not_evaluated"
    assert pol_004_vendor_equity(_rec(), {}).status == "not_evaluated"
