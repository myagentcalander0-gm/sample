"""Top bar: one row with session + backend caption and Refresh button."""
from __future__ import annotations

import streamlit as st

from config import get_backend_display
from datastore import KEY_SESSION_KEY
from services.health import check_health

def render_top_bar() -> None:
    """Full-width top row: left = session + backend caption, right = Refresh."""
    session_key = st.session_state[KEY_SESSION_KEY]
    result = check_health()
    extra = f" · {get_backend_display()}" if not result.ok else ""
    line = (
        f'<span style="font-size:0.85em;">Session: <code>{session_key}</code> · Files in this session only.</span>'
        f' · <span style="color:{result.dot_color}; font-size:1em;">●</span> '
        f'<span style="font-size:0.85em;">{result.label} · {result.latency_ms:.0f} ms{extra}</span>'
    )

    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.markdown(line, unsafe_allow_html=True)
    with top_right:
        if st.button("Refresh", use_container_width=True, key="top_bar_refresh"):
            st.rerun()
