from parser import extract_text_from_pdf
from extractor import (
    extract_name,
    extract_email,
    extract_phone,
)

pdf_path = "E:/Resume-Extractor/resumes/professional_resume.pdf"

text = extract_text_from_pdf(pdf_path)

print("=" * 60)
print("RESUME DETAILS")
print("=" * 60)

print("Name :", extract_name(text))
print("Email:", extract_email(text))
print("Phone:", extract_phone(text))