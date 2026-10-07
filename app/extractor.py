import re

import spacy

from .skills import find_skills

nlp = spacy.load("en_core_web_sm")

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)+"
)
PHONE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d \t()./-]{6,18}\d(?!\d)")
URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+|(?:linkedin|github)\.com/\S+", re.IGNORECASE)
NAME_TOKEN_PATTERN = re.compile(r"^[^\W\d_][^\W\d_]*(?:[-'’][^\W\d_]+)*\.?$", re.UNICODE)

SECTION_GROUPS = {
    "education": {
        "education", "educational background", "academic background", "academic qualifications",
    },
    "experience": {
        "experience", "work experience", "professional experience", "internship experience",
        "employment history", "work history", "career history",
    },
    "skills": {"skills", "technical skills", "key skills", "core competencies"},
}
OTHER_SECTION_HEADINGS = {
    "summary", "professional summary", "objective", "career objective", "projects",
    "key projects", "academic projects", "certifications", "certificates",
    "certifications workshops", "certifications and workshops", "achievements", "awards",
    "publications", "languages", "interests", "volunteer experience", "references",
}
NAME_EXCLUSIONS = {
    "academic", "analyst", "bachelor", "candidate", "certification", "contact", "data",
    "developer", "director", "engineer", "experience", "intern", "internship", "master",
    "objective", "professional", "project", "senior", "software", "student", "summary",
    "technical", "technology", "tamil", "nadu", "krishnagiri", "san", "francisco",
    "california", "remote", "india", "united", "states", "resume", "curriculum", "vitae",
}
ORGANIZATION_SUFFIX_PATTERN = re.compile(
    r"\b(?:Pvt\.?\s+Ltd\.?|Limited|Ltd\.?|LLC|Inc\.?|Corporation|Corp\.?|Foundation|"
    r"University|College|School|Institute|Solutions|Technologies|Technology|Systems|Labs|Group)\b",
    re.IGNORECASE,
)
ORGANIZATION_EXCLUSIONS = {
    "academic", "analyst", "architected", "bachelor", "built", "candidate", "certification",
    "certifications", "cum", "data", "deployed", "developer", "developed", "director",
    "education", "engineer", "engineering", "emerging", "experience", "focus", "gpa",
    "graduated", "hosur", "intern", "internship", "krishnagiri", "laude", "master",
    "semester", "senior", "software", "student", "summary", "tn", "tx", "ca", "remote",
    "workshops",
}


def _clean_line(line: str) -> str:
    line = line.replace("\ufffd", " ")
    line = re.sub(r"[\t ]+", " ", line)
    return line.strip(" \t\r\n\u2022\u25aa\u25cf-")


def _heading_category(line: str) -> str | None:
    key = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
    for category, headings in SECTION_GROUPS.items():
        if key in headings:
            return category
    if key in OTHER_SECTION_HEADINGS:
        return "other"
    return None


def _section_lines(text: str, category: str) -> list[str] | None:
    lines = []
    active = False
    found_section = False

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line:
            continue

        heading = _heading_category(line)
        if heading == category:
            active = True
            found_section = True
            continue
        if heading is not None:
            if active:
                break
            continue
        if active:
            lines.append(line)

    return lines if found_section else None


def _header_lines(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line:
            continue
        if _heading_category(line) is not None:
            break
        lines.append(line)
        if len(lines) == 15:
            break
    return lines


def _is_name_candidate(value: str) -> bool:
    value = _clean_line(value)
    tokens = value.split()
    if not 2 <= len(tokens) <= 4:
        return False
    if any(not NAME_TOKEN_PATTERN.fullmatch(token) for token in tokens):
        return False
    if any(token.rstrip(".").lower() in NAME_EXCLUSIONS for token in tokens):
        return False
    return True


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0).strip(".,;:") if match else None


def extract_phone(text: str) -> str | None:
    for line in text.splitlines():
        for match in PHONE_PATTERN.finditer(line):
            digits = re.sub(r"\D", "", match.group(0))
            if 10 <= len(digits) <= 15:
                return re.sub(r"\s+", " ", match.group(0)).strip()
    return None


def extract_name(text: str) -> str | None:
    header = _header_lines(text)
    for line in header:
        line = EMAIL_PATTERN.sub(" ", line)
        line = PHONE_PATTERN.sub(" ", line)
        line = URL_PATTERN.sub(" ", line)
        line = re.sub(r"\b(?:linkedin|github)\b", " ", line, flags=re.IGNORECASE)
        for candidate in re.split(r"[|•·;,:]", line):
            candidate = _clean_line(candidate)
            if _is_name_candidate(candidate):
                return candidate

    for entity in nlp("\n".join(header)).ents:
        if entity.label_ == "PERSON" and _is_name_candidate(entity.text):
            return entity.text.strip()

    return None


def extract_skills(text: str) -> list[str]:
    return find_skills(text)


def extract_dates(text: str) -> list[str]:
    patterns = [
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b",
        r"\b\d{1,2}[/-]\d{4}\b",
        r"\b\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current)\b",
        r"\b\d{4}\b",
    ]
    dates = []
    for pattern in patterns:
        for match in re.findall(pattern, text, re.IGNORECASE):
            if match not in dates:
                dates.append(match)
    return dates


def _fallback_section_lines(text: str, category: str) -> list[str]:
    lines = [_clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    if category == "education":
        pattern = re.compile(r"\b(b\.?tech|bachelor|master|degree|university|college|school|gpa|cgpa)\b", re.I)
    else:
        pattern = re.compile(r"\b(intern|developer|engineer|analyst|scientist|trainee|manager)\b", re.I)
    return [line for line in lines if pattern.search(line)]


def extract_education(text: str) -> list[str]:
    lines = _section_lines(text, "education")
    return lines if lines is not None else _fallback_section_lines(text, "education")


def extract_experience(text: str) -> list[str]:
    lines = _section_lines(text, "experience")
    return lines if lines is not None else _fallback_section_lines(text, "experience")


def extract_organizations(text: str) -> list[str]:
    experience_lines = _section_lines(text, "experience") or []
    education_lines = _section_lines(text, "education") or []
    context_lines = experience_lines + education_lines
    if not context_lines:
        context_lines = [_clean_line(line) for line in text.splitlines() if _clean_line(line)]

    organizations = []

    def add_organization(value: str) -> None:
        value = _clean_line(value)
        words = re.findall(r"[a-zA-Z]+", value)
        if len(words) < 2 or find_skills(value):
            return
        if any(word.lower() in ORGANIZATION_EXCLUSIONS for word in words):
            return
        if value.casefold() not in {item.casefold() for item in organizations}:
            organizations.append(value)

    for raw_line in context_lines:
        line = _clean_line(raw_line)
        line = re.sub(r"\([^)]*\)", "", line)
        segments = re.split(r"[|•·]", line)
        for segment in segments:
            segment = re.sub(r"\s+-\s+.*$", "", segment)
            segment = re.sub(r"\s+(?:expected|graduated)\s+\d{4}.*$", "", segment, flags=re.I)
            segment = re.sub(r"\s+\d{4}(?:\s*[-–]\s*\d{4})?.*$", "", segment)
            suffixes = list(ORGANIZATION_SUFFIX_PATTERN.finditer(segment))
            if suffixes:
                suffix = suffixes[-1]
                candidate = segment[:suffix.end()]
                remainder = segment[suffix.end():]
                if suffix.group(0).lower() in {"college", "university", "school", "institute"}:
                    extension = re.match(r"\s+(?:of|for|at)\s+[A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)*", remainder)
                    if extension:
                        candidate += extension.group(0)
                candidate = re.sub(r"^(?:HSC|SSLC|SSC),\s*", "", candidate, flags=re.IGNORECASE)
                add_organization(candidate)

    for line, document in zip(context_lines, nlp.pipe(context_lines)):
        for entity in document.ents:
            if entity.label_ == "ORG":
                add_organization(entity.text)
    return organizations
