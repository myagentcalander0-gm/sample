"""In-app markdown → PDF conversion. No external route required."""
from __future__ import annotations


def notes_markdown_to_pdf_bytes(text: str) -> bytes:
    """Convert notes markdown to PDF bytes. Uses weasyprint if available, else fpdf2 plain text."""
    text = (text or "").strip()
    if not text:
        text = " "

    # Prefer weasyprint (markdown → HTML → PDF)
    try:
        import markdown
        from weasyprint import HTML

        html_body = markdown.markdown(text, extensions=["extra", "nl2br"])
        html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body>{html_body}</body></html>"""
        return HTML(string=html_doc).write_pdf()
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: fpdf2 plain text (no markdown styling)
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    for line in text.replace("\r", "").split("\n"):
        pdf.multi_cell(0, 6, line or " ")
    return bytes(pdf.output())
