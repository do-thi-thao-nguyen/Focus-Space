import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bookingdb")

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

venues = [
    {
        "name": "The Light House",
        "address": "Lầu 1, 152 Nam Kỳ Khởi Nghĩa, phường Sài Gòn",
        "capacity": 60,
        "priceMorning": 5000000,
        "priceAfternoon": 5000000,
        "priceFull": 8000000,
        "description": "Không gian thư viện sang trọng, phù hợp tổ chức các sự kiện ra mắt sách, triển lãm...",
        "images": [
            "./assets/img/L1.jpg",
            "./assets/img/L2.jpg",
            "./assets/img/L3.jpg",
            "./assets/img/L4.jpg",
            "./assets/img/L5.jpg",
            "./assets/img/L6.jpg"
        ]
    },
    {
        "name": "The Nest",
        "address": "Lầu 1, 152 Nam Kỳ Khởi Nghĩa, phường Sài Gòn",
        "capacity": 40,
        "priceMorning": 3000000,
        "priceAfternoon": 3000000,
        "priceFull": 5000000,
        "description": "Không gian rộng rãi, sáng tạo cho trẻ em phù hợp với Workshop...",
        "images": [
            "./assets/img/N1.jpg",
            "./assets/img/N2.jpg",
            "./assets/img/N3.jpg",
            "./assets/img/N4.jpg",
            "./assets/img/N5.jpg",
            "./assets/img/N6.jpg",
            "./assets/img/N7.jpg"
        ]
    },
    {
        "name": "The Prism",
        "address": "Tầng Trệt, 152 Nam Kỳ Khởi Nghĩa, phường Sài Gòn",
        "capacity": 70,
        "priceMorning": 8000000,
        "priceAfternoon": 8000000,
        "priceFull": 12000000,
        "description": "Không gian cao cấp, hiện đại, phù hợp với các sự kiện đông người",
        "images": [
            "./assets/img/P1.jpg",
            "./assets/img/P2.jpg",
            "./assets/img/P3.jpg",
            "./assets/img/P4.jpg",
            "./assets/img/P5.jpg"
        ]
    }
]

db.venues.delete_many({})
db.venues.insert_many(venues)
print("✅ Seeded 3 venues với ảnh local thành công!")
