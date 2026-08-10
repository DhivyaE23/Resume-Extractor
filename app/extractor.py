import re
import spacy 
from skills import SKILLS
def extract_email(text):
    pattern=r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match=re.search(pattern,text)
    return match.group() if match else None

def extract_phone(text):
    pattern=r"(\+?\d{1,3}[- ]?)?\d{10}"
    match = re.search(pattern,text)
    return match.group() if match else None

def extract_name(text):
    """
    Simple approach:
    Assume the first non-empty line is the candidate's name.
    """
    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if line:
            return line

def extract_skills(text):
    """
    Extract known technical skills from resume text.
    """

    nlp = spacy.load("en_core_web_sm")

    doc = nlp(text)

    resume_text = doc.text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill.lower() in resume_text:
            found_skills.append(skill)

    return found_skills
def extract_dates(text):
    """
    Extract common date formats from resume text.
    """

    patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b",
        r"\b\d{1,2}[/-]\d{4}\b",
        r"\b\d{4}\s*[-–]\s*\d{4}\b",
        r"\b\d{4}\b"
    ]

    dates = []

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:
            if match not in dates:
                dates.append(match)

    return dates


def extract_education(text):
    """
    Extract lines related to education.
    """

    education_keywords = [
        "b.tech",
        "btech",
        "b.e",
        "bachelor",
        "m.tech",
        "mtech",
        "m.e",
        "master",
        "degree",
        "college",
        "university",
        "school",
        "education"
    ]

    education = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        if any(keyword in line_lower for keyword in education_keywords):
            education.append(line)

    return education


def extract_experience(text):
    """
    Extract lines related to work experience.
    """

    experience_keywords = [
        "intern",
        "internship",
        "developer",
        "engineer",
        "analyst",
        "experience",
        "software",
        "data scientist",
        "project manager",
        "trainee"
    ]

    experience = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        line_lower = line.lower()

        if any(keyword in line_lower for keyword in experience_keywords):
            experience.append(line)

    return experience


    return None