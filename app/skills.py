import re


SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "C#",
    "JavaScript",
    "TypeScript",
    "Go",
    "HTML",
    "CSS",
    "SQL",
    "MongoDB",
    "MySQL",
    "PostgreSQL",
    "React",
    "Angular",
    "Next.js",
    "Node.js",
    "Express.js",
    "FastAPI",
    "Flask",
    "Django",
    "Spring Boot",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analytics",
    "Power Query",
    "DAX",
    "Power BI",
    "Tableau",
    "Excel",
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "Terraform",
    "Redis",
    "GraphQL",
    "GitHub Actions",
    "REST API",
    "AWS",
    "Azure",
    "Linux",
    "TensorFlow",
    "PyTorch",
    "spaCy",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "OpenCV",
    "Scikit-learn",
    "PyQt5",
    "Jupyter Notebook",
]

SKILL_ALIASES = {
    "HTML": ("HTML5",),
    "CSS": ("CSS3",),
    "Go": ("Golang",),
    "React": ("ReactJS",),
    "Node.js": ("NodeJS",),
    "Scikit-learn": ("scikit learn", "sklearn"),
}


def find_skills(text):
    found_skills = []
    normalized_text = text.lower()

    for skill in SKILLS:
        if skill == "C":
            matched = re.search(r"(?<![a-zA-Z0-9+#])C(?![a-zA-Z0-9+#])", text) is not None
        elif skill == "Go":
            matched = re.search(r"(?<![a-zA-Z0-9])(?:Go|Golang)(?![a-zA-Z0-9])", text) is not None
        else:
            variants = (skill, *SKILL_ALIASES.get(skill, ()))
            matched = any(
                re.search(
                    rf"(?<![a-z0-9]){re.escape(variant.lower())}(?![a-z0-9])",
                    normalized_text,
                )
                for variant in variants
            )

        if matched:
            found_skills.append(skill)

    return found_skills
