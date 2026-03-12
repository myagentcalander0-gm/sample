"""Backend API client for PDF query chat."""
from __future__ import annotations

from typing import Any

import requests

from config import get_chat_api_url, get_pdf_detail_from_external_url


def query_pdf(
    query: str,
    pdf_context: str | None = None,
    pdf_id: str | None = None,
    conversation_id: str | None = None,
    base_url: str | None = None,
    timeout_sec: float = 30.0,
) -> dict[str, Any] | list[Any]:
    """
    Call backend API to query the PDF.
    Sends query, optional pdf_context, pdf_id, and conversation_id for thread continuity.
    base_url: if set, use this as the backend base (e.g. from session state).
    """
    url = get_chat_api_url(base_url)
    payload: dict[str, Any] = {"query": query}
    if pdf_context:
        payload["context"] = pdf_context
    if pdf_id:
        payload["pdf_id"] = pdf_id
    if conversation_id:
        payload["conversation_id"] = conversation_id
    r = requests.post(url, json=payload, timeout=timeout_sec)
    r.raise_for_status()
    return r.json()


def pdf_detail_from_external(
    system_prompt: str,
    external_loc: str,
    conversation_id: str | None = None,
    text_output_only: bool = False,
    from_page: int = 0,
    to_page: int = 20,
    base_url: str | None = None,
    timeout_sec: float = 30.0,
) -> dict[str, Any] | list[Any]:
    """
    Called when user clicks Process file: send system_prompt, external_loc, conversation_id,
    text_output_only, from_page, to_page.
    """
    url = get_pdf_detail_from_external_url(base_url)
    payload: dict[str, Any] = {
        "system_prompt": system_prompt,
        "external_loc": external_loc,
        "text_output_only": text_output_only,
        "from_page": from_page,
        "to_page": to_page,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    r = requests.post(url, json=payload, timeout=timeout_sec)
    r.raise_for_status()
    return r.json()


def query_pdf_conversation(
    conversation_id: str,
    conversations: list[dict[str, Any]],
    from_page: int | None = None,
    to_page: int | None = None,
    base_url: str | None = None,
    timeout_sec: float = 30.0,
) -> dict[str, Any] | list[Any]:
    """
    Send conversation_id, conversations (last message). from_page/to_page only on first message.
    Each item: {"is_user": True/False, "context": "message content"}.
    """
    url = get_chat_api_url(base_url)
    payload: dict[str, Any] = {
        "conversation_id": conversation_id,
        "conversations": conversations,
    }
    if from_page is not None:
        payload["from_page"] = from_page
    if to_page is not None:
        payload["to_page"] = to_page
    r = requests.post(url, json=payload, timeout=timeout_sec)
    r.raise_for_status()
    return r.json()
