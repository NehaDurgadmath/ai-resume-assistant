import streamlit as st
import pdfplumber
import io
import os
from openai import OpenAI

# ── CONFIG ────────────────────────────────────────────
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_KEY)

# ── PAGE CONFIG ───────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CUSTOM CSS ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: #050010;
    color: white;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(255,107,157,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(196,79,212,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(79,159,212,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* All text white */
p, span, label, .stMarkdown, .stText {
    color: rgba(255,255,255,0.85) !important;
}

h1, h2, h3 {
    color: white !important;
}

/* Text areas */
.stTextArea textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: white !important;
    font-size: 0.88rem !important;
}
.stTextArea textarea:focus {
    border-color: rgba(255,107,157,0.5) !important;
    box-shadow: 0 0 0 3px rgba(255,107,157,0.1) !important;
}

/* Select box */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* File uploader */
.stFileUploader {
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px dashed rgba(255,107,157,0.4) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

/* Radio buttons */
.stRadio > div {
    background: transparent !important;
}
.stRadio label {
    color: rgba(255,255,255,0.7) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,107,157,0.2) !important;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255,255,255,0.5) !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    color: #FF6B9D !important;
    border-bottom: 2px solid #FF6B9D !important;
    background: transparent !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #FF6B9D, #C44FD4) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    width: 100% !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(196,79,212,0.4) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(196,79,212,0.5) !important;
}

/* Result boxes */
.result-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 0.5rem;
    line-height: 1.8;
    font-size: 0.9rem;
    color: rgba(255,255,255,0.85);
    white-space: pre-wrap;
    min-height: 200px;
}

.result-box.tab1 { border-top: 3px solid #FF6B9D; }
.result-box.tab2 { border-top: 3px solid #C44FD4; }
.result-box.tab3 { border-top: 3px solid #4F9FD4; }
.result-box.tab4 { border-top: 3px solid #4FD4A0; }

/* Score display */
.score-big {
    text-align: center;
    font-size: 5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #FF6B9D, #C44FD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    padding: 1rem 0 0.5rem;
}
.score-label {
    text-align: center;
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.85rem;
    margin-bottom: 1rem;
}

/* Input card */
.input-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-label {
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: linear-gradient(135deg, #FF6B9D, #4FD4A0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.8rem;
    display: block;
}

/* Divider */
.ndiv {
    height: 1px;
    background: linear-gradient(135deg, transparent, #FF6B9D, #C44FD4, #4F9FD4, transparent);
    margin: 1rem 0;
    opacity: 0.3;
}

/* Status placeholder */
.status-placeholder {
    text-align: center;
    color: rgba(255,255,255,0.3) !important;
    font-style: italic;
    padding: 3rem;
    font-size: 0.9rem;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #FF6B9D !important;
}

/* Notification/info boxes */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 12px !important;
}

/* Sidebar if used */
.css-1d391kg { background: #0d0025 !important; }

</style>
""", unsafe_allow_html=True)

# ── HELPER: EXTRACT PDF TEXT ──────────────────────────
def extract_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# ── HELPER: CALL OPENAI ───────────────────────────────
def ask_ai(system_msg, user_msg):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ── HEADER ────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 2rem 0 1.5rem;'>
    <div style='font-size:2.5rem; font-weight:900; background:linear-gradient(135deg,#FF6B9D,#C44FD4,#4F9FD4,#4FD4A0);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.5rem;'>
        🤖 AI Resume Assistant
    </div>
    <div style='color:rgba(255,255,255,0.45); font-size:0.95rem;'>
        Upload your resume · Paste a job description · Get AI-powered insights instantly
    </div>
</div>
<div class='ndiv'></div>
""", unsafe_allow_html=True)

# ── LAYOUT ────────────────────────────────────────────
left_col, right_col = st.columns([4, 6])

with left_col:

    # RESUME INPUT
    st.markdown("<span class='card-label'>📄 Your Resume</span>", unsafe_allow_html=True)
    input_type = st.radio("Input type", ["📋 Paste Text", "📁 Upload PDF"], horizontal=True, label_visibility="collapsed")

    resume_text = ""
    if input_type == "📋 Paste Text":
        resume_text = st.text_area(
            "Resume text",
            placeholder="Paste your full resume here...",
            height=220,
            label_visibility="collapsed"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            resume_text = extract_pdf(uploaded_file)
            st.success(f"✅ PDF loaded! ({len(resume_text)} characters extracted)")

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # JOB DESCRIPTION
    st.markdown("<span class='card-label'>💼 Job Description</span>", unsafe_allow_html=True)
    job_desc = st.text_area(
        "Job description",
        placeholder="Paste the full job description here...",
        height=180,
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # TARGET ROLE
    st.markdown("<span class='card-label'>🎯 Target Role</span>", unsafe_allow_html=True)
    target_role = st.selectbox(
        "Target role",
        options=[
            "AI Engineer",
            "Data Scientist",
            "Data Analyst",
            "Machine Learning Engineer",
            "Business Intelligence Analyst",
            "Cloud Engineer (AWS)",
            "Data Engineer",
            "Software Engineer",
            "Product Manager (Tech)",
            "Other"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ANALYSE BUTTON
    analyse = st.button("✨ Analyse My Resume")

# ── RESULTS ───────────────────────────────────────────
with right_col:

    tab1, tab2, tab3, tab4 = st.tabs([
        "👩‍💻 Role Fit",
        "📋 JD Analysis",
        "📊 Fit Score",
        "📚 Prep List"
    ])

    if analyse:

        # Validation
        if len(resume_text.strip()) < 50:
            st.error("⚠️ Please add your resume first!")
        elif len(job_desc.strip()) < 50:
            st.error("⚠️ Please paste a job description!")
        else:
            with st.spinner("🤖 AI is analysing your resume... this takes about 20 seconds..."):

                # ── TAB 1: ROLE MODIFIER ──
                result_role = ask_ai(
                    system_msg=f"""You are an expert resume writer and career coach.
Your job is to analyse a resume and suggest specific improvements
to make it better suited for the target role.
Be specific, practical and encouraging.""",
                    user_msg=f"""TARGET ROLE: {target_role}

RESUME:
{resume_text}

Please do the following:
1. Rewrite the professional summary to target the {target_role} role
2. Suggest 3-5 specific bullet point improvements or additions
3. List 3-5 key skills this person should highlight more for this role
4. Give one key piece of advice for this specific role

Format clearly with headers and be specific to their actual experience."""
                )

                # ── TAB 2: JD ANALYSER ──
                result_jd = ask_ai(
                    system_msg="""You are an expert ATS resume analyser and career coach.
Compare resumes against job descriptions and give specific, actionable advice.
Be honest, detailed and helpful.""",
                    user_msg=f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{job_desc}

Please analyse and provide:
1. KEYWORDS MISSING: Important keywords from the JD not in the resume
2. SKILLS GAP: What skills the JD requires that the resume lacks
3. WHAT TO ADD: Specific bullet points or sections to add
4. WHAT TO REWORD: Existing resume content to reword to match JD language
5. QUICK WINS: 3 fastest changes that would most improve the match

Be specific and reference actual content from both documents."""
                )

                # ── TAB 3: FIT SCORE ──
                result_score = ask_ai(
                    system_msg="""You are a senior hiring manager with 15 years experience.
You give honest, fair and detailed assessments of candidate fit.
You consider experience level, skills match, seniority alignment and overall profile.""",
                    user_msg=f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{job_desc}

TARGET ROLE: {target_role}

Please provide:
1. OVERALL FIT SCORE: Give a percentage (e.g. 72%) and explain it in one sentence
2. SENIORITY MATCH: Is this person applying above, below or at their level? Explain.
3. STRENGTHS: What makes them a good candidate? (3-4 points)
4. GAPS: What is holding them back? (3-4 honest points)
5. VERDICT: One paragraph honest assessment

Start your response with EXACTLY this format on the first line:
SCORE: XX%"""
                )

                # ── TAB 4: INTERVIEW PREP ──
                result_prep = ask_ai(
                    system_msg="""You are a career coach and technical interview expert.
You create personalised, practical interview preparation guides
based on specific job descriptions and candidate backgrounds.""",
                    user_msg=f"""RESUME:
{resume_text}

JOB DESCRIPTION:
{job_desc}

TARGET ROLE: {target_role}

Create a personalised interview preparation guide:
1. TECHNICAL TOPICS TO STUDY: 8-10 specific technical concepts from the JD
2. LIKELY INTERVIEW QUESTIONS: 5 questions this company will probably ask
3. BEHAVIOURAL QUESTIONS: 3 questions based on their background
4. TOOLS TO BRUSH UP ON: Specific tools mentioned in JD
5. ONE WEEK PREP PLAN: Day-by-day study plan for 5 days before interview

Make it specific to this person's background and this exact job description."""
                )

            # ── DISPLAY RESULTS ──
            with tab1:
                st.markdown(f"<div class='result-box tab1'>{result_role}</div>", unsafe_allow_html=True)

            with tab2:
                st.markdown(f"<div class='result-box tab2'>{result_jd}</div>", unsafe_allow_html=True)

            with tab3:
                # Extract score percentage
                score_pct = "??"
                for line in result_score.split("\n"):
                    if line.strip().startswith("SCORE:"):
                        score_pct = line.replace("SCORE:", "").strip()
                        break

                st.markdown(f"<div class='score-big'>{score_pct}</div>", unsafe_allow_html=True)
                st.markdown("<div class='score-label'>Overall Fit Score</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-box tab3'>{result_score}</div>", unsafe_allow_html=True)

            with tab4:
                st.markdown(f"<div class='result-box tab4'>{result_prep}</div>", unsafe_allow_html=True)

    else:
        with tab1:
            st.markdown("<div class='status-placeholder'>👩‍💻 Your role-specific improvements will appear here after analysis</div>", unsafe_allow_html=True)
        with tab2:
            st.markdown("<div class='status-placeholder'>📋 Your job description analysis will appear here after analysis</div>", unsafe_allow_html=True)
        with tab3:
            st.markdown("<div class='status-placeholder'>📊 Your fit score and honest assessment will appear here after analysis</div>", unsafe_allow_html=True)
        with tab4:
            st.markdown("<div class='status-placeholder'>📚 Your personalised interview prep list will appear here after analysis</div>", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────
st.markdown("""
<div class='ndiv'></div>
<div style='text-align:center; color:rgba(255,255,255,0.2); font-size:0.78rem; padding:1rem 0 2rem;'>
    Built with 💕 by Neha Durgadmath · AI Engineer · Powered by OpenAI GPT-4o-mini
</div>
""", unsafe_allow_html=True)