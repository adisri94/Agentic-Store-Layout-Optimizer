"""Unit tests for product catalog + POS upload validation (US-1.12, US-1.13)."""

from __future__ import annotations

from pathlib import Path

from services.affinity_optimization import get_product_catalog, missing_pos_columns
from services.affinity_optimization.service import MANDATORY_POS_COLUMNS


def test_missing_pos_columns_detects_gaps():
    """TC-1.12.4 — a complete column set passes; an incomplete one reports the gaps."""
    assert missing_pos_columns(MANDATORY_POS_COLUMNS) == []

    incomplete = [c for c in MANDATORY_POS_COLUMNS if c != "basket_id"]
    assert missing_pos_columns(incomplete) == ["basket_id"]


def test_product_catalog_shape(seeded_data_dir: Path):
    """US-1.13 — the catalog returns sku_id, product_name, category_l1 per SKU."""
    catalog = get_product_catalog(data_dir=seeded_data_dir)
    assert catalog
    entry = catalog[0]
    assert set(entry) == {"sku_id", "product_name", "category_l1"}
