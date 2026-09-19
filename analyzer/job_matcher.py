import json
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from analyzer.skill_detector import extract_skill_names_from_text


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROLES_FILE = os.path.join(BASE_DIR, "data", "roles.json")


def load_roles():
    """Load the built-in career role database."""

    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def find_role(target_role):
    """Find a role using flexible matching."""

    roles = load_roles()

    if not target_role:
        return None

    target = target_role.lower().strip()

    if target in roles:
        return roles[target]

    for role_name, role_data in roles.items():
        if target == role_name.lower():
            return role_data

    for role_name, role_data in roles.items():
        if target in role_name.lower() or role_name.lower() in target:
            return role_data

    return None


def normalize_words(text):
    return set(
        re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9+#.-]{1,30}\b",
            text.lower()
        )
    )


def calculate_text_similarity(resume_text, target_text):
    """Calculate TF-IDF cosine similarity."""

    if not resume_text.strip() or not target_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        matrix = vectorizer.fit_transform(
            [resume_text, target_text]
        )

        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

        return round(float(similarity) * 100, 1)

    except Exception:
        return 0.0


def analyze_job_match(
    resume_text,
    target_role="",
    job_description="",
    detected_skills=None
):
    """Analyze how closely a resume matches a role or job description."""

    detected_skills = detected_skills or {
        "technical": [],
        "soft": [],
        "tools": [],
        "other": []
    }

    role_data = find_role(target_role)

    if job_description.strip():
        target_text = job_description.strip()
        analysis_source = "Job Description"

        required_skills = extract_skill_names_from_text(target_text)

        if role_data:
            role_expected = role_data.get("skills", [])
            required_skills = list(
                dict.fromkeys(required_skills + role_expected)
            )

    elif role_data:
        target_text = (
            role_data.get("description", "")
            + " "
            + " ".join(role_data.get("skills", []))
        )

        analysis_source = "Built-in Role Profile"
        required_skills = role_data.get("skills", [])

    elif target_role:
        target_text = target_role
        analysis_source = "Custom Role"
        required_skills = extract_skill_names_from_text(target_role)

    else:
        target_text = ""
        analysis_source = "General Resume Analysis"
        required_skills = []

    candidate_skills = []

    for group in ["technical", "soft", "tools", "other"]:
        candidate_skills.extend(detected_skills.get(group, []))

    candidate_skills = list(dict.fromkeys(
        skill.lower() for skill in candidate_skills
    ))

    required_normalized = list(
        dict.fromkeys(skill.lower() for skill in required_skills)
    )

    matched_skills = []
    missing_skills = []

    for required in required_normalized:

        if any(
            required == candidate
            or required in candidate
            or candidate in required
            for candidate in candidate_skills
        ):
            matched_skills.append(required)
        else:
            missing_skills.append(required)

    if required_normalized:
        skill_match = round(
            (len(matched_skills) / len(required_normalized)) * 100,
            1
        )
    else:
        skill_match = 0.0

    if target_text:
        semantic_match = calculate_text_similarity(
            resume_text,
            target_text
        )
    else:
        semantic_match = 0.0

    resume_words = normalize_words(resume_text)

    if target_text:
        target_words = normalize_words(target_text)

        important_words = {
            word for word in target_words
            if len(word) >= 3
        }

        matched_keywords = sorted(
            word for word in important_words
            if word in resume_words
        )

        missing_keywords = sorted(
            word for word in important_words
            if word not in resume_words
        )[:30]

        keyword_match = round(
            (len(matched_keywords) / max(len(important_words), 1)) * 100,
            1
        )

    else:
        matched_keywords = []
        missing_keywords = []
        keyword_match = 0.0

    job_match = round(
        (
            skill_match * 0.55
            + semantic_match * 0.30
            + keyword_match * 0.15
        ),
        1
    )

    return {
        "analysis_source": analysis_source,
        "role": target_role or "General Analysis",
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match": skill_match,
        "semantic_match": semantic_match,
        "matched_keywords": matched_keywords[:30],
        "missing_keywords": missing_keywords,
        "keyword_match": keyword_match,
        "job_match": job_match,
        "role_data": role_data or {}
    }