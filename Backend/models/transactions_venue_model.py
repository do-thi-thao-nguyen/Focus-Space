from config.config import db
from bson import ObjectId
from datetime import datetime

class TransactionsVenueModel:
    collection = db["transactions_venue"]

    @staticmethod
    def create_transaction(customer, items, total=0):
        transaction = {
            "customer": customer,
            "items": items,        # list venue + device
            "total": total,
            "status": "pending",
            "createdAt": datetime.utcnow()
        }
        result = TransactionsVenueModel.collection.insert_one(transaction)
        return str(result.inserted_id)

    @staticmethod
    def get_transaction(id):
        transaction = TransactionsVenueModel.collection.find_one({"_id": ObjectId(id)})
        if transaction:
            transaction["_id"] = str(transaction["_id"])
        return transaction

    @staticmethod
    def get_simple_history(date=None, session=None):
        """
        Lấy lịch sử thuê Venue từ transactions_venue
        Trả về 3 trường: item, date, session
        """
        pipeline = [
            {"$unwind": "$items"},
            {"$match": {"items.type": "venue"}},  # chỉ lấy venue
            {"$project": {
                "_id": 0,
                "item": "$items.name",
                "date": "$items.date",
                "session": "$items.session"
            }}
        ]

        # Thêm filter nếu có
        match_cond = {}
        if date:
            match_cond["items.date"] = date
        if session:
            match_cond["items.session"] = session
        if match_cond:
            pipeline.insert(1, {"$match": match_cond})

        data = list(TransactionsVenueModel.collection.aggregate(pipeline))
        return data
