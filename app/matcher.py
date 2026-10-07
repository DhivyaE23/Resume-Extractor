from .skills import find_skills


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
