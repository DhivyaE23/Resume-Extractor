"""PDF parser module for extracting text from PDF resumes."""

import logging
from pathlib import Path

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file with validation and error handling."""
    path = Path(pdf_path)

    if not path.exists():
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        logger.error(f"Invalid file type: {path.suffix}")
        raise ValueError(f"File must be a PDF. Got: {path.suffix}")

    text = ""

    try:
        reader = PdfReader(str(path))

        if len(reader.pages) == 0:
            logger.warning(f"PDF has no pages: {pdf_path}")
            raise ValueError("PDF file contains no pages.")

        for page_num, page in enumerate(reader.pages, 1):
            try:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            except Exception as exc:
                logger.warning(f"Failed to extract text from page {page_num}: {str(exc)}")
                continue

        if not text.strip():
            logger.warning(f"No readable text found in PDF: {pdf_path}")
            raise ValueError("PDF does not contain readable text.")

        logger.info(f"Successfully extracted text from {pdf_path}")
        return text

    except PdfReadError as exc:
        logger.error(f"PDF read error: {str(exc)}")
        raise ValueError(f"Failed to read PDF file: {str(exc)}") from exc
    except IOError as exc:
        logger.error(f"IO error reading PDF: {str(exc)}")
        raise IOError(f"Error reading PDF file: {str(exc)}") from exc
