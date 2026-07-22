"""FastAPI application entry point (Layer 2).

Wires routes, authentication, and a standard error envelope. All error responses
follow ``{"error": {"code": ..., "message": ...}}`` (architecture.md §7.4).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.routes import audit, health, recommendations
from platform_services.config import settings

logger = structlog.get_logger(__name__)

_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    422: "validation_error",
    500: "internal_error",
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hook — logs the active mode (architecture.md §13.2)."""
    logger.info(
        "api.startup",
        data_dir=str(settings.data_dir),
        governance_enabled=settings.enable_governance,
        llm_mocked=settings.mock_llm or not settings.anthropic_api_key,
    )
    yield
    logger.info("api.shutdown")


app = FastAPI(title="Store Layout Optimizer API", version="0.1.0", lifespan=lifespan)


def _error_response(status_code: int, message: str) -> JSONResponse:
    """Build a standard error-envelope response."""
    code = _STATUS_CODES.get(status_code, "error")
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Wrap HTTP exceptions in the standard error envelope."""
    return _error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return 422 with the standard error envelope for request validation errors."""
    message = "; ".join(
        f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    return _error_response(422, message or "Request validation failed.")


app.include_router(health.router)
app.include_router(recommendations.router)
app.include_router(audit.router)
