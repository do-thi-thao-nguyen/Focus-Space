from flask import Blueprint, jsonify, request
from models.venue_model import VenueModel

venues_bp = Blueprint("venue", __name__, url_prefix="/venues")

# Lấy tất cả venues
@venues_bp.route("/", methods=["GET"])
def get_all_venues():
    return jsonify(VenueModel.get_all())

# Lấy chi tiết 1 venue
@venues_bp.route("/<venue_id>", methods=["GET"])
def get_venue(venue_id):
    venue = VenueModel.get_by_id(venue_id)
    if not venue:
        return jsonify({"error": "Venue không tồn tại"}), 404
    return jsonify(venue)

# Thêm venue
@venues_bp.route("/", methods=["POST"])
def create_venue():
    data = request.json
    venue_id = VenueModel.create(data)
    return jsonify({"message": "Venue created", "id": venue_id}), 201

# Cập nhật venue
@venues_bp.route("/<venue_id>", methods=["PUT"])
def update_venue(venue_id):
    data = request.json
    result = VenueModel.update(venue_id, data)
    if result.modified_count == 0:
        return jsonify({"error": "Venue không tồn tại"}), 404
    return jsonify({"message": "Venue updated"})

# Xóa venue
@venues_bp.route("/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    result = VenueModel.delete(venue_id)
    if result.deleted_count == 0:
        return jsonify({"error": "Venue không tồn tại"}), 404
    return jsonify({"message": "Venue deleted"})
