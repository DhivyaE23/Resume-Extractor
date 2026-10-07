"""Resume Information Extractor FastAPI application."""

import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

try:
    from .parser import extract_text_from_pdf
    from .extractor import (
        extract_name,
        extract_email,
        extract_phone,
        extract_skills,
        extract_dates,
        extract_education,
        extract_experience,
        extract_organizations,
    )
    from .matcher import extract_job_skills, calculate_match
except ImportError:  # pragma: no cover
    from app.parser import extract_text_from_pdf
    from app.extractor import (
        extract_name,
        extract_email,
        extract_phone,
        extract_skills,
        extract_dates,
        extract_education,
        extract_experience,
        extract_organizations,
    )
    from app.matcher import extract_job_skills, calculate_match


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Information Extractor",
    description="API for extracting information from PDF resumes and matching them with job descriptions",
    version="1.0.0",
)

RESUMES_DIR = Path(__file__).resolve().parent.parent / "resumes"
RESUMES_DIR.mkdir(exist_ok=True)


def validate_pdf(file: UploadFile) -> None:
    """Validate that the uploaded file is a PDF."""
    if not file.filename:
        logger.error("No filename provided in upload")
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    if not file.filename.lower().endswith(".pdf"):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve a light-themed landing page."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Resume Extractor</title>
      <style>
        :root {
          --bg: #f4f7fb;
          --panel: #ffffff;
          --panel-alt: #eef4ff;
          --primary: #3b82f6;
          --primary-soft: #dbeafe;
          --text: #1f2937;
          --muted: #5b6475;
          --border: #e5e7eb;
          --shadow: 0 14px 34px rgba(15, 23, 42, 0.08);
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          font-family: Inter, "Segoe UI", sans-serif;
          background: linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%);
          color: var(--text);
        }
        .wrap {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 32px;
        }
        .card {
          width: min(980px, 100%);
          background: rgba(255,255,255,0.9);
          backdrop-filter: blur(12px);
          border: 1px solid var(--border);
          border-radius: 24px;
          box-shadow: var(--shadow);
          overflow: hidden;
        }
        .hero {
          display: grid;
          grid-template-columns: 1.2fr 0.8fr;
        }
        .content {
          padding: 48px 40px;
        }
        .eyebrow {
          display: inline-flex;
          background: var(--primary-soft);
          color: var(--primary);
          padding: 8px 12px;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        h1 {
          font-size: clamp(2.4rem, 3vw, 4rem);
          margin: 18px 0 16px;
          line-height: 1.05;
        }
        p {
          margin: 0 0 28px;
          font-size: 1.03rem;
          color: var(--muted);
          line-height: 1.7;
        }
        .actions {
          display: flex;
          gap: 14px;
          flex-wrap: wrap;
        }
        .button {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 14px 20px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
        }
        .button.primary {
          background: var(--primary);
          color: white;
          box-shadow: 0 10px 20px rgba(59,130,246,0.22);
        }
        .button.secondary {
          background: white;
          color: var(--text);
          border: 1px solid var(--border);
        }
        .stats {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 14px;
          margin-top: 34px;
        }
        .stat {
          background: var(--panel-alt);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 18px;
        }
        .stat strong {
          display: block;
          font-size: 1.35rem;
          margin-bottom: 6px;
        }
        .stat span {
          color: var(--muted);
          font-size: 0.9rem;
        }
        .preview {
          background: linear-gradient(180deg, #f8fbff 0%, #edf5ff 100%);
          border-left: 1px solid var(--border);
          padding: 30px 24px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .mockup {
          width: 100%;
          max-width: 360px;
          background: white;
          border: 1px solid var(--border);
          border-radius: 24px;
          padding: 18px;
          box-shadow: 0 12px 30px rgba(59,130,246,0.08);
        }
        .mockup-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        .dots {
          display: flex;
          gap: 8px;
        }
        .dots span {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          display: block;
        }
        .dots span:nth-child(1) { background: #f87171; }
        .dots span:nth-child(2) { background: #fbbf24; }
        .dots span:nth-child(3) { background: #4ade80; }
        .card-box {
          background: #f8fafc;
          border: 1px solid var(--border);
          border-radius: 14px;
          padding: 14px;
          margin-bottom: 12px;
        }
        .badge {
          display: inline-block;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 700;
          padding: 6px 10px;
          background: #e0f2fe;
          color: #0369a1;
        }
        .bar {
          height: 10px;
          border-radius: 999px;
          background: #e2e8f0;
          overflow: hidden;
          margin-top: 10px;
        }
        .bar > span {
          display: block;
          height: 100%;
          width: 72%;
          background: linear-gradient(90deg, #60a5fa, #2563eb);
          border-radius: inherit;
        }
        @media (max-width: 760px) {
          .hero { grid-template-columns: 1fr; }
          .preview { border-left: none; border-top: 1px solid var(--border); }
          .stats { grid-template-columns: 1fr; }
        }
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <div class="hero">
            <div class="content">
              <span class="eyebrow">AI Hiring Assistant</span>
              <h1>Extract talent from resumes in seconds.</h1>
              <p>
                Parse PDF resumes, pull out candidate details, compare skills with job requirements,
                and identify the strongest matches with a clean, professional workflow.
              </p>
              <div class="actions">
                <a class="button primary" href="/docs">Open API Docs</a>
                <a class="button secondary" href="/health">Check Health</a>
              </div>
              <div class="stats">
                <div class="stat"><strong>PDF</strong><span>Resume parsing</span></div>
                <div class="stat"><strong>Skills</strong><span>match scoring</span></div>
                <div class="stat"><strong>FastAPI</strong><span>REST endpoints</span></div>
              </div>
            </div>
            <div class="preview">
              <div class="mockup">
                <div class="mockup-header">
                  <div class="dots"><span></span><span></span><span></span></div>
                  <span class="badge">Match 72%</span>
                </div>
                <div class="card-box">
                  <strong>Candidate Profile</strong>
                  <div style="margin-top: 12px; color: var(--muted);">Alex Carter</div>
                  <div style="margin-top: 4px; color: var(--muted);">alex@email.com</div>
                </div>
                <div class="card-box">
                  <strong>Core Skills</strong>
                  <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">
                    <span class="badge">Python</span>
                    <span class="badge">FastAPI</span>
                    <span class="badge">SQL</span>
                  </div>
                </div>
                <div class="card-box">
                  <strong>Job Fit</strong>
                  <div class="bar"><span></span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """Extract information from a PDF resume."""
    try:
        validate_pdf(file)
        file_path = RESUMES_DIR / file.filename

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            text = extract_text_from_pdf(str(file_path))
        except (FileNotFoundError, ValueError, IOError) as exc:
            logger.error(f"PDF extraction error: {str(exc)}")
            raise HTTPException(status_code=400, detail=f"Unable to read the PDF file: {str(exc)}")

        if not text.strip():
            raise HTTPException(status_code=400, detail="The PDF does not contain readable text.")

        return {
            "filename": file.filename,
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "skills": extract_skills(text),
            "education": extract_education(text),
            "experience": extract_experience(text),
            "dates": extract_dates(text),
            "organizations": extract_organizations(text),
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        logger.error(f"Unexpected error in extract_resume: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the resume.")


@app.post("/match-resume")
async def match_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    """Match a resume against a job description."""
    try:
        validate_pdf(file)
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty.")

        file_path = RESUMES_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            resume_text = extract_text_from_pdf(str(file_path))
        except (FileNotFoundError, ValueError, IOError) as exc:
            logger.error(f"PDF extraction error: {str(exc)}")
            raise HTTPException(status_code=400, detail=f"Unable to read the PDF file: {str(exc)}")

        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="The PDF does not contain readable text.")

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
            "total_required_skills": len(job_skills),
            "matched_count": len(matched_skills),
            "missing_count": len(missing_skills),
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        logger.error(f"Unexpected error in match_resume: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while matching the resume.")
