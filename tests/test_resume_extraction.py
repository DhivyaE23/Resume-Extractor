import asyncio
import tempfile
import unittest
from pathlib import Path

import httpx
import pymupdf

from app.extractor import (
    extract_education,
    extract_email,
    extract_experience,
    extract_name,
    extract_organizations,
    extract_phone,
    extract_skills,
)
from app.main import MAX_RESUME_SIZE, app
from app.matcher import calculate_match, find_skill_evidence
from app.parser import extract_text_from_pdf
from app.skills import find_skills


class ResumeApiTests(unittest.TestCase):
    def post(self, path, **kwargs):
        async def send_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.post(path, **kwargs)

        return asyncio.run(send_request())

    def get(self, path):
        async def send_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.get(path)

        return asyncio.run(send_request())

    def test_health_endpoint_reports_ready(self):
        response = self.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_homepage_uses_resume_extractor_branding(self):
        response = self.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Resume Extractor", response.text)
        self.assertNotIn("CV Desk", response.text)

    def test_analyze_endpoint_returns_extraction_and_match_in_one_response(self):
        pdf_path = Path(__file__).resolve().parents[1] / "resumes" / "professional_resume.pdf"
        response = self.post(
            "/analyze-resume",
            files={"file": (pdf_path.name, pdf_path.read_bytes(), "application/pdf")},
            data={"job_description": "Python, Kubernetes, PostgreSQL, C++"},
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["name"], "Alex Mercer")
        self.assertEqual(result["email"], "alex.mercer@email.com")
        self.assertEqual(result["phone"], "+1 (555) 019-2834")
        self.assertEqual(result["matched_skills"], ["Python", "PostgreSQL", "Kubernetes"])
        self.assertEqual(result["missing_skills"], ["C++"])
        self.assertEqual(result["match_score"], 75.0)
        evidence_by_skill = {
            item["skill"]: item["excerpt"] for item in result["matched_skill_evidence"]
        }
        self.assertIn("Python", evidence_by_skill)
        self.assertIn("Python", evidence_by_skill["Python"])
        self.assertIn("Kubernetes", evidence_by_skill["Kubernetes"])

    def test_analyze_endpoint_rejects_non_pdf_upload(self):
        response = self.post(
            "/analyze-resume",
            files={"file": ("resume.txt", b"resume text", "text/plain")},
            data={"job_description": "Python"},
        )
        self.assertEqual(response.status_code, 400)

    def test_extract_endpoint_enforces_upload_size_limit(self):
        response = self.post(
            "/extract-resume",
            files={"file": ("large.pdf", b"%" * (MAX_RESUME_SIZE + 1), "application/pdf")},
        )
        self.assertEqual(response.status_code, 413)

    def test_analyze_endpoint_reports_when_job_has_no_supported_skills(self):
        pdf_path = Path(__file__).resolve().parents[1] / "resumes" / "professional_resume.pdf"
        response = self.post(
            "/analyze-resume",
            files={"file": (pdf_path.name, pdf_path.read_bytes(), "application/pdf")},
            data={"job_description": "Strong communication and collaboration skills."},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("No recognized skills", response.json()["detail"])

    def test_extract_endpoint_explains_when_pdf_has_no_selectable_text(self):
        document = pymupdf.open()
        document.new_page().draw_rect(pymupdf.Rect(40, 40, 180, 100), fill=(0, 0, 0))
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "scanned.pdf"
            document.save(pdf_path)
            document.close()
            response = self.post(
                "/extract-resume",
                files={"file": (pdf_path.name, pdf_path.read_bytes(), "application/pdf")},
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Tesseract OCR", response.json()["detail"])


class ResumeExtractionTests(unittest.TestCase):
    def test_match_evidence_returns_source_line_and_normalizes_alias(self):
        evidence = find_skill_evidence(
            "Skills: HTML5, CSS3\nBuilt accessible pages with HTML5 and CSS3.",
            ["HTML", "CSS"],
        )
        self.assertEqual(
            evidence,
            [
                {"skill": "HTML", "excerpt": "Skills: HTML5, CSS3"},
                {"skill": "CSS", "excerpt": "Skills: HTML5, CSS3"},
            ],
        )

    def test_layout_extraction_preserves_contact_line_separation(self):
        document = pymupdf.open()
        page = document.new_page()
        page.insert_text((50, 50), "alex.mercer@email.com")
        page.insert_text((50, 70), "+1 (555) 019-2834")
        page.insert_text((50, 90), "Alex Mercer")
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "resume.pdf"
            document.save(pdf_path)
            document.close()
            text = extract_text_from_pdf(str(pdf_path))

        self.assertIn("alex.mercer@email.com", text)
        self.assertIn("Alex Mercer", text)
        self.assertEqual(extract_email(text), "alex.mercer@email.com")
        self.assertEqual(extract_phone(text), "+1 (555) 019-2834")
        self.assertEqual(extract_name(text), "Alex Mercer")

    def test_name_detection_uses_header_not_location_or_skill_entities(self):
        text = """DHIVYA E
Krishnagiri, Tamil Nadu | 9443294065 | edhivya236@gmail.com
TECHNICAL SKILLS
Java, Python, SQL
"""
        self.assertEqual(extract_name(text), "DHIVYA E")
        self.assertEqual(extract_email(text), "edhivya236@gmail.com")
        self.assertEqual(extract_phone(text), "9443294065")

    def test_skill_matching_observes_boundaries_and_common_aliases(self):
        skills = find_skills("JavaScript C++ MySQL HTML5 CSS3 sklearn Golang cloud")
        self.assertIn("JavaScript", skills)
        self.assertNotIn("Java", skills)
        self.assertIn("C++", skills)
        self.assertNotIn("C", skills)
        self.assertNotIn("SQL", skills)
        self.assertIn("HTML", skills)
        self.assertIn("CSS", skills)
        self.assertIn("Scikit-learn", skills)
        self.assertIn("Go", skills)

    def test_skill_match_uses_canonical_aliases(self):
        resume_skills = extract_skills("Experience building responsive sites with HTML5 and CSS3.")
        score, matched, missing = calculate_match(resume_skills, ["HTML", "CSS", "Python"])
        self.assertEqual(score, 66.67)
        self.assertEqual(matched, ["HTML", "CSS"])
        self.assertEqual(missing, ["Python"])

    def test_education_and_experience_are_limited_to_their_sections(self):
        text = """SUMMARY
Software engineer with experience in education technology.
EDUCATION
B.S. in Computer Science
State University
PROFESSIONAL EXPERIENCE
Senior Software Engineer
Vertex Tech Solutions
Built Python services.
PROJECTS
Education analytics project
"""
        education = extract_education(text)
        experience = extract_experience(text)
        self.assertEqual(education, ["B.S. in Computer Science", "State University"])
        self.assertEqual(experience, ["Senior Software Engineer", "Vertex Tech Solutions", "Built Python services."])
        self.assertNotIn("Education analytics project", experience)

    def test_organizations_are_extracted_from_work_and_education_sections(self):
        text = """TECHNICAL SKILLS
React, Python, Power BI
PROFESSIONAL EXPERIENCE
Software Engineer
Vertex Tech Solutions
EDUCATION
State University of Technology
"""
        organizations = extract_organizations(text)
        self.assertTrue(any("Vertex" in organization for organization in organizations), organizations)
        self.assertIn("State University of Technology", organizations)
        self.assertFalse(any(organization in {"React", "Python", "Power BI"} for organization in organizations))

    def test_organization_name_drops_school_credential_prefix(self):
        text = """EDUCATION
HSC, Udhayaam Matric Hr Sec School, Mathur 2023 | Percentage: 84.8%
"""
        self.assertIn("Udhayaam Matric Hr Sec School", extract_organizations(text))

    def test_bundled_professional_resume_extracts_header_and_section_data(self):
        pdf_path = Path(__file__).resolve().parents[1] / "resumes" / "professional_resume.pdf"
        text = extract_text_from_pdf(str(pdf_path))
        self.assertEqual(extract_name(text), "Alex Mercer")
        self.assertEqual(extract_email(text), "alex.mercer@email.com")
        self.assertEqual(extract_phone(text), "+1 (555) 019-2834")
        skills = extract_skills(text)
        self.assertIn("Kubernetes", skills)
        self.assertIn("Terraform", skills)
        self.assertTrue(any("State University" in item for item in extract_education(text)))
        self.assertTrue(any("Senior Software Engineer" in item for item in extract_experience(text)))
        organizations = extract_organizations(text)
        self.assertIn("Vertex Tech Solutions", organizations)
        self.assertIn("State University of Technology", organizations)


if __name__ == "__main__":
    unittest.main()