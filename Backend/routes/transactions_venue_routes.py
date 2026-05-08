from flask import Blueprint, request, jsonify
from bson import ObjectId
from config.config import db
from models.transactions_venue_model import TransactionsVenueModel
from bson.json_util import dumps
from bson import json_util
transactions_venue_bp = Blueprint("transactions_venue", __name__)

# ===============================
# Checkout -> tạo transaction mới
# ===============================
@transactions_venue_bp.route("/booking/checkout", methods=["POST"])
def checkout_booking():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Thiếu thông tin khách hàng"}), 400

        customer = {
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "note": data.get("note", "")
        }

        # Lấy toàn bộ giỏ hàng booking
        items = list(db.booking.find({}))
        if not items:
            return jsonify({"error": "Giỏ hàng trống"}), 400

        # Convert ObjectId thành string
        for i in items:
            i["_id"] = str(i["_id"])

        # Tính tổng tiền
        total = sum(i.get("price", 0) for i in items)

        # Tạo transaction mới trong collection transactions_venue
        transaction_id = TransactionsVenueModel.create_transaction(
            customer=customer,
            items=items,
            total=total
        )

        # Xoá giỏ hàng sau khi checkout
        db.booking.delete_many({})

        return jsonify({
            "message": "Checkout thành công",
            "transactionId": transaction_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ===============================
# Xoá 1 transaction
# ===============================
@transactions_venue_bp.route("/transactions_venue/<id>", methods=["DELETE"])
def delete_transaction(id):
    try:
        result = db.transactions_venue.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Không tìm thấy hóa đơn để xoá"}), 404
        return jsonify({"message": "Xoá hóa đơn thành công"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def session_to_time_range(session):
    if session == "morning":
        return ("08:00", "12:00")
    elif session == "afternoon":
        return ("13:00", "17:00")
    elif session == "full":
        return ("08:00", "17:00")
    return None

# ===============================
# Block ghế sau khi thanh toán venue
# ===============================
@transactions_venue_bp.route("/transactions_venue/block/<id>", methods=["POST"])
def block_transaction(id):
    try:
        transaction = db.transactions_venue.find_one({"_id": ObjectId(id)})
        if not transaction:
            return jsonify({"error": "Không tìm thấy giao dịch"}), 404

        items = transaction.get("items", [])
        for item in items:
            if item.get("type") == "venue":
                venue_name = item.get("name")
                date = item.get("date")
                session = item.get("session")  # morning | afternoon | full

                # Mapping giờ theo buổi
                if session == "morning":
                    start, end = "08:00", "12:00"
                elif session == "afternoon":
                    start, end = "13:00", "17:00"
                else:
                    start, end = "08:00", "17:00"

                # 1. Block chính venue
                db.venues.update_one(
                    {"name": venue_name},
                    {
                        "$set": {
                            "status": "booked",
                            "date": date,
                            "start": start,
                            "end": end
                        }
                    }
                )

                # 2. Block toàn bộ vé ghế trong venue đó ngày đó
                db.venue_tickets.update_many(
                    {"venue": venue_name},
                    {
                        "$set": {
                            "status": "booked",
                            "date": date,
                            "start": start,
                            "end": end
                        }
                    }
                )

        return jsonify({"message": "✅ Block venue + vé thành công!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@transactions_venue_bp.route("/transactions_venue", methods=["GET"])
def get_transactions_venue():
    try:
        date = request.args.get("date")
        query = {}
        if date:
            query["items.date"] = date  # lọc theo ngày thuê

        data = list(db.transactions_venue.find(query).sort("createdAt", -1))

        # Dùng json_util để convert ObjectId, datetime...
        return json_util.dumps(data), 200, {"Content-Type": "application/json"}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
