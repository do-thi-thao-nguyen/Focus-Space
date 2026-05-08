# routes/promotion_routes.py
# =====================================================
# API Khuyến mãi (Promotion)
# - Tạo mã giảm:         POST /promotions/
#     body: { code, percent }  (percent: 0..100)
# - Tra cứu mã theo code: GET  /promotions/code?code=SALE10
# - Áp mã tạm tính tiền:  GET  /promotions/apply?code=SALE10&amount=300
# =====================================================

from flask import Blueprint, jsonify, request
from config.config import db

promotions_bp = Blueprint("promotions", __name__, url_prefix="/promotions")

def to_doc(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    return doc

@promotions_bp.route("", methods=["POST"], strict_slashes=False)
@promotions_bp.route("/", methods=["POST"], strict_slashes=False)
def create_promotion():
    data = request.get_json() or {}
    code = (data.get("code") or "").strip().upper()
    percent = data.get("percent")

    if not code or percent is None:
        return jsonify(error="Thiếu 'code' hoặc 'percent'"), 400

    try:
        percent = float(percent)
    except Exception:
        return jsonify(error="'percent' phải là số"), 400

    if percent < 0 or percent > 100:
        return jsonify(error="'percent' phải trong khoảng 0..100"), 400

    # Không trùng code
    old = db.promotions.find_one({"code": code})
    if old:
        return jsonify(error="Code đã tồn tại"), 409

    doc = {"code": code, "percent": percent, "desc": data.get("desc")}
    ins = db.promotions.insert_one(doc)
    saved = db.promotions.find_one({"_id": ins.inserted_id})
    return jsonify(to_doc(saved)), 201

@promotions_bp.route("/code", methods=["GET"], strict_slashes=False)
def get_promotion():
    code = (request.args.get("code") or "").strip().upper()
    if not code:
        return jsonify(error="Thiếu query 'code'"), 400

    doc = db.promotions.find_one({"code": code})
    if not doc:
        return jsonify(error="Không tìm thấy code"), 404

    return jsonify(to_doc(doc)), 200

@promotions_bp.route("/apply", methods=["GET"], strict_slashes=False)
def apply_promotion():
    code = (request.args.get("code") or "").strip().upper()
    amount = request.args.get("amount")
    if not code or amount is None:
        return jsonify(error="Thiếu 'code' hoặc 'amount'"), 400

    try:
        amount = float(amount)
    except Exception:
        return jsonify(error="'amount' phải là số"), 400

    promo = db.promotions.find_one({"code": code})
    if not promo:
        return jsonify(error="Không tìm thấy code"), 404

    percent = float(promo.get("percent", 0))
    discount = round(amount * percent / 100, 2)
    final_amount = max(0.0, round(amount - discount, 2))

    return jsonify({
        "code": code,
        "percent": percent,
        "amount": amount,
        "discount": discount,
        "final_amount": final_amount
    }), 200
