"""Unit tests for the data-access layer (US-1.2).

Covers TC-1.2.1 (load_parquet), TC-1.2.2 (duckdb_query), TC-1.2.3 (unknown domain),
and the SQLite connection/schema behaviour (AC3).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from platform_services.data_access import (
    duckdb_query,
    get_sqlite_conn,
    load_parquet,
)
from platform_services.exceptions import DataFileNotFoundError, UnknownDomainError


def test_load_parquet_returns_populated_frame(seeded_data_dir: Path):
    """TC-1.2.1 — load_parquet returns a non-empty DataFrame with expected columns."""
    products = load_parquet("product_master", data_dir=seeded_data_dir)
    assert not products.empty
    assert "sku_id" in products.columns
    assert "category_l1" in products.columns


def test_duckdb_query_counts_rows(seeded_data_dir: Path):
    """TC-1.2.2 — duckdb_query over Parquet returns the correct row count."""
    expected = len(load_parquet("pos_transactions", data_dir=seeded_data_dir))
    result = duckdb_query(
        "SELECT COUNT(*) AS n FROM pos_transactions", data_dir=seeded_data_dir
    )
    assert int(result["n"].iloc[0]) == expected


def test_unknown_domain_raises(seeded_data_dir: Path):
    """TC-1.2.3 — an unknown domain raises the typed UnknownDomainError."""
    with pytest.raises(UnknownDomainError, match="Unknown data domain"):
        load_parquet("not_a_domain", data_dir=seeded_data_dir)


def test_known_domain_missing_file_raises(tmp_path: Path):
    """A valid domain with no generated file raises DataFileNotFoundError."""
    (tmp_path / "samples").mkdir()
    with pytest.raises(DataFileNotFoundError, match="seed"):
        load_parquet("clickstream", data_dir=tmp_path)


def test_get_sqlite_conn_creates_schema(tmp_path: Path):
    """AC3 — get_sqlite_conn auto-creates app.db and the minimal schema."""
    conn = get_sqlite_conn(data_dir=tmp_path)
    try:
        rows = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchall()
        assert rows == [("1",)]
        assert (tmp_path / "app.db").exists()
    finally:
        conn.close()
