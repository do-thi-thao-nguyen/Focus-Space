import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load biến môi trường
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bookingdb")

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

devices = [
    {
        "name": "Máy chiếu Epson XGA",
        "price": 800000,
        "description": "Máy chiếu sáng rõ, hỗ trợ HDMI/VGA, phù hợp hội thảo và lớp học.",
        "images": ["/assets/img/MC.jpg"]   # đổi sang đường dẫn web
    },
    {
        "name": "Loa Marshall",
        "price": 500000,
        "description": "Loa Marshall cổ điển, sang trọng, chất lượng cao.",
        "images": ["/assets/img/MS1.jpg"]
    },
    {
        "name": "Bảng trắng Flipchart",
        "price": 100000,
        "description": "Bảng trắng flipchart hỗ trợ các lớp dạy học, hội thảo.",
        "images": ["/assets/img/FC.jpg"]
    },
    {
        "name": "Micro không dây",
        "price": 100000,
        "description": "Micro không dây tiện dụng, phù hợp cho các hội thảo và sự kiện.",
        "images": ["/assets/img/Mic.jpg"]
    }
]

if db is not None:
    db.devices.delete_many({})
    result = db.devices.insert_many(devices)
    print("✅ Seeded 4 devices thành công!")

    # In ra _id để copy qua frontend
    for d, oid in zip(devices, result.inserted_ids):
        print(f"{d['name']} => {oid}")
