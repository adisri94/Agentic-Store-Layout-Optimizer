"""HTTP client the UI uses to talk to the API (L1 -> L2 only).

All UI/system interaction goes through these functions; the UI never imports the
services layer directly.
"""

from __future__ import annotations

import requests

from platform_services.config import settings

_TIMEOUT_SECONDS = 30


def _headers() -> dict[str, str]:
    return {"X-API-Key": settings.api_key}


def fetch_recommendations(
    store_id: str, category: str | None = None, top_k: int = 20
) -> list[dict]:
    """POST /api/v1/recommendations and return the governed recommendations."""
    response = requests.post(
        f"{settings.api_base_url}/api/v1/recommendations",
        json={"store_id": store_id, "category": category, "top_k": top_k},
        headers=_headers(),
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def fetch_products() -> list[dict]:
    """GET /api/v1/products and return the product catalog."""
    response = requests.get(
        f"{settings.api_base_url}/api/v1/products",
        headers=_headers(),
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def upload_transactions(filename: str, content: bytes, top_k: int = 20) -> list[dict]:
    """POST an uploaded transactions CSV and return governed recommendations.

    Args:
        filename: The uploaded file's name.
        content: Raw CSV bytes.
        top_k: Maximum number of recommendations to return.

    Returns:
        Governed recommendations parsed from the API response.

    Raises:
        requests.HTTPError: If the API rejects the file (e.g. 422 for a bad schema).
    """
    response = requests.post(
        f"{settings.api_base_url}/api/v1/recommendations/upload",
        params={"top_k": top_k},
        files={"file": (filename, content, "text/csv")},
        headers=_headers(),
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def fetch_audit_log(limit: int = 100) -> list[dict]:
    """GET /api/v1/audit/log and return recent audit entries."""
    response = requests.get(
        f"{settings.api_base_url}/api/v1/audit/log",
        params={"limit": limit},
        headers=_headers(),
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def health() -> bool:
    """Return True if the API health endpoint is reachable and OK."""
    try:
        response = requests.get(f"{settings.api_base_url}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
