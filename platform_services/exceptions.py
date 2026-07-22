"""Typed exceptions for the platform layer."""

from __future__ import annotations


class DataAccessError(Exception):
    """Base class for all data-access errors."""


class UnknownDomainError(DataAccessError):
    """Raised when a data domain name is not recognised."""


class DataFileNotFoundError(DataAccessError):
    """Raised when a known domain's Parquet file is missing (e.g. seed not run)."""
