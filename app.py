import streamlit as st
import pandas as pd
import time
import re
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from database import save_profile, get_profile, register_user, authenticate_user

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AI Career Digital Twin",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:Inter,sans-serif;}
.stApp {background:#f6f8fc;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#111827 0%,#1e293b 100%);}
[data-testid="stSidebar"] * {color:#f8fafc !important;}
.main-title {font-size:34px;font-weight:800;color:#111827;margin-bottom:4px;}
.subtitle {color:#64748b;font-size:15px;margin-bottom:24px;}
.welcome-banner {padding:28px;border-radius:18px;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white;margin-bottom:24px;box-shadow:0 8px 24px rgba(79,70,229,.18);}
.welcome-banner h2 {margin:0;font-size:25px;}
.welcome-banner p {margin:8px 0 0;opacity:.9;}
.metric-card {background:white;padding:22px;border-radius:16px;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(15,23,42,.04);min-height:130px;}
.metric-label {color:#64748b;font-size:13px;font-weight:600;margin-bottom:10px;}
.metric-value {color:#111827;font-size:28px;font-weight:800;}
.metric-subtitle {color:#94a3b8;font-size:12px;margin-top:5px;}
.section-heading {font-size:22px;font-weight:750;color:#111827;margin-top:26px;margin-bottom:14px;}
.content-card {background:white;padding:24px;border-radius:16px;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(15,23,42,.035);margin-bottom:18px;}
.profile-card {background:linear-gradient(135deg,#eef2ff,#f5f3ff);border:1px solid #c7d2fe;padding:24px;border-radius:18px;margin-bottom:20px;}
.profile-name {font-size:24px;font-weight:800;color:#312e81;}
.profile-info {color:#4f46e5;margin-top:5px;font-size:14px;}
.badge {display:inline-block;padding:7px 12px;margin:4px 5px 4px 0;border-radius:20px;background:#eef2ff;color:#4338ca;font-size:12px;font-weight:600;}
.badge-green {background:#dcfce7;color:#166534;}
.badge-orange {background:#ffedd5;color:#9a3412;}
.badge-red {background:#fee2e2;color:#991b1b;}
.empty-state {text-align:center;padding:42px 20px;background:white;border:1px dashed #cbd5e1;border-radius:16px;margin-top:15px;}
.empty-icon {font-size:42px;margin-bottom:12px;}
.empty-title {font-size:18px;font-weight:700;color:#334155;}
.empty-text {color:#64748b;font-size:14px;margin-top:8px;}
.footer {text-align:center;color:#94a3b8;font-size:12px;padding:30px 0 10px;}
.stButton>button {border-radius:10px;font-weight:600;border:none;padding:10px 18px;}
.stButton>button:hover {border:1px solid #6366f1;color:#4f46e5;}
@media(max-width:768px){.main-title{font-size:26px}.welcome-banner{padding:20px}.welcome-banner h2{font-size:21px}}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOCAL SQLITE AUTHENTICATION (NO SUPABASE)
# Accounts and password hashes are stored in career_twin.db.
# =========================================================
if "auth_user_id" not in st.session_state:
    st.session_state.auth_user_id = ""
if "auth_email" not in st.session_state:
    st.session_state.auth_email = ""

if not st.session_state.auth_user_id:
    st.markdown(
        "<div class='main-title'>AI Career Digital Twin</div>"
        "<div class='subtitle'>Create an account or log in to access your career dashboard.</div>",
        unsafe_allow_html=True
    )
    login_tab, signup_tab = st.tabs(["Login", "Create account"])

    with login_tab:
        with st.form("login_form"):
            login_email = st.text_input("Email address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("Login", use_container_width=True)

        if login_submit:
            account = authenticate_user(login_email.strip(), login_password)
            if account:
                st.session_state.auth_user_id = account["user_id"]
                st.session_state.auth_email = account["email"]
                st.rerun()
            else:
                st.error("Login failed. Check your email and password.")

    with signup_tab:
        with st.form("signup_form"):
            signup_email = st.text_input("Email address", key="signup_email")
            signup_password = st.text_input(
                "Create password (at least 8 characters)", type="password", key="signup_password"
            )
            signup_confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
            signup_submit = st.form_submit_button("Create account", use_container_width=True)

        if signup_submit:
            email = signup_email.strip().lower()
            if not email or "@" not in email:
                st.error("Enter a valid email address.")
            elif len(signup_password) < 8:
                st.error("Password must contain at least 8 characters.")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match.")
            else:
                account = register_user(email, signup_password)
                if account:
                    st.session_state.auth_user_id = account["user_id"]
                    st.session_state.auth_email = account["email"]
                    st.success("Account created successfully.")
                    st.rerun()
                else:
                    st.error("An account with this email already exists. Please log in.")
    st.stop()

user_id = st.session_state.auth_user_id


# =========================================================
# CAREER AND SKILL DATA
# =========================================================
SKILLS_DATABASE = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "HTML", "CSS",
    "React", "Node.js", "FastAPI", "Django", "Flask", "SQL", "MySQL",
    "PostgreSQL", "MongoDB", "Git", "GitHub", "Machine Learning",
    "Deep Learning", "Artificial Intelligence", "Data Science", "Pandas",
    "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "NLP",
    "Computer Vision", "Generative AI", "Large Language Models",
    "Statistics", "Data Structures", "Algorithms", "OOP", "REST API",
    "Docker", "AWS", "Communication", "Problem Solving", "Excel",
    "Data Visualization", "Power BI", "Tableau"
]

CAREER_REQUIREMENTS = {
    "Software Developer": [
        "Java", "Python", "JavaScript", "React", "SQL",
        "Git", "Data Structures", "Algorithms", "OOP", "REST API"
    ],
    "AI Engineer": [
        "Python", "Artificial Intelligence", "Machine Learning",
        "Deep Learning", "Generative AI", "Large Language Models",
        "FastAPI", "Git", "Problem Solving"
    ],
    "Machine Learning Engineer": [
        "Python", "Machine Learning", "Deep Learning", "Pandas",
        "NumPy", "Scikit-learn", "TensorFlow", "Statistics", "Git", "SQL"
    ],
    "Data Scientist": [
        "Python", "Machine Learning", "Statistics", "Pandas", "NumPy",
        "Data Science", "SQL", "Data Visualization", "Problem Solving"
    ],
    "Data Analyst": [
        "Python", "SQL", "MySQL", "Pandas", "Statistics",
        "Data Visualization", "Excel", "Communication"
    ]
}

LEARNING_PLANS = {
    "Python": [
        "Learn Python syntax, variables and data types",
        "Practice functions, loops and collections",
        "Build a beginner Python project"
    ],
    "Java": [
        "Learn Java syntax, variables and control flow",
        "Practice classes, objects and collections",
        "Build a small Java application"
    ],
    "JavaScript": [
        "Learn variables, functions, arrays and objects",
        "Practice DOM events and asynchronous JavaScript",
        "Build an interactive webpage"
    ],
    "React": [
        "Learn components, JSX and props",
        "Practice hooks, state and event handling",
        "Build a React application with multiple pages"
    ],
    "OOP": [
        "Learn classes, objects, constructors and encapsulation",
        "Practice inheritance and polymorphism",
        "Build a small project using all four OOP principles"
    ],
    "REST API": [
        "Learn HTTP methods, status codes and JSON",
        "Build GET, POST, PUT and DELETE endpoints",
        "Test a CRUD API using Postman or another API client"
    ],
    "SQL": [
        "Learn SELECT, WHERE, ORDER BY and GROUP BY",
        "Practice joins, subqueries and aggregate functions",
        "Solve SQL interview problems using sample tables"
    ],
    "Git": [
        "Learn add, commit, push and pull",
        "Practice branches, merging and resolving conflicts",
        "Publish a project with a clear README"
    ],
    "Data Structures": [
        "Learn arrays, strings and linked lists",
        "Practice stacks, queues, trees and hash maps",
        "Solve beginner data-structure problems"
    ],
    "Algorithms": [
        "Learn searching and sorting algorithms",
        "Study recursion and time complexity",
        "Practice coding interview problems"
    ],
    "Machine Learning": [
        "Learn supervised and unsupervised learning",
        "Practice Scikit-learn algorithms",
        "Build an end-to-end ML project"
    ],
    "Deep Learning": [
        "Learn neural-network fundamentals",
        "Study CNNs and sequence models",
        "Build a deep-learning project"
    ],
    "FastAPI": [
        "Learn routing, request models and validation",
        "Build REST endpoints with FastAPI",
        "Connect FastAPI to a database and frontend"
    ],
    "Generative AI": [
        "Understand LLM fundamentals and limitations",
        "Learn prompt engineering and structured outputs",
        "Build a small GenAI application"
    ],
    "Large Language Models": [
        "Learn tokens, context windows and model basics",
        "Practice prompting and model evaluation",
        "Build an application using an LLM API"
    ],
    "Artificial Intelligence": [
        "Study search, reasoning and AI fundamentals",
        "Explore practical AI use cases",
        "Build a small AI-powered application"
    ],
    "Pandas": [
        "Learn Series and DataFrame operations",
        "Practice cleaning and transforming datasets",
        "Complete an exploratory data-analysis project"
    ],
    "NumPy": [
        "Learn arrays and array operations",
        "Practice indexing, broadcasting and aggregation",
        "Use NumPy in a data-analysis task"
    ],
    "Scikit-learn": [
        "Learn preprocessing and model selection",
        "Practice classification and regression",
        "Build and evaluate a small ML pipeline"
    ],
    "TensorFlow": [
        "Learn tensors and model-building basics",
        "Train a simple neural network",
        "Evaluate a model on a sample dataset"
    ],
    "PyTorch": [
        "Learn tensors, datasets and dataloaders",
        "Build and train a simple neural network",
        "Evaluate and document a small model"
    ],
    "Statistics": [
        "Revise descriptive statistics and probability",
        "Practice distributions and hypothesis testing",
        "Analyze a dataset and explain its findings"
    ],
    "Excel": [
        "Learn formulas, sorting and filtering",
        "Practice pivot tables and charts",
        "Analyze a small dataset in Excel"
    ],
    "Data Visualization": [
        "Learn chart selection and data storytelling",
        "Practice visualizations with Python or a BI tool",
        "Create a dashboard from a sample dataset"
    ],
    "Power BI": [
        "Learn Power Query and data-modeling basics",
        "Practice DAX measures and visual reports",
        "Build an interactive Power BI dashboard"
    ],
    "Tableau": [
        "Learn worksheets, dimensions and measures",
        "Practice filters and interactive charts",
        "Publish a dashboard using a sample dataset"
    ],
    "Communication": [
        "Practice explaining a technical topic clearly",
        "Write concise project documentation",
        "Present a project and answer questions"
    ],
    "Problem Solving": [
        "Break problems into smaller steps",
        "Solve beginner coding challenges consistently",
        "Review and explain your solution approach"
    ],
    "Data Science": [
        "Learn the data-science workflow",
        "Practice data cleaning and exploratory analysis",
        "Complete a small end-to-end data project"
    ],
    "MySQL": [
        "Learn database creation and SQL queries",
        "Practice joins, indexes and constraints",
        "Design a small relational database"
    ],
    "Node.js": [
        "Learn Node.js modules and asynchronous code",
        "Build a simple server with routes",
        "Create a small backend API"
    ],
    "Docker": [
        "Learn images, containers and Dockerfiles",
        "Containerize a small application",
        "Run the application with environment variables"
    ],
    "AWS": [
        "Learn core cloud concepts and IAM basics",
        "Explore compute and storage services",
        "Deploy a small application in a safe practice environment"
    ]
}

RESOURCE_LINKS = {
    "Python": [("Official Python Tutorial", "https://docs.python.org/3/tutorial/")],
    "Java": [(" dev.java learning", "https://dev.java/learn/")],
    "JavaScript": [("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide")],
    "React": [("React Official Learn", "https://react.dev/learn")],
    "OOP": [("Python Classes Tutorial", "https://docs.python.org/3/tutorial/classes.html")],
    "REST API": [("MDN HTTP Guide", "https://developer.mozilla.org/en-US/docs/Web/HTTP")],
    "SQL": [("SQLBolt Interactive Lessons", "https://sqlbolt.com/")],
    "Git": [("Git Book", "https://git-scm.com/book/en/v2")],
    "Data Structures": [("VisuAlgo", "https://visualgo.net/en")],
    "Algorithms": [("VisuAlgo", "https://visualgo.net/en")],
    "Machine Learning": [("Scikit-learn Tutorials", "https://scikit-learn.org/stable/tutorial/index.html")],
    "FastAPI": [("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/")],
    "Generative AI": [("Google Generative AI Learning", "https://ai.google.dev/gemini-api/docs")],
    "Large Language Models": [("Hugging Face LLM Course", "https://huggingface.co/learn/llm-course/chapter1/1")],
    "Pandas": [("Pandas Getting Started", "https://pandas.pydata.org/docs/getting_started/index.html")],
    "NumPy": [("NumPy Quickstart", "https://numpy.org/doc/stable/user/quickstart.html")],
    "Statistics": [("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability")],
    "Excel": [("Microsoft Excel Help", "https://support.microsoft.com/excel")],
    "Power BI": [("Microsoft Learn Power BI", "https://learn.microsoft.com/power-bi/")],
    "Tableau": [("Tableau Free Training", "https://www.tableau.com/learn/training")],
    "Docker": [("Docker Get Started", "https://docs.docker.com/get-started/")],
    "AWS": [("AWS Skill Builder", "https://skillbuilder.aws/")]
}

# =========================================================
# DATABASE: ROADMAP PROGRESS
# Keep using the same career_twin.db file as database.py.
# =========================================================
DB_PATH = str(Path(__file__).resolve().parent / "career_twin.db")

def initialize_roadmap_table():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_progress_by_user (
            user_id TEXT NOT NULL,
            career TEXT NOT NULL,
            skills_signature TEXT NOT NULL,
            task TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT,
            PRIMARY KEY (user_id, career, skills_signature, task)
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS student_skill_assessments_by_user (
            user_id TEXT NOT NULL,
            career TEXT NOT NULL,
            skill TEXT NOT NULL,
            proficiency INTEGER NOT NULL,
            updated_at TEXT,
            PRIMARY KEY (user_id, career, skill)
        )
    """)
    connection.commit()
    connection.close()

def get_saved_roadmap_progress(user_id, career, signature):
    connection = sqlite3.connect(DB_PATH)
    rows = connection.execute("""
        SELECT task, completed
        FROM roadmap_progress_by_user
        WHERE user_id = ? AND career = ? AND skills_signature = ?
    """, (user_id, career, signature)).fetchall()
    connection.close()
    return {task: bool(completed) for task, completed in rows}


def save_roadmap_progress(user_id, career, signature, task, completed):
    connection = sqlite3.connect(DB_PATH)
    connection.execute("""
        INSERT INTO roadmap_progress_by_user
            (user_id, career, skills_signature, task, completed, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, career, skills_signature, task)
        DO UPDATE SET completed = excluded.completed, updated_at = excluded.updated_at
    """, (user_id, career, signature, task, int(completed), datetime.now().isoformat()))
    connection.commit()
    connection.close()


def get_skill_assessments(user_id, career):
    connection = sqlite3.connect(DB_PATH)
    rows = connection.execute("""
        SELECT skill, proficiency
        FROM student_skill_assessments_by_user
        WHERE user_id = ? AND career = ?
    """, (user_id, career)).fetchall()
    connection.close()
    return {skill: int(score) for skill, score in rows}


def save_skill_assessments(user_id, career, assessment_values):
    connection = sqlite3.connect(DB_PATH)
    for skill, proficiency in assessment_values.items():
        connection.execute("""
            INSERT INTO student_skill_assessments_by_user
                (user_id, career, skill, proficiency, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, career, skill)
            DO UPDATE SET proficiency = excluded.proficiency, updated_at = excluded.updated_at
        """, (user_id, career, skill, int(proficiency), datetime.now().isoformat()))
    connection.commit()
    connection.close()

initialize_roadmap_table()

# =========================================================
# SESSION STATE AND PROFILE RESTORE
# =========================================================
defaults = {
    "student_name": "",
    "education": "",
    "student_skills": [],
    "profile_created": False,
    "target_career": "Not selected"
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.get("_profile_loaded", False):
    saved_profile = get_profile(user_id)
    if saved_profile is not None:
        st.session_state.student_name = saved_profile["student_name"] or ""
        st.session_state.education = saved_profile["education"] or ""
        st.session_state.target_career = saved_profile["target_career"] or "Not selected"
        st.session_state.student_skills = saved_profile["student_skills"] or []
        st.session_state.profile_created = True
    st.session_state["_profile_loaded"] = True

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def calculate_career_scores(student_skills):
    skill_set = {skill.lower() for skill in student_skills}
    scores = {}
    for career, requirements in CAREER_REQUIREMENTS.items():
        matched = [skill for skill in requirements if skill.lower() in skill_set]
        missing = [skill for skill in requirements if skill.lower() not in skill_set]
        score = round(len(matched) / len(requirements) * 100) if requirements else 0
        scores[career] = {"score": score, "matched": matched, "missing": missing}
    return scores


def calculate_integrated_career_scores(student_skills):
    """
    Estimate career readiness using selected skills and saved self-assessments.
    If no assessment exists for a career, retain the original skill-match score.
    """
    skill_scores = calculate_career_scores(student_skills)
    skill_set = {skill.lower() for skill in student_skills}
    integrated = {}

    for career, requirements in CAREER_REQUIREMENTS.items():
        assessments = get_skill_assessments(user_id, career)
        base = skill_scores[career]
        if not assessments:
            integrated[career] = {
                **base,
                "skill_match_score": base["score"],
                "assessment_score": None,
                "low_proficiency": [],
                "assessed_count": 0,
            }
            continue

        skill_points = []
        low_proficiency = []
        for skill in requirements:
            is_selected = skill.lower() in skill_set
            if skill in assessments:
                rating = assessments[skill]
                # Selected skill evidence contributes 40%; practical self-rating contributes 60%.
                points = (40 if is_selected else 0) + (rating / 5 * 60)
                if rating <= 2:
                    low_proficiency.append(skill)
            else:
                # Selected skills not yet self-rated receive a provisional score.
                points = 60 if is_selected else 0
            skill_points.append(points)

        integrated_score = round(sum(skill_points) / len(requirements)) if requirements else 0
        gaps = list(dict.fromkeys(base["missing"] + low_proficiency))
        integrated[career] = {
            "score": integrated_score,
            "matched": base["matched"],
            "missing": gaps,
            "skill_match_score": base["score"],
            "assessment_score": round(
                sum(assessments.values()) / (len(assessments) * 5) * 100
            ) if assessments else None,
            "low_proficiency": low_proficiency,
            "assessed_count": len(assessments),
        }

    return integrated


def prioritize_skills(skills_to_learn, assessments):
    """Put the lowest self-rated skills first, followed by unassessed gaps."""
    original_order = {skill: index for index, skill in enumerate(skills_to_learn)}
    return sorted(
        skills_to_learn,
        key=lambda skill: (
            0 if assessments.get(skill, 0) <= 2 and skill in assessments else 1,
            assessments.get(skill, 3) if skill in assessments else 6,
            original_order[skill],
        ),
    )

def get_best_career(scores):
    if not scores:
        return "Not available"
    return max(scores, key=lambda career: scores[career]["score"])

def readiness_level(score):
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Developing"
    return "Beginner"

def get_skill_priority(skill, position, total):
    if total <= 0:
        return "Low"
    if position < max(1, (total + 2) // 3):
        return "High"
    if position < max(2, (2 * total + 2) // 3):
        return "Medium"
    return "Low"

def get_skill_action(skill):
    actions = {
        "React": "Build a small React app using components, props and state.",
        "OOP": "Implement encapsulation, inheritance, polymorphism and abstraction.",
        "REST API": "Build and test a small CRUD API.",
        "Python": "Complete Python fundamentals and build a small project.",
        "Java": "Practice Java basics, OOP and collections with coding exercises.",
        "JavaScript": "Learn functions, arrays, objects and DOM fundamentals.",
        "SQL": "Practice SELECT, JOIN, GROUP BY and subqueries.",
        "Git": "Create a repository and practice commits, branches and pushes.",
        "Data Structures": "Practice arrays, strings, linked lists, stacks and queues.",
        "Algorithms": "Practice searching, sorting and basic problem-solving patterns."
    }
    return actions.get(skill, f"Study {skill} fundamentals and complete a practical exercise.")

def get_learning_tasks(missing_skills):
    tasks = []
    for skill in missing_skills:
        tasks.extend(LEARNING_PLANS.get(skill, [
            f"Learn {skill} fundamentals",
            f"Practice {skill} with guided exercises",
            f"Complete a small project using {skill}"
        ]))
    return list(dict.fromkeys(tasks))

def get_task_skill_map(missing_skills):
    task_map = {}
    for skill in missing_skills:
        for task in LEARNING_PLANS.get(skill, [
            f"Learn {skill} fundamentals",
            f"Practice {skill} with guided exercises",
            f"Complete a small project using {skill}"
        ]):
            task_map[task] = skill
    return task_map

def show_empty_state(icon, title, message):
    st.markdown(f"""
        <div class="empty-state">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{title}</div>
            <div class="empty-text">{message}</div>
        </div>
    """, unsafe_allow_html=True)

def badge_html(items, badge_class=""):
    if not items:
        return "<span class='badge'>None detected</span>"
    safe_items = [str(item).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for item in items]
    return "".join([f"<span class='badge {badge_class}'>{item}</span>" for item in safe_items])

def roadmap_callback(career, signature, task, widget_key):
    save_roadmap_progress(
        user_id, career, signature, task, st.session_state.get(widget_key, False)
    )

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🧬 Career Twin")
    st.caption("AI-powered career intelligence")
    st.divider()
    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🧬 Digital Twin",
            "🎯 Skill Gap Analysis",
            "📚 Learning Roadmap",
            "📈 Progress Tracking",
            "🧪 Skill Proficiency Assessment",
            "🤖 Career Recommendation",
            "🎤 Interview Preparation"
        ]
    )
    st.divider()
    st.markdown("### Profile Status")
    if st.session_state.profile_created:
        st.success("Profile active")
        st.caption(st.session_state.student_name)
    else:
        st.warning("Profile not created")
    st.divider()
    st.caption(f"Signed in: {st.session_state.auth_email}")
    if st.button("Log out", use_container_width=True):
        for auth_key in ["auth_user_id", "auth_email", "_profile_loaded"]:
            st.session_state.pop(auth_key, None)
        st.rerun()
    st.caption("AI Career Digital Twin v2.0")

# =========================================================
# PROFILE SETUP
# =========================================================
with st.expander("⚙️ Student Profile Setup", expanded=not st.session_state.profile_created):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Student Name", value=st.session_state.student_name,
            placeholder="Enter your name"
        )
        education = st.text_input(
            "Education", value=st.session_state.education,
            placeholder="Example: B.Tech CSE AI & ML"
        )
    with col2:
        career_options = ["Not selected"] + list(CAREER_REQUIREMENTS.keys())
        target_career = st.selectbox(
            "Target Career",
            career_options,
            index=career_options.index(st.session_state.target_career)
            if st.session_state.target_career in career_options else 0
        )
        selected_skills = st.multiselect(
            "Select your current technical skills",
            options=SKILLS_DATABASE,
            default=st.session_state.student_skills,
            help="Choose the skills you currently know. You can update this list anytime."
        )

    if st.button("💾 Save Profile", use_container_width=True):
        if not name.strip():
            st.error("Please enter your name.")
        elif target_career == "Not selected":
            st.error("Please select a target career.")
        else:
            save_profile(
                user_id=user_id,
                student_name=name.strip(),
                education=education.strip(),
                target_career=target_career,
                student_skills=selected_skills,
                resume_text=""
            )
            st.session_state.student_name = name.strip()
            st.session_state.education = education.strip()
            st.session_state.target_career = target_career
            st.session_state.student_skills = selected_skills
            st.session_state.profile_created = True
            st.success("Profile saved successfully. Your Digital Twin is ready.")
            st.rerun()

# =========================================================
# COMMON PROFILE DATA
# Use the student's chosen target career for the roadmap.
# Best career match remains available for recommendations.
# =========================================================
skills = st.session_state.student_skills
skill_scores = calculate_career_scores(skills)
scores = calculate_integrated_career_scores(skills)
best_career = get_best_career(scores)
selected_career = st.session_state.target_career

if selected_career in CAREER_REQUIREMENTS:
    active_career = selected_career
else:
    active_career = best_career

active_assessments = (
    get_skill_assessments(user_id, active_career)
    if active_career in CAREER_REQUIREMENTS else {}
)

if active_career in scores:
    active_career_data = scores[active_career]
    readiness_score = active_career_data["score"]
    missing_for_active = list(active_career_data["missing"])
    missing_for_active = prioritize_skills(missing_for_active, active_assessments)
else:
    readiness_score = 0
    missing_for_active = []

if best_career in scores:
    best_career_score = scores[best_career]["score"]
else:
    best_career_score = 0

learning_tasks = get_learning_tasks(missing_for_active)
task_skill_map = get_task_skill_map(missing_for_active)
skills_signature = json.dumps(sorted(missing_for_active), ensure_ascii=False)
saved_progress = get_saved_roadmap_progress(user_id, active_career, skills_signature) if active_career in CAREER_REQUIREMENTS else {}
completed_tasks = [task for task in learning_tasks if saved_progress.get(task, False)]
learning_progress = round(len(completed_tasks) / len(learning_tasks) * 100) if learning_tasks else 100

# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":
    st.markdown("<div class='main-title'>Career Intelligence Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Understand your current skills, career readiness and growth opportunities.</div>", unsafe_allow_html=True)

    if not st.session_state.profile_created:
        st.markdown("""
            <div class="welcome-banner">
                <h2>Welcome to your AI Career Digital Twin 🚀</h2>
                <p>Create your student profile and select your current skills to generate personalized career insights.</p>
            </div>
        """, unsafe_allow_html=True)
        show_empty_state("👤", "Create your profile to begin", "Add your name, education, target career and current skills above.")
    else:
        st.markdown(f"""
            <div class="welcome-banner">
                <h2>Welcome back, {st.session_state.student_name} 👋</h2>
                <p>Your personalized career intelligence dashboard is ready.</p>
            </div>
        """, unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>ESTIMATED CAREER READINESS</div><div class='metric-value'>{readiness_score}%</div><div class='metric-subtitle'>{readiness_level(readiness_score)} level · skills + self-assessment</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>SELECTED SKILLS</div><div class='metric-value'>{len(skills)}</div><div class='metric-subtitle'>Selected in your profile</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>BEST CAREER MATCH</div><div class='metric-value' style='font-size:19px;'>{best_career}</div><div class='metric-subtitle'>{best_career_score}% compatibility</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>LEARNING PROGRESS</div><div class='metric-value'>{learning_progress}%</div><div class='metric-subtitle'>Target career roadmap</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-heading'>Career Overview</div>", unsafe_allow_html=True)
        left, right = st.columns([1.2, 1])
        with left:
            st.markdown(f"""
                <div class="content-card">
                    <h3>🎯 Selected Career Path</h3>
                    <h2 style="color:#4f46e5;">{active_career}</h2>
                    <p style="color:#64748b;">Your roadmap and target readiness are based on this selected career.</p>
                    <b>Compatibility: {readiness_score}%</b>
                </div>
            """, unsafe_allow_html=True)
            st.progress(readiness_score / 100)
        with right:
            profile_completion = sum([
                bool(st.session_state.student_name),
                bool(st.session_state.education),
                st.session_state.target_career != "Not selected",
                bool(st.session_state.student_skills)
            ]) * 25
            st.markdown(f"""
                <div class="content-card">
                    <h3>👤 Profile Completion</h3>
                    <h2 style="color:#16a34a;">{profile_completion}%</h2>
                    <p style="color:#64748b;">Complete your profile for more accurate insights.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div class='section-heading'>Current Strengths</div>", unsafe_allow_html=True)
        if skills:
            st.markdown(f"<div class='content-card'>{badge_html(skills, 'badge-green')}</div>", unsafe_allow_html=True)
        else:
            show_empty_state("📄", "No skills selected yet", "Select your current technical skills in Profile Setup.")

        st.markdown("<div class='section-heading'>Priority Skill Gaps</div>", unsafe_allow_html=True)
        if missing_for_active:
            st.markdown(f"<div class='content-card'>{badge_html(missing_for_active, 'badge-orange')}</div>", unsafe_allow_html=True)
        else:
            st.success("Your selected skills cover all listed requirements for the selected career.")

        st.markdown("<div class='section-heading'>Career Compatibility</div>", unsafe_allow_html=True)
        chart_data = pd.DataFrame({
            "Career": list(scores.keys()),
            "Compatibility": [item["score"] for item in scores.values()]
        })
        st.bar_chart(chart_data.set_index("Career"), height=320)

# =========================================================
# DIGITAL TWIN
# =========================================================
elif page == "🧬 Digital Twin":
    st.markdown("<div class='main-title'>Your Digital Twin</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>A visual representation of your professional identity and career readiness.</div>", unsafe_allow_html=True)
    if not st.session_state.profile_created:
        show_empty_state("🧬", "Digital Twin not available", "Create your profile to generate your professional Digital Twin.")
    else:
        personality = "Strong technical foundation" if readiness_score >= 60 else "Growing technical potential"
        st.markdown(f"""
            <div class="profile-card">
                <div class="profile-name">🧬 {st.session_state.student_name}</div>
                <div class="profile-info">{st.session_state.education or "Education not specified"}</div>
                <div class="profile-info">Target Career: {active_career}</div>
                <div class="profile-info">Career Personality: {personality}</div>
            </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Technical Skills", len(skills))
        c2.metric("Skill Gaps", len(missing_for_active))
        c3.metric("Target Readiness", f"{readiness_score}%")
        st.markdown("<div class='section-heading'>Skill Strength Visualization</div>", unsafe_allow_html=True)
        if skills:
            strength_data = pd.DataFrame({"Strength": [100] * min(len(skills), 12)}, index=skills[:12])
            st.bar_chart(strength_data, height=350)
        else:
            show_empty_state("📊", "Visualization unavailable", "Select your current skills in Profile Setup to populate your Digital Twin.")
        left, right = st.columns(2)
        with left:
            st.markdown("<div class='content-card'><h3>💪 Skill Strengths</h3>", unsafe_allow_html=True)
            st.markdown(badge_html(skills, "badge-green"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='content-card'><h3>📈 Development Areas</h3>", unsafe_allow_html=True)
            st.markdown(badge_html(missing_for_active, "badge-orange"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.info("Your Digital Twin combines selected skills with saved proficiency self-assessments when available. Advanced AI behavior prediction can be integrated in a later backend phase.")

# =========================================================
# SKILL GAP ANALYSIS
# =========================================================
elif page == "🎯 Skill Gap Analysis":
    st.markdown("<div class='main-title'>Skill Gap Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Compare your current capabilities with the requirements of your target career.</div>", unsafe_allow_html=True)
    if not st.session_state.profile_created:
        show_empty_state("🎯", "Skill analysis unavailable", "Create your profile and select your current skills first.")
    else:
        career_list = list(CAREER_REQUIREMENTS.keys())
        chosen = st.selectbox(
            "Choose career to analyze",
            career_list,
            index=career_list.index(active_career) if active_career in career_list else 0,
            key="gap_analysis_career"
        )
        required = CAREER_REQUIREMENTS[chosen]
        skill_set = {skill.lower() for skill in skills}
        matched = [skill for skill in required if skill.lower() in skill_set]
        missing = [skill for skill in required if skill.lower() not in skill_set]
        chosen_assessments = get_skill_assessments(user_id, chosen)
        low_proficiency = [
            skill for skill in required
            if chosen_assessments.get(skill, 5) <= 2 and skill in chosen_assessments
        ]
        combined_gaps = prioritize_skills(
            list(dict.fromkeys(missing + low_proficiency)),
            chosen_assessments
        )
        chosen_score_data = calculate_integrated_career_scores(skills)[chosen]
        score = chosen_score_data["score"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Required Skills", len(required))
        c2.metric("Skills Matched", len(matched))
        c3.metric("Estimated Readiness", f"{score}%")
        st.progress(score / 100)
        st.caption(
            f"Selected skills match {len(matched)} of {len(required)} required skills. "
            "Estimated readiness also uses saved proficiency ratings when available."
        )
        chosen_assessments = get_skill_assessments(user_id, chosen)
        chosen_low = [skill for skill, rating in chosen_assessments.items() if rating <= 2]
        if chosen_assessments:
            st.info(
                f"Assessment-aware readiness combines selected skills and your self-ratings. "
                f"{len(chosen_assessments)} skills assessed; {len(chosen_low)} rated Beginner or Basic."
            )
        left, right = st.columns(2)
        with left:
            st.markdown("<div class='content-card'><h3>✅ Matched Skills</h3>", unsafe_allow_html=True)
            st.markdown(badge_html(matched, "badge-green"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown("<div class='content-card'><h3>⚠️ Missing Skills</h3>", unsafe_allow_html=True)
            st.markdown(badge_html(missing, "badge-orange"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        if low_proficiency:
            st.markdown("<div class='section-heading'>Skills needing more practice</div>", unsafe_allow_html=True)
            st.markdown(
                badge_html(low_proficiency, "badge-orange"),
                unsafe_allow_html=True
            )
        st.markdown("<div class='section-heading'>Priority Learning Plan</div>", unsafe_allow_html=True)
        if combined_gaps:
            rows = []
            for index, skill in enumerate(combined_gaps):
                rating_note = (
                    f"Self-rating: {chosen_assessments[skill]}/5"
                    if skill in chosen_assessments else
                    ("Not selected in profile" if skill in missing else "Not assessed yet")
                )
                rows.append({
                    "Priority": get_skill_priority(skill, index, len(combined_gaps)),
                    "Skill to Improve": skill,
                    "Current Evidence": rating_note,
                    "Suggested Next Action": get_skill_action(skill)
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.info("Start with High-priority skills, then work through Medium and Low priorities.")
        else:
            st.success("Great work! Your selected skills and saved self-assessments show no current high-priority gaps.")
        with st.expander("How is the skill match calculated?"):
            st.write("Skill Match = (Selected required skills ÷ Total required career skills) × 100. Estimated Career Readiness uses selected skill evidence (40%) and saved self-ratings (60%) for rated skills. Skills rated 1 or 2 are added to your learning plan. These are estimates based partly on self-assessment, not verified test results.")

# =========================================================
# PERSONALIZED LEARNING ROADMAP
# =========================================================
elif page == "📚 Learning Roadmap":
    st.markdown("<div class='main-title'>Personalized Learning Roadmap</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>A career-specific weekly plan generated from skill gaps and lower proficiency ratings.</div>", unsafe_allow_html=True)

    if not st.session_state.profile_created:
        show_empty_state("📚", "Roadmap not available", "Create your profile to generate a personalized roadmap.")
    elif active_career not in CAREER_REQUIREMENTS:
        show_empty_state("🎯", "Choose a target career", "Open Student Profile Setup and select your target career.")
    elif not learning_tasks:
        st.success(f"🎉 Your detected skills cover all listed requirements for {active_career}. No learning gaps were found.")
        st.balloons()
    else:
        st.markdown(f"""
            <div class="content-card">
                <h3>🎯 Recommended Path: {active_career}</h3>
                <p style="color:#64748b;">This plan is generated from {len(missing_for_active)} skill gaps and/or low-proficiency skills.</p>
                <b>Target career match: {readiness_score}%</b>
            </div>
        """, unsafe_allow_html=True)

        saved_progress = get_saved_roadmap_progress(user_id, active_career, skills_signature)
        task_skill_map = get_task_skill_map(missing_for_active)
        total_tasks = len(learning_tasks)
        week_number = 1
        tasks_per_week = 3

        st.markdown("### Your weekly learning schedule")
        for skill_index, skill in enumerate(missing_for_active):
            priority = get_skill_priority(skill, skill_index, len(missing_for_active))
            priority_color = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}[priority]
            st.markdown(f"#### {priority_color} {skill} — {priority} priority")
            st.caption(get_skill_action(skill))

            skill_tasks = LEARNING_PLANS.get(skill, [
                f"Learn {skill} fundamentals",
                f"Practice {skill} with guided exercises",
                f"Complete a small project using {skill}"
            ])

            for local_index, task in enumerate(skill_tasks):
                task_number = learning_tasks.index(task) + 1
                assigned_week = ((task_number - 1) // tasks_per_week) + 1
                widget_key = f"roadmap_{skills_signature}_{task_number}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = saved_progress.get(task, False)
                st.checkbox(
                    f"Week {assigned_week} · {task}",
                    key=widget_key,
                    on_change=roadmap_callback,
                    args=(active_career, skills_signature, task, widget_key)
                )

            resources = RESOURCE_LINKS.get(skill, [])
            if resources:
                resource_text = "  |  ".join([f"[{label}]({url})" for label, url in resources])
                st.markdown(f"📖 **Learning resource:** {resource_text}")

            st.divider()

        current_completed = sum(
            1 for task in learning_tasks
            if st.session_state.get(
                f"roadmap_{skills_signature}_{learning_tasks.index(task) + 1}",
                saved_progress.get(task, False)
            )
        )
        progress = current_completed / total_tasks if total_tasks else 0
        st.markdown("<div class='section-heading'>Roadmap Progress</div>", unsafe_allow_html=True)
        st.progress(progress)
        st.write(f"Completed **{current_completed} of {total_tasks} tasks** ({round(progress * 100)}%).")
        if progress >= 1:
            st.success("🎉 Excellent! You completed your current personalized roadmap.")
            st.balloons()
        else:
            st.info("Your task completion is saved in SQLite. You can close and reopen the app without losing checked tasks.")

        with st.expander("How this roadmap is personalized"):
            st.write(
                f"The roadmap uses your saved target career ({active_career}), compares your selected skills with career requirements, "
                "and adds skills rated Beginner or Basic to the learning plan. Lowest self-rated skills are prioritized first. "
                "If your target career, selected skills, or assessment ratings change, "
                "a new roadmap is generated. Previous progress is retained for its matching career and skill-gap combination."
            )

# =========================================================
# PROGRESS TRACKING
# =========================================================
elif page == "📈 Progress Tracking":
    st.markdown("<div class='main-title'>Progress Tracking</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Monitor your development and career readiness over time.</div>", unsafe_allow_html=True)
    if not st.session_state.profile_created:
        show_empty_state("📈", "Progress tracking unavailable", "Create your profile and start completing roadmap tasks.")
    else:
        completed_count = len(completed_tasks)
        total_tasks = len(learning_tasks)
        c1, c2, c3 = st.columns(3)
        c1.metric("Estimated Career Readiness", f"{readiness_score}%")
        c2.metric("Tasks Completed", completed_count)
        c3.metric("Roadmap Progress", f"{learning_progress}%")
        st.markdown("<div class='section-heading'>Learning Completion</div>", unsafe_allow_html=True)
        st.progress(learning_progress / 100)
        if learning_progress == 0:
            st.info("Start completing roadmap tasks to track your progress.")
        elif learning_progress < 100:
            st.warning("Keep going. Consistent progress improves your readiness.")
        else:
            st.success("You have completed your current learning roadmap.")
        progress_data = pd.DataFrame({
            "Percentage": [readiness_score, learning_progress]
        }, index=["Career Readiness", "Learning Progress"])
        st.bar_chart(progress_data, height=280)
        st.caption(f"Progress is being tracked for {active_career}. Readiness uses selected skills and saved self-assessment ratings when available.")

# =========================================================
# SKILL PROFICIENCY ASSESSMENT
# =========================================================
elif page == "🧪 Skill Proficiency Assessment":
    st.markdown("<div class='main-title'>Skill Proficiency Assessment</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Rate your practical confidence in the skills required for your selected career. Be honest so your learning recommendations are useful.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state("🧪", "Assessment unavailable", "Create your profile and choose a target career first.")
    elif active_career not in CAREER_REQUIREMENTS:
        show_empty_state("🎯", "Choose a target career", "Select a target career in Student Profile Setup.")
    else:
        required_skills = CAREER_REQUIREMENTS[active_career]
        existing_assessments = get_skill_assessments(user_id, active_career)

        st.markdown(f"### Assessment for {active_career}")
        st.caption("Use the scale below: 1 = Beginner, 2 = Basic, 3 = Intermediate, 4 = Advanced, 5 = Confident.")

        with st.form("skill_proficiency_form"):
            assessment_values = {}
            for skill in required_skills:
                default_score = existing_assessments.get(skill, 1)
                assessment_values[skill] = st.slider(
                    f"{skill}",
                    min_value=1,
                    max_value=5,
                    value=default_score,
                    key=f"assessment_{active_career}_{skill}",
                    help="Rate your current practical ability, based on your practical ability."
                )
            submitted = st.form_submit_button("Save Skill Assessment", use_container_width=True)

        if submitted:
            save_skill_assessments(user_id, active_career, assessment_values)
            st.success("Your skill proficiency assessment has been saved.")
            st.rerun()

        latest_assessments = get_skill_assessments(user_id, active_career)
        if latest_assessments:
            average_score = sum(latest_assessments.get(skill, 1) for skill in required_skills) / len(required_skills)
            percentage = round(average_score / 5 * 100)
            st.markdown("### Your assessment summary")
            a1, a2 = st.columns(2)
            a1.metric("Average proficiency", f"{average_score:.1f} / 5")
            a2.metric("Proficiency score", f"{percentage}%")
            st.progress(percentage / 100)

            weak_skills = [
                skill for skill in required_skills
                if latest_assessments.get(skill, 1) <= 2
            ]
            strong_skills = [
                skill for skill in required_skills
                if latest_assessments.get(skill, 1) >= 4
            ]

            left, right = st.columns(2)
            with left:
                st.markdown("#### Skills to strengthen")
                if weak_skills:
                    st.markdown(badge_html(weak_skills, "badge-orange"), unsafe_allow_html=True)
                else:
                    st.success("No beginner-level skills based on your self-rating.")
            with right:
                st.markdown("#### Your stronger skills")
                if strong_skills:
                    st.markdown(badge_html(strong_skills, "badge-green"), unsafe_allow_html=True)
                else:
                    st.info("Rate skills honestly; skills rated 4 or 5 will appear here.")

            st.caption("These ratings are self-assessments, not independently verified test results. Saved ratings influence estimated career readiness, skill-gap priorities, career recommendations, and your learning roadmap.")

# =========================================================
# CAREER RECOMMENDATION
# =========================================================
elif page == "🤖 Career Recommendation":
    st.markdown("<div class='main-title'>Career Recommendation</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Explore which career paths best match your current skill profile.</div>", unsafe_allow_html=True)
    if not st.session_state.profile_created:
        show_empty_state("🤖", "Recommendations unavailable", "Create your profile to receive career recommendations.")
    else:
        ranked = sorted(scores.items(), key=lambda item: item[1]["score"], reverse=True)
        st.info(
            "Recommendations use your selected skill matches. For careers with saved proficiency ratings, "
            "the score also considers those self-assessments."
        )
        for rank, (career, data) in enumerate(ranked, start=1):
            st.markdown(f"""
                <div class="content-card">
                    <h3>#{rank} {career}</h3>
                    <p style="color:#64748b;">Compatibility score: <b>{data["score"]}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            st.progress(data["score"] / 100)
            st.caption(
                f"Selected skills match: {len(data['matched'])} | "
                f"Skills to improve: {len(data['missing'])} | "
                f"Assessed skills: {data.get('assessed_count', 0)}"
            )

# =========================================================
# INTERVIEW PREPARATION
# =========================================================
elif page == "🎤 Interview Preparation":
    st.markdown("<div class='main-title'>Interview Preparation</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Practice common questions based on your career direction.</div>", unsafe_allow_html=True)
    if not st.session_state.profile_created:
        show_empty_state("🎤", "Interview preparation unavailable", "Create your profile to receive relevant interview questions.")
    else:
        questions = [
            "Tell me about yourself.",
            "Explain one project you have built.",
            "What are your strongest technical skills?",
            "What is your biggest technical weakness?",
            "Explain the difference between supervised and unsupervised learning.",
            "What are OOP principles?",
            "Explain a difficult problem you solved.",
            "Why are you interested in this career?"
        ]
        st.markdown(f"<div class='info-box'>Recommended interview direction: {active_career}</div>", unsafe_allow_html=True)
        for number, question in enumerate(questions, start=1):
            with st.expander(f"Question {number}: {question}"):
                st.text_area("Your answer", key=f"interview_answer_{number}", placeholder="Type your answer here...")

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer">
    AI Career Digital Twin • Personalized Roadmap Edition • Built with Streamlit
</div>
""", unsafe_allow_html=True)
