import re


SKILL_DATABASE = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "r", "go", "rust", "php", "kotlin", "swift"
    ],

    "AI & Machine Learning": [
        "machine learning", "deep learning", "artificial intelligence",
        "natural language processing", "nlp", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn",
        "supervised learning", "unsupervised learning"
    ],

    "Data & Analytics": [
        "data analysis", "data analytics", "data science",
        "pandas", "numpy", "matplotlib", "seaborn",
        "power bi", "tableau", "excel", "statistics",
        "data visualization", "sql"
    ],

    "Web Development": [
        "html", "css", "javascript", "react", "angular", "vue",
        "node.js", "node", "express", "flask", "django",
        "rest api", "api development"
    ],

    "Databases": [
        "mysql", "postgresql", "mongodb", "sqlite", "oracle",
        "database", "sql", "firebase"
    ],

    "Cloud & DevOps": [
        "aws", "azure", "google cloud", "gcp", "docker",
        "kubernetes", "git", "github", "gitlab", "ci/cd",
        "linux"
    ],

    "Tools & Technologies": [
        "git", "github", "vs code", "visual studio code",
        "jupyter", "postman", "figma", "powerpoint",
        "microsoft office"
    ],

    "Soft Skills": [
        "communication", "leadership", "teamwork",
        "problem solving", "problem-solving", "adaptability",
        "time management", "critical thinking",
        "creativity", "collaboration", "presentation",
        "analytical thinking"
    ]
}


def normalize_skill(skill):
    return skill.lower().strip()


def contains_skill(text, skill):
    """Check for a skill without incorrectly matching tiny words."""

    pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"

    return bool(re.search(pattern, text, re.IGNORECASE))


def detect_skills(resume_text):
    """Detect skills from resume text."""

    text = resume_text.lower()

    result = {
        "technical": [],
        "soft": [],
        "tools": [],
        "other": [],
        "categories": {}
    }

    category_mapping = {
        "Programming": "technical",
        "AI & Machine Learning": "technical",
        "Data & Analytics": "technical",
        "Web Development": "technical",
        "Databases": "technical",
        "Cloud & DevOps": "tools",
        "Tools & Technologies": "tools",
        "Soft Skills": "soft"
    }

    for category, skills in SKILL_DATABASE.items():

        detected = []

        for skill in skills:
            if contains_skill(text, skill):
                detected.append(skill.title() if skill != "c++" else "C++")

        # Remove duplicates while keeping order.
        detected = list(dict.fromkeys(detected))

        result["categories"][category] = detected

        target_group = category_mapping.get(category, "other")
        result[target_group].extend(detected)

    for key in ["technical", "soft", "tools", "other"]:
        result[key] = list(dict.fromkeys(result[key]))

    result["total"] = sum(
        len(result[key])
        for key in ["technical", "soft", "tools", "other"]
    )

    return result


def extract_skill_names_from_text(text):
    """Extract known skills from arbitrary text such as a job description."""

    if not text:
        return []

    found = []

    for skills in SKILL_DATABASE.values():
        for skill in skills:
            if contains_skill(text.lower(), skill):
                display_name = skill.title()

                if skill == "c++":
                    display_name = "C++"

                found.append(display_name)

    return list(dict.fromkeys(found))