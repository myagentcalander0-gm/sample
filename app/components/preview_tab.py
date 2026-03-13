"""Preview PDF tab with scroll-to-page support."""
from __future__ import annotations

from typing import Any

import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from datastore import KEY_SCROLL_TO_PAGE


def render_preview_tab(current: dict[str, Any]) -> None:
    """Render the PDF preview tab."""
    st.caption("Click «Go to page» in the Converted tab to zoom the PDF to that page.")
    scroll_to = st.session_state.get(KEY_SCROLL_TO_PAGE)
    pdf_viewer(
        current["data"],
        width=800,
        height=900,
        scroll_to_page=scroll_to,
        show_page_separator=True,
    )
