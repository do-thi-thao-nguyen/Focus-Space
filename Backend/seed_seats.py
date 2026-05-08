import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

def connect_db():
    load_dotenv()
    uri = os.getenv("MONGO_URI", "").strip()
    if not uri:
        uri = "mongodb://localhost:27017/bookingdb"

    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=20000
    )
    db_name = uri.rsplit("/", 1)[-1].split("?")[0] or "bookingdb"
    return client[db_name]

def seed_seats():
    db = connect_db()
    db.tickets.delete_many({})

    # Danh sách ghế (theo layout em gửi)
    seats = []

    # Inner (I1-I4)
    seats += [f"I{i}" for i in range(1, 5)]

    # Bàn dài M1-M8
    seats += [f"M{i}" for i in range(1, 9)]

    # Bàn nhóm L1-L8
    seats += [f"L{i}" for i in range(1, 9)]

    # Sofa S1-S8
    seats += [f"S{i}" for i in range(1, 9)]

    # Kệ K1-K2
    seats += [f"K{i}" for i in range(1, 3)]

    # N1-N8
    seats += [f"N{i}" for i in range(1, 9)]
    
    seats += [f"A{i}" for i in range(1, 9)]
    
    seats += [f"B{i}" for i in range(1, 9)]
    
    seats += [f"C{i}" for i in range(1, 9)]

   # Insert vào DB
    docs = [{"_id": seat, "bookings": []} for seat in seats]
    db.tickets.insert_many(docs)

    print(f"✅ Đã tạo {len(seats)} ghế vào DB!")

if __name__ == "__main__":
    seed_seats()