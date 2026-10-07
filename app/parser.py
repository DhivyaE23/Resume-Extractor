import re
import shutil
from pathlib import Path

import pymupdf
from PyPDF2 import PdfReader


def normalize_resume_text(text: str) -> str:
    text = text.replace("\ufffd", " ").replace("\u00ad", "")
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _extract_with_pypdf(pdf_path: str) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File must be a PDF. Got: {path.suffix}")

    reader = PdfReader(str(path))
    if not reader.pages:
        raise ValueError("PDF file contains no pages.")
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File must be a PDF. Got: {path.suffix}")

        with pymupdf.open(str(path)) as document:
            if document.page_count == 0:
                raise ValueError("PDF file contains no pages.")

            page_texts = []
            tesseract_available = shutil.which("tesseract") is not None

            for page in document:
                page_text = page.get_text("text", sort=True)
                if not page_text.strip() and tesseract_available:
                    try:
                        text_page = page.get_textpage_ocr(language="eng", dpi=300, full=True)
                        page_text = page.get_text("text", textpage=text_page, sort=True)
                    except (OSError, RuntimeError, ValueError):
                        page_text = ""
                page_texts.append(page_text)

        text = normalize_resume_text("\n\n".join(page_texts))
        if text:
            return text
    except (pymupdf.FileDataError, OSError):
        return normalize_resume_text(_extract_with_pypdf(pdf_path))

    return normalize_resume_text(_extract_with_pypdf(pdf_path))
