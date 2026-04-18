"""
Job Market Analyzer - EDA & Model Training
==========================================
Run this script to reproduce the full analysis pipeline.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from collections import Counter
import pickle, os

# ── 1. Load Data ─────────────────────────────────────────────────────────────
df = pd.read_csv('../data/jobs.csv')
print(f"Dataset shape: {df.shape}")
print(df.head())

# ── 2. EDA ────────────────────────────────────────────────────────────────────
print("\n── Salary Stats ──")
print(df['salary_lpa'].describe())
print("\n── Top Roles ──")
print(df['job_title'].value_counts())

# ── 3. Feature Engineering ────────────────────────────────────────────────────
all_skills = []
for s in df['skills']:
    all_skills.extend([x.strip() for x in s.split(',')])
skill_counts = Counter(all_skills)
top_skills = [s for s, c in skill_counts.most_common(20)]
print(f"\nTop skills: {top_skills[:10]}")

for sk in top_skills:
    df[f'skill_{sk.replace(" ","_")}'] = df['skills'].apply(lambda x: 1 if sk in x else 0)

le_title = LabelEncoder()
le_loc   = LabelEncoder()
le_exp   = LabelEncoder()
df['title_enc'] = le_title.fit_transform(df['job_title'])
df['loc_enc']   = le_loc.fit_transform(df['location'])
df['exp_enc']   = le_exp.fit_transform(df['experience_level'])

# ── 4. TF-IDF + SVD (Skills NLP) ─────────────────────────────────────────────
# Applies the same Truncated SVD technique from the SVD Compressor project
# to reduce high-dimensional TF-IDF skill vectors into dense latent features.
tfidf = TfidfVectorizer(max_features=50)
X_tfidf = tfidf.fit_transform(df['skills'])
svd = TruncatedSVD(n_components=5, random_state=42)
X_svd = svd.fit_transform(X_tfidf)
print(f"\nSVD explained variance ratio: {svd.explained_variance_ratio_.sum():.3f}")

svd_df = pd.DataFrame(X_svd, columns=[f'svd_{i}' for i in range(5)])
df = pd.concat([df.reset_index(drop=True), svd_df], axis=1)

# ── 5. Model Training ─────────────────────────────────────────────────────────
skill_cols   = [f'skill_{sk.replace(" ","_")}' for sk in top_skills]
svd_cols     = [f'svd_{i}' for i in range(5)]
feature_cols = ['title_enc', 'loc_enc', 'exp_enc', 'num_skills', 'remote'] + skill_cols + svd_cols

X = df[feature_cols]
y = df['salary_tier']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42)
rf.fit(X_train, y_train)

y_pred = rf.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
cv     = cross_val_score(rf, X, y, cv=5, scoring='accuracy').mean()

print(f"\nTest Accuracy  : {acc:.4f}")
print(f"5-Fold CV Mean : {cv:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── 6. Save Artifacts ─────────────────────────────────────────────────────────
os.makedirs('../models', exist_ok=True)
with open('../models/rf_model.pkl', 'wb') as f:  pickle.dump(rf, f)
with open('../models/tfidf.pkl', 'wb') as f:     pickle.dump(tfidf, f)
with open('../models/svd.pkl', 'wb') as f:       pickle.dump(svd, f)
with open('../models/encoders.pkl', 'wb') as f:
    pickle.dump({
        'le_title': le_title, 'le_loc': le_loc, 'le_exp': le_exp,
        'top_skills': top_skills, 'feature_cols': feature_cols
    }, f)

print("\nAll model artifacts saved to ../models/")
