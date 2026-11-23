
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
        pdf_bytes = uploaded_file.getvalue()

        reader = PdfReader(io.BytesIO(pdf_bytes))

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
            "Check GEMINI_API_KEY in Streamlit Cloud Secrets."
        )

    client = None

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

        # Maximum 90 seconds for the complete request.
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
            timeout=90,
            automatic_continuation=False
        )

        analysis = interaction.output_text

        if not analysis:
            raise ValueError(
                "Gemini returned an empty response."
            )

        return analysis

    except TimeoutError:
        raise RuntimeError(
            "Gemini request timed out after 90 seconds. "
            "Please try again. If the problem continues, "
            "check your API quota and Gemini API status."
        )

    except Exception as error:
        error_message = str(error)

        if "429" in error_message:
            raise RuntimeError(
                "Gemini API quota or rate limit exceeded. "
                "Please wait and try again."
            )

        elif "401" in error_message or "403" in error_message:
            raise RuntimeError(
                "Gemini API authentication failed. "
                "Check your API key in Streamlit Cloud Secrets."
            )

        else:
            raise RuntimeError(
                f"Gemini analysis failed: {error_message}"
            )

    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


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
                "Gemini AI is analyzing your resume. "
                "Please wait..."
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

                    st.session_state[
                        "resume_analysis"
                    ] = analysis

                    st.session_state[
                        "resume_target_role"
                    ] = target_role

                    st.success(
                        "Resume analysis completed successfully!"
                    )

        except Exception as error:

            st.error("Resume analysis failed.")

            st.error(str(error))


# =====================================================
# DISPLAY REPORT
# =====================================================

if "resume_analysis" in st.session_state:

    st.divider()

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

