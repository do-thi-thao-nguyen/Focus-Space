from flask import Blueprint, request, jsonify
from bson import ObjectId
from config.config import db

devices_bp = Blueprint("devices", __name__)

# Lấy danh sách thiết bị
@devices_bp.route("/", methods=["GET"])
def get_devices():
    devices = list(db.devices.find())
    for d in devices:
        d["_id"] = str(d["_id"])
    return jsonify(devices)

# Lấy chi tiết thiết bị
@devices_bp.route("/<id>", methods=["GET"])
def get_device(id):
    d = db.devices.find_one({"_id": ObjectId(id)})
    if not d:
        return jsonify({"error": "Device not found"}), 404
    d["_id"] = str(d["_id"])
    return jsonify(d)

# Thêm thiết bị vào giỏ hàng
@devices_bp.route("/cart/add_device", methods=["POST"])
def add_device_cart():
    data = request.json
    device_id = data.get("device_id")
    cart_item = {"type": "device", "item_id": device_id}
    db.cart.insert_one(cart_item)
    return jsonify({"message": "Đã thêm thiết bị vào giỏ hàng"})
