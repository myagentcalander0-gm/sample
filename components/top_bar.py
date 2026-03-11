"""Full-width top bar: session first, then backend; optional Refresh and column ratio."""
from __future__ import annotations

import streamlit as st

from config import get_backend_display, is_dev
from datastore import KEY_COLUMN_RATIO_LEFT, KEY_COLUMN_RATIO_RIGHT, KEY_SESSION_KEY
from services.health import check_health

RATIO_OPTIONS = ["1 : 1", "1 : 2", "1 : 3", "2 : 1", "2 : 3", "3 : 2"]


def render_top_bar() -> None:
    """Render Session first, then Backend; in dev: column ratio selector and Refresh button."""
    session_key = st.session_state[KEY_SESSION_KEY]
    result = check_health()
    dot_color = "#22c55e" if result.ok else "#ef4444"
    label = "Backend" if result.ok else "Backend (off)"
    extra = f" · {get_backend_display()}" if not result.ok else ""
    # Session first, then backend
    line = (
        f'<span style="font-size:0.85em;">Session: <code>{session_key}</code> · Files in this session only.</span>'
        f' · <span style="color:{dot_color}; font-size:1em;">●</span> '
        f'<span style="font-size:0.85em;">{label} · {result.latency_ms:.0f} ms{extra}</span>'
    )

    if is_dev():
        bar_col1, bar_col2 = st.columns([14, 1])
        with bar_col1:
            st.markdown(
                f'<div style="line-height:1.3; margin:0 0 -0.35rem 0; padding:0;">{line}</div>',
                unsafe_allow_html=True,
            )
        with bar_col2:
            if st.button("Refresh", key="top_bar_refresh"):
                st.rerun()

    else:
        with st.columns(1)[0]:
            st.markdown(
                f'<div style="line-height:1.3; margin:0 0 -0.35rem 0; padding:0;">{line}</div>',
                unsafe_allow_html=True,
            )
