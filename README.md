# Job Market Analyzer — India Data Science Roles

> End-to-end ML pipeline: data → feature engineering → TF-IDF + SVD → Random Forest → FastAPI → Streamlit dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![sklearn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What This Project Does

Analyzes 500+ data science job listings across 9 Indian cities and predicts whether a candidate's profile falls in a **Low / Mid / High** salary tier using machine learning. Built as a full research-grade pipeline with a REST API and an interactive dashboard.

**Live Demo** → [your-app-name.streamlit.app](https://your-app-name.streamlit.app)  
**API Docs** → [your-api.railway.app/docs](https://your-api.railway.app/docs)

---

## Project Structure

```
job-analyzer/
├── streamlit_app.py          # Dashboard entry point (Streamlit Cloud)
├── requirements.txt          # All dependencies
├── Procfile                  # FastAPI deployment (Railway / Render)
├── .gitignore
├── .streamlit/
│   └── config.toml           # Streamlit theme config
│
├── data/
│   └── jobs.csv              # 500 India DS job listings
│
├── models/
│   ├── rf_model.pkl          # Trained RandomForest classifier
│   ├── tfidf.pkl             # TF-IDF vectorizer (fitted)
│   ├── svd.pkl               # TruncatedSVD (5 components)
│   └── encoders.pkl          # Label encoders + metadata
│
├── notebooks/
│   └── analysis.py           # Full EDA + training script (reproduce results)
│
├── api/
│   └── main.py               # FastAPI backend (4 endpoints)
│
└── app/
    ├── streamlit_app.py      # Original dashboard (local paths)
    └── static/               # Pre-generated charts
        ├── analysis.png
        ├── feature_importance.png
        └── confusion_matrix.png
```

---

## Methodology

### 1. Feature Engineering
- Label encoding for job title, location, experience level
- Binary skill flags for top 20 in-demand skills
- Skills count per listing, remote flag

### 2. NLP + SVD (Key Innovation)
Job skills text is vectorized using **TF-IDF** (50 features) then compressed using **Truncated SVD** (5 components), capturing 23.6% of skill variance as dense latent features.

```python
tfidf = TfidfVectorizer(max_features=50)
X_tfidf = tfidf.fit_transform(df['skills'])

svd = TruncatedSVD(n_components=5, random_state=42)
X_svd = svd.fit_transform(X_tfidf)
```

> This directly applies the same matrix decomposition principle used in image compression (SVD Compressor project) to NLP feature reduction — demonstrating the universality of linear algebra across domains.

### 3. Classification
- **Model**: RandomForestClassifier (150 trees, max_depth=12)
- **Target**: Salary tier — Low (3–10L) / Mid (10–25L) / High (25L+)
- **Test Accuracy**: 72% | **High-tier F1**: 0.79 | **5-fold CV**: ~70%

---

## API Reference

Start the API locally:
```bash
cd api
uvicorn main:app --reload
# Docs at http://localhost:8000/docs
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Status check |
| `POST` | `/predict` | Predict salary tier |
| `GET`  | `/top-skills` | Top 20 in-demand skills |
| `GET`  | `/market-summary` | Avg salary by role |
| `GET`  | `/locations` | Jobs + salary by city |

### Sample Request
```bash
curl -X POST https://your-api.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Data Scientist",
    "location": "Bangalore",
    "experience_level": "Mid",
    "skills": ["Python", "SQL", "Machine Learning", "TensorFlow"]
  }'
```

### Sample Response
```json
{
  "salary_tier": "High",
  "salary_range_lpa": "25L+ LPA",
  "confidence": 0.81,
  "top_skills_to_add": ["Deep Learning", "AWS", "Docker"]
}
```

---

## Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/job-analyzer.git
cd job-analyzer

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Retrain the model
cd notebooks && python analysis.py && cd ..

# 4. Run the dashboard
streamlit run streamlit_app.py

# 5. Run the API (in a separate terminal)
cd api && uvicorn main:app --reload
```

---

## Key Findings

| Insight | Detail |
|---------|--------|
| Highest-paid role | Research Scientist (avg 32L LPA) |
| Top skill | Python (present in 65% of listings) |
| City premium | Bangalore / Delhi / Gurgaon pay 3–5L more |
| Experience jump | Senior earns 2–3× Entry in same role |
| SVD components | Reveal 3 skill clusters: classical ML, cloud/DevOps, BI/viz |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data | pandas, numpy |
| NLP | TfidfVectorizer, TruncatedSVD |
| ML | RandomForestClassifier, scikit-learn |
| Visualization | matplotlib, seaborn |
| API | FastAPI, uvicorn, pydantic |
| Dashboard | Streamlit |
| Deployment | Streamlit Cloud (dashboard) · Railway (API) |

---

## Research Alignment

This project maps to **IIT Kharagpur's "AI for Societal Needs"** research initiative — applying ML to labor market intelligence and skill gap analysis, a high-impact problem for India's growing data economy.

---

## License

MIT License — free to use, modify, and distribute.

---

*Built as part of a research internship portfolio · April 2026*
