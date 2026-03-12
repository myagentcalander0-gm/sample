"""Interactive chat tab: per-PDF conversation storage and conversation_id for backend."""
from __future__ import annotations

import re
from typing import Any

import streamlit as st

from datastore import (
    KEY_CURRENT_UPLOAD,
    KEY_CONVERSATIONS,
    KEY_FROM_PAGE,
    KEY_GO_TO_NOTES_TAB,
    KEY_PROMPT_EDITOR,
    KEY_SCROLL_TO_PAGE,
    KEY_TEMPLATE_ROWS,
    KEY_TEXT_OUTPUT_ONLY,
    KEY_TO_PAGE,
)
from state import get_current_upload, get_or_create_conversation, get_backend_base_url
from services.chat_api import query_pdf_conversation
from components.template_tab import _template_text_key

# Match "page 1", "Page 2", "p. 3", "p 4" etc. for clickable page links
PAGE_REF_PATTERN = re.compile(r"\b([Pp]age\s+|[Pp]\.?\s*)(\d+)\b")


PAGE_BUTTONS_PER_ROW = 4

# CSS: hover over assistant message reveals Insert button (first column); 20x10px, light grey, slight black text
_CHAT_INSERT_CSS = """
<style>
[data-testid="stChatMessage"] { position: relative; }
[data-testid="stChatMessage"] [data-testid="stHorizontalBlock"] > div:first-child { opacity: 0; transition: opacity 0.15s; position: absolute !important; top: 4px; right: 4px; z-index: 2; }
[data-testid="stChatMessage"]:hover [data-testid="stHorizontalBlock"] > div:first-child { opacity: 1; }
[data-testid="stChatMessage"] [data-testid="stHorizontalBlock"] > div:first-child button {
  width: 55px !important;
  position: absolute !important;
  top: 10px !important;
  left: -10px !important;
  min-width: 20px !important;
  height: 30px !important;
  min-height: 20px !important;
  padding: 0 !important;
  font-size: 6px !important;
  line-height: 1 !important;
  background-color: #d3d3d3 !important;
  color: rgba(0, 0, 0, 0.75) !important;
  border: 1px solid #bbb !important;
  border-radius: 3px !important;
}
</style>
"""


def _render_assistant_message_with_insert(content: str, message_id: str, pdf_id: str) -> None:
    """Render assistant message with hover-reveal Insert button (adds response as new row in this PDF's notes)."""
    st.markdown(_CHAT_INSERT_CSS, unsafe_allow_html=True)
    col_btn, col_msg = st.columns([0.08, 0.92])
    with col_btn:
        insert_key = f"insert_tpl_{message_id}"
        if st.button("Insert", key=insert_key, type="secondary"):
            rows_by_pdf = st.session_state.get(KEY_TEMPLATE_ROWS, {})
            rows = list(rows_by_pdf.get(pdf_id, []))
            rows.append(content)
            if KEY_TEMPLATE_ROWS not in st.session_state:
                st.session_state[KEY_TEMPLATE_ROWS] = {}
            st.session_state[KEY_TEMPLATE_ROWS][pdf_id] = rows
            st.session_state[_template_text_key(pdf_id)] = "\n\n".join(rows)
            st.session_state[KEY_GO_TO_NOTES_TAB] = True  # switch main panel to Notes tab
            st.rerun()
    with col_msg:
        _render_message_with_page_links(content, message_id)


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
                if st.button(f"#page_{page_num}", key=key, type="tertiary"):
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
                _render_assistant_message_with_insert(msg["content"], f"{pdf_id}_{idx}", pdf_id)
            else:
                st.markdown(msg["content"])

    # Page selection: options from max(1, from_page) to min(num_pages, to_page) after process
    num_pages = current.get("num_pages") or 0
    pdf_start = max(1, st.session_state.get(KEY_FROM_PAGE, 1))
    pdf_end = min(num_pages, st.session_state.get(KEY_TO_PAGE, 20)) if num_pages else 0
    page_options = list(range(pdf_start, pdf_end + 1)) if pdf_end >= pdf_start else []
    page_selection_key = f"page_selection_{pdf_id}"
    if page_options and page_selection_key not in st.session_state:
        st.session_state[page_selection_key] = page_options.copy()
    if page_options:
        st.multiselect(
            "Pages",
            options=page_options,
            key=page_selection_key,
            format_func=lambda x: f"Page {x}",
        )

    if prompt := st.chat_input("Ask something about the PDF..."):
        prompt_prefix = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
        user_content = f"{prompt_prefix}\n\n{prompt}" if prompt_prefix else prompt
        messages.append({"role": "user", "content": user_content})
        with st.chat_message("user"):
            st.markdown(user_content)

        with st.chat_message("assistant"):
            with st.spinner("Querying..."):
                try:
                    base_url = get_backend_base_url()
                    # Only send from_page / to_page on first message; derive from page selection (min/max window)
                    is_first = len(messages) == 1
                    if is_first and page_options:
                        selected_pages = st.session_state.get(page_selection_key, [])
                        if selected_pages:
                            from_page = max(min(selected_pages), pdf_start)
                            to_page = min(max(selected_pages), pdf_end)
                        else:
                            from_page = pdf_start
                            to_page = pdf_end
                    elif is_first and pdf_end >= pdf_start:
                        from_page = pdf_start
                        to_page = pdf_end
                    else:
                        from_page = None
                        to_page = None
                    last_msg = messages[-1]
                    conversations_payload = [
                        {"is_user": last_msg["role"] == "user", "context": last_msg["content"]}
                    ]
                    response = query_pdf_conversation(
                        conversation_id=conversation_id,
                        conversations=conversations_payload,
                        from_page=from_page,
                        to_page=to_page,
                        base_url=base_url,
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
                    _render_assistant_message_with_insert(answer, f"{pdf_id}_new", pdf_id)
                    messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"API error: {e}")
                    messages.append({"role": "assistant", "content": f"Error: {e}"})

        conv["messages"] = messages
        st.rerun()
