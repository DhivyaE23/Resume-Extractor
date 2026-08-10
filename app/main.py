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
from matcher import(
    extract_job_skills,
    calculate_match
)

pdf_path = "E:/Resume-Extractor/resumes/professional_resume.pdf"

text = extract_text_from_pdf(pdf_path)

print("=" * 60)
print("RESUME DETAILS")
print("=" * 60)

print("Name :", extract_name(text))
print("Email:", extract_email(text))
print("Phone:", extract_phone(text))
print("\nSkills:")
for skill in extract_skills(text):
    print("-", skill)
print("\nEducation:")
for education in extract_education(text):
    print("-", education)

print("\nExperience:")
for experience in extract_experience(text):
    print("-", experience)

print("\nDates:")
for date in extract_dates(text):
    print("-", date)

print("\n" + "=" * 60)
print("JOB DESCRIPTION MATCHING")
print("=" * 60)

with open("../job_description.txt", "r", encoding="utf-8") as file:
    job_description = file.read()

job_skills = extract_job_skills(job_description)

resume_skills = extract_skills(text)

score, matched_skills, missing_skills = calculate_match(
    resume_skills,
    job_skills
)

print(f"\nMatch Score: {score}%")

print("\nMatched Skills:")
for skill in matched_skills:
    print("✓", skill)

print("\nMissing Skills:")
for skill in missing_skills:
    print("✗", skill)