"""Top bar: one row with session + backend caption and Refresh button."""
from __future__ import annotations

import streamlit as st

from config import get_backend_display, is_dev
from datastore import KEY_BACKEND_BASE_URL, KEY_SESSION_KEY
from state import get_backend_base_url
from services.health import check_health


def render_top_bar() -> None:
    """Full-width top row: session + backend (editable in dev) + Refresh."""
    session_key = st.session_state[KEY_SESSION_KEY]
    base_url = get_backend_base_url()
    result = check_health(base_url=base_url)
    # In non-dev show backend in the line; in dev we show an editable field instead
    extra = "" if is_dev() else (f" · {get_backend_display(base_url)}" if not result.ok else "")
    line = (
        f'<span style="font-size:0.85em;">Session: <code>{session_key}</code> · Files in this session only.</span>'
        f' · <span style="color:{result.dot_color}; font-size:1em;">●</span> '
        f'<span style="font-size:0.85em;">{result.label} · {result.latency_ms:.0f} ms{extra}</span>'
    )

    if is_dev():
        col_status, col_url, col_btn = st.columns([4, 2, 1])
        with col_status:
            st.markdown(line, unsafe_allow_html=True)
        with col_url:
            st.text_input(
                "Backend URL",
                key=KEY_BACKEND_BASE_URL,
                label_visibility="collapsed",
                placeholder="http://localhost:8000",
            )
        with col_btn:
            if st.button("Refresh", use_container_width=True, key="top_bar_refresh"):
                st.rerun()
    else:
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown(line, unsafe_allow_html=True)
        with top_right:
            if st.button("Refresh", use_container_width=True, key="top_bar_refresh"):
                st.rerun()
