"""Synthetic data generator for the Store Layout Optimizer demo (US-1.1).

Generates the two data domains Sprint 1 needs to mine market baskets:

* **Product Master** — the golden SKU record (schema per ``data_contract.md`` §5.2.3).
* **POS Transactions** — basket line items (schema per ``data_contract.md`` §5.1.3).

The generator is **deterministic** given a fixed seed (``random.seed`` equivalent,
per ``architecture.md`` §6.3): two runs with the same seed produce byte-identical
row counts and identical basket contents. It builds in deliberate SKU affinities so
that Market Basket Analysis returns non-trivial association rules.

Run it via the task runner (``./tasks.ps1 seed``) or directly::

    uv run python -m data.seed              # full demo volumes -> data/samples/
    uv run python -m data.seed --sample     # small deterministic set (fast)

Design note: no ``datetime.now()`` is used anywhere — timestamps derive from a fixed
base date so output is reproducible across machines and runs.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random

import pandas as pd
import structlog
import typer
from faker import Faker

logger = structlog.get_logger(__name__)

# --------------------------------------------------------------------------- #
# Reference data (fictional global sports-apparel retailer)
# --------------------------------------------------------------------------- #

# (category_l1, category_l2, category_l3, department, gender)
CATEGORIES: list[tuple[str, str, str, str, str]] = [
    ("Apparel", "Men's", "Running Tops", "Sportswear", "Men"),
    ("Apparel", "Men's", "Shorts", "Sportswear", "Men"),
    ("Apparel", "Women's", "Leggings", "Sportswear", "Women"),
    ("Apparel", "Women's", "Sports Bras", "Sportswear", "Women"),
    ("Footwear", "Men's", "Running Shoes", "Footwear", "Men"),
    ("Footwear", "Women's", "Running Shoes", "Footwear", "Women"),
    ("Accessories", "Unisex", "Socks", "Accessories", "Unisex"),
    ("Accessories", "Unisex", "Caps", "Accessories", "Unisex"),
    ("Equipment", "Unisex", "Water Bottles", "Equipment", "Unisex"),
    ("Equipment", "Unisex", "Yoga Mats", "Equipment", "Unisex"),
    ("Nutrition", "Unisex", "Protein Bars", "Nutrition", "Unisex"),
    ("Nutrition", "Unisex", "Energy Drinks", "Nutrition", "Unisex"),
]

# Category-level affinities: items from these level-3 categories are made to
# co-occur far more often than chance, so MBA surfaces real association rules.
AFFINITY_CATEGORY_PAIRS: list[tuple[str, str]] = [
    ("Running Shoes", "Socks"),
    ("Leggings", "Sports Bras"),
    ("Water Bottles", "Yoga Mats"),
    ("Running Tops", "Shorts"),
    ("Energy Drinks", "Protein Bars"),
]

BRANDS = ["AeroFit", "StridePro", "PeakForm", "UrbanPace", "CoreMotion", "VeloxGear"]
COLORS = ["Black", "White", "Blue", "Red", "Grey", "Green"]
SIZES = ["XS", "S", "M", "L", "XL"]
COUNTRIES = ["VN", "CN", "IN", "ID", "PT"]
PAYMENT_METHODS = ["CARD", "CASH", "WALLET"]

# Fixed reference points so generation never depends on the wall clock.
BASE_TXN_DATETIME = datetime(2026, 6, 1, 8, 0, 0)
BASE_CREATED_DATE = date(2025, 1, 1)

# Canonical column order (matches data_contract.md schemas exactly).
PRODUCT_MASTER_COLUMNS = [
    "sku_id", "gtin_upc", "product_name", "brand", "category_l1", "category_l2",
    "category_l3", "department", "color", "size", "gender", "pack_size",
    "unit_of_measure", "unit_cost", "unit_price_msrp", "margin_pct", "supplier_id",
    "country_of_origin", "dimensions_lwh", "weight", "sustainability_score",
    "lifecycle_status", "created_date", "last_updated", "source_system",
]

POS_TRANSACTION_COLUMNS = [
    "transaction_id", "transaction_datetime", "store_id", "register_id", "cashier_id",
    "customer_id", "loyalty_card_number", "basket_id", "line_item_seq", "sku_id",
    "sku_description", "quantity", "unit_price", "discount_amount", "promotion_id",
    "tax_amount", "payment_method", "currency_code", "tender_total", "source_system",
]

# Volume profiles. ``full`` targets D-009 demo volumes; ``small`` is a fast,
# test-friendly deterministic set.
PROFILES: dict[str, dict[str, int]] = {
    "full": {"n_products": 10_000, "n_transactions": 500_000, "n_stores": 50},
    "small": {"n_products": 40, "n_transactions": 300, "n_stores": 5},
}

TAX_RATE = 0.08


def _append_unique(basket: list[str], seen: set[str], sku: str) -> None:
    """Append ``sku`` to ``basket`` only if not already present (order-preserving)."""
    if sku not in seen:
        seen.add(sku)
        basket.append(sku)


def _generate_product_master(rng: Random, fake: Faker, n_products: int) -> pd.DataFrame:
    """Build the Product Master DataFrame.

    Args:
        rng: Seeded random generator for reproducibility.
        fake: Seeded Faker instance (used for GTIN generation).
        n_products: Number of SKUs to generate.

    Returns:
        A DataFrame with exactly ``PRODUCT_MASTER_COLUMNS``, one row per SKU.
    """
    rows: list[dict] = []
    for i in range(n_products):
        cat_l1, cat_l2, cat_l3, department, gender = CATEGORIES[i % len(CATEGORIES)]
        brand = rng.choice(BRANDS)
        color = rng.choice(COLORS)
        size = rng.choice(SIZES)
        unit_cost = round(rng.uniform(5.0, 80.0), 2)
        msrp = round(unit_cost * rng.uniform(1.4, 3.0), 2)
        margin_pct = round((msrp - unit_cost) / msrp * 100, 2)
        created = BASE_CREATED_DATE + timedelta(days=rng.randint(0, 300))
        rows.append(
            {
                "sku_id": f"SKU-{100000 + i}",
                "gtin_upc": fake.numerify("#############"),
                "product_name": f"{brand} {color} {cat_l3}",
                "brand": brand,
                "category_l1": cat_l1,
                "category_l2": cat_l2,
                "category_l3": cat_l3,
                "department": department,
                "color": color,
                "size": size,
                "gender": gender,
                "pack_size": 1.00,
                "unit_of_measure": "EA",
                "unit_cost": unit_cost,
                "unit_price_msrp": msrp,
                "margin_pct": margin_pct,
                "supplier_id": f"VEND-{2200 + (i % 25)}",
                "country_of_origin": rng.choice(COUNTRIES),
                "dimensions_lwh": "30x25x2 cm",
                "weight": round(rng.uniform(0.05, 1.5), 3),
                "sustainability_score": round(rng.uniform(3.0, 9.5), 1),
                "lifecycle_status": "Active",
                "created_date": created,
                "last_updated": created + timedelta(days=rng.randint(0, 200)),
                "source_system": "SAP_MDGM_v3",
            }
        )
    return pd.DataFrame(rows, columns=PRODUCT_MASTER_COLUMNS)


def _build_affinity_map(products: pd.DataFrame) -> dict[str, str]:
    """Map anchor SKU -> partner SKU for the configured affinity category pairs.

    Picks the first SKU in each level-3 category (deterministic given the product
    ordering) and links the pair in both directions.

    Args:
        products: The generated Product Master.

    Returns:
        A dict where each key/value is a SKU that should co-occur with the other.
    """
    first_sku_by_cat: dict[str, str] = {}
    for cat_l3, group in products.groupby("category_l3", sort=True):
        first_sku_by_cat[cat_l3] = group["sku_id"].iloc[0]

    affinity: dict[str, str] = {}
    for cat_a, cat_b in AFFINITY_CATEGORY_PAIRS:
        sku_a = first_sku_by_cat.get(cat_a)
        sku_b = first_sku_by_cat.get(cat_b)
        if sku_a and sku_b:
            affinity[sku_a] = sku_b
            affinity[sku_b] = sku_a
    return affinity


def _generate_pos_transactions(
    rng: Random,
    products: pd.DataFrame,
    n_transactions: int,
    n_stores: int,
) -> pd.DataFrame:
    """Build the POS Transactions DataFrame (one row per basket line item).

    Baskets are assembled around an anchor SKU; configured affinity partners are
    added with high probability so co-purchase patterns emerge for MBA.

    Args:
        rng: Seeded random generator for reproducibility.
        products: The generated Product Master (for prices and descriptions).
        n_transactions: Number of baskets/transactions to generate.
        n_stores: Number of distinct stores.

    Returns:
        A DataFrame with exactly ``POS_TRANSACTION_COLUMNS``.
    """
    skus: list[str] = products["sku_id"].tolist()
    price_by_sku = dict(zip(products["sku_id"], products["unit_price_msrp"], strict=True))
    desc_by_sku = dict(zip(products["sku_id"], products["product_name"], strict=True))
    affinity = _build_affinity_map(products)
    affinity_anchors: list[str] = sorted(affinity.keys())
    stores = [f"STR-{i:04d}" for i in range(1, n_stores + 1)]

    rows: list[dict] = []
    for t in range(n_transactions):
        # Compose the basket as an ordered, de-duplicated list.
        basket: list[str] = []
        seen: set[str] = set()

        # Anchor: biased toward affinity anchors so pair support is meaningful.
        if affinity_anchors and rng.random() < 0.5:
            anchor = rng.choice(affinity_anchors)
        else:
            anchor = rng.choice(skus)
        _append_unique(basket, seen, anchor)
        if anchor in affinity and rng.random() < 0.7:
            _append_unique(basket, seen, affinity[anchor])
        for _ in range(rng.randint(0, 3)):
            _append_unique(basket, seen, rng.choice(skus))

        # Basket-level attributes.
        identified = rng.random() < 0.6
        customer_id = f"CUST-{rng.randint(100000, 999999)}" if identified else None
        loyalty = (
            f"LOY-{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}" if identified else None
        )
        txn_dt = BASE_TXN_DATETIME + timedelta(minutes=rng.randint(0, 60 * 24 * 30))
        store_id = rng.choice(stores)
        register_id = f"REG-{rng.randint(1, 8):02d}"
        cashier_id = f"EMP-{rng.randint(1000, 9999)}"
        payment_method = rng.choice(PAYMENT_METHODS)

        # Build line items; tender_total is basket-level so we fill it after summing.
        basket_lines: list[dict] = []
        tender_total = 0.0
        for seq, sku in enumerate(basket, start=1):
            quantity = rng.randint(1, 3)
            unit_price = price_by_sku[sku]
            discount = round(unit_price * rng.choice([0.0, 0.0, 0.0, 0.1, 0.2]), 2)
            line_net = round(quantity * unit_price - discount, 2)
            tax = round(line_net * TAX_RATE, 2)
            tender_total += line_net + tax
            basket_lines.append(
                {
                    "transaction_id": f"TXN-2026-{t:06d}",
                    "transaction_datetime": txn_dt,
                    "store_id": store_id,
                    "register_id": register_id,
                    "cashier_id": cashier_id,
                    "customer_id": customer_id,
                    "loyalty_card_number": loyalty,
                    "basket_id": f"BSK-2026-{t:06d}",
                    "line_item_seq": seq,
                    "sku_id": sku,
                    "sku_description": desc_by_sku[sku],
                    "quantity": float(quantity),
                    "unit_price": unit_price,
                    "discount_amount": discount,
                    "promotion_id": (
                        f"PROMO-SUM26-{rng.randint(1, 9):02d}" if discount > 0 else None
                    ),
                    "tax_amount": tax,
                    "payment_method": payment_method,
                    "currency_code": "USD",
                    "tender_total": None,  # set below
                    "source_system": "XSTORE_v22",
                }
            )

        tender_total = round(tender_total, 2)
        for line in basket_lines:
            line["tender_total"] = tender_total
        rows.extend(basket_lines)

    return pd.DataFrame(rows, columns=POS_TRANSACTION_COLUMNS)


def generate(profile: str = "small", seed: int = 42) -> dict[str, pd.DataFrame]:
    """Generate the Sprint 1 data domains in memory (no file I/O).

    Args:
        profile: ``"small"`` (fast, test-friendly) or ``"full"`` (demo volumes).
        seed: Random seed controlling reproducibility.

    Returns:
        A dict with keys ``"product_master"`` and ``"pos_transactions"``.

    Raises:
        ValueError: If ``profile`` is not a known profile.
    """
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile '{profile}'. Valid: {sorted(PROFILES)}")

    config = PROFILES[profile]
    rng = Random(seed)
    fake = Faker()
    Faker.seed(seed)

    products = _generate_product_master(rng, fake, config["n_products"])
    transactions = _generate_pos_transactions(
        rng, products, config["n_transactions"], config["n_stores"]
    )
    return {"product_master": products, "pos_transactions": transactions}


def write_samples(
    frames: dict[str, pd.DataFrame], out_dir: Path
) -> dict[str, Path]:
    """Write generated domains to Parquet under ``out_dir``.

    Args:
        frames: Output of :func:`generate`.
        out_dir: Target directory (created if missing), e.g. ``data/samples``.

    Returns:
        A dict mapping domain name to the written Parquet path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for domain, frame in frames.items():
        path = out_dir / f"{domain}.parquet"
        frame.to_parquet(path, index=False)
        written[domain] = path
    return written


app = typer.Typer(add_completion=False, help="Generate synthetic retail data.")


@app.command()
def main(
    sample: bool = typer.Option(
        False, "--sample", help="Generate the small, fast, test-friendly dataset."
    ),
    seed: int = typer.Option(42, help="Random seed for reproducible output."),
    out_dir: Path = typer.Option(
        Path("data/samples"), help="Directory to write Parquet files into."
    ),
) -> None:
    """Generate synthetic Product Master + POS Transactions and write them to Parquet."""
    profile = "small" if sample else "full"
    logger.info("seed.start", profile=profile, seed=seed, out_dir=str(out_dir))
    frames = generate(profile=profile, seed=seed)
    written = write_samples(frames, out_dir)
    for domain, path in written.items():
        logger.info("seed.written", domain=domain, rows=len(frames[domain]), path=str(path))
    logger.info("seed.done", profile=profile)


if __name__ == "__main__":
    app()
