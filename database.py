
import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "career_twin.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY,
            student_name TEXT,
            education TEXT,
            target_career TEXT,
            student_skills TEXT,
            resume_text TEXT,
            updated_at TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_profile(
    student_name,
    education,
    target_career,
    student_skills,
    resume_text
):
    connection = get_connection()
    cursor = connection.cursor()

    skills_json = json.dumps(student_skills)

    cursor.execute("""
        INSERT INTO student_profiles (
            id,
            student_name,
            education,
            target_career,
            student_skills,
            resume_text,
            updated_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            student_name = excluded.student_name,
            education = excluded.education,
            target_career = excluded.target_career,
            student_skills = excluded.student_skills,
            resume_text = excluded.resume_text,
            updated_at = excluded.updated_at
    """, (
        student_name,
        education,
        target_career,
        skills_json,
        resume_text,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_profile():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT student_name, education, target_career,
               student_skills, resume_text, updated_at
        FROM student_profiles
        WHERE id = 1
    """)

    result = cursor.fetchone()
    connection.close()

    if result is None:
        return None

    return {
        "student_name": result[0],
        "education": result[1],
        "target_career": result[2],
        "student_skills": json.loads(result[3]),
        "resume_text": result[4],
        "updated_at": result[5]
    }


initialize_database()
