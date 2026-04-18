"""
Job Market Analyzer — Streamlit Dashboard
Deployed via Streamlit Cloud (root-level entry point)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
from collections import Counter

st.set_page_config(
    page_title="Job Market Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Paths (root-relative for Streamlit Cloud) ─────────────────────────────────
BASE      = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, 'models')
DATA_PATH = os.path.join(BASE, 'data', 'jobs.csv')
STATIC    = os.path.join(BASE, 'app', 'static')

# ── Load ──────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    with open(os.path.join(MODEL_DIR, 'rf_model.pkl'),  'rb') as f: rf    = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'tfidf.pkl'),     'rb') as f: tfidf = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'svd.pkl'),       'rb') as f: svd   = pickle.load(f)
    with open(os.path.join(MODEL_DIR, 'encoders.pkl'),  'rb') as f: enc   = pickle.load(f)
    return rf, tfidf, svd, enc

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

rf, tfidf, svd, enc = load_models()
le_title     = enc['le_title']
le_loc       = enc['le_loc']
le_exp       = enc['le_exp']
top_skills   = enc['top_skills']
feature_cols = enc['feature_cols']
df           = load_data()

# ── Constants ─────────────────────────────────────────────────────────────────
SALARY_RANGES = {"Low": "3L – 10L LPA", "Mid": "10L – 25L LPA", "High": "25L+ LPA"}
TIER_COLORS   = {"Low": "#FFF3CD", "Mid": "#D1ECF1", "High": "#D4EDDA"}
TIER_ICONS    = {"Low": "🟡", "Mid": "🔵", "High": "🟢"}

# ── Helpers ───────────────────────────────────────────────────────────────────
def encode_safe(le, val, fallback=0):
    try:    return int(le.transform([val])[0])
    except: return fallback

def predict_salary(job_title, location, experience, skills_list):
    skills_str = ', '.join(skills_list)
    row = {
        'title_enc':  encode_safe(le_title, job_title),
        'loc_enc':    encode_safe(le_loc,   location),
        'exp_enc':    encode_safe(le_exp,   experience),
        'num_skills': len(skills_list),
        'remote':     1 if location.lower() == 'remote' else 0,
    }
    for sk in top_skills:
        row[f'skill_{sk.replace(" ","_")}'] = 1 if sk in skills_list else 0
    X_tfidf = tfidf.transform([skills_str])
    X_svd   = svd.transform(X_tfidf)
    for i in range(5):
        row[f'svd_{i}'] = float(X_svd[0, i])
    X    = pd.DataFrame([row])[feature_cols]
    tier = rf.predict(X)[0]
    prob = rf.predict_proba(X)[0]
    return tier, float(max(prob)), dict(zip(rf.classes_, [round(p, 3) for p in prob]))

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image("https://img.shields.io/badge/Model-Random%20Forest-blue", width=180)
st.sidebar.title("Job Market Analyzer")
st.sidebar.caption("India · Data Science Roles · 2024")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["Salary Predictor", "Market Insights", "Model Report"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Tech Stack**")
st.sidebar.code("Python · sklearn · FastAPI\nTF-IDF · SVD · Streamlit")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SALARY PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
if page == "Salary Predictor":
    st.title("Salary Tier Predictor")
    st.caption("Powered by Random Forest + TF-IDF + SVD · India Data Science Job Market")
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Your Profile")
        job_title  = st.selectbox("Job Title",         sorted(le_title.classes_))
        location   = st.selectbox("Location",           sorted(le_loc.classes_))
        experience = st.selectbox("Experience Level",   ['Entry', 'Mid', 'Senior', 'Lead'])
        st.write("---")
        # Ek hi bar skills list define karein
        available_skills = sorted(list(set(top_skills + ['Spark', 'Hadoop', 'R', 'Scala', 'Excel', 'Airflow', 'MongoDB', 'Tableau', 'PowerBI', 'Cloud'])))
        
        selected_skills = st.multiselect(
            "Select Technical Skills",
            options=available_skills,
            default=["Python"] if "Python" in available_skills else None,
            help="Prediction accuracy depends on the skills you select."
        )
        st.markdown("")
        predict_btn = st.button("Predict Salary Tier", type="primary", use_container_width=True)

    with col2:
        st.subheader("Prediction")
        if predict_btn:
            if not selected_skills:
                st.warning("Please select at least one skill.")
            else:
                with st.spinner("Running model..."):
                    tier, confidence, probs = predict_salary(job_title, location, experience, selected_skills)

                color = TIER_COLORS[tier]
                icon  = TIER_ICONS[tier]

                st.markdown(
                    f"""<div style="background:{color};padding:24px;border-radius:12px;
                    text-align:center;border:1px solid #dee2e6;">
                    <p style="font-size:14px;color:#6c757d;margin:0;">Predicted Salary Tier</p>
                    <h1 style="margin:8px 0 4px;">{icon} {tier}</h1>
                    <h3 style="margin:0;color:#495057;">{SALARY_RANGES[tier]}</h3>
                    <p style="margin:8px 0 0;color:#6c757d;font-size:13px;">
                    Model confidence: {confidence:.0%}</p></div>""",
                    unsafe_allow_html=True
                )

                st.markdown("")
                st.markdown("**Probability by tier**")
                prob_df = pd.DataFrame({
                    'Tier': list(probs.keys()),
                    'Probability (%)': [round(v * 100, 1) for v in probs.values()]
                }).set_index('Tier')
                st.bar_chart(prob_df)

                missing = [s for s in top_skills if s not in selected_skills][:4]
                if missing:
                    st.info(f"**Add these skills to improve your tier:**\n{' · '.join(missing)}")
        else:
            st.info("Fill in your profile and click **Predict Salary Tier**")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MARKET INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Market Insights":
    st.title("Market Insights")
    st.caption("India Data Science Job Market · 500 listings analyzed")
    st.markdown("---")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Jobs",      f"{len(df):,}")
    k2.metric("Avg Salary",      f"{df['salary_lpa'].mean():.1f} LPA")
    k3.metric("Unique Roles",    str(df['job_title'].nunique()))
    k4.metric("Cities Covered",  str(df['location'].nunique()))

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Salary by Role", "Top Skills", "City Analysis"])

    with tab1:
        fig, ax = plt.subplots(figsize=(10, 5))
        role_sal = df.groupby('job_title')['salary_lpa'].mean().sort_values(ascending=True)
        bars = ax.barh(role_sal.index, role_sal.values,
                       color=plt.cm.Blues(np.linspace(0.4, 0.85, len(role_sal))))
        ax.set_xlabel('Average Salary (LPA)')
        ax.set_title('Average Salary by Role')
        for bar, val in zip(bars, role_sal.values):
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}L', va='center', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with tab2:
        all_skills_list = []
        for s in df['skills']:
            all_skills_list.extend([x.strip() for x in s.split(',')])
        skill_counts = Counter(all_skills_list)
        top15 = skill_counts.most_common(15)
        names, vals = zip(*top15)
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Greens(np.linspace(0.85, 0.4, 15))
        ax2.bar(names, vals, color=colors)
        ax2.set_xticklabels(names, rotation=45, ha='right')
        ax2.set_title('Top 15 In-Demand Skills')
        ax2.set_ylabel('Job Count')
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

    with tab3:
        fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 5))
        city_c = df['location'].value_counts()
        ax3a.pie(city_c.values, labels=city_c.index, autopct='%1.0f%%',
                 colors=plt.cm.Set2(np.linspace(0, 1, len(city_c))),
                 startangle=140, textprops={'fontsize': 8})
        ax3a.set_title('Jobs by City')
        city_sal = df.groupby('location')['salary_lpa'].mean().sort_values(ascending=False)
        ax3b.bar(city_sal.index, city_sal.values,
                 color=plt.cm.Oranges(np.linspace(0.85, 0.4, len(city_sal))))
        ax3b.set_xticklabels(city_sal.index, rotation=45, ha='right')
        ax3b.set_title('Avg Salary by City (LPA)')
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

    st.markdown("---")
    st.subheader("Raw Data")
    role_filter = st.multiselect("Filter by Role", df['job_title'].unique(),
                                  default=list(df['job_title'].unique()[:3]))
    show = df[df['job_title'].isin(role_filter)][
        ['job_title','company','location','experience_level','salary_lpa','salary_tier','skills']
    ].reset_index(drop=True)
    st.dataframe(show, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MODEL REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Model Report":
    st.title("Model & Methodology Report")
    st.markdown("---")

    st.subheader("Pipeline")
    steps = {
        "1. Data": "500 India DS job listings · 9 cities · 8 roles",
        "2. Feature Engineering": "Label encoding · binary skill flags · experience mapping",
        "3. TF-IDF + SVD": "Skills text → 50-dim TF-IDF → TruncatedSVD (5 components) = 23.6% variance",
        "4. Classification": "RandomForestClassifier · 150 trees · max_depth=12",
        "5. API": "FastAPI serving /predict · /top-skills · /market-summary",
        "6. Dashboard": "Streamlit 3-page interactive UI (this app)"
    }
    for step, detail in steps.items():
        c1, c2 = st.columns([1, 3])
        c1.markdown(f"**{step}**")
        c2.markdown(detail)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Model Performance")
        perf = pd.DataFrame({
            'Metric': ['Test Accuracy','High Tier F1','Mid Tier F1','5-Fold CV Mean'],
            'Score':  ['72%', '0.79', '0.71', '~70%']
        })
        st.table(perf)

        st.subheader("SVD Connection")
        st.info(
            "The TruncatedSVD step compresses the 50-dim TF-IDF skill matrix "
            "into 5 latent components — directly applying the same matrix "
            "decomposition principle from the SVD Compressor project to NLP "
            "feature reduction."
        )

    with col2:
        st.subheader("Feature Importances (Top 10)")
        fi_path = os.path.join(STATIC, 'feature_importance.png')
        if os.path.exists(fi_path):
            st.image(fi_path, use_container_width=True)
        else:
            st.caption("Run notebooks/analysis.py to generate this chart.")

    st.markdown("---")
    st.subheader("Tech Stack")
    cols = st.columns(3)
    cols[0].markdown("**ML / Data**\n- pandas, numpy\n- scikit-learn\n- TfidfVectorizer\n- TruncatedSVD\n- RandomForest")
    cols[1].markdown("**Visualization**\n- matplotlib\n- seaborn\n- Streamlit charts")
    cols[2].markdown("**API / Deploy**\n- FastAPI\n- uvicorn\n- Streamlit Cloud\n- GitHub Actions")
