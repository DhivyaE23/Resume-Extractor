# 📄 Resume Information Extractor

A Python-based Resume Information Extractor that parses PDF resumes, extracts important information such as personal details, skills, education, experience, and compares resumes with job descriptions.

## Features

- Extract text from PDF resumes
- Identify Name, Email and Phone Number
- Extract known technical skills with token-aware matching
- Detect education, experience, and organizations using resume sections
- Resume Matching with Job Description
- REST API using FastAPI

PDF text is read in page layout order, with PyPDF2 used as a fallback. Image-only scanned PDFs can use OCR when Tesseract is installed and available on `PATH`; otherwise the API reports that OCR is required.

## Run

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Run the extraction regression tests with `python -m unittest discover -s tests`.

## Current Features

- PDF resume text extraction
- Personal information extraction
- Skill extraction
- Resume-job description matching
- FastAPI REST API

## Tech Stack

- Python
- FastAPI
- spaCy
- PyPDF2
- Regular Expressions

## Project Structure

```
Resume-Extractor/
│
├── app/
├── resumes/
├── requirements.txt
└── README.md
```

## Status

🚧 Project setup completed. Development in progress.
