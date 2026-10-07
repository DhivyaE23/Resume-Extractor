from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.extractor import (
    extract_dates,
    extract_education,
    extract_email,
    extract_experience,
    extract_name,
    extract_organizations,
    extract_phone,
    extract_skills,
)
from app.matcher import calculate_match, extract_job_skills
from app.parser import extract_text_from_pdf

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Resume Information Extractor",
    description="API for extracting information from PDF resumes and matching them with job descriptions",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
MAX_RESUME_SIZE = 10 * 1024 * 1024


def validate_pdf(file: UploadFile):
    """
    Validate that the uploaded file is a PDF.
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


async def get_resume_text(file: UploadFile) -> tuple[str, str]:
    validate_pdf(file)
    filename = Path(file.filename).name

    content = await file.read(MAX_RESUME_SIZE + 1)
    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=413, detail="Resume PDF must be 10 MB or smaller.")

    with NamedTemporaryFile(suffix=".pdf", delete=False) as buffer:
        buffer.write(content)
        file_path = Path(buffer.name)

    try:
        text = extract_text_from_pdf(str(file_path))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Unable to read the PDF file.") from exc
    finally:
        file_path.unlink(missing_ok=True)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No selectable text was found. Scanned PDFs require Tesseract OCR to be installed.",
        )

    return filename, text


def get_resume_details(filename: str, text: str) -> dict:
    return {
        "filename": filename,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "dates": extract_dates(text),
        "organizations": extract_organizations(text),
    }


@app.get("/", response_class=HTMLResponse)
async def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """
    Extract information from a PDF resume.
    """

    filename, text = await get_resume_text(file)
    return get_resume_details(filename, text)


@app.post("/match-resume")
async def match_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    """
    Match a resume against a job description.
    """

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    _, resume_text = await get_resume_text(file)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_job_skills(job_description)

    if not job_skills:
        raise HTTPException(status_code=400, detail="No recognized skills were found in the job description.")

    score, matched_skills, missing_skills = calculate_match(resume_skills, job_skills)

    return {
        "filename": file.filename,
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


@app.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    filename, text = await get_resume_text(file)
    job_skills = extract_job_skills(job_description)

    if not job_skills:
        raise HTTPException(status_code=400, detail="No recognized skills were found in the job description.")

    resume_skills = extract_skills(text)
    score, matched_skills, missing_skills = calculate_match(resume_skills, job_skills)
    result = get_resume_details(filename, text)
    result.update({
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    })
    return result
