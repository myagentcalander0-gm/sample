"""Template tab: per-PDF notes editor and Download as PDF via backend POST."""
from __future__ import annotations

import base64
from typing import Any

import requests
import streamlit as st

from config import get_notes_to_pdf_url
from state import get_backend_base_url

KEY_PENDING_PDF = "pending_pdf_download"  # {b64: str, filename: str} after POST; trigger JS download then clear


def _template_text_key(pdf_id: str) -> str:
    """Session state key for this PDF's template text."""
    return f"template_text_{pdf_id}"


def render_template_tab(current: dict[str, Any] | None) -> None:
    """Render the Template tab: per-PDF notes and Download as PDF (POST to backend on click)."""
    if current is None:
        st.info("Select a PDF to see and edit its notes.")
        return
    pdf_id = current.get("id") or ""
    text_key = _template_text_key(pdf_id)
    st.caption(f"Notes for **{current.get('name', 'PDF')}**. Use **Insert** on chat responses to add rows here.")
    text = st.text_area(
        "Notes",
        value=st.session_state.get(text_key, ""),
        key=text_key,
        height=400,
        placeholder="Insert chat responses with the Insert button, or type here…",
        label_visibility="collapsed",
    )

    # Download filename: Case ID (per-PDF) if set, else PDF base name + _notes
    case_id = (st.session_state.get(f"case_id_{pdf_id}") or "").strip()
    if case_id:
        filename = f"{case_id}.pdf" if not case_id.lower().endswith(".pdf") else case_id
    else:
        filename = (current.get("name") or "template").rsplit(".", 1)[0] + "_notes.pdf"

    # Only convert on click: POST to backend when user clicks the button
    if st.button("Download as PDF", type="primary", key=f"btn_dl_pdf_{pdf_id}"):
        base_url = get_backend_base_url()
        url = get_notes_to_pdf_url(base_url)
        try:
            r = requests.post(url, json={"text": text or ""}, timeout=30)
            r.raise_for_status()
            pdf_bytes = r.content
            b64 = base64.b64encode(pdf_bytes).decode("ascii")
            st.session_state[KEY_PENDING_PDF] = {"b64": b64, "filename": filename}  # filename uses Case ID when set
            st.rerun()
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
        except Exception as e:
            st.error(f"Download failed: {e}")

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
