"""Recommendations endpoint (US-1.8)."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from api.auth import verify_api_key
from api.schemas import GovernedRecommendation, RecommendationRequest
from services.affinity_optimization import (
    get_recommendations,
    get_recommendations_for_transactions,
    missing_pos_columns,
)

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


@router.post(
    "/recommendations/upload",
    response_model=list[GovernedRecommendation],
    dependencies=[Depends(verify_api_key)],
)
def upload_recommendations(
    file: UploadFile = File(...), top_k: int = 20
) -> list[GovernedRecommendation]:
    """Generate governed recommendations from an uploaded POS transactions CSV (US-1.12).

    The file is validated against the full POS schema, processed in memory (never
    persisted), and every recommendation is governed.

    Args:
        file: An uploaded CSV of POS transactions.
        top_k: Maximum number of recommendations to return.

    Returns:
        Governed recommendations mined from the uploaded data.

    Raises:
        HTTPException: 422 if the file can't be parsed or is missing mandatory columns.
    """
    try:
        transactions = pd.read_csv(file.file)
    except Exception as exc:  # noqa: BLE001 - surface any parse failure as a 422
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not read the uploaded CSV: {exc}",
        ) from exc

    missing = missing_pos_columns(transactions.columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Uploaded file is missing required POS columns: {missing}",
        )

    return get_recommendations_for_transactions(transactions, top_k=top_k)
