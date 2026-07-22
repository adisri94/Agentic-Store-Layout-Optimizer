"""Category Manager mode (US-1.10, refined per D-035).

Lets a category manager request recommendations (from seeded store data or an
uploaded transactions file) and inspect the plain-English rationale and policy
warnings behind each one. Category is a dropdown (US-1.13) and results show SKU
names alongside codes (US-1.14).
"""

from __future__ import annotations

from pathlib import Path

import requests
import streamlit as st

from ui.api_client import fetch_products, fetch_recommendations, upload_transactions
from ui.formatting import (
    ALL_CATEGORIES,
    category_options,
    name_map,
    recommendation_display_row,
    sku_label,
)

_SAMPLE_CSV = Path(__file__).resolve().parent.parent / "sample_transactions.csv"


def _render_results(recommendations: list[dict], names: dict[str, str]) -> None:
    """Render the results table and the per-recommendation rationale panels."""
    if not recommendations:
        st.warning("No recommendations for that selection.")
        return

    st.dataframe(
        [recommendation_display_row(rec, names) for rec in recommendations],
        use_container_width=True,
    )

    st.subheader("Why these recommendations?")
    for rec in recommendations:
        label = f"{sku_label(rec['sku_a'], names)}  →  {sku_label(rec['sku_b'], names)}"
        with st.expander(f"{label}   (lift {rec['lift']:.2f})"):
            st.write(rec["rationale"])
            warnings = rec.get("policy_warnings", [])
            if warnings:
                st.warning("Policy warnings:\n\n" + "\n".join(f"- {w}" for w in warnings))
            else:
                st.success("No policy warnings.")
            st.caption(f"Audit id: {rec['audit_id']}")


def render() -> None:
    """Render the Category Manager view."""
    st.header("Category Manager — Placement Recommendations")
    st.caption(
        "Recommendations are mined from POS baskets and governed (#9): each carries "
        "a plain-English rationale and any policy warnings."
    )

    try:
        products = fetch_products()
    except requests.RequestException as exc:
        st.error(f"Could not reach the API: {exc}")
        return

    names = name_map(products)

    col1, col2, col3 = st.columns(3)
    store_id = col1.text_input("Store ID", value="STR-0001")
    category = col2.selectbox("Category", category_options(products))
    top_k = col3.slider("How many", min_value=1, max_value=20, value=10)

    if st.button("Get recommendations"):
        try:
            recommendations = fetch_recommendations(
                store_id=store_id,
                category=None if category == ALL_CATEGORIES else category,
                top_k=top_k,
            )
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            _render_results(recommendations, names)

    st.divider()

    st.subheader("Use your own data")
    st.caption(
        "Upload a POS transactions CSV to prove the tool computes on real data. "
        "The file is validated against the full POS schema and processed in memory "
        "(never saved)."
    )
    if _SAMPLE_CSV.exists():
        st.download_button(
            "Download sample template",
            data=_SAMPLE_CSV.read_bytes(),
            file_name="sample_transactions.csv",
            mime="text/csv",
        )
    uploaded = st.file_uploader("POS transactions CSV", type=["csv"])
    if uploaded is not None and st.button("Analyze uploaded data"):
        try:
            recommendations = upload_transactions(
                filename=uploaded.name, content=uploaded.getvalue(), top_k=top_k
            )
        except requests.HTTPError as exc:
            detail = ""
            try:
                detail = exc.response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = str(exc)
            st.error(f"Upload rejected: {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach the API: {exc}")
        else:
            st.success(f"Analyzed uploaded data — {len(recommendations)} recommendation(s).")
            _render_results(recommendations, names)
