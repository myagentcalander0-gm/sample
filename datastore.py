"""Data-related types and session state keys. All in-memory/session data shapes live here."""
from __future__ import annotations

from typing import Any, TypedDict


# -----------------------------------------------------------------------------
# Session state keys (single source of truth)
# -----------------------------------------------------------------------------
KEY_UPLOADS = "uploads"
KEY_SELECTED_ID = "selected_id"
KEY_SCROLL_TO_PAGE = "scroll_to_page"
KEY_SESSION_KEY = "session_key"
KEY_CHAT_MESSAGES = "chat_messages"  # legacy; use KEY_CONVERSATIONS per-PDF
KEY_CONVERSATIONS = "conversations"  # dict[pdf_id, {"conversation_id": str, "messages": list[ChatMessage]}]
KEY_CURRENT_UPLOAD = "current_upload"
KEY_COLUMN_RATIO_LEFT = "column_ratio_left"
KEY_COLUMN_RATIO_RIGHT = "column_ratio_right"
KEY_UPLOADER_RESET = "uploader_reset"  # bumped after Process file to clear uploader (no x to remove)
KEY_TEXT_OUTPUT_ONLY = "text_output_only"  # toggle next to Process file: when True, process for text only
KEY_BACKEND_BASE_URL = "backend_base_url"  # editable in dev; used for health and chat requests
KEY_PROMPT_EDITOR = "prompt_editor"  # prompt text (in Upload tab); used as system_prompt and prefix
KEY_FROM_PAGE = "from_page"  # page range start (default 0)
KEY_TO_PAGE = "to_page"  # page range end (default 20)
KEY_LEFT_TAB = "left_tab"  # 0 = Upload, 1 = Chat
KEY_GO_TO_CHAT = "go_to_chat"  # set True when Process file clicked; applied before radio so we can switch tab
KEY_GO_TO_NOTES_TAB = "go_to_notes_tab"  # set True when Insert clicked in chat; switch main panel to Notes tab
KEY_ACTIVE_MAIN_TAB = "active_main_tab"  # 0=Preview, 1=Analyzed PDF, 2=Notes; used so Insert can open Notes
KEY_CONVERTED_IMAGES = "converted_images"  # dict[pdf_id, list[bytes]]: per-page image bytes for Converted tab
KEY_TEMPLATE_ROWS = "template_rows"  # dict[pdf_id, list[str]]: per-PDF rows from Insert
# Template text per PDF is in st.session_state[f"template_text_{pdf_id}"] (widget key)


# -----------------------------------------------------------------------------
# Data shapes
# -----------------------------------------------------------------------------
class UploadEntry(TypedDict, total=False):
    """One processed PDF in session. id, name, data, num_pages, text_by_page."""
    id: str
    name: str
    data: bytes
    num_pages: int
    text_by_page: list[str]


class ChatMessage(TypedDict):
    """One chat message (user or assistant)."""
    role: str
    content: str


# -----------------------------------------------------------------------------
# Defaults / initial values
# -----------------------------------------------------------------------------
def default_uploads() -> list[dict[str, Any]]:
    return []


def default_chat_messages() -> list[ChatMessage]:
    return []


def default_conversations() -> dict[str, Any]:
    """Per-PDF conversations: pdf_id -> {conversation_id, messages}."""
    return {}


def upload_entry(
    id: str,
    name: str,
    data: bytes,
    num_pages: int,
    text_by_page: list[str],
) -> dict[str, Any]:
    """Build an UploadEntry-shaped dict."""
    return {
        "id": id,
        "name": name,
        "data": data,
        "num_pages": num_pages,
        "text_by_page": text_by_page,
    }


def chat_message(role: str, content: str) -> ChatMessage:
    """Build a ChatMessage-shaped dict."""
    return {"role": role, "content": content}
