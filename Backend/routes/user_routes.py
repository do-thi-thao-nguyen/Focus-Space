# routes/user_routes.py
# --------------------
from flask import Blueprint, request, jsonify
from bson import ObjectId
from config.config import db  # db = mongo.db (đã gán trong init_db)

users_bp = Blueprint("users", __name__)

# Tạo user
@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json(force=True, silent=True) or {}
    required = ["username", "password", "fullname", "email"]
    if not all(k in data and str(data[k]).strip() for k in required):
        return jsonify(error="Thiếu field bắt buộc"), 400

    # demo: không hash pass; production nên hash!
    if db.users.find_one({"username": data["username"]}):
        return jsonify(error="username đã tồn tại"), 409

    doc = {
        "username": data["username"].strip(),
        "password": data["password"],
        "fullname": data["fullname"].strip(),
        "email": data["email"].strip(),
    }
    res = db.users.insert_one(doc)
    return jsonify(id=str(res.inserted_id), username=doc["username"]), 201


# Đăng nhập (CHO PHÉP POST)
@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True, silent=True) or {}
    u = data.get("username", "").strip()
    p = data.get("password", "")
    if not u or not p:
        return jsonify(error="Thiếu username/password"), 400

    user = db.users.find_one({"username": u, "password": p})
    if not user:
        return jsonify(error="Sai thông tin đăng nhập"), 401

    # demo: trả user cơ bản (có thể phát JWT nếu bạn muốn)
    return jsonify(
    message="login ok",
    user={
        "id": str(user["_id"]),   # đảm bảo ObjectId thành string
        "username": user["username"],
    }
), 200



# Lấy chi tiết user theo id hoặc username (tùy bạn dùng gì)
@users_bp.route("/<user_id>", methods=["GET", "PATCH", "DELETE"])
def user_detail(user_id):
    # nếu bạn lưu id dạng string (vd "u1"): dùng theo username
    user = db.users.find_one({"username": user_id}) or db.users.find_one({"_id": ObjectId(user_id)})  # thử cả 2 kiểu
    if not user:
        return jsonify(error="User không tồn tại"), 404

    if request.method == "GET":
        return jsonify(
            id=str(user["_id"]), username=user["username"],
            fullname=user.get("fullname"), email=user.get("email"),
        )

    if request.method == "PATCH":
        data = request.get_json(force=True, silent=True) or {}
        up = {k: v for k, v in data.items() if k in ["fullname", "email", "password"]}
        if not up:
            return jsonify(error="Không có gì để cập nhật"), 400
        db.users.update_one({"_id": user["_id"]}, {"$set": up})
        user.update(up)
        return jsonify(message="updated", id=str(user["_id"]))

    # DELETE
    db.users.delete_one({"_id": user["_id"]})
    return jsonify(message="deleted", id=str(user["_id"])), 200
