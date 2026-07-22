"""Streamlit entry point — the Store Layout Optimizer demo UI.

Run with: ``uv run streamlit run ui/streamlit_app.py`` (or ``./tasks.ps1 demo``).
Sprint 1 ships two of the three modes: Category Manager and Admin/Governance.
"""

from __future__ import annotations

import streamlit as st

from ui.api_client import health
from ui.modes import admin_governance, category_manager


def main() -> None:
    """Render the app shell and dispatch to the selected mode."""
    st.set_page_config(page_title="Store Layout Optimizer", layout="wide")
    st.sidebar.title("Store Layout Optimizer")
    st.sidebar.caption("Agentic Shelf Intelligence Platform — Sprint 1 demo")

    if health():
        st.sidebar.success("API: connected")
    else:
        st.sidebar.error("API: unreachable — start it with ./tasks.ps1 demo")

    mode = st.sidebar.radio("Mode", ["Category Manager", "Admin / Governance"])

    if mode == "Category Manager":
        category_manager.render()
    else:
        admin_governance.render()


main()
