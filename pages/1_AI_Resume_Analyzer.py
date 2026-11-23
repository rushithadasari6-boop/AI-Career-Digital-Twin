
import io
import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =====================================================
# LOAD GEMINI API KEY
# Supports local .env and Streamlit Cloud Secrets
# =====================================================

load_dotenv()

try:
    GEMINI_API_KEY = st.secrets.get(
        "GEMINI_API_KEY",
        os.getenv("GEMINI_API_KEY", "")
    )
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# =====================================================
# PAGE HEADER
# =====================================================

st.title("📄 AI-Powered Resume Analyzer")

st.write(
    "Get personalized resume feedback powered by Google Gemini AI."
)

st.divider()


# =====================================================
# EXTRACT RESUME TEXT
# =====================================================

def extract_resume_text(uploaded_file):

    try:
        reader = PdfReader(
            io.BytesIO(uploaded_file.getvalue())
        )

        extracted_text = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                extracted_text.append(page_text)

        return "\n".join(extracted_text).strip()

    except Exception as error:

        raise ValueError(
            f"Unable to read PDF file: {error}"
        )


# =====================================================
# GEMINI AI ANALYSIS
# =====================================================

def analyze_resume(resume_text, target_role):

    if not GEMINI_API_KEY:

        raise ValueError(
            "Gemini API key not found. "
            "Add GEMINI_API_KEY to Streamlit Cloud Secrets "
            "or your local .env file."
        )

    try:

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        prompt = f"""
You are an experienced technical recruiter,
ATS resume evaluator, and career mentor.

Analyze this resume for the target role: {target_role}

RESUME CONTENT:
{resume_text[:18000]}

Provide a detailed report with these sections:

1. OVERALL RESUME REVIEW
2. KEY STRENGTHS
3. MISSING TECHNICAL SKILLS
4. MISSING SOFT SKILLS
5. ATS FRIENDLINESS
6. PROJECT IMPROVEMENTS
7. RESUME WRITING IMPROVEMENTS
8. FIVE IMPORTANT SKILLS TO LEARN
9. PERSONALIZED LEARNING ROADMAP
10. FINAL RECOMMENDATIONS

Be honest and constructive.

Do not invent achievements, qualifications, or experience.

Explain that ATS scores cannot be guaranteed.

Use beginner-friendly language.
"""

        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        return interaction.output_text

    except Exception as error:

        raise RuntimeError(
            f"Gemini AI analysis error: {error}"
        )


# =====================================================
# CAREER SELECTION
# =====================================================

st.subheader("🎯 Select Your Target Career")

target_role = st.selectbox(
    "Choose your target role",
    [
        "Software Developer",
        "AI Engineer",
        "Machine Learning Engineer",
        "Data Scientist",
        "Data Analyst",
        "Python Developer",
        "Full Stack Developer",
        "Web Developer"
    ]
)


# =====================================================
# RESUME UPLOAD
# =====================================================

st.subheader("📤 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"]
)

st.caption(
    "Privacy tip: Remove personal details you do not want "
    "to share with the AI service before uploading."
)


# =====================================================
# ANALYZE RESUME
# =====================================================

if st.button(
    "🚀 Analyze My Resume",
    type="primary",
    use_container_width=True
):

    if uploaded_file is None:

        st.warning(
            "Please upload your PDF resume."
        )

    else:

        try:

            with st.spinner(
                "Gemini AI is analyzing your resume..."
            ):

                resume_text = extract_resume_text(
                    uploaded_file
                )

                if len(resume_text) < 100:

                    st.error(
                        "Could not extract enough text. "
                        "Please upload a readable text-based PDF."
                    )

                else:

                    analysis = analyze_resume(
                        resume_text,
                        target_role
                    )

                    if not analysis:

                        raise ValueError(
                            "Gemini returned an empty response."
                        )

                    st.session_state[
                        "resume_analysis"
                    ] = analysis

                    st.session_state[
                        "resume_target_role"
                    ] = target_role

        except Exception as error:

            st.error(
                "Resume analysis failed."
            )

            st.error(str(error))


# =====================================================
# DISPLAY REPORT
# =====================================================

if "resume_analysis" in st.session_state:

    st.divider()

    st.success(
        "Resume analysis completed successfully!"
    )

    st.subheader(
        "📊 Your AI Resume Report"
    )

    st.write(
        "**Target Career:** "
        + st.session_state["resume_target_role"]
    )

    analysis = st.session_state["resume_analysis"]

    st.markdown(analysis)

    st.download_button(
        label="⬇️ Download Resume Analysis",
        data=analysis,
        file_name="AI_Resume_Analysis.txt",
        mime="text/plain",
        use_container_width=True
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "AI Career Digital Twin | Powered by Google Gemini"
)
