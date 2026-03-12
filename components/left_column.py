"""Left column: PDF upload (process file) and Chat."""
from __future__ import annotations

import streamlit as st

from datastore import KEY_SELECTED_ID, KEY_UPLOADS, KEY_UPLOADER_RESET
from state import get_current_upload
from pdf_utils import add_upload
from components.chat_tab import render_chat_tab


def render_left_column() -> None:
    """Render the app sidebar. Session block, then Upload | Chat tabs."""
    with st.sidebar:
        if st.session_state[KEY_UPLOADS]:
            uploads = st.session_state[KEY_UPLOADS]
            selected_id = st.session_state[KEY_SELECTED_ID]
            idx = st.selectbox(
                "Select PDF",
                range(len(uploads)),
                format_func=lambda i: f"{uploads[i]['name']} ({uploads[i]['num_pages']} p.)",
                index=next((i for i, u in enumerate(uploads) if u["id"] == selected_id), 0),
            )
            st.session_state[KEY_SELECTED_ID] = uploads[idx]["id"]

        tab_upload, tab_chat = st.tabs(["Upload", "Chat"])
        with tab_upload:
            uploader_key = f"pdf_uploader_{st.session_state[KEY_UPLOADER_RESET]}"
            uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], key=uploader_key)
            if uploaded_file is not None:
                if st.button("Process file", key="btn_process_file"):
                    add_upload(st.session_state, uploaded_file.name, uploaded_file.getvalue())
                    st.session_state[KEY_UPLOADER_RESET] += 1  # clear uploader so x is gone
                    st.rerun()

        with tab_chat:
            render_chat_tab(get_current_upload())
