
from pathlib import Path

from flask import Flask, jsonify, request, render_template, Response
import pandas as pd
import joblib


# --------------------------------------------------
# PROJECT PATHS AND APP SETUP
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent

DATA_FILE = ROOT / "data" / "cleaned_traffic_data.csv"
MODEL_FILE = ROOT / "models" / "traffic_model.joblib"

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


# --------------------------------------------------
# LOAD TRAINED MACHINE LEARNING MODEL
# --------------------------------------------------

try:
    model_bundle = joblib.load(MODEL_FILE)
    traffic_model = model_bundle["model"]
    MODEL_FEATURES = model_bundle["features"]

    print("Trained ML model loaded successfully.")

except Exception as error:
    traffic_model = None
    MODEL_FEATURES = ["AverageTCI", "MaxTCI"]
    print("Warning: ML model could not be loaded:", error)


# --------------------------------------------------
# LOAD AND CLEAN TRAFFIC DATA
# --------------------------------------------------

def load_data():
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

    required = {"City", "AverageTCI", "MaxTCI"}

    if not required.issubset(df.columns):
        raise ValueError(
            "CSV must contain City, AverageTCI and MaxTCI columns."
        )

    for col in ("AverageTCI", "MaxTCI"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=["City", "AverageTCI", "MaxTCI"]
    ).copy()

    df["City"] = df["City"].astype(str)

    return df


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.get("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# OTHER HTML PAGES
# --------------------------------------------------

@app.get("/<page>")
@app.get("/<page>.html")
def pages(page):
    allowed = {
        "index",
        "dashboard",
        "patterns",
        "predict",
        "reports",
        "about"
    }

    if page not in allowed:
        return "Page not found", 404

    return render_template(f"{page}.html")


# --------------------------------------------------
# BACKEND HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "TrafficAI backend is running",
        "modelLoaded": traffic_model is not None
    })


# --------------------------------------------------
# TRAFFIC DATA API
# --------------------------------------------------

@app.get("/api/data")
def data_csv():
    df = load_data()

    return Response(
        df.to_csv(index=False),
        mimetype="text/csv"
    )


# --------------------------------------------------
# DASHBOARD STATISTICS API
# --------------------------------------------------

@app.get("/api/stats")
def stats():
    df = load_data()

    highest = df.loc[df["AverageTCI"].idxmax()]
    lowest = df.loc[df["AverageTCI"].idxmin()]

    if "CongestionLevel" in df.columns:
        categories = (
            df["CongestionLevel"]
            .astype(str)
            .str.title()
            .value_counts()
            .to_dict()
        )
    else:
        levels = pd.cut(
            df["AverageTCI"],
            bins=[-float("inf"), 10, 25, float("inf")],
            labels=["Low", "Medium", "High"]
        ).astype(str)

        categories = levels.value_counts().to_dict()

    return jsonify({
        "totalCities": int(len(df)),
        "highestCity": str(highest["City"]),
        "lowestCity": str(lowest["City"]),
        "averageTCI": round(float(df["AverageTCI"].mean()), 2),
        "maximumTCI": round(float(df["MaxTCI"].max()), 2),

        "topCities": (
            df.sort_values("AverageTCI", ascending=False)
            .head(10)[["City", "AverageTCI", "MaxTCI"]]
            .to_dict("records")
        ),

        "categorySummary": categories
    })


# --------------------------------------------------
# TRAFFIC PATTERNS API
# --------------------------------------------------

@app.get("/api/patterns")
def patterns():
    df = load_data()

    if "CongestionLevel" not in df.columns:
        df["CongestionLevel"] = pd.cut(
            df["AverageTCI"],
            bins=[-float("inf"), 10, 25, float("inf")],
            labels=["Low", "Medium", "High"]
        ).astype(str)

    categories = (
        df["CongestionLevel"]
        .astype(str)
        .str.title()
        .value_counts()
        .to_dict()
    )

    top_cities = (
        df.sort_values("AverageTCI", ascending=False)
        .head(10)
        .copy()
    )

    top_cities["CongestionLevel"] = pd.cut(
        top_cities["AverageTCI"],
        bins=[-float("inf"), 10, 25, float("inf")],
        labels=["Low", "Medium", "High"]
    ).astype(str)

    return jsonify({
        "categories": categories,
        "topCities": top_cities[
            ["City", "AverageTCI", "CongestionLevel"]
        ].to_dict("records"),

        "note": (
            "Patterns are based on city-level AverageTCI and MaxTCI "
            "data. Time and weather patterns are not available "
            "in the current dataset."
        )
    })


# --------------------------------------------------
# DOWNLOAD TRAFFIC REPORT
# --------------------------------------------------

@app.get("/api/reports.csv")
def report_csv():
    df = load_data().sort_values(
        "AverageTCI",
        ascending=False
    )

    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=traffic-analysis-report.csv"
        }
    )


# --------------------------------------------------
# MACHINE LEARNING PREDICTION API
# --------------------------------------------------

@app.post("/api/predict")
def predict():

    if traffic_model is None:
        return jsonify({
            "error": (
                "The trained ML model could not be loaded. "
                "Run py train_model.py first."
            )
        }), 500

    payload = request.get_json(silent=True) or {}

    required = ["AverageTCI", "MaxTCI"]

    missing = [
        key for key in required
        if payload.get(key) in (None, "")
    ]

    if missing:
        return jsonify({
            "error": "Please enter Average TCI and Maximum TCI.",
            "missing": missing
        }), 400

    try:
        average_tci = float(payload["AverageTCI"])
        max_tci = float(payload["MaxTCI"])

    except (TypeError, ValueError):
        return jsonify({
            "error": "Both TCI values must be numbers."
        }), 400

    if (
        not pd.notna(average_tci)
        or not pd.notna(max_tci)
        or average_tci < 0
        or max_tci < 0
    ):
        return jsonify({
            "error": "TCI values must be valid, non-negative numbers."
        }), 400

    if average_tci > max_tci:
        return jsonify({
            "error": "Average TCI cannot exceed Maximum TCI."
        }), 400

    try:
        input_data = pd.DataFrame(
            [[average_tci, max_tci]],
            columns=MODEL_FEATURES
        )

        prediction = traffic_model.predict(input_data)[0]
        level = str(prediction).title()

        return jsonify({
            "level": level,
            "method": "Trained Random Forest ML model",

            "inputs": {
                "AverageTCI": average_tci,
                "MaxTCI": max_tci
            },

            "message": (
                "Congestion category estimated by the trained "
                "model using the supplied traffic index values. "
                "This is a demonstration model, not a validated "
                "forecast of future traffic."
            )
        })

    except Exception as error:
        app.logger.exception("Prediction failed")

        return jsonify({
            "error": "Prediction failed. Please check the model and inputs."
        }), 500


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
