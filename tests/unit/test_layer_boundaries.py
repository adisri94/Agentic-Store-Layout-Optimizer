"""Structural test enforcing layer boundaries (US-1.2 TC-1.2.4).

Services (Layer 3) must access data only through ``platform_services.data_access`` —
they must never open Parquet files or SQLite connections directly (architecture.md
§3.2, §5.2, §6.3). This scans service source for forbidden direct-access patterns.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "services"

FORBIDDEN_PATTERNS = [
    "sqlite3.connect(",
    "read_parquet(",
    "pd.read_parquet(",
    "pyarrow",
]


def test_services_do_not_bypass_data_access():
    """No module under services/ performs direct Parquet/SQLite access."""
    if not SERVICES_DIR.exists():
        return  # No services yet (early Sprint 1); nothing to check.

    offenders: list[str] = []
    for py_file in SERVICES_DIR.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                offenders.append(f"{py_file.relative_to(REPO_ROOT)}: '{pattern}'")

    assert not offenders, "Services must use platform_services.data_access:\n" + "\n".join(
        offenders
    )
