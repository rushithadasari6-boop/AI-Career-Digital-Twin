import streamlit as st
import pandas as pd
import time
import re
from pypdf import PdfReader

# =========================================================
# PAGE CONFIG
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

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f6f8fc;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #1e293b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #111827;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #64748b;
        font-size: 15px;
        margin-bottom: 24px;
    }

    .welcome-banner {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.18);
    }

    .welcome-banner h2 {
        margin: 0;
        font-size: 25px;
    }

    .welcome-banner p {
        margin: 8px 0 0 0;
        opacity: 0.9;
    }

    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        min-height: 130px;
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #111827;
        font-size: 28px;
        font-weight: 800;
    }

    .metric-subtitle {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-heading {
        font-size: 22px;
        font-weight: 750;
        color: #111827;
        margin-top: 26px;
        margin-bottom: 14px;
    }

    .section-description {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 16px;
    }

    .content-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.035);
        margin-bottom: 18px;
    }

    .profile-card {
        background: linear-gradient(135deg, #eef2ff, #f5f3ff);
        border: 1px solid #c7d2fe;
        padding: 24px;
        border-radius: 18px;
        margin-bottom: 20px;
    }

    .profile-name {
        font-size: 24px;
        font-weight: 800;
        color: #312e81;
    }

    .profile-info {
        color: #4f46e5;
        margin-top: 5px;
        font-size: 14px;
    }

    .badge {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px 5px 4px 0;
        border-radius: 20px;
        background: #eef2ff;
        color: #4338ca;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-green {
        background: #dcfce7;
        color: #166534;
    }

    .badge-orange {
        background: #ffedd5;
        color: #9a3412;
    }

    .badge-red {
        background: #fee2e2;
        color: #991b1b;
    }

    .empty-state {
        text-align: center;
        padding: 42px 20px;
        background: white;
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        margin-top: 15px;
    }

    .empty-icon {
        font-size: 42px;
        margin-bottom: 12px;
    }

    .empty-title {
        font-size: 18px;
        font-weight: 700;
        color: #334155;
    }

    .empty-text {
        color: #64748b;
        font-size: 14px;
        margin-top: 8px;
    }

    .success-box {
        padding: 14px 18px;
        background: #dcfce7;
        color: #166534;
        border-radius: 12px;
        font-weight: 600;
        margin: 15px 0;
    }

    .warning-box {
        padding: 14px 18px;
        background: #fef3c7;
        color: #92400e;
        border-radius: 12px;
        font-weight: 600;
        margin: 15px 0;
    }

    .info-box {
        padding: 14px 18px;
        background: #dbeafe;
        color: #1e40af;
        border-radius: 12px;
        font-weight: 600;
        margin: 15px 0;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 12px;
        padding: 30px 0 10px 0;
    }

    div[data-testid="stProgressBar"] > div > div {
        border-radius: 10px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 10px 18px;
    }

    .stButton > button:hover {
        border: 1px solid #6366f1;
        color: #4f46e5;
    }

    @media only screen and (max-width: 768px) {
        .main-title {
            font-size: 26px;
        }

        .welcome-banner {
            padding: 20px;
        }

        .welcome-banner h2 {
            font-size: 21px;
        }

        .metric-card {
            margin-bottom: 12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DATA
# =========================================================

SKILLS_DATABASE = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Git",
    "GitHub",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "NLP",
    "Computer Vision",
    "Generative AI",
    "Large Language Models",
    "Statistics",
    "Data Structures",
    "Algorithms",
    "OOP",
    "REST API",
    "Docker",
    "AWS",
    "Communication",
    "Problem Solving"
]

CAREER_REQUIREMENTS = {
    "Software Developer": [
        "Java",
        "Python",
        "JavaScript",
        "React",
        "SQL",
        "Git",
        "Data Structures",
        "Algorithms",
        "OOP",
        "REST API"
    ],
    "AI Engineer": [
        "Python",
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Generative AI",
        "Large Language Models",
        "FastAPI",
        "Git",
        "Problem Solving"
    ],
    "Machine Learning Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "Statistics",
        "Git",
        "SQL"
    ],
    "Data Scientist": [
        "Python",
        "Machine Learning",
        "Statistics",
        "Pandas",
        "NumPy",
        "Data Science",
        "SQL",
        "Data Visualization",
        "Problem Solving"
    ],
    "Data Analyst": [
        "Python",
        "SQL",
        "MySQL",
        "Pandas",
        "Statistics",
        "Data Visualization",
        "Excel",
        "Communication"
    ]
}

LEARNING_PLANS = {
    "Python": [
        "Learn Python syntax and fundamentals",
        "Practice functions, loops and collections",
        "Build beginner Python projects"
    ],
    "Machine Learning": [
        "Learn supervised and unsupervised learning",
        "Practice Scikit-learn algorithms",
        "Build an end-to-end ML project"
    ],
    "Deep Learning": [
        "Learn neural network fundamentals",
        "Study CNNs and RNNs",
        "Build a deep learning project"
    ],
    "SQL": [
        "Learn SQL queries and filtering",
        "Practice joins and subqueries",
        "Solve SQL interview problems"
    ],
    "React": [
        "Learn components and props",
        "Practice hooks and state management",
        "Build a React application"
    ],
    "FastAPI": [
        "Learn API routing",
        "Build REST endpoints",
        "Connect FastAPI with a frontend"
    ],
    "Generative AI": [
        "Understand LLM fundamentals",
        "Learn prompt engineering",
        "Build a GenAI application"
    ],
    "Data Structures": [
        "Learn arrays, strings and linked lists",
        "Practice stacks, queues and trees",
        "Solve coding problems regularly"
    ],
    "Algorithms": [
        "Learn searching and sorting",
        "Study recursion and dynamic programming",
        "Practice interview-level problems"
    ]
}

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "student_name": "",
    "education": "",
    "student_skills": [],
    "resume_text": "",
    "profile_created": False,
    "target_career": "Not selected"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def extract_resume_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text
    except Exception:
        return ""


def detect_skills(text):
    detected = []
    lower_text = text.lower()

    for skill in SKILLS_DATABASE:
        if skill.lower() in lower_text:
            detected.append(skill)

    return sorted(list(set(detected)))


def calculate_career_scores(skills):
    scores = {}

    for career, requirements in CAREER_REQUIREMENTS.items():
        matched = [
            skill for skill in requirements
            if skill.lower() in [s.lower() for s in skills]
        ]

        score = round((len(matched) / len(requirements)) * 100)
        scores[career] = {
            "score": score,
            "matched": matched,
            "missing": [s for s in requirements if s not in matched]
        }

    return scores


def get_best_career(scores):
    if not scores:
        return "Not available"

    return max(scores, key=lambda career: scores[career]["score"])


def readiness_level(score):
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Developing"
    return "Beginner"


def get_learning_tasks(missing_skills):
    tasks = []

    for skill in missing_skills:
        if skill in LEARNING_PLANS:
            tasks.extend(LEARNING_PLANS[skill])
        else:
            tasks.append(f"Learn and practice {skill}")

    return list(dict.fromkeys(tasks))[:12]


def show_empty_state(icon, title, message):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-icon">{icon}</div>
            <div class="empty-title">{title}</div>
            <div class="empty-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def badge_html(items, badge_class=""):
    if not items:
        return "<span class='badge'>None detected</span>"

    return "".join(
        [f"<span class='badge {badge_class}'>{item}</span>" for item in items]
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
    st.caption("AI Career Digital Twin v1.0")

# =========================================================
# PROFILE SETUP
# =========================================================

with st.expander("⚙️ Student Profile Setup", expanded=not st.session_state.profile_created):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Student Name",
            value=st.session_state.student_name,
            placeholder="Enter your name"
        )

        education = st.text_input(
            "Education",
            value=st.session_state.education,
            placeholder="Example: B.Tech CSE AI & ML"
        )

    with col2:
        target_career = st.selectbox(
            "Target Career",
            ["Not selected"] + list(CAREER_REQUIREMENTS.keys()),
            index=(
                ["Not selected"] + list(CAREER_REQUIREMENTS.keys())
            ).index(st.session_state.target_career)
            if st.session_state.target_career in
            ["Not selected"] + list(CAREER_REQUIREMENTS.keys())
            else 0
        )

        uploaded_resume = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

    if st.button("💾 Save Profile", use_container_width=True):
        if not name.strip():
            st.error("Please enter your name.")
        else:
            resume_text = st.session_state.resume_text

            if uploaded_resume is not None:
                resume_text = extract_resume_text(uploaded_resume)

            detected = detect_skills(resume_text)

            st.session_state.student_name = name
            st.session_state.education = education
            st.session_state.target_career = target_career
            st.session_state.resume_text = resume_text
            st.session_state.student_skills = detected
            st.session_state.profile_created = True

            with st.spinner("Creating your Digital Twin..."):
                time.sleep(1)

            st.success("Profile saved successfully. Your Digital Twin is ready.")

# =========================================================
# COMMON PROFILE DATA
# =========================================================

skills = st.session_state.student_skills
scores = calculate_career_scores(skills)
best_career = get_best_career(scores)

if scores:
    readiness_score = scores[best_career]["score"]
else:
    readiness_score = 0

missing_for_best = (
    scores[best_career]["missing"]
    if best_career in scores
    else []
)

learning_tasks = get_learning_tasks(missing_for_best)

completed_tasks = [
    task for task in learning_tasks
    if st.session_state.get(f"task_{task}", False)
]

learning_progress = (
    round((len(completed_tasks) / len(learning_tasks)) * 100)
    if learning_tasks
    else 0
)

# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":
    st.markdown(
        "<div class='main-title'>Career Intelligence Dashboard</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Understand your current skills, career readiness and growth opportunities.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        st.markdown(
            """
            <div class="welcome-banner">
                <h2>Welcome to your AI Career Digital Twin 🚀</h2>
                <p>Create your student profile and upload your resume to generate personalized career insights.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        show_empty_state(
            "👤",
            "Create your profile to begin",
            "Add your name, education and resume from the Student Profile Setup section."
        )

    else:
        st.markdown(
            f"""
            <div class="welcome-banner">
                <h2>Welcome back, {st.session_state.student_name} 👋</h2>
                <p>Your personalized career intelligence dashboard is ready.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">CAREER READINESS</div>
                    <div class="metric-value">{readiness_score}%</div>
                    <div class="metric-subtitle">{readiness_level(readiness_score)} level</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">DETECTED SKILLS</div>
                    <div class="metric-value">{len(skills)}</div>
                    <div class="metric-subtitle">From your resume</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">BEST CAREER MATCH</div>
                    <div class="metric-value" style="font-size:19px;">{best_career}</div>
                    <div class="metric-subtitle">{readiness_score}% compatibility</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">LEARNING PROGRESS</div>
                    <div class="metric-value">{learning_progress}%</div>
                    <div class="metric-subtitle">Roadmap completion</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            "<div class='section-heading'>Career Overview</div>",
            unsafe_allow_html=True
        )

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown(
                f"""
                <div class="content-card">
                    <h3>🎯 Recommended Career</h3>
                    <h2 style="color:#4f46e5;">{best_career}</h2>
                    <p style="color:#64748b;">
                        Your current profile shows the strongest alignment with this career path.
                    </p>
                    <div style="margin-top:15px;">
                        <b>Compatibility: {readiness_score}%</b>
                    </div>
                    """,
                unsafe_allow_html=True
            )

            st.progress(readiness_score / 100)

            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True
            )

        with right:
            profile_completion = 0

            if st.session_state.student_name:
                profile_completion += 25
            if st.session_state.education:
                profile_completion += 25
            if st.session_state.target_career != "Not selected":
                profile_completion += 25
            if st.session_state.resume_text:
                profile_completion += 25

            st.markdown(
                f"""
                <div class="content-card">
                    <h3>👤 Profile Completion</h3>
                    <h2 style="color:#16a34a;">{profile_completion}%</h2>
                    <p style="color:#64748b;">Complete your profile for more accurate insights.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            "<div class='section-heading'>Current Strengths</div>",
            unsafe_allow_html=True
        )

        if skills:
            st.markdown(
                f"<div class='content-card'>{badge_html(skills, 'badge-green')}</div>",
                unsafe_allow_html=True
            )
        else:
            show_empty_state(
                "📄",
                "No skills detected yet",
                "Upload a resume containing your technical skills."
            )

        st.markdown(
            "<div class='section-heading'>Priority Skill Gaps</div>",
            unsafe_allow_html=True
        )

        if missing_for_best:
            st.markdown(
                f"<div class='content-card'>{badge_html(missing_for_best, 'badge-orange')}</div>",
                unsafe_allow_html=True
            )
        else:
            st.success("You have no major skill gaps for this career.")

        if scores:
            st.markdown(
                "<div class='section-heading'>Career Compatibility</div>",
                unsafe_allow_html=True
            )

            chart_data = pd.DataFrame(
                {
                    "Career": list(scores.keys()),
                    "Compatibility": [
                        item["score"] for item in scores.values()
                    ]
                }
            )

            st.bar_chart(
                chart_data.set_index("Career"),
                height=320
            )

# =========================================================
# DIGITAL TWIN
# =========================================================

elif page == "🧬 Digital Twin":
    st.markdown(
        "<div class='main-title'>Your Digital Twin</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>A visual representation of your current professional identity and career readiness.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "🧬",
            "Digital Twin not available",
            "Create your profile to generate your professional Digital Twin."
        )
    else:
        personality = (
            "Strong technical foundation"
            if readiness_score >= 60
            else "Growing technical potential"
        )

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-name">🧬 {st.session_state.student_name}</div>
                <div class="profile-info">{st.session_state.education or "Education not specified"}</div>
                <div class="profile-info">Target Career: {st.session_state.target_career}</div>
                <div class="profile-info">Career Personality: {personality}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">TECHNICAL SKILLS</div>
                    <div class="metric-value">{len(skills)}</div>
                    <div class="metric-subtitle">Identified capabilities</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">SKILL GAPS</div>
                    <div class="metric-value">{len(missing_for_best)}</div>
                    <div class="metric-subtitle">Areas to improve</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">READINESS</div>
                    <div class="metric-value">{readiness_score}%</div>
                    <div class="metric-subtitle">{readiness_level(readiness_score)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            "<div class='section-heading'>Skill Strength Visualization</div>",
            unsafe_allow_html=True
        )

        if skills:
            strength_data = pd.DataFrame(
                {
                    "Skill": skills[:12],
                    "Strength": [100] * min(len(skills), 12)
                }
            )

            st.bar_chart(
                strength_data.set_index("Skill"),
                height=350
            )
        else:
            show_empty_state(
                "📊",
                "Visualization unavailable",
                "Upload a resume to populate your Digital Twin skill profile."
            )

        left, right = st.columns(2)

        with left:
            st.markdown(
                "<div class='content-card'><h3>💪 Skill Strengths</h3>",
                unsafe_allow_html=True
            )

            if skills:
                st.markdown(
                    badge_html(skills, "badge-green"),
                    unsafe_allow_html=True
                )
            else:
                st.write("No strengths detected yet.")

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                "<div class='content-card'><h3>📈 Development Areas</h3>",
                unsafe_allow_html=True
            )

            if missing_for_best:
                st.markdown(
                    badge_html(missing_for_best, "badge-orange"),
                    unsafe_allow_html=True
                )
            else:
                st.write("No major development areas identified.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.info(
            "The current Digital Twin uses resume-based skill intelligence. "
            "AI-powered behavior prediction and personalized growth modeling can be integrated in the backend phase."
        )

# =========================================================
# SKILL GAP ANALYSIS
# =========================================================

elif page == "🎯 Skill Gap Analysis":
    st.markdown(
        "<div class='main-title'>Skill Gap Analysis</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Compare your current capabilities with the requirements of your target career.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "🎯",
            "Skill analysis unavailable",
            "Create your profile and upload a resume first."
        )
    else:
        selected_career = st.selectbox(
            "Choose career to analyze",
            list(CAREER_REQUIREMENTS.keys()),
            index=(
                list(CAREER_REQUIREMENTS.keys()).index(
                    st.session_state.target_career
                )
                if st.session_state.target_career in CAREER_REQUIREMENTS
                else 0
            )
        )

        required = CAREER_REQUIREMENTS[selected_career]
        matched = [
            skill for skill in required
            if skill.lower() in [s.lower() for s in skills]
        ]
        missing = [skill for skill in required if skill not in matched]

        score = round((len(matched) / len(required)) * 100)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Required Skills", len(required))

        with col2:
            st.metric("Matched Skills", len(matched))

        with col3:
            st.metric("Skill Match", f"{score}%")

        st.progress(score / 100)

        left, right = st.columns(2)

        with left:
            st.markdown(
                "<div class='content-card'><h3>✅ Matched Skills</h3>",
                unsafe_allow_html=True
            )

            if matched:
                st.markdown(
                    badge_html(matched, "badge-green"),
                    unsafe_allow_html=True
                )
            else:
                st.write("No matching skills found.")

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                "<div class='content-card'><h3>⚠️ Missing Skills</h3>",
                unsafe_allow_html=True
            )

            if missing:
                st.markdown(
                    badge_html(missing, "badge-orange"),
                    unsafe_allow_html=True
                )
            else:
                st.success("No skill gaps detected.")

            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# LEARNING ROADMAP
# =========================================================

elif page == "📚 Learning Roadmap":
    st.markdown(
        "<div class='main-title'>Adaptive Learning Roadmap</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Follow a personalized learning sequence based on your skill gaps.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "📚",
            "Roadmap not available",
            "Create your profile to generate a personalized roadmap."
        )
    elif not learning_tasks:
        show_empty_state(
            "🎉",
            "No roadmap required",
            "Your current skills already match the selected career requirements."
        )
    else:
        st.markdown(
            f"""
            <div class="content-card">
                <h3>Recommended Path: {best_career}</h3>
                <p style="color:#64748b;">
                    Complete the following tasks to improve your career readiness.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for index, task in enumerate(learning_tasks, start=1):
            st.checkbox(
                f"{index}. {task}",
                key=f"task_{task}"
            )

        completed_count = len(
            [
                task for task in learning_tasks
                if st.session_state.get(f"task_{task}", False)
            ]
        )

        progress = (
            completed_count / len(learning_tasks)
            if learning_tasks
            else 0
        )

        st.markdown(
            "<div class='section-heading'>Roadmap Progress</div>",
            unsafe_allow_html=True
        )

        st.progress(progress)
        st.write(f"Completed {completed_count} of {len(learning_tasks)} tasks")

        if progress == 1:
            st.success("🎉 Excellent! You completed your current roadmap.")

# =========================================================
# PROGRESS TRACKING
# =========================================================

elif page == "📈 Progress Tracking":
    st.markdown(
        "<div class='main-title'>Progress Tracking</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Monitor your development and career readiness over time.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "📈",
            "Progress tracking unavailable",
            "Create your profile and start completing roadmap tasks."
        )
    else:
        completed_count = len(completed_tasks)
        total_tasks = len(learning_tasks)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Career Readiness", f"{readiness_score}%")

        with col2:
            st.metric("Tasks Completed", completed_count)

        with col3:
            st.metric("Roadmap Progress", f"{learning_progress}%")

        st.markdown(
            "<div class='section-heading'>Learning Completion</div>",
            unsafe_allow_html=True
        )

        st.progress(learning_progress / 100)

        if learning_progress == 0:
            st.info("Start completing roadmap tasks to track your progress.")
        elif learning_progress < 100:
            st.warning("Keep going. Consistent progress improves your readiness.")
        else:
            st.success("You have completed your current learning roadmap.")

        progress_data = pd.DataFrame(
            {
                "Category": [
                    "Career Readiness",
                    "Learning Progress"
                ],
                "Percentage": [
                    readiness_score,
                    learning_progress
                ]
            }
        )

        st.bar_chart(
            progress_data.set_index("Category"),
            height=280
        )

# =========================================================
# CAREER RECOMMENDATION
# =========================================================

elif page == "🤖 Career Recommendation":
    st.markdown(
        "<div class='main-title'>AI Career Recommendation</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Explore which career paths best match your current skill profile.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "🤖",
            "Recommendations unavailable",
            "Create your profile to receive career recommendations."
        )
    else:
        ranked = sorted(
            scores.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )

        for rank, (career, data) in enumerate(ranked, start=1):
            st.markdown(
                f"""
                <div class="content-card">
                    <h3>#{rank} {career}</h3>
                    <p style="color:#64748b;">
                        Compatibility score: <b>{data["score"]}%</b>
                    </p>
                """,
                unsafe_allow_html=True
            )

            st.progress(data["score"] / 100)

            st.markdown(
                f"""
                    <p style="color:#64748b;">
                        Matched skills: {len(data["matched"])} |
                        Missing skills: {len(data["missing"])}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================================================
# INTERVIEW PREPARATION
# =========================================================

elif page == "🎤 Interview Preparation":
    st.markdown(
        "<div class='main-title'>Interview Preparation</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Practice common questions based on your career direction.</div>",
        unsafe_allow_html=True
    )

    if not st.session_state.profile_created:
        show_empty_state(
            "🎤",
            "Interview preparation unavailable",
            "Create your profile to receive relevant interview questions."
        )
    else:
        interview_questions = [
            "Tell me about yourself.",
            "Explain one project you have built.",
            "What are your strongest technical skills?",
            "What is your biggest technical weakness?",
            "Explain the difference between supervised and unsupervised learning.",
            "What are OOP principles?",
            "Explain a difficult problem you solved.",
            "Why are you interested in this career?"
        ]

        st.markdown(
            f"""
            <div class="info-box">
                Recommended interview direction: {best_career}
            </div>
            """,
            unsafe_allow_html=True
        )

        for number, question in enumerate(interview_questions, start=1):
            with st.expander(f"Question {number}: {question}"):
                st.text_area(
                    "Your answer",
                    key=f"interview_answer_{number}",
                    placeholder="Type your answer here..."
                )

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        AI Career Digital Twin • Frontend Prototype • Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)