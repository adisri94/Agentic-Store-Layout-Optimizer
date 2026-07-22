"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from data.seed import generate, write_samples


@pytest.fixture
def seeded_data_dir(tmp_path: Path) -> Path:
    """Write the small deterministic dataset into a temp data dir and return it.

    The returned path is a data root containing ``samples/*.parquet``, suitable for
    passing as ``data_dir`` to ``platform_services.data_access`` functions.
    """
    frames = generate(profile="small", seed=42)
    write_samples(frames, tmp_path / "samples")
    return tmp_path
