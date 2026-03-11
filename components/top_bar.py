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
    label = "Backend" if result.ok else "Backend (off)"
    extra = f" · {get_backend_display()}" if not result.ok else ""
    line = f"Session: {session_key} · Files in this session only. · {label} · {result.latency_ms:.0f} ms{extra}"

    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.caption(line)
    with top_right:
        if st.button("Refresh", use_container_width=True, key="top_bar_refresh"):
            st.rerun()
