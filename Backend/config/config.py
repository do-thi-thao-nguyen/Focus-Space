import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

client = None
db = None

def _extract_db_name(uri: str, fallback: str = "bookingdb") -> str:
    try:
        tail = uri.rsplit("/", 1)[-1]
        return (tail.split("?", 1)[0] or fallback).strip()
    except Exception:
        return fallback

def init_db(app):
    global client, db
    load_dotenv()
    uri = os.getenv("MONGO_URI", "").strip()
    if not uri:
        uri = "mongodb://localhost:27017/bookingdb"
    app.config["MONGO_URI"] = uri

    db_name = _extract_db_name(uri, "bookingdb")

    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=20000
    )
    db = client[db_name]

    client.admin.command("ping")
    print(f"[mongo] Connected OK to '{db_name}' via TLS")
    return db

# Load MoMo keys
load_dotenv()
MOMO_PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE", "MOMO")
MOMO_ACCESS_KEY   = os.getenv("MOMO_ACCESS_KEY", "")
MOMO_SECRET_KEY   = os.getenv("MOMO_SECRET_KEY", "")
