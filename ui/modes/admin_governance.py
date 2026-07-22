"""Admin / Governance mode (US-1.11).

Displays the append-only audit log so a Data Steward can demonstrate that every
recommendation was governed and recorded.
"""

from __future__ import annotations

import requests
import streamlit as st

from ui.api_client import fetch_audit_log
from ui.formatting import audit_display_row


def render() -> None:
    """Render the Admin / Governance view."""
    st.header("Admin / Governance — Audit Log")
    st.caption(
        "Every recommendation shown to a user is intercepted by the governance layer "
        "and written here — a permanent, append-only record."
    )

    limit = st.slider("Entries to show", min_value=10, max_value=500, value=100, step=10)

    try:
        entries = fetch_audit_log(limit=limit)
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return

    if not entries:
        st.info("No audit entries yet. Generate recommendations in Category Manager mode.")
        return

    st.metric("Audit entries", len(entries))
    st.dataframe([audit_display_row(entry) for entry in entries], use_container_width=True)
