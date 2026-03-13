"""Notes → PDF using pure Python only (fpdf2 + text sanitization). No WeasyPrint or system libraries."""
from __future__ import annotations

import re


# Printable ASCII only (32-126); fpdf2 can choke on other codepoints → "Not enough horizontal space"
def _to_printable_ascii(s: str, keep_newline: bool = True) -> str:
    """Force string to printable ASCII so fpdf2 never sees a bad character. Tab → space."""
    if not s:
        return " "
    out = []
    for c in s:
        if c == "\n" and keep_newline:
            out.append(c)
        elif c == "\t":
            out.append(" ")
        elif 32 <= ord(c) <= 126:
            out.append(c)
        else:
            out.append("?" if ord(c) > 126 else " ")
    return "".join(out) or " "


def _markdown_to_plain(text: str) -> str:
    """Strip markdown to plain text so PDF is readable without ** and #."""
    s = (text or "").replace("\r", "")
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    s = re.sub(r"^#+\s*", "", s, flags=re.MULTILINE)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return s


def _split_to_fit_width(pdf: object, line: str, max_width: float) -> list[str]:
    """Split a sanitized line so each chunk fits max_width in current PDF font."""
    safe = _to_printable_ascii(line, keep_newline=False)
    if not safe.strip():
        return [" "]

    chunks: list[str] = []
    current = ""
    for ch in safe:
        candidate = current + ch
        if candidate and pdf.get_string_width(candidate) <= (max_width - 0.5):
            current = candidate
            continue

        if current:
            chunks.append(current)

        # If a single character still does not fit (extremely unlikely), degrade to '?'
        if pdf.get_string_width(ch) <= (max_width - 0.5):
            current = ch
        else:
            current = "?"

    if current:
        chunks.append(current)
    return chunks or [" "]


def _build_pdf(plain: str) -> bytes:
    """Build PDF from plain text with width-safe splitting to avoid layout errors."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    usable_width = max(20.0, pdf.w - pdf.l_margin - pdf.r_margin)
    for line in plain.split("\n"):
        for part in _split_to_fit_width(pdf, line, usable_width):
            safe = part.strip() or " "
            # Always reset x to left margin before writing the next chunk.
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(usable_width, 6, safe)
    return bytes(pdf.output())


def notes_markdown_to_pdf_bytes(text: str) -> bytes:
    """Convert notes to PDF with cleaned text. Uses only fpdf2 (pure Python). All text forced to printable ASCII to avoid 'Not enough horizontal space'."""
    text = (text or "").strip()
    if not text:
        text = " "
    plain = _markdown_to_plain(text)
    plain = _to_printable_ascii(plain)  # tabs → space, non-printable → ? or space

    try:
        return _build_pdf(plain)
    except Exception as e:
        if "horizontal" in str(e).lower() or "space" in str(e).lower() or "character" in str(e).lower():
            # Retry with tabs removed and strict printable-ASCII only
            plain = plain.replace("\t", " ")
            plain = _to_printable_ascii(plain)
            return _build_pdf(plain)
        raise
