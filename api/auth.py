"""API authentication (D-029).

Sprint 1 uses a simple ``X-API-Key`` header check against the configured key. Vendor
scope isolation (``X-Vendor-Id``) arrives with the vendor module in Sprint 5.
"""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from platform_services.config import settings


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """FastAPI dependency: require a valid ``X-API-Key`` header.

    Args:
        x_api_key: Value of the ``X-API-Key`` request header.

    Raises:
        HTTPException: 401 if the header is missing or does not match the configured key.
    """
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
