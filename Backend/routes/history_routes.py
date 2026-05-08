from flask import Blueprint, request, jsonify
from models.transactions_venue_model import TransactionsVenueModel

history_bp = Blueprint("history", __name__)

@history_bp.route("/history", methods=["GET"])
def get_history():
    try:
        date = request.args.get("date")
        session = request.args.get("session")
        data = TransactionsVenueModel.get_simple_history(date, session)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
