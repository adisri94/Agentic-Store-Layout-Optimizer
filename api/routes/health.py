"""Health / liveness endpoint."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Liveness probe.

    Returns:
        A small payload indicating the service is up.
    """
    return {"status": "ok", "service": "store-layout-optimizer"}
