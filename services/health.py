"""Backend service health check and latency measurement."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from config import get_health_url


@dataclass
class HealthResult:
    """Result of a health check."""
    ok: bool
    latency_ms: float
    message: str = ""


def check_health(timeout_sec: float = 3.0) -> HealthResult:
    """
    Check backend service health and measure latency.
    Returns green-dot status (ok) and latency in milliseconds.
    """
    url = get_health_url()
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
