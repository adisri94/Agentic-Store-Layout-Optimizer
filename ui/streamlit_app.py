"""Streamlit entry point — the Store Layout Optimizer demo UI.

Run with: ``uv run streamlit run ui/streamlit_app.py`` (or ``./tasks.ps1 demo``).
Sprint 1 ships two of the three modes: Category Manager and Admin/Governance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this file by path, which puts the ui/ folder (not the project
# root) on sys.path — so the `ui` package can't be imported. Add the repo root
# before importing anything from `ui`.
_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from ui.api_client import health  # noqa: E402
from ui.modes import admin_governance, category_manager  # noqa: E402


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
