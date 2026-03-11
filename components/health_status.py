"""Service health indicator: green dot when on, plus latency."""
from __future__ import annotations

import streamlit as st

from config import get_backend_display
from services.health import check_health, HealthResult


def render_health_status(container: object | None = None) -> HealthResult:
    """
    Check backend health and render a green dot when on, plus latency.
    When disconnected, show only host:port (no long error message).
    """
    target = container if container is not None else st
    result = check_health()
    dot_color = "#22c55e" if result.ok else "#ef4444"
    label = "Backend" if result.ok else "Backend (off)"
    extra = f" · {get_backend_display()}" if not result.ok else ""
    with target.container():
        target.markdown(
            f'<span style="color:{dot_color}; font-size:1.1em;">●</span> '
            f'<span style="font-size:0.9em;">{label} · {result.latency_ms:.0f} ms{extra}</span>',
            unsafe_allow_html=True,
        )
    return result
