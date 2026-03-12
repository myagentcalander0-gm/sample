"""Backend API client for PDF query chat."""
from __future__ import annotations

from typing import Any

import requests

from config import get_chat_api_url


def query_pdf(
    query: str,
    pdf_context: str | None = None,
    pdf_id: str | None = None,
    conversation_id: str | None = None,
    timeout_sec: float = 30.0,
) -> dict[str, Any] | list[Any]:
    """
    Call backend API to query the PDF.
    Sends query, optional pdf_context, pdf_id, and conversation_id for thread continuity.
    """
    url = get_chat_api_url()
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
