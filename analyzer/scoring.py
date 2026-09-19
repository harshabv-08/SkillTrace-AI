import re


SECTION_ALIASES = {
    "Professional Summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective"
    ],
    "Education": [
        "education",
        "academic background",
        "qualifications"
    ],
    "Experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment"
    ],
    "Projects": [
        "projects",
        "academic projects",
        "personal projects"
    ],
    "Skills": [
        "skills",
        "technical skills",
        "core skills",
        "technologies"
    ],
    "Certifications": [
        "certifications",
        "certificates",
        "courses"
    ],
    "Achievements": [
        "achievements",
        "awards",
        "accomplishments"
    ]
}


ACTION_VERBS = [
    "built", "developed", "created", "designed", "implemented",
    "analyzed", "managed", "led", "improved", "optimized",
    "automated", "engineered", "deployed", "developed",
    "integrated", "tested", "delivered"
]


def has_heading(text, aliases):
    """Detect a likely section heading."""

    lines = [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:
        cleaned = re.sub(r"[^a-z0-9+#& ]", "", line)

        for alias in aliases:
            if cleaned == alias.lower():
                return True

    return False


def analyze_sections(resume_text):
    """Perform a lightweight section audit."""

    scores = {}
    detected_sections = []

    for section, aliases in SECTION_ALIASES.items():

        present = has_heading(resume_text, aliases)

        if present:
            detected_sections.append(section)

            # Base score for having the section.
            score = 65

            if section == "Professional Summary":
                if len(resume_text.split()) >= 80:
                    score += 10

            if section == "Experience":
                if re.search(
                    r"\b(19|20)\d{2}\b",
                    resume_text
                ):
                    score += 10

            if section == "Projects":
                if re.search(
                    r"\b(built|developed|created|implemented|designed)\b",
                    resume_text,
                    re.IGNORECASE
                ):
                    score += 10

            if section == "Skills":
                score += 15

            scores[section] = min(score, 100)

        else:
            scores[section] = 0

    return {
        "scores": scores,
        "detected_sections": detected_sections
    }


def calculate_content_quality(resume_text):
    """Estimate resume content quality using explainable signals."""

    words = resume_text.split()
    word_count = len(words)

    if word_count < 150:
        length_score = 40
    elif word_count < 250:
        length_score = 70
    elif word_count <= 800:
        length_score = 100
    else:
        length_score = 75

    action_count = sum(
        len(re.findall(
            r"\b" + re.escape(verb) + r"\b",
            resume_text,
            re.IGNORECASE
        ))
        for verb in ACTION_VERBS
    )

    action_score = min(action_count * 8, 100)

    number_count = len(re.findall(r"\b\d+%?\b", resume_text))
    quant_score = min(number_count * 10, 100)

    quality_score = round(
        length_score * 0.40
        + action_score * 0.30
        + quant_score * 0.30,
        1
    )

    return {
        "score": quality_score,
        "word_count": word_count,
        "action_verbs": action_count,
        "quantifiable_items": number_count
    }


def calculate_readability(resume_text):
    """Estimate basic readability and structure."""

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return 0.0

    average_line_length = sum(len(line) for line in lines) / len(lines)

    score = 100

    if average_line_length > 180:
        score -= 20

    if len(lines) < 8:
        score -= 20

    if len(resume_text) > 12000:
        score -= 15

    return max(round(score, 1), 0.0)


def calculate_scores(
    resume_text,
    job_analysis,
    detected_skills
):
    """Calculate all major SkillTrace AI scores."""

    section_analysis = analyze_sections(resume_text)
    content_analysis = calculate_content_quality(resume_text)
    readability_score = calculate_readability(resume_text)

    section_values = list(section_analysis["scores"].values())

    section_score = (
        round(sum(section_values) / len(section_values), 1)
        if section_values
        else 0.0
    )

    structure_score = round(
        section_score * 0.65
        + readability_score * 0.35,
        1
    )

    keyword_score = job_analysis.get("keyword_match", 0.0)

    job_match_score = job_analysis.get("job_match", 0.0)

    skill_match_score = job_analysis.get("skill_match", 0.0)

    # ATS-style estimate:
    # Structure = 25%
    # Job keywords = 25%
    # Content quality = 25%
    # Readability = 25%
    ats_score = round(
        structure_score * 0.25
        + keyword_score * 0.25
        + content_analysis["score"] * 0.25
        + readability_score * 0.25,
        1
    )

    breakdown = {
        "Structure": structure_score,
        "Job Keywords": keyword_score,
        "Content Quality": content_analysis["score"],
        "Readability": readability_score
    }

    return {
        "ats_score": ats_score,
        "job_match_score": job_match_score,
        "skill_match": skill_match_score,
        "keyword_match": keyword_score,
        "structure_score": structure_score,
        "content_quality": content_analysis["score"],
        "readability": readability_score,
        "breakdown": breakdown,
        "section_scores": section_analysis["scores"],
        "detected_sections": section_analysis["detected_sections"],
        "content_analysis": content_analysis
    }