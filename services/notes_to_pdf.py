"""In-app markdown → PDF conversion. No external route required."""
from __future__ import annotations

import unicodedata


def _sanitize_for_pdf(text: str, aggressive: bool = False) -> str:
    """Reduce character-conversion errors (e.g. 'not enough horizontal space' from unsupported glyphs)."""
    if not text:
        return " "
    # Strip control chars and normalize
    out = []
    for c in text:
        if unicodedata.category(c)[0] == "C":  # control, format, surrogate
            if c in "\n\r\t":
                out.append(c)
            else:
                out.append(" ")
        elif aggressive:
            # ASCII-only fallback when fonts can't render other codepoints
            out.append(c if ord(c) < 128 else "?")
        else:
            out.append(c)
    return "".join(out) or " "


def notes_markdown_to_pdf_bytes(text: str) -> bytes:
    """Convert notes markdown to PDF bytes. Uses weasyprint if available, else fpdf2 plain text. Sanitizes text to avoid character-rendering errors ('not enough horizontal space' etc.)."""
    text = (text or "").strip()
    if not text:
        text = " "
    text = _sanitize_for_pdf(text, aggressive=False)

    # Prefer weasyprint (markdown → HTML → PDF)
    try:
        import markdown
        from weasyprint import HTML

        html_body = markdown.markdown(text, extensions=["extra", "nl2br"])
        html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body>{html_body}</body></html>"""
        return HTML(string=html_doc).write_pdf()
    except ImportError:
        pass
    except Exception as e:
        err_msg = str(e).lower()
        # "not enough horizontal space" / glyph / character conversion: retry with ASCII-safe text
        if "horizontal" in err_msg or "glyph" in err_msg or "character" in err_msg or "space" in err_msg:
            try:
                import markdown as _md
                from weasyprint import HTML as _HTML
                text_ascii = _sanitize_for_pdf(text, aggressive=True)
                html_body = _md.markdown(text_ascii, extensions=["extra", "nl2br"])
                html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body>{html_body}</body></html>"""
                return _HTML(string=html_doc).write_pdf()
            except Exception:
                pass
        else:
            raise
    return _notes_to_pdf_fallback(text)


def _notes_to_pdf_fallback(text: str) -> bytes:
    """fpdf2 plain-text fallback (no markdown). Use sanitized text."""
    text = _sanitize_for_pdf(text, aggressive=True)
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    for line in text.replace("\r", "").split("\n"):
        pdf.multi_cell(0, 6, line or " ")
    return bytes(pdf.output())
