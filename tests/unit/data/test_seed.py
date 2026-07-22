"""Unit tests for the synthetic data generator (US-1.1).

Covers TC-1.1.1 (determinism), TC-1.1.2 (schema conformance), TC-1.1.3 (mandatory
fields populated), TC-1.1.4 (referential integrity), plus AC4 (affinity co-occurrence
strong enough for MBA to surface rules).

Expected column lists are hard-coded here (copied from ``data_contract.md``) so the
test independently pins the contract rather than trusting the generator's constants.
"""

from __future__ import annotations

from itertools import combinations

from data.seed import generate

# Independent copies of the schemas from data_contract.md (§5.1.3 / §5.2.3).
EXPECTED_POS_COLUMNS = [
    "transaction_id", "transaction_datetime", "store_id", "register_id", "cashier_id",
    "customer_id", "loyalty_card_number", "basket_id", "line_item_seq", "sku_id",
    "sku_description", "quantity", "unit_price", "discount_amount", "promotion_id",
    "tax_amount", "payment_method", "currency_code", "tender_total", "source_system",
]

EXPECTED_PRODUCT_COLUMNS = [
    "sku_id", "gtin_upc", "product_name", "brand", "category_l1", "category_l2",
    "category_l3", "department", "color", "size", "gender", "pack_size",
    "unit_of_measure", "unit_cost", "unit_price_msrp", "margin_pct", "supplier_id",
    "country_of_origin", "dimensions_lwh", "weight", "sustainability_score",
    "lifecycle_status", "created_date", "last_updated", "source_system",
]


def _baskets(pos) -> list[tuple[str, ...]]:
    """Return one sorted SKU tuple per basket, ordered by basket_id."""
    grouped = pos.groupby("basket_id")["sku_id"].apply(lambda s: tuple(sorted(s)))
    return [grouped[key] for key in sorted(grouped.index)]


def test_generation_is_deterministic():
    """TC-1.1.1 — same seed -> identical shapes and identical basket contents."""
    first = generate(profile="small", seed=42)
    second = generate(profile="small", seed=42)

    assert first["product_master"].shape == second["product_master"].shape
    assert first["pos_transactions"].shape == second["pos_transactions"].shape
    assert _baskets(first["pos_transactions"]) == _baskets(second["pos_transactions"])


def test_pos_columns_match_contract():
    """TC-1.1.2 — POS columns exactly match the data contract schema."""
    pos = generate(profile="small", seed=42)["pos_transactions"]
    assert list(pos.columns) == EXPECTED_POS_COLUMNS


def test_product_columns_match_contract():
    """POS-companion check — Product Master columns match the data contract schema."""
    products = generate(profile="small", seed=42)["product_master"]
    assert list(products.columns) == EXPECTED_PRODUCT_COLUMNS


def test_product_master_mandatory_fields_populated():
    """TC-1.1.3 — category and margin fields are non-null for every SKU."""
    products = generate(profile="small", seed=42)["product_master"]
    for column in ["category_l1", "category_l2", "category_l3", "margin_pct", "unit_cost",
                   "unit_price_msrp"]:
        assert products[column].notna().all(), f"{column} has nulls"


def test_referential_integrity_pos_to_product():
    """TC-1.1.4 — every SKU sold in POS exists in Product Master."""
    frames = generate(profile="small", seed=42)
    pos_skus = set(frames["pos_transactions"]["sku_id"])
    master_skus = set(frames["product_master"]["sku_id"])
    assert pos_skus <= master_skus


def test_affinity_pairs_cooccur_above_threshold():
    """AC4 — at least one SKU pair co-occurs in > 1% of baskets (MBA has signal)."""
    pos = generate(profile="small", seed=42)["pos_transactions"]
    baskets = _baskets(pos)
    n_baskets = len(baskets)

    pair_counts: dict[tuple[str, str], int] = {}
    for basket in baskets:
        for pair in combinations(sorted(set(basket)), 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    max_support = max(pair_counts.values()) / n_baskets
    assert max_support > 0.01


def test_unknown_profile_raises():
    """Guard — an unknown profile raises a clear ValueError."""
    import pytest

    with pytest.raises(ValueError, match="Unknown profile"):
        generate(profile="enormous", seed=42)
