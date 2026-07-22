"""Product-catalog endpoint (US-1.13 / US-1.14).

Serves the minimal product list the UI uses for the category dropdown and SKU-name
lookup.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.auth import verify_api_key
from api.schemas import ProductSummary
from services.affinity_optimization import get_product_catalog

router = APIRouter(prefix="/api/v1", tags=["products"])


@router.get(
    "/products",
    response_model=list[ProductSummary],
    dependencies=[Depends(verify_api_key)],
)
def list_products() -> list[dict]:
    """Return the product catalog (sku_id, product_name, category_l1)."""
    return get_product_catalog()
