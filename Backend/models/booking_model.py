from config.config import db
from bson import ObjectId

class BookingModel:
    collection = db.booking

    @staticmethod
    def get_all():
        bookings = list(BookingModel.collection.find())
        for b in bookings:
            b["_id"] = str(b["_id"])
        return bookings

    @staticmethod
    def add(data):
        item = {
            "type": data.get("type"),      # "venue" hoặc "device"
            "itemId": data.get("itemId"),
            "name": data.get("name"),
            "date": data.get("date"),
            "session": data.get("session"),
            "guests": data.get("guests"),
            "price": data.get("price", 0)
        }
        BookingModel.collection.insert_one(item)
        return True

    @staticmethod
    def delete(id):
        return BookingModel.collection.delete_one({"_id": ObjectId(id)})

    @staticmethod
    def clear():
        BookingModel.collection.delete_many({})
        return True
