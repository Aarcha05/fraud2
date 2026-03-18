import pandas as pd
import os
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URI)
db = client.get_database(os.getenv("MONGODB_DB", "fraud_db"))
transactions_col = db.get_collection("transactions")

def import_csv(path="creditcard.csv", chunk_size=10000):
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    for chunk in pd.read_csv(path, chunksize=chunk_size):
        records = chunk.to_dict(orient="records")
        transactions_col.insert_many(records)

if __name__ == "__main__":
    print("Importing creditcard.csv into MongoDB (collection=transactions)...")
    import_csv()
    print("Done")
