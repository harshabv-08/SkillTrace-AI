import sqlite3
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "skilltrace.db")


def get_connection():
    """Create a database connection."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create application tables."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            resume_name TEXT,
            target_role TEXT,
            ats_score REAL,
            job_match_score REAL,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_analysis(
    user_name,
    resume_name,
    target_role,
    ats_score,
    job_match_score
):
    """Save a lightweight analysis record."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            user_name,
            resume_name,
            target_role,
            ats_score,
            job_match_score,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_name,
        resume_name,
        target_role,
        ats_score,
        job_match_score,
        datetime.now().isoformat(timespec="seconds")
    ))

    connection.commit()
    connection.close()


def get_analysis_history(limit=20):
    """Return recent analysis records."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM analyses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]