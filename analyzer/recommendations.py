def generate_recommendations(
    resume_text,
    job_analysis,
    detected_skills,
    scores
):
    """Generate explainable resume improvement recommendations."""

    strengths = []
    critical_issues = []
    improvements = []
    skill_gaps = []

    ats_score = scores.get("ats_score", 0)
    job_match = scores.get("job_match_score", 0)

    # -----------------------------
    # Strengths
    # -----------------------------

    if ats_score >= 70:
        strengths.append(
            "Your resume has a solid overall structure and content foundation."
        )

    if scores.get("skill_match", 0) >= 60:
        strengths.append(
            "A good portion of the detected role-related skills are present."
        )

    if scores.get("content_quality", 0) >= 70:
        strengths.append(
            "Your resume contains useful evidence of skills and experience."
        )

    if scores.get("readability", 0) >= 80:
        strengths.append(
            "The extracted resume content appears reasonably readable."
        )

    if detected_skills.get("technical"):
        strengths.append(
            f"{len(detected_skills['technical'])} technical skills were detected."
        )

    if not strengths:
        strengths.append(
            "Your resume provides a starting point that can be improved systematically."
        )

    # -----------------------------
    # Critical issues
    # -----------------------------

    if ats_score < 50:
        critical_issues.append(
            "The current ATS-style estimate is below the recommended target range."
        )

    if not scores.get("detected_sections"):
        critical_issues.append(
            "Standard resume sections could not be detected reliably."
        )

    if scores.get("keyword_match", 0) < 40 and job_analysis.get("analysis_source") != "General Resume Analysis":
        critical_issues.append(
            "Several job-related keywords are missing from the resume."
        )

    if scores.get("content_analysis", {}).get("quantifiable_items", 0) == 0:
        critical_issues.append(
            "Very few measurable results or numbers were detected."
        )

    if scores.get("content_analysis", {}).get("action_verbs", 0) < 3:
        critical_issues.append(
            "More strong action-oriented language could improve project and experience descriptions."
        )

    # -----------------------------
    # Skill gaps
    # -----------------------------

    for skill in job_analysis.get("missing_skills", [])[:12]:
        skill_gaps.append({
            "skill": skill.title(),
            "priority": "High" if len(skill_gaps) < 4 else "Medium",
            "why": "This skill appears relevant to the selected role or job description.",
            "learning_direction": f"Build practical exposure through a small project, course, or hands-on exercise involving {skill.title()}."
        })

    # -----------------------------
    # Improvements
    # -----------------------------

    if scores.get("content_analysis", {}).get("quantifiable_items", 0) == 0:
        improvements.append({
            "title": "Add measurable achievements",
            "problem": "The resume has limited measurable evidence.",
            "why": "Numbers help recruiters understand the scale or result of your work.",
            "action": "Add percentages, counts, time saved, users reached, accuracy, performance improvements, or other genuine measurements.",
            "example": "Improved model accuracy from X% to Y% using documented evaluation results."
        })

    if scores.get("content_analysis", {}).get("action_verbs", 0) < 3:
        improvements.append({
            "title": "Strengthen action verbs",
            "problem": "Few strong action verbs were detected.",
            "why": "Action-oriented wording makes responsibilities and contributions clearer.",
            "action": "Begin project and experience bullets with verbs such as Built, Developed, Implemented, Analyzed, Designed, or Optimized.",
            "example": "Developed a Python-based analytics dashboard to visualize student performance data."
        })

    if scores.get("keyword_match", 0) < 60 and job_analysis.get("missing_keywords"):
        improvements.append({
            "title": "Improve job-specific keyword alignment",
            "problem": "Some important terms from the target role are not visible in the resume.",
            "why": "Relevant terminology can help automated screening and recruiter review.",
            "action": "Add genuinely relevant missing skills or terminology where they accurately describe your experience.",
            "example": "Include relevant technologies in the Skills or Projects section when you have real experience with them."
        })

    if scores.get("readability", 0) < 75:
        improvements.append({
            "title": "Improve readability",
            "problem": "The extracted text suggests the resume may benefit from clearer organization.",
            "why": "A clean structure helps both automated systems and human reviewers scan the document.",
            "action": "Use clear headings, concise bullets, consistent spacing, and simple formatting.",
            "example": "Use consistent section headings and short achievement-focused bullet points."
        })

    # -----------------------------
    # Section-specific improvements
    # -----------------------------

    section_scores = scores.get("section_scores", {})

    if section_scores.get("Professional Summary", 0) == 0:
        improvements.append({
            "title": "Add a professional summary",
            "problem": "A professional summary was not detected.",
            "why": "A concise summary can quickly communicate your profile and target direction.",
            "action": "Write 2–4 lines covering your current profile, key strengths, and career direction.",
            "example": "AI & Data Science student with hands-on experience in Python, data analysis, machine learning, and practical software projects."
        })

    if section_scores.get("Projects", 0) == 0:
        improvements.append({
            "title": "Add a projects section",
            "problem": "A projects section was not detected.",
            "why": "Projects provide practical evidence of technical ability, especially for students and early-career candidates.",
            "action": "Add 2–4 relevant projects with technology used, what you built, and measurable results when available.",
            "example": "Built a resume analysis platform using Python, Flask, NLP techniques, and TF-IDF similarity."
        })

    if section_scores.get("Skills", 0) == 0:
        improvements.append({
            "title": "Add a dedicated skills section",
            "problem": "A dedicated skills section was not detected.",
            "why": "A structured skills section makes relevant technologies easier to identify.",
            "action": "Group skills into categories such as Programming, AI/ML, Data, Tools, and Soft Skills.",
            "example": "Programming: Python, JavaScript | Data: SQL, Pandas | Tools: Git, GitHub"
        })

    return {
        "strengths": strengths,
        "critical_issues": critical_issues,
        "improvements": improvements,
        "skill_gaps": skill_gaps
    }