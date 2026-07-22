"""Layer 4 — Local Platform Services.

Shared, infrastructure-facing utilities used by the Layer 3 services: configuration,
data access, and (in later sprints) the LLM client, vector store, and graph store.

Named ``platform_services`` rather than ``platform`` to avoid shadowing Python's
standard-library ``platform`` module (see decision_log.md D-033).
"""
