# Resume Information Extractor

A FastAPI application that extracts candidate details from PDF resumes and compares listed technical skills with a job description.

## Features

- Layout-aware PDF text extraction using PyMuPDF, with PyPDF2 fallback
- Candidate name, email, and phone extraction
- Technical skill matching with common aliases
- Education, experience, organization, and date extraction
- Combined resume analysis endpoint and standalone extraction/matching endpoints
- Light-theme browser interface
- Upload-size validation and temporary-file cleanup
- Health endpoint at `/health`

Scanned PDFs use Tesseract OCR when it is installed and available on `PATH`. Without it, the API returns an actionable error for image-only PDFs. Install Tesseract with your operating system's package manager if scanned-resume OCR is required.

## Local Development

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Run regression and API tests:

```powershell
python -m unittest discover -s tests
```

## Deployment Without Docker

Install the requirements in a Python environment on your hosting service, then start the ASGI application with:

```text
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Configure the hosting service's start command with the same Uvicorn command. The application reads the platform-provided `PORT` environment variable and provides a `/health` endpoint.

## Project Structure

```text
app/          FastAPI routes and extraction logic
static/       Browser JavaScript and styles
templates/    Dashboard HTML
tests/        Extraction and API regression tests
```

Candidate resumes and environment secrets should not be committed to the repository.

