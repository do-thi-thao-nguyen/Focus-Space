# models/cart_model.py
from config.config import db

class CartModel:
    @staticmethod
    def add_item(user_id, item):
        return db.carts.update_one(
            {"user_id": user_id},
            {"$push": {"items": item}},
            upsert=True
        )

    @staticmethod
    def get_cart(user_id):
        return db.carts.find_one({"user_id": user_id})

    @staticmethod
    def remove_item(user_id, item_id):
        return db.carts.update_one(
            {"user_id": user_id},
            {"$pull": {"items.id": item_id}}
        )

    @staticmethod
    def clear(user_id):
        return db.carts.update_one(
            {"user_id": user_id},
            {"$set": {"items": []}}
        )
