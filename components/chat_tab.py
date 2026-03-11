"""Interactive chat tab: query the PDF via backend API."""
from __future__ import annotations

from typing import Any

import streamlit as st

from datastore import KEY_CHAT_MESSAGES, KEY_CURRENT_UPLOAD
from services.chat_api import query_pdf


def _get_context_from_current() -> str | None:
    """Build context from current PDF text for the API."""
    current = st.session_state.get(KEY_CURRENT_UPLOAD)
    if not current:
        return None
    parts = current.get("text_by_page") or []
    return "\n\n".join(f"Page {i+1}:\n{p}" for i, p in enumerate(parts))


def render_chat_tab(current: dict[str, Any] | None) -> None:
    """Render the chat tab; calls backend API for each user message."""
    if current is None:
        st.info("Select a PDF in the Upload tab to chat about it.")
        return

    # Persist current for API context (in case state is read in callback)
    st.session_state[KEY_CURRENT_UPLOAD] = current

    # Chat message list
    messages = st.session_state.get(KEY_CHAT_MESSAGES, [])

    for msg in messages:
        with st.chat_message(msg["role"]):
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
                        pdf_id=current.get("id"),
                    )
                    # Backend may return {"answer": "..."}, {"response": "..."}, list, or raw
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
                    st.markdown(answer)
                    messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"API error: {e}")
                    messages.append({"role": "assistant", "content": f"Error: {e}"})

        st.session_state[KEY_CHAT_MESSAGES] = messages
        st.rerun()
