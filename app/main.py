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