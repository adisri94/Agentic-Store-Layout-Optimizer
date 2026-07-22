"""Layer 1 — Streamlit UI (Category Manager and Admin/Governance modes).

The UI talks to the system only over HTTP via the API layer (L1 -> L2). It must
never import the services layer directly (architecture.md §3.2).
"""
