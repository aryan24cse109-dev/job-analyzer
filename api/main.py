"""
Job Market Analyzer — FastAPI Backend
======================================
Endpoints:
  POST /predict        — predict salary tier for a given profile
  GET  /top-skills     — top 20 in-demand skills
  GET  /market-summary — avg salary by role
  GET  /health         — health check

Run:
  pip install fastapi uvicorn
  uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import pickle
import os

# ── Load artifacts ────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, '..', 'models')
DATA_PATH = os.path.join(BASE, '..', 'data', 'jobs.csv')

with open(os.path.join(MODEL_DIR, 'rf_model.pkl'), 'rb') as f: rf = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'tfidf.pkl'),    'rb') as f: tfidf = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'svd.pkl'),      'rb') as f: svd = pickle.load(f)
with open(os.path.join(MODEL_DIR, 'encoders.pkl'), 'rb') as f: enc = pickle.load(f)

le_title     = enc['le_title']
le_loc       = enc['le_loc']
le_exp       = enc['le_exp']
top_skills   = enc['top_skills']
feature_cols = enc['feature_cols']

df = pd.read_csv(DATA_PATH)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Job Market Analyzer API",
    description="Predict data science salary tiers and explore job market insights.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# ── Schemas ───────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    job_title: str       # e.g. "Data Scientist"
    location: str        # e.g. "Bangalore"
    experience_level: str  # Entry | Mid | Senior | Lead
    skills: List[str]    # e.g. ["Python", "SQL", "Machine Learning"]

class PredictResponse(BaseModel):
    salary_tier: str         # Low | Mid | High
    salary_range_lpa: str    # human-readable
    confidence: float        # max class probability
    top_skills_to_add: List[str]

# ── Helpers ───────────────────────────────────────────────────────────────────
SALARY_RANGES = {"Low": "₹3L – ₹10L", "Mid": "₹10L – ₹25L", "High": "₹25L+"}

def encode_safe(le: object, val: str, fallback: int = 0) -> int:
    try:
        return int(le.transform([val])[0])
    except ValueError:
        return fallback

def build_feature_vector(req: PredictRequest) -> pd.DataFrame:
    skills_str = ', '.join(req.skills)
    row = {
        'title_enc':  encode_safe(le_title, req.job_title),
        'loc_enc':    encode_safe(le_loc,   req.location),
        'exp_enc':    encode_safe(le_exp,   req.experience_level),
        'num_skills': len(req.skills),
        'remote':     1 if req.location.lower() == 'remote' else 0,
    }
    for sk in top_skills:
        row[f'skill_{sk.replace(" ","_")}'] = 1 if sk in req.skills else 0

    # SVD on skills text (same technique as SVD Compressor project)
    X_tfidf = tfidf.transform([skills_str])
    X_svd   = svd.transform(X_tfidf)
    for i in range(5):
        row[f'svd_{i}'] = float(X_svd[0, i])

    return pd.DataFrame([row])[feature_cols]

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "RandomForest v1.0", "records": len(df)}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    valid_titles = list(le_title.classes_)
    valid_locs   = list(le_loc.classes_)
    valid_exps   = list(le_exp.classes_)

    if req.job_title not in valid_titles:
        raise HTTPException(400, f"job_title must be one of {valid_titles}")
    if req.location not in valid_locs:
        raise HTTPException(400, f"location must be one of {valid_locs}")
    if req.experience_level not in valid_exps:
        raise HTTPException(400, f"experience_level must be one of {valid_exps}")

    X   = build_feature_vector(req)
    tier = rf.predict(X)[0]
    proba = rf.predict_proba(X)[0]
    confidence = float(round(max(proba), 3))

    # Recommend skills the user doesn't have from top 20
    user_skills_set = set(req.skills)
    missing = [s for s in top_skills if s not in user_skills_set][:3]

    return PredictResponse(
        salary_tier=tier,
        salary_range_lpa=SALARY_RANGES[tier],
        confidence=confidence,
        top_skills_to_add=missing
    )


@app.get("/top-skills")
def top_skills_route(top_n: int = 20):
    from collections import Counter
    all_skills = []
    for s in df['skills']:
        all_skills.extend([x.strip() for x in s.split(',')])
    counts = Counter(all_skills)
    return {
        "top_skills": [
            {"skill": s, "count": c, "demand_pct": round(c / len(df) * 100, 1)}
            for s, c in counts.most_common(top_n)
        ]
    }


@app.get("/market-summary")
def market_summary():
    summary = (
        df.groupby('job_title')['salary_lpa']
        .agg(['mean', 'median', 'count'])
        .rename(columns={'mean': 'avg_salary_lpa', 'median': 'median_salary_lpa', 'count': 'num_jobs'})
        .round(1)
        .reset_index()
        .sort_values('avg_salary_lpa', ascending=False)
    )
    return {
        "roles": summary.to_dict(orient='records'),
        "total_jobs": int(len(df)),
        "overall_avg_salary": round(float(df['salary_lpa'].mean()), 1)
    }


@app.get("/locations")
def locations():
    loc_data = (
        df.groupby('location')
        .agg(num_jobs=('job_title', 'count'), avg_salary=('salary_lpa', 'mean'))
        .round(1).reset_index()
        .sort_values('num_jobs', ascending=False)
    )
    return {"locations": loc_data.to_dict(orient='records')}
