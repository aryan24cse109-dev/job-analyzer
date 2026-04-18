"""
Job Market Analyzer — Streamlit Dashboard
==========================================
Run:
  streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pickle
import os
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, '..', 'models')
DATA_PATH = os.path.join(BASE, '..', 'data', 'jobs.csv')
STATIC    = os.path.join(BASE, 'static')

# ── Load ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    with open(os.path.join(MODEL_DIR, 'rf_model.pkl'), 'rb') as f: rf = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'tfidf.pkl'),    'rb') as f: tfidf = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'svd.pkl'),      'rb') as f: svd = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'encoders.pkl'), 'rb') as f: enc = pickle.load(f)
    return rf, tfidf, svd, enc

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

rf, tfidf, svd, enc = load_models()
le_title, le_loc, le_exp = enc['le_title'], enc['le_loc'], enc['le_exp']
top_skills, feature_cols = enc['top_skills'], enc['feature_cols']
df = load_data()

# ── Helpers ───────────────────────────────────────────────────────────────────
SALARY_RANGES  = {"Low": "₹3L – ₹10L", "Mid": "₹10L – ₹25L", "High": "₹25L+"}
TIER_COLORS    = {"Low": "#F5CBA7", "Mid": "#AED6F1", "High": "#A9DFBF"}
TIER_EMOJIS    = {"Low": "🟡", "Mid": "🔵", "High": "🟢"}

def encode_safe(le, val, fallback=0):
    try:    return int(le.transform([val])[0])
    except: return fallback

def predict_salary(job_title, location, experience_level, skills_list):
    skills_str = ', '.join(skills_list)
    row = {
        'title_enc':  encode_safe(le_title, job_title),
        'loc_enc':    encode_safe(le_loc,   location),
        'exp_enc':    encode_safe(le_exp,   experience_level),
        'num_skills': len(skills_list),
        'remote':     1 if location.lower() == 'remote' else 0,
    }
    for sk in top_skills:
        row[f'skill_{sk.replace(" ","_")}'] = 1 if sk in skills_list else 0
    X_tfidf = tfidf.transform([skills_str])
    X_svd   = svd.transform(X_tfidf)
    for i in range(5): row[f'svd_{i}'] = float(X_svd[0, i])
    X    = pd.DataFrame([row])[feature_cols]
    tier = rf.predict(X)[0]
    prob = rf.predict_proba(X)[0]
    return tier, float(max(prob)), dict(zip(rf.classes_, prob))

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("📊 Job Market Analyzer")
st.sidebar.caption("India · Data Science Roles · 2024")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["🔮 Salary Predictor", "📈 Market Insights", "🧠 Model Report"])

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SALARY PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
if page == "🔮 Salary Predictor":
    st.title("🔮 Salary Tier Predictor")
    st.caption("Enter your profile to get a salary tier prediction powered by Random Forest + SVD")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Your Profile")
        job_title  = st.selectbox("Job Title", sorted(le_title.classes_))
        location   = st.selectbox("Location",  sorted(le_loc.classes_))
        experience = st.selectbox("Experience Level", ['Entry', 'Mid', 'Senior', 'Lead'])
        selected_skills = st.multiselect(
            "Skills (select all that apply)",
            options=top_skills + ['Spark', 'Hadoop', 'R', 'Scala', 'Excel'],
            default=['Python', 'SQL', 'Machine Learning']
        )

        predict_btn = st.button("Predict My Salary Tier", type="primary", use_container_width=True)

    with col2:
        if predict_btn and selected_skills:
            tier, confidence, probs = predict_salary(job_title, location, experience, selected_skills)
            color = TIER_COLORS[tier]
            emoji = TIER_EMOJIS[tier]

            st.subheader("Prediction Result")
            st.markdown(
                f"""<div style="background:{color};padding:20px;border-radius:12px;text-align:center;">
                <h2 style="margin:0;">{emoji} {tier} Salary Tier</h2>
                <h3 style="margin:8px 0 0;">{SALARY_RANGES[tier]}</h3>
                <p style="margin:4px 0 0;opacity:0.7;">Confidence: {confidence:.0%}</p>
                </div>""",
                unsafe_allow_html=True
            )

            st.markdown("**Probability breakdown**")
            prob_df = pd.DataFrame({
                'Tier': list(probs.keys()),
                'Probability': [round(v * 100, 1) for v in probs.values()]
            })
            st.bar_chart(prob_df.set_index('Tier'))

            missing = [s for s in top_skills if s not in selected_skills][:4]
            if missing:
                st.info(f"**Skills to boost your tier:** {', '.join(missing)}")

        elif predict_btn:
            st.warning("Please select at least one skill.")
        else:
            st.info("Fill in your profile on the left and click Predict.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MARKET INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Market Insights":
    st.title("📈 Market Insights")

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Jobs",     f"{len(df):,}")
    k2.metric("Avg Salary",     f"₹{df['salary_lpa'].mean():.1f}L")
    k3.metric("Unique Roles",   df['job_title'].nunique())
    k4.metric("Cities Covered", df['location'].nunique())

    st.markdown("---")

    # Use the pre-generated plot
    img_path = os.path.join(STATIC, 'analysis.png')
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning("Run notebooks/analysis.py first to generate charts.")

    st.markdown("---")
    st.subheader("Raw Data Explorer")
    filters = st.multiselect("Filter by Role", df['job_title'].unique(), default=list(df['job_title'].unique()[:3]))
    st.dataframe(df[df['job_title'].isin(filters)][['job_title','company','location','experience_level','salary_lpa','salary_tier','skills']].reset_index(drop=True), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MODEL REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Model Report":
    st.title("🧠 Model & Methodology Report")

    st.markdown("""
    ### Pipeline Overview
    1. **Data Collection** — 500 data science job listings (India, 2024)
    2. **Feature Engineering** — Label encoding for categorical fields, binary skill flags
    3. **NLP + SVD** — TF-IDF on job skills text → Truncated SVD (5 components) to extract latent skill patterns *(same technique as the SVD Compressor project)*
    4. **Classification** — Random Forest (150 trees, max_depth=12) predicting salary tier: Low / Mid / High
    5. **API** — FastAPI serving `/predict`, `/top-skills`, `/market-summary`
    6. **Dashboard** — Streamlit interactive UI (this app)
    """)

    c1, c2 = st.columns(2)
    with c1:
        fi_path = os.path.join(STATIC, 'feature_importance.png')
        if os.path.exists(fi_path):
            st.image(fi_path, caption="Top 15 Feature Importances", use_container_width=True)
    with c2:
        cm_path = os.path.join(STATIC, 'confusion_matrix.png')
        if os.path.exists(cm_path):
            st.image(cm_path, caption="Confusion Matrix (72% Accuracy)", use_container_width=True)

    st.markdown("""
    ### SVD Connection
    The **TruncatedSVD** step compresses the 50-dim TF-IDF skill matrix into 5 latent components, 
    capturing 23.6% of variance. This mirrors the image/matrix compression approach from the 
    SVD Compressor project — demonstrating that the same linear algebra principle applies to NLP.

    ### Model Performance
    | Metric | Score |
    |--------|-------|
    | Test Accuracy | 72% |
    | High Tier F1 | 0.79 |
    | Mid Tier F1 | 0.71 |
    | CV Mean (5-fold) | ~70% |

    ### Tech Stack
    `Python 3.12` · `pandas` · `scikit-learn` · `matplotlib` · `seaborn` · `FastAPI` · `Streamlit` · `TruncatedSVD` · `TfidfVectorizer` · `RandomForestClassifier`
    """)
