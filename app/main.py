from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from parser import extract_text_from_pdf

from extractor import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    extract_dates,
    extract_education,
    extract_experience,
    extract_organizations,
)

from matcher import (
    extract_job_skills,
    calculate_match,
)


app = FastAPI(
    title="Resume Information Extractor",
    description="API for extracting information from PDF resumes and matching them with job descriptions",
    version="1.0.0"
)


def validate_pdf(file: UploadFile):
    """
    Validate that the uploaded file is a PDF.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


@app.get("/")
def home():
    return {
        "message": "Resume Information Extractor API is running"
    }


@app.post("/extract-resume")
async def extract_resume(
    file: UploadFile = File(...)
):
    """
    Extract information from a PDF resume.
    """

    validate_pdf(file)

    file_path = f"../resumes/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        text = extract_text_from_pdf(file_path)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the PDF file."
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="The PDF does not contain readable text."
        )

    return {
        "filename": file.filename,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "dates": extract_dates(text),
        "organizations": extract_organizations(text)
    }


@app.post("/match-resume")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Match a resume against a job description.
    """

    validate_pdf(file)

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    file_path = f"../resumes/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    try:
        resume_text = extract_text_from_pdf(file_path)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read the PDF file."
        )

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The PDF does not contain readable text."
        )

    resume_skills = extract_skills(resume_text)

    job_skills = extract_job_skills(job_description)

    if not job_skills:
        raise HTTPException(
            status_code=400,
            detail="No recognized skills were found in the job description."
        )

    score, matched_skills, missing_skills = calculate_match(
        resume_skills,
        job_skills
    )

    return {
        "filename": file.filename,
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
