"""Audit-log endpoints (US-1.9)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.auth import verify_api_key
from api.schemas import AuditEntry
from services.governance import get_audit_log

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/log", response_model=list[AuditEntry], dependencies=[Depends(verify_api_key)])
def audit_log(limit: int = 100) -> list[AuditEntry]:
    """Return recent audit entries, newest first.

    Args:
        limit: Maximum number of entries to return.

    Returns:
        Recent audit entries.
    """
    return get_audit_log(limit=limit)


@router.get(
    "/{recommendation_id}",
    response_model=list[AuditEntry],
    dependencies=[Depends(verify_api_key)],
)
def audit_for_recommendation(recommendation_id: str) -> list[AuditEntry]:
    """Return the audit entries for a single recommendation.

    Args:
        recommendation_id: The recommendation id to look up.

    Returns:
        Matching audit entries.

    Raises:
        HTTPException: 404 if no audit entries exist for the id.
    """
    entries = [
        entry
        for entry in get_audit_log(limit=100_000)
        if entry.recommendation_id == recommendation_id
    ]
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audit entries for recommendation '{recommendation_id}'.",
        )
    return entries
