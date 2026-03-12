"""Converted text tab: per-page text and converted images (when Text Output Only is off)."""
from __future__ import annotations

from typing import Any

import streamlit as st

from datastore import KEY_CONVERTED_IMAGES, KEY_SCROLL_TO_PAGE


def render_converted_tab(current: dict[str, Any]) -> None:
    """Render the converted text tab with download, per-page text, and images when available."""
    full_text = "\n\n--- Page break ---\n\n".join(
        f"## Page {i + 1}\n\n{t}" for i, t in enumerate(current["text_by_page"])
    )
    st.download_button(
        "Download converted PDF",
        data=full_text,
        file_name=current["name"].rsplit(".", 1)[0] + "_converted.txt",
        mime="text/plain",
        key="dl_converted",
    )
    st.divider()
    pdf_id = current.get("id") or ""
    page_images: list[bytes] = (
        st.session_state.get(KEY_CONVERTED_IMAGES) or {}
    ).get(pdf_id, [])
    scroll_to = st.session_state.get(KEY_SCROLL_TO_PAGE)
    for i, text in enumerate(current["text_by_page"]):
        page_num = i + 1
        with st.expander(f"Page {page_num}", expanded=(scroll_to == page_num)):
            if i < len(page_images) and page_images[i]:
                st.image(page_images[i], use_container_width=True)
            st.text_area(
                "",
                value=text or "(no text)",
                height=120,
                key=f"text_{current['id']}_{i}",
                disabled=True,
            )
