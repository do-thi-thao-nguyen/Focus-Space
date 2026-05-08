# models/device_model.py
from config.config import db
from bson import ObjectId

def device_serializer(device) -> dict:
    return {
        "_id": str(device["_id"]),
        "name": device["name"],
        "price": device["price"],
        "description": device["description"],
        "images": device.get("images", [])
    }

# Lấy tất cả thiết bị
def get_all_devices():
    devices = db.devices.find()
    return [device_serializer(d) for d in devices]

# Lấy 1 thiết bị theo id
def get_device_by_id(device_id: str):
    d = db.devices.find_one({"_id": ObjectId(device_id)})
    return device_serializer(d) if d else None

# Thêm thiết bị
def create_device(data: dict):
    result = db.devices.insert_one(data)
    return str(result.inserted_id)

# Xóa thiết bị
def delete_device(device_id: str):
    return db.devices.delete_one({"_id": ObjectId(device_id)}).deleted_count > 0
