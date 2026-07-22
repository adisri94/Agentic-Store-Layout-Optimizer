"""Central data access (Layer 4, US-1.2).

The single entry point for reading analytical data (Parquet via DuckDB/pandas) and
for the operational SQLite database. Service code must never open Parquet files or
call ``sqlite3.connect()`` directly — it goes through here (architecture.md §5.2, §6.3).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import duckdb
import pandas as pd

from platform_services.config import settings
from platform_services.exceptions import DataFileNotFoundError, UnknownDomainError

# The six analytical domains defined in data_contract.md. Only a subset exists in
# early sprints, but the set of *valid names* is fixed so typos fail loudly.
KNOWN_DOMAINS: frozenset[str] = frozenset(
    {
        "pos_transactions",
        "product_master",
        "store_master",
        "clickstream",
        "loyalty",
        "vendor_promo",
    }
)


def _samples_dir(data_dir: Path | None = None) -> Path:
    """Return the Parquet samples directory under the active data dir."""
    return (data_dir or settings.data_dir) / "samples"


def load_parquet(domain: str, data_dir: Path | None = None) -> pd.DataFrame:
    """Load a full data domain into a DataFrame.

    Args:
        domain: One of :data:`KNOWN_DOMAINS`.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        The domain's contents as a DataFrame.

    Raises:
        UnknownDomainError: If ``domain`` is not a recognised domain name.
        DataFileNotFoundError: If the domain is valid but its Parquet file is absent.
    """
    if domain not in KNOWN_DOMAINS:
        raise UnknownDomainError(
            f"Unknown data domain '{domain}'. Valid domains: {sorted(KNOWN_DOMAINS)}."
        )
    path = _samples_dir(data_dir) / f"{domain}.parquet"
    if not path.exists():
        raise DataFileNotFoundError(
            f"No Parquet file for domain '{domain}' at {path}. "
            "Generate data first (./tasks.ps1 seed)."
        )
    return pd.read_parquet(path)


def duckdb_query(
    sql: str,
    parameters: list | dict | None = None,
    data_dir: Path | None = None,
) -> pd.DataFrame:
    """Execute SQL over the Parquet sample files.

    Each ``*.parquet`` file under the samples directory is exposed as a view named
    after the file stem (e.g. ``pos_transactions``), so queries can ``SELECT`` from
    domains by name.

    Args:
        sql: SQL to execute.
        parameters: Optional bind parameters passed to DuckDB.
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        The query result as a DataFrame.
    """
    con = duckdb.connect()
    try:
        for parquet_path in sorted(_samples_dir(data_dir).glob("*.parquet")):
            view = parquet_path.stem
            con.execute(
                f'CREATE OR REPLACE VIEW "{view}" AS '
                f"SELECT * FROM read_parquet('{parquet_path.as_posix()}')"
            )
        result = con.execute(sql, parameters) if parameters else con.execute(sql)
        return result.df()
    finally:
        con.close()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create the minimal operational schema if it does not yet exist."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO schema_meta (key, value) VALUES ('schema_version', '1')"
    )
    conn.commit()


def get_sqlite_conn(data_dir: Path | None = None) -> sqlite3.Connection:
    """Return a connection to the operational SQLite DB (``app.db``).

    Auto-creates the data directory and the minimal schema on first call.

    Args:
        data_dir: Override the data root (defaults to ``settings.data_dir``).

    Returns:
        An open SQLite connection.
    """
    root = data_dir or settings.data_dir
    root.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(root / "app.db")
    _ensure_schema(conn)
    return conn
