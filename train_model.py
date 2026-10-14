
import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Load the existing traffic dataset
DATA_FILE = os.path.join("data", "cleaned_traffic_data.csv")

df = pd.read_csv(DATA_FILE)

# Check the required columns
required = ["AverageTCI", "MaxTCI"]
if not all(col in df.columns for col in required):
    raise ValueError(
        "Dataset must contain AverageTCI and MaxTCI columns."
    )

# Use the existing congestion categories if available;
# otherwise create categories from AverageTCI.
if "CongestionLevel" in df.columns:
    y = df["CongestionLevel"].astype(str).str.title()
else:
    y = pd.cut(
        df["AverageTCI"],
        bins=[-float("inf"), 10, 30, float("inf")],
        labels=["Low", "Medium", "High"]
    ).astype(str)

X = df[["AverageTCI", "MaxTCI"]].copy()

# Remove invalid or missing rows
valid = X.notna().all(axis=1) & y.notna() & (y != "Nan")
X = X.loc[valid]
y = y.loc[valid]

if y.nunique() < 2:
    raise ValueError("Training data needs at least two classes.")

# Train a Random Forest classifier
model = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    ))
])

model.fit(X, y)

# Save the trained model and feature names
os.makedirs("models", exist_ok=True)

joblib.dump(
    {
        "model": model,
        "features": ["AverageTCI", "MaxTCI"]
    },
    os.path.join("models", "traffic_model.joblib")
)

print("Model training completed successfully.")
print("Rows used:", len(X))
print("Classes:", sorted(y.unique()))
print("Saved to: models/traffic_model.joblib")

# Small dataset: show cross-validation only if each class
# has enough examples for 3-fold validation.
class_counts = y.value_counts()

if class_counts.min() >= 3:
    scores = cross_val_score(model, X, y, cv=3)
    print("3-fold cross-validation accuracy:",
          round(scores.mean(), 3))
else:
    print("Cross-validation skipped: a class has fewer than 3 rows.")
print("\nTraining classification report (training data only):")
print(classification_report(y, model.predict(X), zero_division=0))
