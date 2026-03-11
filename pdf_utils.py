"""PDF text extraction and upload helpers. Uses datastore for entry shape."""
from __future__ import annotations

import io
import uuid
from typing import TYPE_CHECKING

from pypdf import PdfReader

from datastore import KEY_SELECTED_ID, KEY_UPLOADS, upload_entry

if TYPE_CHECKING:
    import streamlit as st


def extract_text_by_page(data: bytes) -> tuple[int, list[str]]:
    """Extract text per page. Returns (num_pages, list of page texts)."""
    reader = PdfReader(io.BytesIO(data))
    n = len(reader.pages)
    texts = []
    for i in range(n):
        try:
            texts.append(reader.pages[i].extract_text() or "")
        except Exception:
            texts.append("")
    return n, texts


def add_upload(session_state: object, name: str, data: bytes) -> None:
    """Add uploaded PDF to session uploads and set as selected."""
    num_pages, text_by_page = extract_text_by_page(data)
    entry = upload_entry(
        id=str(uuid.uuid4()),
        name=name,
        data=data,
        num_pages=num_pages,
        text_by_page=text_by_page,
    )
    uploads = getattr(session_state, KEY_UPLOADS, [])
    uploads.append(entry)
    setattr(session_state, KEY_SELECTED_ID, entry["id"])
