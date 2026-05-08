from flask import Blueprint, request, jsonify
from datetime import datetime
from config.config import db

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")

# =========================
# API: Lấy trạng thái tất cả ghế
# =========================
@tickets_bp.route("/status_all", methods=["GET"])
def get_status_all():
    date = request.args.get("date")  # yyyy-mm-dd
    time = request.args.get("time")  # HH:MM (optional)

    if not date:
        return jsonify({"error": "Thiếu ngày (date)"}), 400

    if not time:
        time = "09:00"

    query_time = datetime.fromisoformat(f"{date}T{time}:00")

    results = []
    seats = list(db.tickets.find({}))
    for s in seats:
        status = "available"
        for b in s.get("bookings", []):
            try:
                start = datetime.fromisoformat(b["start"])
                end = datetime.fromisoformat(b["end"])
                if start <= query_time < end:
                    status = "sold"
                    break
            except Exception:
                continue
        results.append({
            "seat": s["_id"],
            "status": status
        })

    return jsonify(results), 200


# =========================
# API: Block ghế khi thanh toán
# =========================
@tickets_bp.route("/block", methods=["POST"])
def block_seat():
    data = request.get_json(force=True, silent=True) or {}

    seat_id = data.get("seat")
    date = data.get("date")
    start_str = data.get("start")   # ISO string
    end_str = data.get("end")       # ISO string
    ticket_type = data.get("ticket_type")

    if not seat_id or not date or not start_str or not end_str or not ticket_type:
        return jsonify({"error": "Thiếu dữ liệu đặt chỗ"}), 400

    try:
        start = datetime.fromisoformat(start_str)
        end = datetime.fromisoformat(end_str)
    except Exception:
        return jsonify({"error": "Sai định dạng ngày giờ"}), 400

    # Check overlap: tìm trong DB xem có booking nào cùng ghế
    seat_doc = db.tickets.find_one({"_id": seat_id})
    if not seat_doc:
        seat_doc = {"_id": seat_id, "bookings": []}

    for b in seat_doc.get("bookings", []):
        try:
            b_start = datetime.fromisoformat(b["start"])
            b_end = datetime.fromisoformat(b["end"])

            # Nếu vé lẻ -> chỉ check trong ngày đó
            if ticket_type != "combo":
                if not (end <= b_start or start >= b_end):
                    return jsonify({
                        "error": f"❌ Ghế {seat_id} đã có người đặt từ {b_start.strftime('%H:%M')} đến {b_end.strftime('%H:%M')}"
                    }), 400
            else:
                # Vé combo (nguyên ngày) -> block toàn bộ ngày
                if start.date() == b_start.date():
                    return jsonify({
                        "error": f"❌ Ghế {seat_id} đã có người đặt nguyên ngày {start.strftime('%d/%m/%Y')}"
                    }), 400
        except Exception:
            continue

    # Nếu ok -> thêm vào bookings
    db.tickets.update_one(
        {"_id": seat_id},
        {"$push": {
            "bookings": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "ticket_type": ticket_type
            }
        }},
        upsert=True
    )

    return jsonify({"message": f"✅ Đã block ghế {seat_id} từ {start.strftime('%H:%M')} đến {end.strftime('%H:%M')}"})