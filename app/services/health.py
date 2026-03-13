"""Backend service health check and latency measurement."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from config import get_health_url


def check_health(base_url: str | None = None, timeout_sec: float = 3.0) -> HealthResult:
    """
    Check backend service health and measure latency.
    base_url: if set, use this as the backend base (e.g. from session state in dev).
    Returns green-dot status (ok) and latency in milliseconds.
    """
    url = get_health_url(base_url)
    start = time.perf_counter()
    try:
        r = requests.get(url, timeout=timeout_sec)
        latency_ms = (time.perf_counter() - start) * 1000
        ok = 200 <= r.status_code < 400
        message = "" if ok else f"HTTP {r.status_code}"
        return HealthResult(ok=ok, latency_ms=latency_ms, message=message)
    except requests.RequestException as e:  # type: ignore[attr-defined]
        latency_ms = (time.perf_counter() - start) * 1000
        return HealthResult(ok=False, latency_ms=latency_ms, message=str(e))


@dataclass
class HealthResult:
    """Result of a health check. Use dot_color and label for UI."""
    ok: bool
    latency_ms: float
    message: str = ""

    @property
    def dot_color(self) -> str:
        """Green if healthy, red otherwise."""
        return "#22c55e" if self.ok else "#ef4444"

    @property
    def label(self) -> str:
        """Backend status label for display."""
        return "Backend" if self.ok else "Backend (off)"
