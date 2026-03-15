"""Tests for the resume parsing service."""

import pytest
import fitz  # PyMuPDF

from app.services.parser import extract_text_from_pdf, parse_resume


def _make_minimal_pdf(text: str = "Hello Resume") -> bytes:
    """Create a minimal in-memory PDF containing the given text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_unsupported_extension() -> None:
    """parse_resume should raise ValueError for unsupported file extensions."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        parse_resume(b"data", "resume.txt")


def test_empty_pdf_raises() -> None:
    """parse_resume should raise ValueError when no text can be extracted."""
    empty_doc = fitz.open()
    empty_doc.new_page()  # blank page, no text
    empty_bytes = empty_doc.tobytes()
    empty_doc.close()

    with pytest.raises(ValueError, match="No text could be extracted"):
        parse_resume(empty_bytes, "resume.pdf")


def test_pdf_extraction_returns_string() -> None:
    """extract_text_from_pdf should return a non-empty string from a valid PDF."""
    pdf_bytes = _make_minimal_pdf("Software Engineer with Python experience")
    result = extract_text_from_pdf(pdf_bytes)
    assert isinstance(result, str)
    assert len(result.strip()) > 0
