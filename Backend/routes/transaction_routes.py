# routes/transaction_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from bson import ObjectId
from config.config import db
from models.transaction_model import TransactionModel

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")

# =========================
# Tạo giao dịch (checkout)
# =========================
@transactions_bp.route("/", methods=["POST"])
def create_transaction():
    data = request.get_json(force=True, silent=True) or {}
    method = data.get("method")
    items = data.get("items", [])
    proof = data.get("proof")

    if not method or not items:
        return jsonify(error="Thiếu dữ liệu giao dịch"), 400

    # Tạo giao dịch trong DB
    tx = TransactionModel.create_transaction(method, items, proof)

    # ✅ Block ghế theo thời gian đã chọn
    for item in items:
        seat_id = item["seat"]
        date = item["date"]
        time = item["time"]
        ticket_type = item["ticket_type"]

        start = datetime.fromisoformat(f"{date}T{time}:00")

        if ticket_type == "1hour":
            duration = 1
        elif ticket_type == "4hour":
            duration = 4
        elif ticket_type == "student":
            duration = 4   # 👈 chỉnh student = 4h
        else:  # combo
            duration = 9   # 👈 combo = 9h

        end = start + timedelta(hours=duration)

        db.tickets.update_one(
            {"_id": seat_id},
            {"$push": {
                "bookings": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "tx_id": str(tx["_id"])
                }
            }}
        )

    return jsonify(tx), 201

# =========================
# Lấy danh sách giao dịch
# =========================
@transactions_bp.route("/", methods=["GET"])
def list_transactions():
    txs = list(db.transactions.find({}).sort("created_at", -1))
    for t in txs:
        t["_id"] = str(t["_id"])
    return jsonify(txs), 200

# =========================
# Lấy chi tiết giao dịch theo id
# =========================
@transactions_bp.route("/<tx_id>", methods=["GET"])
def get_transaction(tx_id):
    tx = db.transactions.find_one({"_id": ObjectId(tx_id)})
    if not tx:
        return jsonify(error="Không tìm thấy giao dịch"), 404

    tx["_id"] = str(tx["_id"])
    return jsonify(tx), 200
