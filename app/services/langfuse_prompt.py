"""Fetch prompt content from Langfuse. Returns empty string if not configured or not connectable."""
from __future__ import annotations

from config import (
    LANGFUSE_PROMPT_NAME,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
    LANGFUSE_URL,
)


def get_prompt_from_langfuse() -> str:
    """
    Fetch prompt content from Langfuse by name (latest label).
    Returns empty string if Langfuse is not configured (pk/sk/url), not connectable, or on any error.
    """
    if not LANGFUSE_PUBLIC_KEY.strip() or not LANGFUSE_SECRET_KEY.strip():
        return ""

    try:
        from langfuse import Langfuse

        base = LANGFUSE_URL.strip()
        if base and not base.startswith("http"):
            base = f"https://{base}"
        client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            base_url=base or "https://cloud.langfuse.com",
        )
        prompt = client.get_prompt(LANGFUSE_PROMPT_NAME or "pdf-chat-prompt", label="latest")
        if prompt is None:
            return ""
        # TextPromptClient / ChatPromptClient expose .prompt for raw content
        content = getattr(prompt, "prompt", None) or getattr(prompt, "content", None)
        if content is None:
            return ""
        return content if isinstance(content, str) else str(content)
    except Exception:
        return ""
