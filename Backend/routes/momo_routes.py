from flask import Blueprint, request, jsonify
import requests, hmac, hashlib, time
from config.config import MOMO_PARTNER_CODE, MOMO_ACCESS_KEY, MOMO_SECRET_KEY, db

momo_bp = Blueprint("momo", __name__)

# ========================
# API tạo payment link
# ========================
@momo_bp.route("/create_payment", methods=["POST"])
def create_payment():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Thiếu dữ liệu"}), 400

        amount = str(data.get("amount", 0))
        order_id = data.get("orderId", f"order_{int(time.time())}")
        order_info = data.get("orderInfo", "Thanh toán MoMo")
        user_id = str(data.get("extraData", ""))  # ✅ nhận user_id từ frontend

        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"

        redirect_url = "http://localhost:5500/transactions.html"
        ipn_url = "http://localhost:5000/momo/ipn"

        raw_signature = (
            f"accessKey={MOMO_ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData={user_id}"
            f"&ipnUrl={ipn_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={MOMO_PARTNER_CODE}"
            f"&redirectUrl={redirect_url}"
            f"&requestId={order_id}"
            f"&requestType=captureWallet"
        )

        signature = hmac.new(
            MOMO_SECRET_KEY.encode("utf-8"),
            raw_signature.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        payload = {
            "partnerCode": MOMO_PARTNER_CODE,
            "accessKey": MOMO_ACCESS_KEY,
            "requestId": order_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": redirect_url,
            "ipnUrl": ipn_url,
            "extraData": user_id,
            "requestType": "payWithATM",   # ✅ đổi từ captureWallet sang payWithATM
            "signature": signature
        }


        res = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"})
        result = res.json()

        if res.status_code != 200 or "payUrl" not in result:
            return jsonify({"error": "MoMo API error", "detail": result}), 400

        return jsonify({"payUrl": result["payUrl"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================
# API IPN callback từ MoMo
# ========================
from flask import Blueprint, request, jsonify
import requests, hmac, hashlib, time
from config.config import MOMO_PARTNER_CODE, MOMO_ACCESS_KEY, MOMO_SECRET_KEY, db

momo_bp = Blueprint("momo", __name__)

# ========================
# API tạo payment link
# ========================
@momo_bp.route("/create_payment", methods=["POST"])
def create_payment():
    try:
        data = request.json or {}
        amount = str(data.get("amount", 0))
        order_id = data.get("orderId", f"order_{int(time.time())}")
        order_info = data.get("orderInfo", "Thanh toán MoMo")
        user_id = str(data.get("extraData", ""))  # ✅ user_id để lưu kèm

        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"

        redirect_url = "http://localhost:5500/transactions.html"
        ipn_url = "http://localhost:5000/momo/ipn"

        # ✅ Tính chữ ký theo payWithATM
        raw_signature = (
            f"accessKey={MOMO_ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData={user_id}"
            f"&ipnUrl={ipn_url}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&partnerCode={MOMO_PARTNER_CODE}"
            f"&redirectUrl={redirect_url}"
            f"&requestId={order_id}"
            f"&requestType=payWithATM"
        )

        signature = hmac.new(
            MOMO_SECRET_KEY.encode("utf-8"),
            raw_signature.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        payload = {
            "partnerCode": MOMO_PARTNER_CODE,
            "accessKey": MOMO_ACCESS_KEY,
            "requestId": order_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": redirect_url,
            "ipnUrl": ipn_url,
            "extraData": user_id,
            "requestType": "payWithATM",   # ✅ ATM
            "signature": signature
        }

        res = requests.post(endpoint, json=payload, headers={"Content-Type": "application/json"})
        result = res.json()

        if res.status_code != 200 or "payUrl" not in result:
            return jsonify({"error": "MoMo API error", "detail": result}), 400

        return jsonify({"payUrl": result["payUrl"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ========================
# API IPN callback từ MoMo
# ========================
@momo_bp.route("/ipn", methods=["POST"])
def momo_ipn():
    try:
        data = request.json or {}

        # Lấy các field từ MoMo callback
        amount = str(data.get("amount", "0"))
        order_id = data.get("orderId", "")
        order_info = data.get("orderInfo", "")
        user_id = data.get("extraData", "")
        request_id = data.get("requestId", "")

        # ✅ Tính lại signature để verify
        raw_signature = (
            f"accessKey={MOMO_ACCESS_KEY}"
            f"&amount={amount}"
            f"&extraData={user_id}"
            f"&orderId={order_id}"
            f"&orderInfo={order_info}"
            f"&orderType=momo_wallet"
            f"&partnerCode={MOMO_PARTNER_CODE}"
            f"&payType={data.get('payType','')}"
            f"&requestId={request_id}"
            f"&responseTime={data.get('responseTime','')}"
            f"&resultCode={data.get('resultCode','')}"
            f"&transId={data.get('transId','')}"
        )

        signature = hmac.new(
            MOMO_SECRET_KEY.encode("utf-8"),
            raw_signature.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if signature != data.get("signature"):
            return jsonify({"error": "Invalid signature"}), 400

        # ========================
        # Thanh toán thành công
        # ========================
        if str(data.get("resultCode")) == "0":
            transaction = {
                "user_id": user_id,
                "amount": amount,
                "status": "success",
                "method": "MoMo-ATM",
                "time": int(time.time()),
                "raw": data
            }
            db.transactions.insert_one(transaction)

            # Clear cart
            db.carts.update_one({"user_id": str(user_id)}, {"$set": {"items": []}})
            print("✅ Thanh toán thành công cho user:", user_id)
            return jsonify({"message": "success"}), 200

        # ========================
        # Thanh toán thất bại
        # ========================
        else:
            db.transactions.insert_one({
                "user_id": user_id,
                "amount": amount,
                "status": "fail",
                "method": "MoMo-ATM",
                "time": int(time.time()),
                "raw": data
            })
            print("❌ Thanh toán thất bại:", order_id)
            return jsonify({"message": "failed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
