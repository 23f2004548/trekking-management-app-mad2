from flask import Blueprint, jsonify
from models.models import Treks, Bookings

main = Blueprint("main", __name__)
main_bp = main

@main.route("/", methods=["GET"])
def landing_page():
    return jsonify({
        "message": "Welcome to Trekking Management Application V2 API",
        "status": "Online",
        "open_treks": Treks.query.filter_by(status="Open").count()
    }), 200

__all__ = ["main", "main_bp", "landing_page"]
