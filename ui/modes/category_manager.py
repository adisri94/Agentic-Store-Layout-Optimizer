"""Category Manager mode (US-1.10).

Lets a category manager request recommendations and inspect the plain-English
rationale and policy warnings behind each one.
"""

from __future__ import annotations

import requests
import streamlit as st

from ui.api_client import fetch_recommendations
from ui.formatting import recommendation_display_row


def render() -> None:
    """Render the Category Manager view."""
    st.header("Category Manager — Placement Recommendations")
    st.caption(
        "Recommendations are mined from POS baskets and governed (#9): each carries "
        "a plain-English rationale and any policy warnings."
    )

    col1, col2, col3 = st.columns(3)
    store_id = col1.text_input("Store ID", value="STR-0001")
    category = col2.text_input("Category (optional)", value="")
    top_k = col3.slider("How many", min_value=1, max_value=20, value=10)

    if not st.button("Get Recommendations"):
        return

    try:
        recommendations = fetch_recommendations(
            store_id=store_id,
            category=category or None,
            top_k=top_k,
        )
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return

    if not recommendations:
        st.warning("No recommendations for that selection.")
        return

    st.dataframe(
        [recommendation_display_row(rec) for rec in recommendations],
        use_container_width=True,
    )

    st.subheader("Why these recommendations?")
    for rec in recommendations:
        with st.expander(f"{rec['sku_a']} → {rec['sku_b']}  (lift {rec['lift']:.2f})"):
            st.write(rec["rationale"])
            warnings = rec.get("policy_warnings", [])
            if warnings:
                st.warning("Policy warnings:\n\n" + "\n".join(f"- {w}" for w in warnings))
            else:
                st.success("No policy warnings.")
            st.caption(f"Audit id: {rec['audit_id']}")
