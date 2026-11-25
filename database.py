import sqlite3
import json
import hashlib
import hmac
import secrets
import uuid
from datetime import datetime
from pathlib import Path

DATABASE_NAME = str(Path(__file__).resolve().parent / "career_twin.db")
PBKDF2_ITERATIONS = 310_000

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection

def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return salt.hex(), digest.hex()

def _verify_password(password, salt_hex, expected_hex):
    try:
        salt = bytes.fromhex(salt_hex)
        _, actual_hex = _hash_password(password, salt)
        return hmac.compare_digest(actual_hex, expected_hex)
    except (ValueError, TypeError):
        return False

def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                student_name TEXT,
                education TEXT,
                target_career TEXT,
                student_skills TEXT,
                resume_text TEXT,
                updated_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        # Keep the original table for compatibility with older project data.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                id INTEGER PRIMARY KEY, student_name TEXT, education TEXT,
                target_career TEXT, student_skills TEXT, resume_text TEXT, updated_at TEXT
            )
        """)

def register_user(email, password):
    email = (email or "").strip().lower()
    if not email or len(password or "") < 8:
        return None
    salt_hex, hash_hex = _hash_password(password)
    user_id = str(uuid.uuid4())
    try:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO users (user_id,email,password_salt,password_hash,created_at) VALUES (?,?,?,?,?)",
                (user_id, email, salt_hex, hash_hex, datetime.now().isoformat())
            )
        return {"user_id": user_id, "email": email}
    except sqlite3.IntegrityError:
        return None

def authenticate_user(email, password):
    email = (email or "").strip().lower()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT user_id,email,password_salt,password_hash FROM users WHERE email = ? COLLATE NOCASE",
            (email,)
        ).fetchone()
    if row and _verify_password(password or "", row["password_salt"], row["password_hash"]):
        return {"user_id": row["user_id"], "email": row["email"]}
    return None

def save_profile(user_id, student_name, education, target_career, student_skills, resume_text):
    skills_json = json.dumps(student_skills)
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO user_profiles (user_id,student_name,education,target_career,student_skills,resume_text,updated_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
                student_name=excluded.student_name, education=excluded.education,
                target_career=excluded.target_career, student_skills=excluded.student_skills,
                resume_text=excluded.resume_text, updated_at=excluded.updated_at
        """, (user_id, student_name, education, target_career, skills_json, resume_text, datetime.now().isoformat()))

def get_profile(user_id):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT student_name,education,target_career,student_skills,resume_text,updated_at
            FROM user_profiles WHERE user_id = ?
        """, (user_id,)).fetchone()
    if row is None:
        return None
    return {
        "student_name": row["student_name"],
        "education": row["education"],
        "target_career": row["target_career"],
        "student_skills": json.loads(row["student_skills"] or "[]"),
        "resume_text": row["resume_text"] or "",
        "updated_at": row["updated_at"]
    }

initialize_database()
