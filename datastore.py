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
KEY_CHAT_MESSAGES = "chat_messages"
KEY_CURRENT_UPLOAD = "current_upload"
KEY_COLUMN_RATIO_LEFT = "column_ratio_left"
KEY_COLUMN_RATIO_RIGHT = "column_ratio_right"


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
