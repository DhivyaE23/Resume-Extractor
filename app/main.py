from fastapi import FastAPI, UploadFile, File,Form
from parser import extract_text_from_pdf
from extractor import (
    extract_name,
    extract_email,
    extract_phone,
    extract_skills,
    extract_dates,
    extract_education,
    extract_experience,
)
from matcher import extract_job_skills, calculate_match
app = FastAPI(
    title="Resume Information Extractor",
    description="API for extracting information from PDF resumes",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Resume Information Extractor API is running"
    }


@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):

    file_path = f"../resumes/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    text = extract_text_from_pdf(file_path)

    return {
        "filename": file.filename,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "dates": extract_dates(text)
    }
@app.post("/match-resume")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    file_path = f"../resumes/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    resume_text = extract_text_from_pdf(file_path)

    resume_skills = extract_skills(resume_text)

    job_skills = extract_job_skills(job_description)

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