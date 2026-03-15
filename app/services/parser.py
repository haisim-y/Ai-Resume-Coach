"""Resume file parsing service supporting PDF and DOCX formats."""

import logging
from io import BytesIO
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

from app.config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF using PyMuPDF (fitz). Join pages with newline."""
    text_pages: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_pages.append(page.get_text())
    return "\n".join(text_pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all paragraph text from a DOCX using python-docx with BytesIO."""
    document = Document(BytesIO(file_bytes))
    paragraphs = [para.text for para in document.paragraphs]
    return "\n".join(paragraphs)


def parse_resume(file_bytes: bytes, filename: str) -> str:
    """
    Route to the correct extractor based on file extension.

    Raises:
        ValueError: If the file exceeds MAX_FILE_SIZE_MB.
        ValueError: If the file extension is not in ALLOWED_EXTENSIONS.
        ValueError: If the extracted text is empty.
    """
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValueError(
            f"File size exceeds the {settings.MAX_FILE_SIZE_MB} MB limit."
        )

    extension = Path(filename).suffix.lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    logger.info("Parsing resume file: %s (ext=%s)", filename, extension)

    if extension == ".pdf":
        text = extract_text_from_pdf(file_bytes)
    else:
        text = extract_text_from_docx(file_bytes)

    if not text.strip():
        raise ValueError("No text could be extracted from the uploaded file.")

    return text
