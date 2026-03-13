"""Notes → PDF using pure Python only (fpdf2 + text sanitization). No WeasyPrint or system libraries."""
from __future__ import annotations

import re
import unicodedata


# Map "weird" (non-ASCII) characters to safe ASCII for PDF. Editor keeps originals; only PDF export uses these.
# Add more entries as needed; these are common symbols that break fpdf2 or look wrong in PDF.
WEIRD_TO_SAFE: dict[str, str] = {
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2022": "*",   # bullet
    "\u2026": "...", # ellipsis
    "\u2192": "->",  # right arrow
    "\u2190": "<-",  # left arrow
    "\u2194": "<->", # left-right arrow
    "\u00a0": " ",   # nbsp
    "\u00ae": "(R)", # registered
    "\u2122": "(TM)",# trademark
    "\u00a9": "(c)", # copyright
}


def _weird_to_safe(text: str) -> str:
    """Replace known weird characters with safe ASCII. Original notes in app are unchanged; use this only for the PDF copy."""
    for char, safe in WEIRD_TO_SAFE.items():
        text = text.replace(char, safe)
    return text


# Printable ASCII only (32-126); fpdf2 can choke on other codepoints
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


def _build_pdf(plain: str) -> bytes:
    """Build PDF from plain text. Each line forced to printable ASCII before multi_cell."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    for line in plain.split("\n"):
        safe = _to_printable_ascii(line, keep_newline=False).strip() or " "
        pdf.multi_cell(0, 6, safe)
    return bytes(pdf.output())


def notes_markdown_to_pdf_bytes(text: str) -> bytes:
    """Convert notes to PDF with cleaned text. Uses only fpdf2 (pure Python). All text forced to printable ASCII to avoid 'Not enough horizontal space'."""
    text = (text or "").strip()
    if not text:
        text = " "
    plain = _markdown_to_plain(text)
    plain = _weird_to_safe(plain)      # replace known symbols with safe ASCII (→ ->, • *, etc.)
    plain = _to_printable_ascii(plain) # any remaining non-ASCII → ? or space

    try:
        return _build_pdf(plain)
    except Exception as e:
        if "horizontal" in str(e).lower() or "space" in str(e).lower() or "character" in str(e).lower():
            # Retry with tabs removed and strict printable-ASCII only
            plain = plain.replace("\t", " ")
            plain = _to_printable_ascii(plain)
            return _build_pdf(plain)
        raise
