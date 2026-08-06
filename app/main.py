from parser import extract_text_from_pdf
pdf_path="E:/Resume-Extractor/resumes/professional_resume.pdf"
text=extract_text_from_pdf(pdf_path)
print("="*50)
print("Extracted Resume Text")
print("="*50)
print(text)