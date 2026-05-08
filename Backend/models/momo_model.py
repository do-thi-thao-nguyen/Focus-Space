from datetime import datetime
from config.config import db

class MomoModel:
    @staticmethod
    def create_transaction(user_id, amount, order_id, request_id, pay_url):
        doc = {
            "user_id": user_id,
            "method": "momo",
            "amount": amount,
            "order_id": order_id,
            "request_id": request_id,
            "pay_url": pay_url,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        db.transactions.insert_one(doc)
        return doc

    @staticmethod
    def update_status(order_id, status, response=None):
        db.transactions.update_one(
            {"order_id": order_id},
            {"$set": {"status": status, "response": response, "updated_at": datetime.utcnow()}}
        )
