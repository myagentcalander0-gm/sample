"""Template tab: per-PDF notes editor and Download as PDF (in-app conversion, no external route)."""
from __future__ import annotations

import base64
from typing import Any

import streamlit as st

from services.notes_to_pdf import notes_markdown_to_pdf_bytes

KEY_PENDING_PDF = "pending_pdf_download"  # {b64: str, filename: str} after POST; trigger JS download then clear


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

    # Download as PDF: converts all edited notes (markdown) to PDF; output filename = case_id.pdf (Case ID required)
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
        help="Converts all edited notes to PDF. Set Case ID in the sidebar; output will be case_id.pdf.",
    ):
        # Convert notes to PDF in-app (no HTTP route). Streamlit has no /notes_to_pdf endpoint; we do markdown→PDF here and pass bytes to the browser for auto-download.
        editor_content = (st.session_state.get(text_key) or "").strip()
        try:
            pdf_bytes = notes_markdown_to_pdf_bytes(editor_content)
            b64 = base64.b64encode(pdf_bytes).decode("ascii")
            st.session_state[KEY_PENDING_PDF] = {"b64": b64, "filename": filename}
            st.rerun()
        except Exception as e:
            st.error(f"Download failed: {e}")

    if not filename:
        st.caption("Set **Case ID** in the sidebar to download. Output file will be **case_id.pdf**.")

    # After rerun with pending PDF: trigger browser download via JS, then clear
    pending = st.session_state.pop(KEY_PENDING_PDF, None)
    if pending:
        b64 = pending["b64"].replace("'", "\\'").replace('"', '\\"')
        fn = pending["filename"].replace("'", "\\'").replace('"', '\\"')
        st.markdown(
            f'<script>(function(){{'
            f'var b64="{b64}";'
            f'var fn="{fn}";'
            f'var bin=atob(b64);'
            f'var arr=new Uint8Array(bin.length);'
            f'for(var i=0;i<bin.length;i++) arr[i]=bin.charCodeAt(i);'
            f'var blob=new Blob([arr],{{type:"application/pdf"}});'
            f'var a=document.createElement("a");'
            f'a.href=URL.createObjectURL(blob);'
            f'a.download=fn;'
            f'a.click();'
            f'URL.revokeObjectURL(a.href);'
            f'}})();</script>',
            unsafe_allow_html=True,
        )
