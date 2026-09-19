from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

import os
import uuid

from analyzer.resume_parser import extract_resume_text
from analyzer.skill_detector import detect_skills
from analyzer.job_matcher import analyze_job_match
from analyzer.scoring import calculate_scores
from analyzer.recommendations import generate_recommendations

from database.database import initialize_database


app = Flask(__name__)

app.secret_key = "skilltrace-ai-local-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

initialize_database()


def allowed_file(filename):
    """Check whether a file extension is supported."""

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["GET", "POST"])
def analyze():

    if request.method == "GET":
        return render_template("analyze.html")


    resume_text = request.form.get(
        "resume_text",
        ""
    ).strip()

    target_role = request.form.get(
        "target_role",
        ""
    ).strip()

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()


    uploaded_file = request.files.get(
        "resume_file"
    )


    # -----------------------------------------
    # Resume upload
    # -----------------------------------------

    if uploaded_file and uploaded_file.filename:

        if not allowed_file(
            uploaded_file.filename
        ):

            flash(
                "Please upload a PDF, DOCX, or TXT resume."
            )

            return redirect(
                url_for("analyze")
            )


        original_name = secure_filename(
            uploaded_file.filename
        )

        unique_name = (
            f"{uuid.uuid4().hex}_{original_name}"
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_name
        )


        try:

            uploaded_file.save(
                file_path
            )

            resume_text = extract_resume_text(
                file_path
            )

        except Exception as error:

            flash(
                f"Could not read the uploaded resume: {error}"
            )

            return redirect(
                url_for("analyze")
            )

        finally:

            if os.path.exists(file_path):

                os.remove(file_path)


    # -----------------------------------------
    # Validate resume
    # -----------------------------------------

    if not resume_text:

        flash(
            "Please upload a resume or paste your resume text."
        )

        return redirect(
            url_for("analyze")
        )


    if len(resume_text.strip()) < 100:

        flash(
            "The resume content is too short to analyze reliably."
        )

        return redirect(
            url_for("analyze")
        )


    # -----------------------------------------
    # Detect skills
    # -----------------------------------------

    detected_skills = detect_skills(
        resume_text
    )


    # -----------------------------------------
    # Job analysis
    # -----------------------------------------

    job_analysis = analyze_job_match(
        resume_text=resume_text,
        target_role=target_role,
        job_description=job_description,
        detected_skills=detected_skills
    )


    # -----------------------------------------
    # Scores
    # -----------------------------------------

    scores = calculate_scores(
        resume_text=resume_text,
        job_analysis=job_analysis,
        detected_skills=detected_skills
    )


    # -----------------------------------------
    # Recommendations
    # -----------------------------------------

    recommendations = generate_recommendations(
        resume_text=resume_text,
        job_analysis=job_analysis,
        detected_skills=detected_skills,
        scores=scores
    )


    # -----------------------------------------
    # Results
    # -----------------------------------------

    results = {

        "scores": scores,

        "job_analysis": job_analysis,

        "detected_skills": detected_skills,

        "recommendations": recommendations,

        "target_role": target_role,

        "has_job_description": bool(
            job_description
        ),

        "resume_length": len(
            resume_text
        )
    }


    return render_template(
        "results.html",
        results=results
    )


@app.route("/health")
def health():

    return {
        "status": "online",
        "application": "SkillTrace AI"
    }


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        error="The page you requested was not found."
    ), 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        "index.html",
        error="Something went wrong. Please try again."
    ), 500


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )