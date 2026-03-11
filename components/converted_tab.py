"""Converted text tab: per-page text and go-to-page buttons."""
from __future__ import annotations

from typing import Any

import streamlit as st

from datastore import KEY_SCROLL_TO_PAGE


def render_converted_tab(current: dict[str, Any]) -> None:
    """Render the converted text tab with download and go-to-page."""
    full_text = "\n\n--- Page break ---\n\n".join(
        f"## Page {i + 1}\n\n{t}" for i, t in enumerate(current["text_by_page"])
    )
    st.download_button(
        "Download converted text",
        data=full_text,
        file_name=current["name"].rsplit(".", 1)[0] + "_converted.txt",
        mime="text/plain",
        key="dl_converted",
    )
    st.divider()
    scroll_to = st.session_state.get(KEY_SCROLL_TO_PAGE)
    for i, text in enumerate(current["text_by_page"]):
        page_num = i + 1
        with st.expander(f"Page {page_num}", expanded=(scroll_to == page_num)):
            if st.button(f"Go to page {page_num} in PDF", key=f"goto_{current['id']}_{page_num}"):
                st.session_state[KEY_SCROLL_TO_PAGE] = page_num
                st.rerun()
            st.text_area(
                "",
                value=text or "(no text)",
                height=120,
                key=f"text_{current['id']}_{i}",
                disabled=True,
            )
