"""Analyzed PDF tab: summary images from server (page range only, no text)."""
from __future__ import annotations

from typing import Any

import streamlit as st

from datastore import (
    KEY_CONVERTED_IMAGES,
    KEY_FROM_PAGE,
    KEY_SCROLL_TO_PAGE,
    KEY_TEXT_OUTPUT_ONLY,
    KEY_TO_PAGE,
)


def render_converted_tab(current: dict[str, Any]) -> None:
    """Render the Analyzed PDF tab: one summary image per page in the selected range (from_page–to_page)."""
    if st.session_state.get(KEY_TEXT_OUTPUT_ONLY, True):
        return

    pdf_id = current.get("id") or ""
    num_pages = current.get("num_pages") or 0
    from_page = max(1, st.session_state.get(KEY_FROM_PAGE, 1))
    to_page = st.session_state.get(KEY_TO_PAGE, 20)
    end_page = min(to_page, num_pages) if num_pages else to_page
    start_page = min(from_page, end_page) if end_page else from_page
    range_len = max(0, end_page - start_page + 1)

    page_images: list[bytes] = (
        st.session_state.get(KEY_CONVERTED_IMAGES) or {}
    ).get(pdf_id, [])
    scroll_to = st.session_state.get(KEY_SCROLL_TO_PAGE)

    if range_len == 0:
        st.caption("No page range. Set From/To in the Upload tab and run Process file.")
        return

    st.caption(f"Summary images for pages **{start_page}–{end_page}** ({range_len} page{'s' if range_len != 1 else ''}).")
    for i in range(range_len):
        page_num = start_page + i
        with st.expander(f"Page {page_num}", expanded=(scroll_to == page_num)):
            if i < len(page_images) and page_images[i]:
                st.image(page_images[i], use_container_width=True)
            else:
                st.caption("_No summary image for this page yet._")
