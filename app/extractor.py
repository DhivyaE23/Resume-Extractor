"""Resume information extraction module."""

import logging
import re

import spacy

from .skills import FLAT_SKILLS

logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found. Install it with: python -m spacy download en_core_web_sm")
    raise


def extract_email(text: str):
    """Extract email address from resume text."""
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_phone(text: str):
    """Extract phone number from resume text."""
    patterns = [
        r"\+91[-\s]?\d{10}",
        r"\b\d{10}\b",
        r"\+\d{1,3}[-\s]?\d{7,12}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return None


def extract_name(text: str):
    """Extract candidate name using spaCy NER."""
    try:
        doc = nlp(text)
        for entity in doc.ents:
            if entity.label_ == "PERSON":
                return entity.text.strip()
    except Exception as exc:
        logger.warning(f"Error in NER extraction: {str(exc)}")

    for line in text.split("\n"):
        line = line.strip()
        if line:
            return line

    return None


def extract_skills(text: str):
    """Extract known skills from resume text."""
    try:
        doc = nlp(text)
        resume_text = doc.text.lower()
    except Exception as exc:
        logger.warning(f"Error processing text with spaCy: {str(exc)}")
        resume_text = text.lower()

    found_skills = []
    for skill in FLAT_SKILLS:
        if skill.lower() in resume_text:
            found_skills.append(skill)

    return list(dict.fromkeys(found_skills))


def extract_dates(text: str):
    """Extract common date formats from resume text."""
    patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b\d{1,2}[/-]\d{4}\b",
        r"\b\d{4}\s*[-–]\s*\d{4}\b",
        r"\b\d{4}\b",
    ]

    dates = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match not in dates:
                dates.append(match)

    return dates


def extract_education(text: str):
    """Extract lines related to education."""
    education_keywords = [
        "b.tech",
        "btech",
        "b.e",
        "bachelor",
        "m.tech",
        "mtech",
        "master",
        "degree",
        "college",
        "university",
        "school",
        "education",
        "graduation",
        "gpa",
        "cgpa",
    ]

    education = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if any(keyword in line.lower() for keyword in education_keywords):
            education.append(line)

    return education


def extract_experience(text: str):
    """Extract lines related to work experience."""
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
        "trainee",
        "associate",
        "senior",
        "lead",
        "manager",
        "architect",
        "consultant",
    ]

    experience = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if any(keyword in line.lower() for keyword in experience_keywords):
            experience.append(line)

    return experience


def extract_organizations(text: str):
    """Extract organizations using spaCy NER."""
    try:
        doc = nlp(text)
        organizations = []
        for entity in doc.ents:
            if entity.label_ == "ORG":
                organization = entity.text.strip()
                if organization not in organizations:
                    organizations.append(organization)
        return organizations
    except Exception as exc:
        logger.warning(f"Error extracting organizations: {str(exc)}")
        return []
