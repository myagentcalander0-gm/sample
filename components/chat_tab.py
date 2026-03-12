"""Interactive chat tab: per-PDF conversation storage and conversation_id for backend."""
from __future__ import annotations

import re
from typing import Any

import streamlit as st

from datastore import KEY_CURRENT_UPLOAD, KEY_CONVERSATIONS, KEY_SCROLL_TO_PAGE
from state import get_current_upload, get_or_create_conversation
from services.chat_api import query_pdf

# Match "page 1", "Page 2", "p. 3", "p 4" etc. for clickable page links
PAGE_REF_PATTERN = re.compile(r"\b([Pp]age\s+|[Pp]\.?\s*)(\d+)\b")


PAGE_BUTTONS_PER_ROW = 4


def _render_message_with_page_links(content: str, message_id: str) -> None:
    """Render message content; page references become clickable #page_N links in sorted rows of 4."""
    parts = PAGE_REF_PATTERN.split(content)
    if len(parts) == 1:
        st.markdown(content)
        return
    # Collect all page numbers and render message text (refs as plain "page N")
    page_nums: list[int] = []
    for i, part in enumerate(parts):
        if part.isdigit():
            page_nums.append(int(part))
            st.markdown(f"page {part}")
        elif part:
            st.markdown(part)
    # Sorted, deduplicated page buttons in rows of PAGE_BUTTONS_PER_ROW
    if not page_nums:
        return
    unique_sorted = sorted(set(page_nums))
    for row_start in range(0, len(unique_sorted), PAGE_BUTTONS_PER_ROW):
        row = unique_sorted[row_start : row_start + PAGE_BUTTONS_PER_ROW]
        if not row:
            break
        cols = st.columns(PAGE_BUTTONS_PER_ROW)
        for j, page_num in enumerate(row):
            with cols[j]:
                key = f"chat_goto_{message_id}_p{page_num}_r{row_start}"
                if st.button(f"#page_{page_num}", key=key, type="secondary"):
                    st.session_state[KEY_SCROLL_TO_PAGE] = page_num
                    st.rerun()


def _get_context_from_current() -> str | None:
    """Build context from current PDF text for the API."""
    current = st.session_state.get(KEY_CURRENT_UPLOAD)
    if not current:
        return None
    parts = current.get("text_by_page") or []
    return "\n\n".join(f"Page {i+1}:\n{p}" for i, p in enumerate(parts))


def render_chat_tab(current: dict[str, Any] | None) -> None:
    """Render the chat tab. Each PDF has its own conversation and conversation_id for the backend."""
    if current is None:
        st.info("Select a PDF in the Upload tab to chat about it.")
        return

    pdf_id = current.get("id") or ""
    st.session_state[KEY_CURRENT_UPLOAD] = current

    # Per-PDF conversation: one conversation_id and message list per PDF
    conv = get_or_create_conversation(pdf_id)
    conversation_id = conv["conversation_id"]
    messages = conv["messages"]

    for idx, msg in enumerate(messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                _render_message_with_page_links(msg["content"], f"{pdf_id}_{idx}")
            else:
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask something about the PDF..."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Querying..."):
                try:
                    context = _get_context_from_current()
                    response = query_pdf(
                        query=prompt,
                        pdf_context=context,
                        pdf_id=pdf_id,
                        conversation_id=conversation_id,
                    )
                    if isinstance(response, dict):
                        answer = (
                            response.get("answer")
                            or response.get("response")
                            or response.get("text")
                            or str(response)
                        )
                    elif isinstance(response, list):
                        answer = "\n".join(str(x) for x in response)
                    else:
                        answer = str(response)
           
                    _render_message_with_page_links(answer, f"{pdf_id}_new")
                    messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"API error: {e}")
                    messages.append({"role": "assistant", "content": f"Error: {e}"})

        conv["messages"] = messages
        st.rerun()
