"""App configuration from environment."""
import os

# Set DEPLOYMENT_ENV=dev to enable dev-only UI (e.g. Refresh button).
DEPLOYMENT_ENV: str = os.getenv("DEPLOYMENT_ENV", "")

# Sidebar max width when expanded (e.g. "400px", "30rem"). Unset = use Streamlit default.
SIDEBAR_MAX_WIDTH: str = os.getenv("SIDEBAR_MAX_WIDTH", "")

# Backend API for PDF query chat. Set PDF_QUERY_API_URL in env or .env.
PDF_QUERY_API_URL: str = os.getenv("PDF_QUERY_API_URL", "http://localhost:8000")
HEALTH_PATH: str = os.getenv("HEALTH_PATH", "/health")
CHAT_PATH: str = os.getenv("CHAT_PATH", "/query")


def get_health_url() -> str:
    base = PDF_QUERY_API_URL.rstrip("/")
    path = HEALTH_PATH if HEALTH_PATH.startswith("/") else f"/{HEALTH_PATH}"
    return f"{base}{path}"


def get_chat_api_url() -> str:
    base = PDF_QUERY_API_URL.rstrip("/")
    path = CHAT_PATH if CHAT_PATH.startswith("/") else f"/{CHAT_PATH}"
    return f"{base}{path}"


def is_dev() -> bool:
    """True when DEPLOYMENT_ENV is 'dev' (enables dev-only UI)."""
    return DEPLOYMENT_ENV.strip().lower() == "dev"


def get_backend_display() -> str:
    """Return host:port for display when backend is off (e.g. 'localhost:8000')."""
    from urllib.parse import urlparse
    parsed = urlparse(PDF_QUERY_API_URL)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return f"{host}:{port}"
