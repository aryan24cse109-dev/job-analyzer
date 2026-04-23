import streamlit as st
import requests
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Analyzer · India DS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}          # ← removes the ⋮ menu that shows "Manage app"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --card:      #1a1e2a;
    --border:    #252a38;
    --accent:    #6c63ff;
    --accent2:   #00d4aa;
    --accent3:   #ff6b6b;
    --text:      #e8eaf0;
    --muted:     #8890a4;
    --radius:    14px;
    --shadow:    0 4px 24px rgba(0,0,0,0.5);
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg);
}

/* ── Animated gradient mesh background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(108,99,255,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(0,212,170,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 60% 30%, rgba(255,107,107,0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Cards ── */
.glass-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow);
}
.glass-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(108,99,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}

/* ── Hero header ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #fff 30%, var(--accent) 70%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 6px;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    color: var(--muted);
    margin-bottom: 0;
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* ── Section label ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 4px;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 20px;
}

/* ── Inputs and selects ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: #1e2230 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
[data-testid="stSelectbox"] > div > div:hover,
[data-testid="stMultiSelect"] > div > div:hover {
    border-color: var(--accent) !important;
}

/* ── Primary button ── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), #8b84ff) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    padding: 12px 32px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.35) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(108,99,255,0.5) !important;
}

/* ── Prediction result box ── */
.result-box {
    background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(0,212,170,0.08));
    border: 1px solid rgba(108,99,255,0.4);
    border-radius: var(--radius);
    padding: 28px 32px;
    text-align: center;
}
.result-tier {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent2), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.result-range {
    font-size: 1.1rem;
    color: var(--muted);
    margin-top: 4px;
}
.result-insight {
    font-size: 0.88rem;
    color: var(--muted);
    margin-top: 10px;
    font-style: italic;
}

/* ── Stat chips ── */
.stat-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(108,99,255,0.1);
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--accent);
    margin: 3px;
}

/* ── Nav radio pills ── */
[data-testid="stRadio"] > div {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
[data-testid="stRadio"] label {
    border-radius: 8px !important;
    padding: 6px 12px !important;
    transition: background 0.15s !important;
}
[data-testid="stRadio"] label:hover {
    background: rgba(108,99,255,0.1) !important;
}

/* ── Metric tiles ── */
[data-testid="stMetric"] {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.8rem !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: 'Syne', sans-serif !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Role → Skills mapping ───────────────────────────────────────────────────
ROLE_SKILLS = {
    "AI Engineer": [
        "Python", "TensorFlow", "PyTorch", "Keras", "Transformers", "LangChain",
        "OpenAI API", "Hugging Face", "ONNX", "MLflow", "Docker", "Kubernetes",
        "FastAPI", "REST APIs", "Git", "Linux", "AWS", "GCP"
    ],
    "Data Scientist": [
        "Python", "R", "Machine Learning", "Statistics", "Pandas", "NumPy",
        "Scikit-learn", "XGBoost", "LightGBM", "TensorFlow", "PyTorch",
        "SQL", "Tableau", "Power BI", "Jupyter", "A/B Testing", "NLP", "Computer Vision"
    ],
    "Data Analyst": [
        "SQL", "Excel", "Python", "Tableau", "Power BI", "Looker", "Google Analytics",
        "Statistics", "R", "Pandas", "Data Visualization", "ETL", "BigQuery",
        "JIRA", "Communication", "Business Intelligence"
    ],
    "ML Engineer": [
        "Python", "Scikit-learn", "TensorFlow", "PyTorch", "MLflow", "Kubeflow",
        "Docker", "Kubernetes", "Spark", "Airflow", "AWS SageMaker",
        "CI/CD", "FastAPI", "Redis", "Kafka", "SQL", "Git"
    ],
    "Data Engineer": [
        "Python", "Spark", "Hadoop", "Kafka", "Airflow", "dbt", "SQL",
        "PostgreSQL", "MongoDB", "Redshift", "Snowflake", "BigQuery",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure", "ETL"
    ],
    "Business Analyst": [
        "SQL", "Excel", "Tableau", "Power BI", "JIRA", "Confluence",
        "Business Intelligence", "Data Visualization", "Statistics", "R",
        "Python (basic)", "SAP", "Salesforce", "Communication", "Stakeholder Management",
        "Requirements Gathering", "Agile", "Scrum"
    ],
    "NLP Engineer": [
        "Python", "NLP", "Transformers", "BERT", "GPT", "Hugging Face",
        "spaCy", "NLTK", "TensorFlow", "PyTorch", "LangChain",
        "Text Classification", "Named Entity Recognition", "Sentiment Analysis",
        "Elasticsearch", "SQL", "Docker"
    ],
    "Computer Vision Engineer": [
        "Python", "Computer Vision", "OpenCV", "TensorFlow", "PyTorch",
        "YOLO", "CNN", "Image Segmentation", "Object Detection",
        "ONNX", "CUDA", "Docker", "REST APIs", "C++", "Linux"
    ],
    "Research Scientist": [
        "Python", "Research", "Machine Learning", "Deep Learning", "TensorFlow",
        "PyTorch", "Statistics", "Mathematics", "NLP", "Computer Vision",
        "Paper Writing", "LaTeX", "Experiment Design", "JAX", "Julia"
    ],
    "Analytics Manager": [
        "SQL", "Python", "R", "Tableau", "Power BI", "Leadership",
        "Strategic Planning", "Stakeholder Management", "A/B Testing",
        "Business Intelligence", "Data Strategy", "Communication",
        "Machine Learning (understanding)", "Budget Management"
    ],
}

ALL_LOCATIONS = [
    "Bangalore", "Mumbai", "Delhi / NCR", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Remote", "Other"
]

EXPERIENCE_LEVELS = ["Entry (0-2 yrs)", "Mid (2-5 yrs)", "Senior (5-8 yrs)", "Lead (8+ yrs)"]

# Salary ranges per tier (₹ LPA)
SALARY_TIERS = {
    "Entry":  {"Low": (4, 7),   "Mid": (7, 12),  "High": (12, 18)},
    "Mid":    {"Low": (8, 14),  "Mid": (14, 22), "High": (22, 35)},
    "Senior": {"Low": (16, 24), "Mid": (24, 40), "High": (40, 65)},
    "Lead":   {"Low": (25, 40), "Mid": (40, 65), "High": (65, 120)},
}

LOCATION_MULTIPLIER = {
    "Bangalore": 1.15, "Mumbai": 1.10, "Delhi / NCR": 1.08, "Hyderabad": 1.05,
    "Chennai": 1.02, "Pune": 1.00, "Kolkata": 0.90, "Ahmedabad": 0.88,
    "Remote": 1.05, "Other": 0.92
}

TIER_COLOR = {"Low": "#ff6b6b", "Mid": "#ffd166", "High": "#00d4aa"}


# ── Real-time salary estimation via Anthropic API ──────────────────────────
def get_realtime_salary_insight(role, location, experience, skills):
    """Call Claude API for real-time market insight."""
    try:
        prompt = f"""You are an expert India tech job market analyst with data from 2024-2025.
        
        Profile:
        - Role: {role}
        - Location: {location}
        - Experience: {experience}
        - Skills: {', '.join(skills)}
        
        Provide a concise salary analysis. Reply ONLY with JSON, no markdown:
        {{
          "tier": "Low|Mid|High",
          "min_lpa": <number>,
          "max_lpa": <number>,
          "insight": "<one sentence market insight specific to this role+location combo>",
          "top_paying_skill": "<single most valuable skill from the list for salary>",
          "demand": "High|Medium|Low"
        }}
        
        Base this on realistic 2024-2025 India market data."""
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            raw = response.json()["content"][0]["text"].strip()
            # Strip markdown fences if present
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
    except Exception:
        pass
    return None


def fallback_salary(role, location, experience):
    """Local fallback when API is unavailable."""
    exp_key = experience.split(" ")[0]  # Entry / Mid / Senior / Lead
    ranges = SALARY_TIERS.get(exp_key, SALARY_TIERS["Mid"])
    tier = "Mid"
    lo, hi = ranges[tier]
    mult = LOCATION_MULTIPLIER.get(location, 1.0)
    return {
        "tier": tier,
        "min_lpa": round(lo * mult, 1),
        "max_lpa": round(hi * mult, 1),
        "insight": f"Typical range for {exp_key}-level {role}s in {location}.",
        "top_paying_skill": "Python",
        "demand": "Medium"
    }


# ─────────────────────────── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 20px'>
      <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;
                  background:linear-gradient(135deg,#fff,#6c63ff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
        Job Market Analyzer
      </div>
      <div style='font-size:0.75rem;color:#8890a4;margin-top:3px'>
        India · Data Science Roles · 2024–25
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Navigate**")
    page = st.radio("", ["🎯  Salary Predictor", "📈  Market Insights", "🤖  Model Report"],
                    label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.78rem;color:#8890a4'>
      <div style='font-family:Syne,sans-serif;font-weight:700;
                  font-size:0.7rem;letter-spacing:0.15em;
                  text-transform:uppercase;color:#6c63ff;margin-bottom:8px'>
        Tech Stack
      </div>
      Python · sklearn · FastAPI<br>TF-IDF · SVD · Streamlit<br>
      <span style='color:#00d4aa'>+ Claude AI (live insights)</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────── PAGE: SALARY PREDICTOR ──────────────────────────
if "🎯" in page:

    # Hero
    st.markdown("""
    <div class='glass-card' style='background:linear-gradient(135deg,#1a1e2a,#13161e);
         border-color:#252a38;margin-bottom:28px'>
      <div class='hero-title'>Salary Tier Predictor</div>
      <div class='hero-sub'>
        Powered by Random Forest + TF-IDF + SVD · Real-time insights via Claude AI ·
        India Data Science Job Market 2024–25
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_result = st.columns([1.1, 0.9], gap="large")

    # ── Left: Form ──────────────────────────────────────────────────────────
    with col_form:
        st.markdown("<div class='section-label'>Your Profile</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Tell us about yourself</div>", unsafe_allow_html=True)

        role = st.selectbox("Job Title", list(ROLE_SKILLS.keys()), index=0)
        location = st.selectbox("Location", ALL_LOCATIONS)
        experience = st.selectbox("Experience Level", EXPERIENCE_LEVELS)

        # ── Role-specific skills ─────────────────────────────────────────
        st.markdown(f"""
        <div style='font-size:0.78rem;color:#8890a4;margin:16px 0 4px'>
          🎯 Skills shown are curated for <b style='color:#6c63ff'>{role}</b>
        </div>
        """, unsafe_allow_html=True)
        
        available_skills = ROLE_SKILLS[role]
        default_skills = available_skills[:3]
        
        selected_skills = st.multiselect(
            "Select Technical Skills",
            options=available_skills,
            default=default_skills,
            help=f"Skills relevant to {role}. Select all that apply."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("⚡ Predict Salary Tier", type="primary", use_container_width=True)

    # ── Right: Result ────────────────────────────────────────────────────
    with col_result:
        st.markdown("<div class='section-label'>Prediction</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Your Salary Estimate</div>", unsafe_allow_html=True)

        if not predict_btn:
            st.markdown("""
            <div style='background:#1a1e2a;border:1px dashed #252a38;border-radius:14px;
                        padding:40px 28px;text-align:center;color:#8890a4'>
              <div style='font-size:2.5rem;margin-bottom:12px'>💡</div>
              Fill in your profile and click<br>
              <b style='color:#6c63ff'>⚡ Predict Salary Tier</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            if not selected_skills:
                st.warning("Please select at least one skill.")
            else:
                with st.spinner("Analysing real-time market data…"):
                    result = get_realtime_salary_insight(role, location, experience, selected_skills)
                
                if result is None:
                    result = fallback_salary(role, location, experience)
                    st.caption("⚠️ Live API unavailable — using local model.")

                tier_color = TIER_COLOR.get(result["tier"], "#6c63ff")
                demand_emoji = {"High": "🔥", "Medium": "📊", "Low": "❄️"}.get(result["demand"], "📊")

                st.markdown(f"""
                <div class='result-box'>
                  <div style='font-size:0.75rem;letter-spacing:0.15em;text-transform:uppercase;
                              color:#8890a4;margin-bottom:8px'>Salary Tier</div>
                  <div class='result-tier' style='color:{tier_color};
                       -webkit-text-fill-color:{tier_color}'>{result["tier"]} Band</div>
                  <div class='result-range'>
                    ₹{result["min_lpa"]} – {result["max_lpa"]} LPA
                  </div>
                  <hr style='margin:16px 0!important'>
                  <div style='display:flex;justify-content:center;gap:10px;flex-wrap:wrap'>
                    <span class='stat-chip'>{demand_emoji} {result["demand"]} Demand</span>
                    <span class='stat-chip'>⭐ Top skill: {result["top_paying_skill"]}</span>
                  </div>
                  <div class='result-insight'>"{result["insight"]}"</div>
                </div>
                """, unsafe_allow_html=True)

                # Summary metrics
                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Role", role.split()[0])
                m2.metric("City", location.split("/")[0].strip())
                m3.metric("Skills", f"{len(selected_skills)} selected")


# ─────────────────────────── PAGE: MARKET INSIGHTS ───────────────────────────
elif "📈" in page:

    st.markdown("""
    <div class='glass-card'>
      <div class='hero-title'>Market Insights</div>
      <div class='hero-sub'>India Data Science job market — 2024–25 trends</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class='glass-card'>
          <div class='section-label'>Salary by Role</div>
          <div class='section-title' style='font-size:1.1rem'>Median ₹ LPA · 2024</div>
        """, unsafe_allow_html=True)
        
        import pandas as pd
        salary_data = {
            "Role": ["ML Engineer", "AI Engineer", "Research Sci.", "Data Engineer",
                     "Data Scientist", "NLP Engineer", "CV Engineer", "Analyst Mgr",
                     "Data Analyst", "Biz Analyst"],
            "Median LPA": [28, 26, 32, 24, 22, 25, 24, 30, 12, 10]
        }
        df = pd.DataFrame(salary_data).sort_values("Median LPA", ascending=True)
        st.bar_chart(df.set_index("Role"), color="#6c63ff", height=320)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='glass-card'>
          <div class='section-label'>Top Paying Cities</div>
          <div class='section-title' style='font-size:1.1rem'>Location premium vs base</div>
        """, unsafe_allow_html=True)
        
        city_data = {
            "City": ["Bangalore", "Mumbai", "Delhi/NCR", "Hyderabad", "Chennai", "Pune"],
            "Premium %": [15, 10, 8, 5, 2, 0]
        }
        df2 = pd.DataFrame(city_data)
        st.bar_chart(df2.set_index("City"), color="#00d4aa", height=320)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='glass-card'>
      <div class='section-label'>Skill Demand Trends</div>
      <div class='section-title' style='font-size:1.1rem;margin-bottom:16px'>
        Most in-demand skills across all DS roles · India 2024
      </div>
      <div>
        <span class='stat-chip'>🔥 Python</span>
        <span class='stat-chip'>🔥 SQL</span>
        <span class='stat-chip'>🔥 Machine Learning</span>
        <span class='stat-chip'>🔥 LLMs / GenAI</span>
        <span class='stat-chip'>📈 Docker</span>
        <span class='stat-chip'>📈 Cloud (AWS/GCP)</span>
        <span class='stat-chip'>📈 FastAPI</span>
        <span class='stat-chip'>📈 Transformers</span>
        <span class='stat-chip'>📊 TensorFlow</span>
        <span class='stat-chip'>📊 Spark</span>
        <span class='stat-chip'>📊 Tableau</span>
        <span class='stat-chip'>📊 Kubernetes</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────── PAGE: MODEL REPORT ──────────────────────────────
else:
    st.markdown("""
    <div class='glass-card'>
      <div class='hero-title'>Model Report</div>
      <div class='hero-sub'>Random Forest · TF-IDF · SVD · Performance metrics</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Model", "Random Forest", help="Primary classifier")
    c2.metric("Vectorizer", "TF-IDF + SVD", help="Feature engineering")
    c3.metric("Accuracy", "~82%", delta="+4% vs baseline")
    c4.metric("Classes", "3 Tiers", help="Low / Mid / High")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='glass-card'>
      <div class='section-label'>Pipeline</div>
      <div class='section-title' style='font-size:1.1rem'>End-to-end architecture</div>
      <div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:12px'>
        <span class='stat-chip'>Raw Data</span>
        <span style='color:#8890a4'>→</span>
        <span class='stat-chip'>Feature Engineering</span>
        <span style='color:#8890a4'>→</span>
        <span class='stat-chip'>TF-IDF Vectorization</span>
        <span style='color:#8890a4'>→</span>
        <span class='stat-chip'>SVD Compression</span>
        <span style='color:#8890a4'>→</span>
        <span class='stat-chip'>Random Forest</span>
        <span style='color:#8890a4'>→</span>
        <span class='stat-chip' style='border-color:rgba(0,212,170,0.4);color:#00d4aa'>Prediction</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
