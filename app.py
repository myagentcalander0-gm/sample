"""
PDF Host & Preview: top bar, then full-width resizable left | right columns.
"""
import streamlit as st
from streamlit_adjustable_columns import adjustable_columns

from datastore import KEY_SCROLL_TO_PAGE
from state import ensure_session_state, get_current_upload, clear_scroll_target
from components import render_top_bar, render_left_column, render_preview_tab, render_converted_tab

st.set_page_config(
    page_title="PDF Host & Preview",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ensure_session_state()

# Top bar only (session + backend + Refresh)
render_top_bar()
st.divider()

# Whole area below top bar is resizable: drag the handle between left and right

render_left_column()

current = get_current_upload()
if current is None:
    st.markdown("### Preview")
    st.info("Upload a PDF in the left column to get started. Your data stays in this session only.")
else:
    st.markdown(f"### 📄 {current['name']}")
    if st.button("Preview PDF", type="primary"):
        st.session_state[KEY_SCROLL_TO_PAGE] = None
        st.rerun()

    tab_preview, tab_converted = st.tabs(["Preview PDF", "Converted (text)"])
    with tab_preview:
        render_preview_tab(current)
    with tab_converted:
        render_converted_tab(current)

    clear_scroll_target()
