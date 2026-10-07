import pytest

from app.matcher import calculate_match, extract_job_skills
from app.parser import extract_text_from_pdf
from app.extractor import extract_skills, extract_email, extract_phone


@pytest.fixture
def sample_job_description():
    return "We are looking for Python, FastAPI, SQL, Docker, and AWS experience."


@pytest.fixture
def sample_resume_text():
    return """
    Alice Johnson
    alice@example.com
    +1 415 555 1234
    Skills: Python, FastAPI, SQL, Docker, AWS
    Education: B.Tech in Computer Science
    Experience: Worked as a software engineer with Python and backend APIs.
    """


def test_extract_job_skills(sample_job_description):
    skills = extract_job_skills(sample_job_description)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQL" in skills


def test_calculate_match():
    resume_skills = ["Python", "FastAPI", "SQL", "AWS"]
    job_skills = ["Python", "FastAPI", "SQL", "Docker", "AWS"]
    score, matched, missing = calculate_match(resume_skills, job_skills)

    assert score == 80.0
    assert "Python" in matched
    assert "Docker" in missing


def test_extract_skills(sample_resume_text):
    skills = extract_skills(sample_resume_text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQL" in skills


def test_extract_contact_details(sample_resume_text):
    assert extract_email(sample_resume_text) == "alice@example.com"
    assert extract_phone(sample_resume_text) == "+1 415 555 1234"


def test_pdf_validation_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("missing-file.pdf")
