# Resume Extractor

A Python-based resume analysis API that parses PDF resumes, extracts candidate information, and matches resume skills to job requirements.

## Features

- Extract PDF resume text with validation
- Detect candidate name, email, phone number, and organizations
- Identify skills using a broader dictionary and matching logic
- Extract education, experience, and date information
- Match resumes against job descriptions with a match score
- Serve a light-themed landing page and API

## Tech Stack

- Python 3.11+
- FastAPI
- PyPDF2
- spaCy
- pytest

## Project Structure

```text
Resume-Extractor/
├── app/
│   ├── __init__.py
│   ├── extractor.py
│   ├── main.py
│   ├── matcher.py
│   ├── parser.py
│   └── skills.py
├── resumes/
├── tests/
├── README.md
├── requirements.txt
└── .gitignore
```

## Prerequisites

- Python 3.11 or newer
- pip
- A virtual environment is recommended

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/DhivyaE23/Resume-Extractor.git
   cd Resume-Extractor
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy language model
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. Run the FastAPI app
   ```bash
   uvicorn app.main:app --reload
   ```

6. Open the app
   - API docs: http://127.0.0.1:8000/docs
   - Landing page: http://127.0.0.1:8000/

## API Usage

### Extract resume details

```bash
curl -X POST "http://127.0.0.1:8000/extract-resume" \
  -F "file=@/path/to/resume.pdf"
```

### Match resume to a job description

```bash
curl -X POST "http://127.0.0.1:8000/match-resume" \
  -F "file=@/path/to/resume.pdf" \
  -F "job_description=We are looking for Python, FastAPI, SQL, Docker, and AWS experience."
```

## Notes

- PDF parsing now validates empty, non-PDF, and unreadable files.
- Matching uses a larger skill dictionary and normalizes names for cleaner comparison.
- Results are deduplicated and returned consistently.

## Testing

Run tests with:

```bash
pytest
```

## Status

The project is now set up for local development, improved validation, stronger matching, better docs, and a cleaner light-themed UI.
