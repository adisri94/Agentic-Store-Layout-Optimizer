"""API integration tests (US-1.8, US-1.9) via FastAPI TestClient.

Uses a temp seeded data dir (no live LLM). Covers TC-1.8.1..1.8.4 and TC-1.9.1..1.9.3.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from platform_services.config import settings

API_KEY = "demo-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def client(seeded_data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """A TestClient wired to a temp seeded data dir."""
    monkeypatch.setattr(settings, "data_dir", seeded_data_dir)
    monkeypatch.setattr(settings, "api_key", API_KEY)
    from api.main import app

    return TestClient(app)


def test_recommendations_happy_path(client: TestClient):
    """TC-1.8.1 — valid key + body returns governed recommendations."""
    resp = client.post(
        "/api/v1/recommendations", json={"store_id": "STR-0001", "top_k": 10}, headers=HEADERS
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list) and body, "expected at least one recommendation"
    first = body[0]
    assert "rationale" in first and first["rationale"]
    assert "audit_id" in first and first["audit_id"]


def test_recommendations_requires_api_key(client: TestClient):
    """TC-1.8.2 — a missing API key is rejected with 401."""
    resp = client.post("/api/v1/recommendations", json={"store_id": "STR-0001"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


def test_recommendations_validation_error(client: TestClient):
    """TC-1.8.3 — a missing store_id yields 422 in the standard error shape."""
    resp = client.post("/api/v1/recommendations", json={"top_k": 5}, headers=HEADERS)
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


def test_health(client: TestClient):
    """TC-1.8.4 — health endpoint returns 200."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_audit_log_lists_entries(client: TestClient):
    """TC-1.9.1 — after generating recs, the audit log lists at least as many."""
    recs = client.post(
        "/api/v1/recommendations", json={"store_id": "STR-0001", "top_k": 10}, headers=HEADERS
    ).json()
    resp = client.get("/api/v1/audit/log?limit=1000", headers=HEADERS)
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) >= len(recs) >= 1


def test_audit_for_recommendation(client: TestClient):
    """TC-1.9.2 — audit-by-id returns the entry; unknown id returns 404."""
    recs = client.post(
        "/api/v1/recommendations", json={"store_id": "STR-0001", "top_k": 5}, headers=HEADERS
    ).json()
    rec_id = recs[0]["recommendation_id"]

    ok = client.get(f"/api/v1/audit/{rec_id}", headers=HEADERS)
    assert ok.status_code == 200
    assert all(e["recommendation_id"] == rec_id for e in ok.json())

    missing = client.get("/api/v1/audit/rec-does-not-exist", headers=HEADERS)
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"


def test_audit_requires_api_key(client: TestClient):
    """TC-1.9.3 — audit endpoints require the API key."""
    assert client.get("/api/v1/audit/log").status_code == 401


def test_products_endpoint(client: TestClient):
    """TC-1.13.1 — /products returns entries with sku_id, product_name, category_l1."""
    resp = client.get("/api/v1/products", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body
    assert {"sku_id", "product_name", "category_l1"} <= set(body[0])


def _pos_csv(seeded_data_dir: Path) -> bytes:
    """Return the seeded POS transactions as CSV bytes."""
    import pandas as pd

    frame = pd.read_parquet(seeded_data_dir / "samples" / "pos_transactions.parquet")
    return frame.to_csv(index=False).encode("utf-8")


def test_upload_happy_path(client: TestClient, seeded_data_dir: Path):
    """TC-1.12.1 — a valid POS CSV upload returns governed recommendations."""
    resp = client.post(
        "/api/v1/recommendations/upload",
        params={"top_k": 10},
        files={"file": ("txns.csv", _pos_csv(seeded_data_dir), "text/csv")},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body and "rationale" in body[0] and body[0]["audit_id"]


def test_upload_missing_columns_rejected(client: TestClient):
    """TC-1.12.2 — a CSV missing a mandatory column returns 422 (standard shape)."""
    bad = b"sku_id,quantity\nSKU-1,1\nSKU-2,1\n"
    resp = client.post(
        "/api/v1/recommendations/upload",
        files={"file": ("bad.csv", bad, "text/csv")},
        headers=HEADERS,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"
    assert "basket_id" in resp.json()["error"]["message"]


def test_upload_does_not_persist_parquet(client: TestClient, seeded_data_dir: Path):
    """TC-1.12.3 — an upload does not create/modify any Parquet sample (in-memory only)."""
    samples = seeded_data_dir / "samples"
    before = {p.name for p in samples.glob("*.parquet")}
    client.post(
        "/api/v1/recommendations/upload",
        files={"file": ("txns.csv", _pos_csv(seeded_data_dir), "text/csv")},
        headers=HEADERS,
    )
    after = {p.name for p in samples.glob("*.parquet")}
    assert before == after
