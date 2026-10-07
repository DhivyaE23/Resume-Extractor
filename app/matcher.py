import re

from .skills import SKILL_ALIASES, find_skills


def _skill_pattern(skill):
    if skill == "C":
        return re.compile(r"(?<![a-zA-Z0-9+#])C(?![a-zA-Z0-9+#])")
    if skill == "Go":
        return re.compile(r"(?<![a-zA-Z0-9])(?:Go|Golang)(?![a-zA-Z0-9])")

    variants = (skill, *SKILL_ALIASES.get(skill, ()))
    alternatives = "|".join(re.escape(variant) for variant in variants)
    return re.compile(rf"(?<![a-z0-9])(?:{alternatives})(?![a-z0-9])", re.IGNORECASE)


def find_skill_evidence(resume_text, matched_skills, max_excerpt_length=220):
    """Return the first resume line supporting each matched skill."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in resume_text.splitlines()]
    evidence = []

    for skill in matched_skills:
        pattern = _skill_pattern(skill)
        excerpt = next((line for line in lines if pattern.search(line)), None)
        if excerpt is None:
            continue
        if len(excerpt) > max_excerpt_length:
            excerpt = excerpt[: max_excerpt_length - 3].rstrip() + "..."
        evidence.append({"skill": skill, "excerpt": excerpt})

    return evidence


def extract_job_skills(job_description):
    """
    Extract known skills from the job description.
    """

    return find_skills(job_description)


def calculate_match(resume_skills, job_skills):
    """
    Calculate the percentage of job-required skills
    present in the resume.
    """

    resume_skills_lower = {
        skill.lower() for skill in resume_skills
    }

    job_skills_lower = {
        skill.lower() for skill in job_skills
    }

    if not job_skills_lower:
        return 0, [], list(job_skills)

    matched = resume_skills_lower.intersection(job_skills_lower)

    missing = job_skills_lower - resume_skills_lower

    score = (len(matched) / len(job_skills_lower)) * 100

    matched_skills = [
        skill for skill in job_skills
        if skill.lower() in matched
    ]

    missing_skills = [
        skill for skill in job_skills
        if skill.lower() in missing
    ]

    return round(score, 2), matched_skills, missing_skills
