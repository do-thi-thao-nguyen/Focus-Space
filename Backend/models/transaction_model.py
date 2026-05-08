from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bookingdb")

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]


# ===========================
# Model Transaction
# ===========================
class TransactionModel:

    @staticmethod
    def create_transaction(customer, items):
        """
        Tạo mới một transaction khi checkout
        :param customer: dict thông tin khách hàng
        :param items: list các item (venue/device)
        :return: transaction_id
        """
        transaction = {
            "customer": customer,
            "items": items,
            "status": "pending",   # pending | paid | cancelled
        }
        result = db.transactions.insert_one(transaction)
        return str(result.inserted_id)

    @staticmethod
    def get_transaction(transaction_id):
        """
        Lấy transaction theo ID
        """
        try:
            transaction = db.transactions.find_one({"_id": ObjectId(transaction_id)})
            if not transaction:
                return None

            transaction["_id"] = str(transaction["_id"])  # Convert ObjectId -> str
            return transaction
        except Exception as e:
            print("Lỗi khi lấy transaction:", e)
            return None

    @staticmethod
    def update_status(transaction_id, status):
        """
        Cập nhật trạng thái giao dịch
        """
        try:
            result = db.transactions.update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": {"status": status}}
            )
            return result.modified_count > 0
        except Exception as e:
            print("Lỗi update status:", e)
            return False
