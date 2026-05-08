from flask import Blueprint, request, jsonify
from config.config import db
from bson import ObjectId
from datetime import datetime, timedelta

cart_bp = Blueprint("cart", __name__)

# ========================
# Helper: convert ObjectId -> string
# ========================
def convert_objid(doc):
    if isinstance(doc, list):
        return [convert_objid(x) for x in doc]
    elif isinstance(doc, dict):
        return {k: convert_objid(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc


# ========================
# Lấy giỏ hàng của user
# ========================
@cart_bp.route("/<user_id>", methods=["GET"])
def get_cart(user_id):
    try:
        cart = db.carts.find_one({"user_id": str(user_id)})
        if not cart:
            return jsonify({
                "user_id": str(user_id),
                "items": [],
                "customer": {
                    "name": "-",
                    "email": "-",
                    "phone": "-",
                    "address": "-"
                }
            }), 200

        cart = convert_objid(cart)
        if "items" not in cart:
            cart["items"] = []
        if "customer" not in cart:
            cart["customer"] = {
                "name": "-",
                "email": "-",
                "phone": "-",
                "address": "-"
            }

        return jsonify(cart), 200
    except Exception as e:
        print("❌ Lỗi trong get_cart:", e)
        return jsonify({"error": str(e)}), 500


# ========================
# Thêm item vào giỏ
# ========================
@cart_bp.route("/<user_id>/add", methods=["POST"])
def add_to_cart(user_id):
    data = request.json
    if not data:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    seat = data.get("seat")
    ticket_type = data.get("ticket_type")
    qty = int(data.get("qty", 1))
    price = int(data.get("price", 0))
    date_str = data.get("date")
    time_str = data.get("time")

    if not seat or not ticket_type or not date_str or not time_str:
        return jsonify({"error": "Thiếu thông tin vé"}), 400

    # Parse ngày + giờ
    start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    # Xác định end_time theo loại vé
    if ticket_type == "1hour":
        end_dt = start_dt + timedelta(hours=1)
    elif ticket_type == "4hour":
        end_dt = start_dt + timedelta(hours=4)
    elif ticket_type == "student":
        end_dt = start_dt + timedelta(hours=4)
    elif ticket_type == "combo":
        end_dt = start_dt + timedelta(hours=9)   # cả ngày
    else:
        return jsonify({"error": "Loại vé không hợp lệ"}), 400

    # Check overlap trong DB
    conflict = db.carts.find_one({
        "items": {
            "$elemMatch": {
                "seat": seat,
                "date": date_str,
                "start_time": {"$lt": end_dt.strftime("%H:%M")},
                "end_time": {"$gt": start_dt.strftime("%H:%M")}
            }
        }
    })

    if conflict:
        # Nếu có trùng thì thông báo luôn
        booked_item = next(
            (i for i in conflict.get("items", []) if i["seat"] == seat and i["date"] == date_str),
            None
        )
        if booked_item:
            return jsonify({
                "error": f"❌ Ghế {seat} đã có người đặt từ {booked_item['start_time']} đến {booked_item['end_time']}. "
                         f"Vui lòng chọn giờ khác hoặc ghế khác."
            }), 400

    # Nếu không trùng thì thêm vào giỏ
    item = {
        "_id": ObjectId(),
        "seat": seat,
        "ticket_type": ticket_type,
        "qty": qty,
        "price": price,
        "date": date_str,
        "start_time": start_dt.strftime("%H:%M"),
        "end_time": end_dt.strftime("%H:%M")
    }

    db.carts.update_one(
        {"user_id": str(user_id)},
        {"$push": {"items": item}},
        upsert=True
    )

    return jsonify({"message": "✅ Thêm vào giỏ hàng thành công", "item_id": str(item["_id"])}), 200

# ========================
# Cập nhật thông tin khách hàng
# ========================
@cart_bp.route("/<user_id>/update_customer", methods=["POST"])
def update_customer(user_id):
    data = request.json or {}
    customer = {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", "")
    }

    db.carts.update_one(
        {"user_id": str(user_id)},
        {"$set": {"customer": customer}},
        upsert=True
    )
    return jsonify({"message": "Cập nhật thông tin khách hàng thành công"}), 200


# ========================
# Xóa 1 item theo _id
# ========================
@cart_bp.route("/<user_id>/remove", methods=["POST"])
def remove_item(user_id):
    data = request.json
    item_id = data.get("id")
    if not item_id:
        return jsonify({"error": "Thiếu id sản phẩm"}), 400

    result = db.carts.update_one(
        {"user_id": str(user_id)},
        {"$pull": {"items": {"_id": ObjectId(item_id)}}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"message": "Item removed"}), 200


# ========================
# Xóa toàn bộ giỏ
# ========================
@cart_bp.route("/<user_id>/clear", methods=["POST"])
def clear_cart(user_id):
    db.carts.update_one(
        {"user_id": str(user_id)},
        {"$set": {"items": [], "customer": {}}},
        upsert=True
    )
    return jsonify({"message": "Cart cleared"}), 200
