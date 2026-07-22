"""Recommendations endpoint (US-1.8)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.auth import verify_api_key
from api.schemas import GovernedRecommendation, RecommendationRequest
from services.affinity_optimization import get_recommendations

router = APIRouter(prefix="/api/v1", tags=["recommendations"])


@router.post(
    "/recommendations",
    response_model=list[GovernedRecommendation],
    dependencies=[Depends(verify_api_key)],
)
def post_recommendations(request: RecommendationRequest) -> list[GovernedRecommendation]:
    """Return governed placement recommendations for a store/category.

    Args:
        request: The recommendation request (store_id, optional category, top_k).

    Returns:
        A list of governed recommendations (may be empty).
    """
    return get_recommendations(
        store_id=request.store_id,
        category=request.category,
        top_k=request.top_k,
    )
