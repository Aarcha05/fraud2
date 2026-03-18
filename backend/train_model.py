import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
from pymongo import MongoClient

# MongoDB connection (falls back to CSV if DB empty)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client.get_database(os.getenv("MONGODB_DB", "fraud_db"))
transactions_col = db.get_collection("transactions")

# 🔥 FIXED feature order (IMPORTANT)
FEATURES = [
    "Time",
    "V1","V2","V3","V4","V5","V6","V7","V8","V9","V10",
    "V11","V12","V13","V14","V15","V16","V17","V18","V19","V20",
    "V21","V22","V23","V24","V25","V26","V27","V28",
    "Amount"
]

# Try loading data from MongoDB
docs = list(transactions_col.find({}, {k: 1 for k in FEATURES + ["Class"]}))
if docs:
    df = pd.DataFrame(docs)
    # If Mongo documents have an `_id` column, drop it
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    # Ensure all FEATURES exist
    for col in FEATURES + ["Class"]:
        if col not in df.columns:
            df[col] = 0
else:
    # fallback to CSV
    df = pd.read_csv("creditcard.csv")

X = df[FEATURES]
y = df["Class"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model retrained with fixed feature order")
