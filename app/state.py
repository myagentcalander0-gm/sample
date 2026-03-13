"""Session state initialization and helpers. Uses keys and types from datastore."""
from __future__ import annotations

import uuid
from typing import Any

import streamlit as st

from config import PDF_QUERY_API_URL, STREAMLIT_APP_URL
from datastore import (
    KEY_ACTIVE_MAIN_TAB,
    KEY_BACKEND_BASE_URL,
    KEY_CONVERSATIONS,
    KEY_CONVERTED_IMAGES,
    KEY_FROM_PAGE,
    KEY_GO_TO_NOTES_TAB,
    KEY_LEFT_TAB,
    KEY_PROMPT_EDITOR,
    KEY_SCROLL_TO_PAGE,
    KEY_SELECTED_ID,
    KEY_SESSION_KEY,
    KEY_TEMPLATE_ROWS,
    KEY_TEXT_OUTPUT_ONLY,
    KEY_TO_PAGE,
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
    if KEY_TEXT_OUTPUT_ONLY not in st.session_state:
        st.session_state[KEY_TEXT_OUTPUT_ONLY] = True
    if KEY_BACKEND_BASE_URL not in st.session_state:
        st.session_state[KEY_BACKEND_BASE_URL] = PDF_QUERY_API_URL
    if KEY_PROMPT_EDITOR not in st.session_state:
        st.session_state[KEY_PROMPT_EDITOR] = ""
    if KEY_FROM_PAGE not in st.session_state:
        st.session_state[KEY_FROM_PAGE] = 0
    if KEY_TO_PAGE not in st.session_state:
        st.session_state[KEY_TO_PAGE] = 20
    if KEY_LEFT_TAB not in st.session_state:
        st.session_state[KEY_LEFT_TAB] = 0
    if KEY_CONVERTED_IMAGES not in st.session_state:
        st.session_state[KEY_CONVERTED_IMAGES] = {}
    if KEY_TEMPLATE_ROWS not in st.session_state:
        st.session_state[KEY_TEMPLATE_ROWS] = {}
    if KEY_ACTIVE_MAIN_TAB not in st.session_state:
        st.session_state[KEY_ACTIVE_MAIN_TAB] = 0


def get_backend_base_url() -> str:
    """Backend base URL for health/chat requests; from session state (editable in dev) or config."""
    return (st.session_state.get(KEY_BACKEND_BASE_URL) or "").strip() or PDF_QUERY_API_URL


def get_streamlit_app_url() -> str:
    """Full base URL of the current Streamlit app (origin), for external_loc etc. Falls back to STREAMLIT_APP_URL env."""
    # 1) st.context.url (Streamlit 1.45+): use origin only (strip path)
    try:
        ctx_url = getattr(st.context, "url", None)
        if ctx_url:
            from urllib.parse import urlparse
            parsed = urlparse(ctx_url)
            scheme = parsed.scheme or "https"
            netloc = parsed.netloc or "localhost:8501"
            return f"{scheme}://{netloc}".rstrip("/")
    except Exception:
        pass
    # 2) Build from request headers (Host, X-Forwarded-Proto)
    try:
        headers = getattr(st.context, "headers", None)
        if headers:
            host = (headers.get("host") or headers.get("Host") or "").strip()
            proto = (headers.get("x-forwarded-proto") or headers.get("X-Forwarded-Proto") or "").strip().lower()
            if not proto and "localhost" in host:
                proto = "http"
            if not proto:
                proto = "https"
            if host:
                return f"{proto}://{host}".rstrip("/")
    except Exception:
        pass
    # 3) Env fallback
    if (STREAMLIT_APP_URL or "").strip():
        return (STREAMLIT_APP_URL or "").strip().rstrip("/")
    return "http://localhost:8501"


def get_current_upload() -> dict[str, Any] | None:
    """Return the currently selected upload or None."""
    uploads = st.session_state.get(KEY_UPLOADS, default_uploads())
    selected_id = st.session_state.get(KEY_SELECTED_ID)
    return next((u for u in uploads if u["id"] == selected_id), None)


def clear_scroll_target() -> None:
    """Clear scroll_to_page after it has been consumed."""
    if st.session_state.get(KEY_SCROLL_TO_PAGE) is not None:
        st.session_state[KEY_SCROLL_TO_PAGE] = None


def get_or_create_conversation(
    pdf_id: str,
    initial_messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Get the conversation for this PDF (conversation_id + messages).
    Creates one with a new conversation_id if missing.
    initial_messages: when creating a new conversation, seed messages (e.g. [{"role": "user", "content": prompt}]).
    """
    conversations = st.session_state.get(KEY_CONVERSATIONS, default_conversations())
    if pdf_id not in conversations:
        conversations[pdf_id] = {
            "conversation_id": str(uuid.uuid4()),
            "messages": list(initial_messages) if initial_messages else [],
        }
        st.session_state[KEY_CONVERSATIONS] = conversations
    return conversations[pdf_id]
