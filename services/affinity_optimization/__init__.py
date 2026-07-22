"""Service 1 — Affinity & Optimization.

Covers the MBA core plus enhancements #1, #4, #5, #6. Sprint 1 implements the
baseline Market Basket Analysis engine (``mba_core``) and the governed public
entry point :func:`get_recommendations` (US-1.7), which routes every recommendation
through the governance service before returning.
"""

from services.affinity_optimization.service import get_recommendations

__all__ = ["get_recommendations"]
