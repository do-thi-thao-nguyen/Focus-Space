import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load biến môi trường
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bookingdb")

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

# ===== Danh sách ghế Light House =====
light_house_seats = (
    [f"I{i}" for i in range(1, 5)] +
    [f"M{i}" for i in range(1, 9)] +
    [f"N{i}" for i in range(1, 9)] +
    [f"L{i}" for i in range(1, 9)] +
    [f"S{i}" for i in range(1, 9)] +
    [f"K{i}" for i in range(1, 3)]
)

# ===== Danh sách ghế The Nest =====
nest_seats = (
    [f"A{i}" for i in range(1, 9)] +
    [f"B{i}" for i in range(1, 9)] +
    [f"C{i}" for i in range(1, 9)] 
)

# ===== Giá vé =====
pricing = {
    "1hour": 30000,
    "4hours": 80000,
    "student": 60000,
    "combo": 135000
}

def make_tickets(venue, seats):
    tickets = []
    for seat in seats:
        tickets.append({
            "venue": venue,
            "seat": seat,
            "pricing": pricing,
            "status": "available"  # default: available
        })
    return tickets

if db is not None:
    venue_tickets = db["venue_tickets"]

    # Xóa dữ liệu cũ
    venue_tickets.delete_many({"venue": {"$in": ["The Light House", "The Nest"]}})

    # Thêm mới
    result1 = venue_tickets.insert_many(make_tickets("The Light House", light_house_seats))
    result2 = venue_tickets.insert_many(make_tickets("The Nest", nest_seats))

    print("✅ Seeded venue_tickets thành công!")

    print(f"The Light House => {len(result1.inserted_ids)} ghế")
    print(f"The Nest => {len(result2.inserted_ids)} ghế")
else:
    print("❌ Không kết nối được database")
