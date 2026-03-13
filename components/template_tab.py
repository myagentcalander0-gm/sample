"""Template tab: per-PDF notes editor and Download as PDF (in-app conversion, no external route)."""
from __future__ import annotations

from typing import Any

import streamlit as st

from services.notes_to_pdf import notes_markdown_to_pdf_bytes


def _template_text_key(pdf_id: str) -> str:
    """Session state key for this PDF's template text."""
    return f"template_text_{pdf_id}"


@st.cache_data(show_spinner=False)
def _build_pdf_cached(editor_content: str) -> bytes:
    """Cache PDF bytes by notes content so download stays one-click and fast."""
    return notes_markdown_to_pdf_bytes(editor_content)


def render_template_tab(current: dict[str, Any] | None) -> None:
    """Render the Template tab: per-PDF notes and Download as PDF (in-app conversion on click)."""
    if current is None:
        st.info("Select a PDF to see and edit its notes.")
        return
    pdf_id = current.get("id") or ""
    text_key = _template_text_key(pdf_id)
    st.caption(f"Notes for **{current.get('name', 'PDF')}**. Use **Insert** on chat responses to add rows here. Markdown is supported.")
    # Case ID: per-PDF, used as download filename (case_id.pdf); placed right before Editor/Edit Preview tabs
    st.text_input("Case ID", key=f"case_id_{pdf_id}", placeholder="Case ID (used for download filename)", label_visibility="visible")
    text = st.session_state.get(text_key, "")

    tab_editor, tab_preview = st.tabs(["Editor", "Edit Preview"])
    with tab_editor:
        st.text_area(
            "Notes (markdown)",
            value=text,
            key=text_key,
            height=450,
            placeholder="Paste markdown from the agent or type here…",
            label_visibility="collapsed",
        )
    with tab_preview:
        # Approximate PDF content width so users can estimate line wraps before download.
        st.markdown('<div style="max-width: 680px;">', unsafe_allow_html=True)
        preview_text = st.session_state.get(text_key, "")
        if (preview_text or "").strip():
            st.markdown(preview_text)
        else:
            st.caption("_No content yet. Add markdown in the Editor tab._")
        st.markdown("</div>", unsafe_allow_html=True)

    text = st.session_state.get(text_key, "")

    # Download as PDF: convert only when user clicks (not on every page load).
    case_id = (st.session_state.get(f"case_id_{pdf_id}") or "").strip()
    if case_id:
        filename = case_id if case_id.lower().endswith(".pdf") else f"{case_id}.pdf"
    else:
        filename = None

    if not filename:
        st.caption("Set **Case ID** above to download. Output file will be **case_id.pdf**.")
        return

    editor_content = (st.session_state.get(text_key) or "").strip()
    try:
        pdf_bytes = _build_pdf_cached(editor_content)
        st.download_button(
            "Download as PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            key=f"dl_pdf_{pdf_id}",
            help="Downloads case_id.pdf from current notes.",
        )
    except Exception as e:
        st.error(f"Download failed: {e}")
