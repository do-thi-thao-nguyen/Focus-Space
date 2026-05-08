from flask import Blueprint, request, jsonify
from bson import ObjectId
from config.config import db
from datetime import datetime

booking_bp = Blueprint("booking", __name__)

# Lấy toàn bộ booking
@booking_bp.route("/", methods=["GET"])
def get_all():
    bookings = list(db.booking.find())
    for b in bookings:
        b["_id"] = str(b["_id"])
    return jsonify(bookings)

# Thêm booking
@booking_bp.route("/", methods=["POST"])
def add_booking():
    data = request.json
    if not data:
        return jsonify({"error": "Thiếu dữ liệu"}), 400

    # Nếu là venue mà chưa có name thì lấy từ DB venues
    if data.get("type") == "venue":
        if not data.get("name") and data.get("itemId"):
            venue = db.venues.find_one({"_id": ObjectId(data["itemId"])})
            if venue:
                data["name"] = venue["name"]

    # Nếu là device mà chưa có name thì lấy từ DB devices
    if data.get("type") == "device":
        if not data.get("name") and data.get("itemId"):
            device = db.devices.find_one({"_id": ObjectId(data["itemId"])})
            if device:
                data["name"] = device["name"]

    db.booking.insert_one(data)
    return jsonify({"message": "Đã thêm vào booking!"})

# Xóa booking theo id
@booking_bp.route("/<id>", methods=["DELETE"])
def delete_booking(id):
    db.booking.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Đã xóa thành công!"})

@booking_bp.route("/clear", methods=["DELETE"])
def clear_booking():
    try:
        db.booking.delete_many({})
        return jsonify({"message": "Cart cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@booking_bp.route("/checkout", methods=["POST"])
def checkout_booking():
    data = request.json
    customer = {
        "name": data.get("name"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "address": data.get("address"),
        "note": data.get("note")
    }

    bookings = list(db.booking.find({}))  # lấy toàn bộ giỏ hàng
    if not bookings:
        return jsonify({"error": "Giỏ hàng trống"}), 400

    # ✅ Kiểm tra venue có bị block chưa
    for item in bookings:
        if item.get("type") == "venue" and item.get("itemId"):
            try:
                venue = db.venues.find_one({"_id": ObjectId(item["itemId"])})
                if venue and venue.get("booked") is True:
                    return jsonify({"error": "Venue đã có người đặt trước, vui lòng chọn ngày khác"}), 400
            except Exception:
                return jsonify({"error": "ID venue không hợp lệ"}), 400

    total = sum(item.get("price", 0) for item in bookings)

    transaction = {
        "customer": customer,
        "items": bookings,
        "total": total,
        "createdAt": datetime.now()
    }

    result = db.transactions_venue.insert_one(transaction)
    db.booking.delete_many({})  # clear giỏ hàng

    return jsonify({
        "message": "Checkout thành công",
        "transactionId": str(result.inserted_id)
    }), 201

@booking_bp.route("/transactions_venue/<id>", methods=["GET"])
def get_transaction_venue(id):
    try:
        from bson import ObjectId
        trans = db.transactions_venue.find_one({"_id": ObjectId(id)})
        if not trans:
            return jsonify({"error": "Không tìm thấy hóa đơn"}), 404

        trans["_id"] = str(trans["_id"])
        return jsonify(trans)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@booking_bp.route("/transactions_venue/block/<id>", methods=["POST"])
def block_transaction_venue(id):
    try:
        trans = db.transactions_venue.find_one({"_id": ObjectId(id)})
        if not trans:
            return jsonify({"error": "Không tìm thấy hóa đơn"}), 404

        # Duyệt qua items để block
        for item in trans.get("items", []):
            try:
                oid = ObjectId(item["itemId"])
            except:
                continue  # skip item không hợp lệ

            if item.get("type") == "venue":
                db.venues.update_one({"_id": oid}, {"$set": {"booked": True}})
            elif item.get("type") == "device":
                db.devices.update_one({"_id": oid}, {"$set": {"booked": True}})

        # Mark transaction đã block
        db.transactions_venue.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"blocked": True}}
        )

        return jsonify({"message": "Block venue/device thành công!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
