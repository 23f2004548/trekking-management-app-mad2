from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from werkzeug.security import generate_password_hash
from role_required import role_required
from models.db_models import db, User, Trek, Booking
from . import user_bp


# ── 1. User Dashboard ─────────────────────────────────────────────────────────
@user_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("user")
def dashboard():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()

    total_bookings = len(user_bookings)
    confirmed_bookings = sum(1 for b in user_bookings if b.status in ["Booked", "Confirmed"])
    pending_bookings = sum(1 for b in user_bookings if b.status == "Pending")
    completed_bookings = sum(1 for b in user_bookings if b.status == "Completed")
    cancelled_bookings = sum(1 for b in user_bookings if b.status == "Cancelled")

    easy = 0
    moderate = 0
    hard = 0
    for b in user_bookings:
        if b.trek and b.trek.difficulty:
            diff = b.trek.difficulty.strip().lower()
            if diff == "easy":
                easy += 1
            elif diff == "moderate":
                moderate += 1
            elif diff == "hard":
                hard += 1

    diff_labels = ["Easy", "Moderate", "Hard"]
    diff_counts = [easy, moderate, hard]

    recent_bookings = [b.to_dict() for b in user_bookings[:5]]

    return jsonify({
        "stats": {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "diff_labels": diff_labels,
            "diff_counts": diff_counts
        },
        "recent_bookings": recent_bookings,
        "user_name": current_user.name
    }), 200


# ── 2. Browse Treks ───────────────────────────────────────────────────────────
@user_bp.route("/treks", methods=["GET"])
@jwt_required()
@role_required("user")
def browse_treks():
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    difficulty = request.args.get("difficulty", "all").strip().lower()

    query = Trek.query.filter(Trek.status == "Open")

    if search:
        query = query.filter(Trek.name.ilike(f"%{search}%"))
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if difficulty and difficulty != "all":
        query = query.filter(Trek.difficulty.ilike(f"%{difficulty}%"))

    treks = query.order_by(Trek.start_date.asc()).all()

    # Get set of trek IDs currently booked by this user to indicate booking state
    active_booked_trek_ids = [
        b.trek_id for b in Booking.query.filter_by(user_id=current_user.id)
        .filter(Booking.status.in_(["Booked", "Confirmed", "Pending"])).all()
    ]

    trek_list = []
    for t in treks:
        d = t.to_dict()
        d["is_booked_by_user"] = t.id in active_booked_trek_ids
        trek_list.append(d)

    return jsonify({"treks": trek_list}), 200


# ── 3. Book Trek ──────────────────────────────────────────────────────────────
@user_bp.route("/book/<int:trek_id>", methods=["POST"])
@jwt_required()
@role_required("user")
def book_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status != "Open":
        return jsonify({"message": f"Trek is currently '{trek.status}' and not open for bookings"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available for this trek"}), 400

    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek_id).first()

    if existing_booking:
        if existing_booking.status in ["Booked", "Confirmed", "Pending"]:
            return jsonify({"message": "You have already booked this trek"}), 409
        elif existing_booking.status == "Cancelled":
            # Re-activate booking
            existing_booking.status = "Booked"
            trek.available_slots -= 1
            db.session.commit()
            return jsonify({
                "message": "Booking re-submitted successfully!",
                "booking": existing_booking.to_dict()
            }), 200

    # Create new booking
    booking = Booking(user_id=current_user.id, trek_id=trek.id, status="Booked")
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "message": "Trek booked successfully!",
        "booking": booking.to_dict()
    }), 201


# ── 4. My Bookings ────────────────────────────────────────────────────────────
@user_bp.route("/bookings", methods=["GET"])
@jwt_required()
@role_required("user")
def get_user_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return jsonify({"bookings": [b.to_dict() for b in bookings]}), 200


# ── 5. Cancel Booking ─────────────────────────────────────────────────────────
@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
@role_required("user")
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Booking not found"}), 404

    if booking.user_id != current_user.id:
        return jsonify({"message": "You are not authorized to cancel this booking"}), 403

    if booking.status == "Cancelled":
        return jsonify({"message": "Booking is already cancelled"}), 400

    if booking.status == "Completed":
        return jsonify({"message": "Completed treks cannot be cancelled"}), 400

    booking.status = "Cancelled"
    if booking.trek:
        booking.trek.available_slots += 1

    db.session.commit()
    return jsonify({
        "message": "Booking cancelled successfully",
        "booking": booking.to_dict()
    }), 200


# ── 6. Trekking History ───────────────────────────────────────────────────────
@user_bp.route("/history", methods=["GET"])
@jwt_required()
@role_required("user")
def history():
    # Filter completed bookings or bookings where trek is completed
    bookings = (
        Booking.query.join(Trek)
        .filter(
            Booking.user_id == current_user.id,
            (Booking.status == "Completed") | (Trek.status == "Completed")
        )
        .order_by(Booking.booking_date.desc())
        .all()
    )
    return jsonify({"history": [b.to_dict() for b in bookings]}), 200


# ── 7. Profile Management ─────────────────────────────────────────────────────
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@role_required("user")
def get_profile():
    return jsonify({
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.strftime("%Y-%m-%d %H:%M") if current_user.created_at else None
        }
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
@role_required("user")
def update_profile():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not email:
        return jsonify({"message": "Name and email are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        return jsonify({"message": "Email is already taken by another account"}), 400

    current_user.name = name
    current_user.email = email
    if password:
        if len(password) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        current_user.password = generate_password_hash(password)

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        }
    }), 200
