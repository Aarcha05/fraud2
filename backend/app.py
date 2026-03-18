from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory
from flask_cors import CORS
import pickle
import pandas as pd
import os
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURES = list(model.feature_names_in_)

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client.get_database(os.getenv("MONGODB_DB", "fraud_db"))
predictions_col = db.get_collection("predictions")
users_col = db.get_collection("users")  # ← users collection


# Path to frontend folder (one level up from backend)
FRONTEND = os.path.join(os.path.dirname(__file__), '..', 'frontend')
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')


# ─── Serve static files ───────────────────────────────────────────────────────
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


# ─── Pages ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND, "index.html")


# ─── Register ─────────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email    = request.form.get("email")
        password = request.form.get("password")

        # Check if username already exists
        if users_col.find_one({"username": username}):
            return send_from_directory(FRONTEND, "register.html")

        # Save new user to MongoDB
        users_col.insert_one({
            "username": username,
            "email": email,
            "password": password,
            "created_at": datetime.utcnow()
        })

        return redirect(url_for("home"))  # redirect to login after register

    return send_from_directory(FRONTEND, "register.html")


# ─── Login ────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Check user in MongoDB
    user = users_col.find_one({"username": username, "password": password})

    if user:
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid username or password")


# ─── Predict ──────────────────────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    df = pd.DataFrame(
        [[data.get(col, 0) for col in FEATURES]],
        columns=FEATURES
    )

    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]

    # Log to MongoDB (best-effort)
    try:
        doc = {k: (v if not pd.isna(v) else None) for k, v in data.items()}
        doc.update({"Fraud": int(pred), "Probability": float(prob), "timestamp": datetime.utcnow()})
        predictions_col.insert_one(doc)
    except Exception:
        pass

    return jsonify({
        "Fraud": int(pred),
        "Probability": float(prob)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)