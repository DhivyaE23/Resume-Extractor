"""Resume and job description matching module."""

import logging

from .skills import FLAT_SKILLS

logger = logging.getLogger(__name__)


def extract_job_skills(job_description: str):
    """Extract known skills from the job description."""
    if not job_description or not job_description.strip():
        logger.warning("Empty job description provided")
        return []

    job_text = job_description.lower()
    found_skills = []
    for skill in FLAT_SKILLS:
        if skill.lower() in job_text:
            found_skills.append(skill)

    return list(dict.fromkeys(found_skills))


def calculate_match(resume_skills, job_skills):
    """Calculate the percentage of job-required skills present in the resume."""
    if not job_skills:
        logger.warning("No job skills provided for matching")
        return 0.0, [], []

    resume_skills_lower = {skill.lower() for skill in resume_skills}
    job_skills_lower = {skill.lower() for skill in job_skills}

    matched = resume_skills_lower.intersection(job_skills_lower)
    missing = job_skills_lower - resume_skills_lower

    score = (len(matched) / len(job_skills_lower)) * 100 if job_skills_lower else 0.0

    matched_skills = [skill for skill in job_skills if skill.lower() in matched]
    missing_skills = [skill for skill in job_skills if skill.lower() in missing]

    return round(score, 2), matched_skills, missing_skills
