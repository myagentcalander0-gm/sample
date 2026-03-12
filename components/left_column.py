"""Left column: PDF upload (process file) and Chat."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from datastore import (
    KEY_FROM_PAGE,
    KEY_GO_TO_CHAT,
    KEY_LEFT_TAB,
    KEY_PROMPT_EDITOR,
    KEY_SELECTED_ID,
    KEY_TEXT_OUTPUT_ONLY,
    KEY_TO_PAGE,
    KEY_UPLOADS,
    KEY_UPLOADER_RESET,
)
from state import get_current_upload, get_or_create_conversation, get_backend_base_url
from pdf_utils import add_upload
from components.chat_tab import render_chat_tab
from services.chat_api import pdf_detail_from_external
from services.langfuse_prompt import get_prompt_from_langfuse


def _load_default_prompt_from_file() -> str:
    """Load prompt content from prompts/default.md (relative to project root). Returns "" if missing or on error."""
    try:
        path = Path(__file__).resolve().parent.parent / "prompts" / "default.md"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""


def render_left_column() -> None:
    """Render the app sidebar. Session block, then Upload | Chat tabs."""
    with st.sidebar:
        if st.session_state[KEY_UPLOADS]:
            uploads = st.session_state[KEY_UPLOADS]
            selected_id = st.session_state.get(KEY_SELECTED_ID)
            default_idx = next((i for i, u in enumerate(uploads) if u["id"] == selected_id), 0)
            # No widget key: use index= so selection is driven by KEY_SELECTED_ID; unique label per doc so same file twice = two options
            idx = st.selectbox(
                "Select PDF",
                range(len(uploads)),
                format_func=lambda i: f"{uploads[i]['name']} ({uploads[i]['num_pages']} p.) · {uploads[i]['id'][:8]}",
                index=default_idx,
            )
            st.session_state[KEY_SELECTED_ID] = uploads[idx]["id"]

        # Apply "go to Chat" from Process file click before radio is created (can't modify widget key after)
        if st.session_state.pop(KEY_GO_TO_CHAT, None):
            st.session_state[KEY_LEFT_TAB] = 1

        tab_index = st.radio(
            "Section",
            options=[0, 1],
            format_func=lambda i: ["Upload", "Chat"][i],
            key=KEY_LEFT_TAB,
            horizontal=True,
            label_visibility="collapsed",
        )
        if tab_index == 0:
            # Prompt section: default from prompts/default.md, then Langfuse when empty
            if KEY_PROMPT_EDITOR not in st.session_state:
                st.session_state[KEY_PROMPT_EDITOR] = ""
            current_prompt = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
            if not current_prompt:
                file_content = _load_default_prompt_from_file()
                if file_content:
                    st.session_state[KEY_PROMPT_EDITOR] = file_content
                else:
                    langfuse_content = get_prompt_from_langfuse()
                    if langfuse_content:
                        st.session_state[KEY_PROMPT_EDITOR] = langfuse_content
            with st.expander("Prompt (optional)", expanded=False):
                st.text_area(
                    "Edit prompt",
                    height=120,
                    key=KEY_PROMPT_EDITOR,
                    placeholder="Add optional context or instructions for your questions...",
                    label_visibility="collapsed",
                )

            uploader_key = f"pdf_uploader_{st.session_state[KEY_UPLOADER_RESET]}"
            uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], key=uploader_key)
            if uploaded_file is not None:
                col_from, col_to = st.columns(2)
                with col_from:
                    st.number_input("From", min_value=0, value=st.session_state.get(KEY_FROM_PAGE, 0), key=KEY_FROM_PAGE)
                with col_to:
                    st.number_input("To", min_value=0, value=st.session_state.get(KEY_TO_PAGE, 20), key=KEY_TO_PAGE)
                col_btn, col_toggle = st.columns([1, 1])
                with col_btn:
                    if st.button("Process file", key="btn_process_file"):
                        # 1. Load the PDF: add to session and extract text by page (pypdf)
                        add_upload(st.session_state, uploaded_file.name, uploaded_file.getvalue())
                        pdf_id = st.session_state[KEY_SELECTED_ID]
                        prompt_prefix = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
                        conv = get_or_create_conversation(
                            pdf_id,
                            initial_messages=[{"role": "user", "content": prompt_prefix}],
                        )
                        # 2. Send first prompt to backend POST /pdf_detail_from_external
                        text_output_only = st.session_state.get(KEY_TEXT_OUTPUT_ONLY, False)
                        from_page = st.session_state.get(KEY_FROM_PAGE, 0)
                        to_page = st.session_state.get(KEY_TO_PAGE, 20)
                        base_url = get_backend_base_url()
                        try:
                            pdf_detail_from_external(
                                system_prompt=prompt_prefix or "",
                                external_loc=uploaded_file.name,
                                from_page=from_page,
                                to_page=to_page,
                                conversation_id=conv["conversation_id"],
                                text_output_only=text_output_only,
                                base_url=base_url,
                            )
                        except Exception:
                            pass  # don't block Process file if backend fails
                        st.session_state[KEY_UPLOADER_RESET] += 1  # clear uploader so x is gone
                        st.session_state[KEY_GO_TO_CHAT] = True  # switch to Chat on next run
                        st.rerun()
                with col_toggle:
                    st.checkbox(
                        "Text Output Only",
                        value=st.session_state.get(KEY_TEXT_OUTPUT_ONLY, False),
                        key=KEY_TEXT_OUTPUT_ONLY,
                    )
        else:
            render_chat_tab(get_current_upload())
