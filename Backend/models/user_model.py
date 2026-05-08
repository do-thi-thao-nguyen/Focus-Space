from bson import ObjectId
from config.config import db

class UserModel:
    collection = db.users

    @staticmethod
    def create_user(data):
        required = ["username", "password", "fullname", "email"]
        if not all(k in data and str(data[k]).strip() for k in required):
            return None, "Thiếu field bắt buộc"

        # Check username tồn tại
        if UserModel.collection.find_one({"username": data["username"].strip()}):
            return None, "username đã tồn tại"

        doc = {
            "username": data["username"].strip(),
            "password": data["password"],  # demo: chưa hash
            "fullname": data["fullname"].strip(),
            "email": data["email"].strip(),
        }
        res = UserModel.collection.insert_one(doc)
        return str(res.inserted_id), None

    @staticmethod
    def login(username, password):
        user = UserModel.collection.find_one({"username": username.strip(), "password": password})
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "fullname": user.get("fullname"),
            "email": user.get("email"),
        }

    @staticmethod
    def get_user(user_id):
        user = None
        try:
            user = UserModel.collection.find_one({"_id": ObjectId(user_id)})
        except:
            user = UserModel.collection.find_one({"username": user_id})
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "username": user["username"],
            "fullname": user.get("fullname"),
            "email": user.get("email"),
        }

    @staticmethod
    def update_user(user_id, data):
        try:
            user = UserModel.collection.find_one({"_id": ObjectId(user_id)})
        except:
            user = UserModel.collection.find_one({"username": user_id})

        if not user:
            return None, "User không tồn tại"

        up = {k: v for k, v in data.items() if k in ["fullname", "email", "password"]}
        if not up:
            return None, "Không có gì để cập nhật"

        UserModel.collection.update_one({"_id": user["_id"]}, {"$set": up})
        return str(user["_id"]), None

    @staticmethod
    def delete_user(user_id):
        try:
            user = UserModel.collection.find_one({"_id": ObjectId(user_id)})
        except:
            user = UserModel.collection.find_one({"username": user_id})

        if not user:
            return None, "User không tồn tại"

        UserModel.collection.delete_one({"_id": user["_id"]})
        return str(user["_id"]), None
