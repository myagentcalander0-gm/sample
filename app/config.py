"""App configuration from environment."""
import os

# Set DEPLOYMENT_ENV=dev to enable dev-only UI (e.g. Refresh button).
DEPLOYMENT_ENV: str = os.getenv("DEPLOYMENT_ENV", "")

# Sidebar max width when expanded (e.g. "400px", "30rem"). Unset = use Streamlit default.
SIDEBAR_MAX_WIDTH: str = os.getenv("SIDEBAR_MAX_WIDTH", "900px")

# Backend API for PDF query chat. Set PDF_QUERY_API_URL in env or .env.
PDF_QUERY_API_URL: str = os.getenv("PDF_QUERY_API_URL", "http://localhost:8000")
# Streamlit app base URL (for external_loc when backend needs the host). Set STREAMLIT_APP_URL if auto-detect fails.
STREAMLIT_APP_URL: str = os.getenv("STREAMLIT_APP_URL", "")
HEALTH_PATH: str = os.getenv("HEALTH_PATH", "/health")
# How often to re-run the health check (seconds). Top bar fragment uses this.
HEALTH_CHECK_INTERVAL_SEC: float = float(os.getenv("HEALTH_CHECK_INTERVAL_SEC", "15"))
CHAT_PATH: str = os.getenv("CHAT_PATH", "/continue_chat")
# Optional API key sent as x-api-key header on backend requests.
X_API_KEY: str = os.getenv("X_API_KEY", "asd")


def get_api_headers() -> dict[str, str]:
    """Headers for backend API requests: Content-Type application/json and x-api-key."""
    key = (X_API_KEY or "asd").strip()
    return {
        "Content-Type": "application/json",
        "x-api-key": key,
    }


# Langfuse: prompt source (pk, sk, url). If set, Prompt editor pulls from Langfuse when empty.
LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_URL: str = os.getenv("LANGFUSE_URL", "https://cloud.langfuse.com")
LANGFUSE_PROMPT_NAME: str = os.getenv("LANGFUSE_PROMPT_NAME", "pdf-chat-prompt")


def get_health_url(base_url: str | None = None) -> str:
    base = (base_url or PDF_QUERY_API_URL).rstrip("/")
    path = HEALTH_PATH if HEALTH_PATH.startswith("/") else f"/{HEALTH_PATH}"
    return f"{base}{path}"


def get_chat_api_url(base_url: str | None = None) -> str:
    base = (base_url or PDF_QUERY_API_URL).rstrip("/")
    path = CHAT_PATH if CHAT_PATH.startswith("/") else f"/{CHAT_PATH}"
    return f"{base}{path}"


NOTES_TO_PDF_PATH: str = os.getenv("NOTES_TO_PDF_PATH", "notes_to_pdf")
# Base URL for notes→PDF: use Streamlit server (not the summarize API). Set NOTES_TO_PDF_BASE_URL if auto-detect fails.
NOTES_TO_PDF_BASE_URL: str = os.getenv("NOTES_TO_PDF_BASE_URL", "").strip()


def get_notes_to_pdf_url(base_url: str | None = None) -> str:
    """URL for POST notes text -> PDF. base_url should be the Streamlit server (not PDF_QUERY_API_URL)."""
    base = (base_url or "").rstrip("/")
    if not base:
        return ""
    path = NOTES_TO_PDF_PATH if NOTES_TO_PDF_PATH.startswith("/") else f"/{NOTES_TO_PDF_PATH}"
    return f"{base}{path}"


def get_pdf_detail_from_external_url(base_url: str | None = None) -> str:
    """URL for first-message endpoint: pdf_detail_from_external."""
    base = (base_url or PDF_QUERY_API_URL).rstrip("/")
    path = "pdf_detail_from_external"
    return f"{base}/{path}" if not path.startswith("/") else f"{base}{path}"


def is_dev() -> bool:
    """True when DEPLOYMENT_ENV is 'dev' (enables dev-only UI)."""
    return DEPLOYMENT_ENV.strip().lower() == "dev"


def get_backend_display(base_url: str | None = None) -> str:
    """Return host:port for display when backend is off (e.g. 'localhost:8000')."""
    from urllib.parse import urlparse
    url = base_url or PDF_QUERY_API_URL
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return f"{host}:{port}"
