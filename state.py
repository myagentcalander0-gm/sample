"""Session state initialization and helpers. Uses keys and types from datastore."""
from __future__ import annotations

import uuid
from typing import Any

import streamlit as st

from datastore import (
    KEY_CONVERSATIONS,
    KEY_SCROLL_TO_PAGE,
    KEY_SELECTED_ID,
    KEY_SESSION_KEY,
    KEY_UPLOADS,
    KEY_UPLOADER_RESET,
    default_conversations,
    default_uploads,
)


def ensure_session_state() -> None:
    """Initialize default session state keys (from datastore)."""
    if KEY_UPLOADS not in st.session_state:
        st.session_state[KEY_UPLOADS] = default_uploads()
    if KEY_SELECTED_ID not in st.session_state:
        st.session_state[KEY_SELECTED_ID] = None
    if KEY_SCROLL_TO_PAGE not in st.session_state:
        st.session_state[KEY_SCROLL_TO_PAGE] = None
    if KEY_SESSION_KEY not in st.session_state:
        st.session_state[KEY_SESSION_KEY] = str(uuid.uuid4())[:8]
    if KEY_CONVERSATIONS not in st.session_state:
        st.session_state[KEY_CONVERSATIONS] = default_conversations()
    if KEY_UPLOADER_RESET not in st.session_state:
        st.session_state[KEY_UPLOADER_RESET] = 0


def get_current_upload() -> dict[str, Any] | None:
    """Return the currently selected upload or None."""
    uploads = st.session_state.get(KEY_UPLOADS, default_uploads())
    selected_id = st.session_state.get(KEY_SELECTED_ID)
    return next((u for u in uploads if u["id"] == selected_id), None)


def clear_scroll_target() -> None:
    """Clear scroll_to_page after it has been consumed."""
    if st.session_state.get(KEY_SCROLL_TO_PAGE) is not None:
        st.session_state[KEY_SCROLL_TO_PAGE] = None


def get_or_create_conversation(pdf_id: str) -> dict[str, Any]:
    """
    Get the conversation for this PDF (conversation_id + messages).
    Creates one with a new conversation_id if missing.
    """
    conversations = st.session_state.get(KEY_CONVERSATIONS, default_conversations())
    if pdf_id not in conversations:
        conversations[pdf_id] = {
            "conversation_id": str(uuid.uuid4()),
            "messages": [],
        }
        st.session_state[KEY_CONVERSATIONS] = conversations
    return conversations[pdf_id]
