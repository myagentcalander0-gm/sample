"""Template tab: per-PDF notes editor and Download as PDF (in-app conversion, no external route)."""
from __future__ import annotations

from typing import Any

import streamlit as st

from services.notes_to_pdf import notes_markdown_to_pdf_bytes

KEY_PENDING_PDF = "pending_pdf_download"  # {bytes: bytes, filename: str} — set only when user clicks Download as PDF


def _template_text_key(pdf_id: str) -> str:
    """Session state key for this PDF's template text."""
    return f"template_text_{pdf_id}"


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
            height=300,
            placeholder="Paste markdown from the agent or type here…",
            label_visibility="collapsed",
        )
    with tab_preview:
        preview_text = st.session_state.get(text_key, "")
        if (preview_text or "").strip():
            st.markdown(preview_text)
        else:
            st.caption("_No content yet. Add markdown in the Editor tab._")

    text = st.session_state.get(text_key, "")

    # Download as PDF: convert only when user clicks (not on every page load).
    case_id = (st.session_state.get(f"case_id_{pdf_id}") or "").strip()
    if case_id:
        filename = case_id if case_id.lower().endswith(".pdf") else f"{case_id}.pdf"
    else:
        filename = None

    if st.button(
        "Download as PDF",
        type="primary",
        key=f"btn_dl_pdf_{pdf_id}",
        disabled=(not filename),
        help="Converts current notes to PDF and downloads as case_id.pdf.",
    ) and filename:
        editor_content = (st.session_state.get(text_key) or "").strip()
        try:
            pdf_bytes = notes_markdown_to_pdf_bytes(editor_content)
            st.session_state[KEY_PENDING_PDF] = {"bytes": pdf_bytes, "filename": filename}
            st.rerun()
        except Exception as e:
            st.error(f"Download failed: {e}")

    if not filename:
        st.caption("Set **Case ID** above to download. Output file will be **case_id.pdf**.")

    # Show download button only after user clicked "Download as PDF" (so conversion runs once per click).
    pending = st.session_state.pop(KEY_PENDING_PDF, None)
    if pending:
        st.download_button(
            label=f"Download {pending['filename']}",
            data=pending["bytes"],
            file_name=pending["filename"],
            mime="application/pdf",
            type="primary",
            key=f"dl_pdf_{pdf_id}",
        )
