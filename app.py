"""
PDF Host & Preview: top bar (session + host), column 1 = upload + chat, column 2 = preview + text.
"""
import streamlit as st
from streamlit_adjustable_columns import adjustable_columns


from config import is_dev
from datastore import KEY_COLUMN_RATIO_LEFT, KEY_COLUMN_RATIO_RIGHT, KEY_SCROLL_TO_PAGE
from state import ensure_session_state, get_current_upload, clear_scroll_target
from components import render_top_bar, render_left_column, render_preview_tab, render_converted_tab

st.set_page_config(
    page_title="PDF Host & Preview",
    layout="wide",
    initial_sidebar_state="collapsed",
)
ensure_session_state()

# --- Top bar (full width): session + host info ---
render_top_bar()
st.divider()

# --- Two columns (adjustable if streamlit-adjustable-columns is installed) ---
ratio_left = st.session_state.get(KEY_COLUMN_RATIO_LEFT, 1)
ratio_right = st.session_state.get(KEY_COLUMN_RATIO_RIGHT, 2)
col_left, col_right = adjustable_columns(
    [ratio_left, ratio_right],
    labels=["Upload & Chat", "Preview"],
    gap="medium",
    key="main_columns",
)

# Left column: Upload (process file) + Chat
with col_left:
    render_left_column()

# Right column: PDF preview and converted text
with col_right:
    current = get_current_upload()
    if current is None:
        st.info("Upload a PDF in the left column to get started. Your data stays in this session only.")
    else:
        # One line: PDF name + Preview PDF button
        r1, r2 = st.columns([2, 1])
        with r1:
            st.markdown(f"### 📄 {current['name']}")
        with r2:
            if st.button("Preview PDF", type="primary"):
                st.session_state[KEY_SCROLL_TO_PAGE] = None
                st.rerun()

        # Tabs: Preview PDF | Converted (text)
        tab_preview, tab_converted = st.tabs(["Preview PDF", "Converted (text)"])
        with tab_preview:
            render_preview_tab(current)
        with tab_converted:
            render_converted_tab(current)

        clear_scroll_target()
