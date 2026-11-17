from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from role_required import role_required
from models.db_models import db, User, StaffProfile, Trek, Booking
from cache import cache
from . import staff_bp


def get_current_staff():
    """Helper to retrieve the authenticated staff profile."""
    if not current_user:
        return None
    return StaffProfile.query.filter_by(user_id=current_user.id).first()


# ── 1. Staff Dashboard ────────────────────────────────────────────────────────
@staff_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("staff")
@cache.cached(timeout=60)
def dashboard():
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    if staff.status == "blacklisted":
        return jsonify({"message": "Your staff account has been blacklisted"}), 403

    my_treks = Trek.query.filter_by(staff_id=staff.id).all()
    assigned_count = len(my_treks)
    open_count = sum(1 for t in my_treks if t.status == "Open")

    trek_summaries = []
    total_participants = 0
    for t in my_treks:
        active_bookings = Booking.query.filter_by(trek_id=t.id, status="Booked").count()
        total_participants += active_bookings
        trek_summaries.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "difficulty": t.difficulty,
            "duration": t.duration,
            "available_slots": t.available_slots,
            "total_slots": t.total_slots,
            "status": t.status,
            "start_date": t.start_date.strftime("%Y-%m-%d") if t.start_date else None,
            "end_date": t.end_date.strftime("%Y-%m-%d") if t.end_date else None,
            "registered_trekkers": active_bookings,
            "total_bookings": len(t.bookings)
        })

    return jsonify({
        "staff": staff.to_dict(),
        "assigned_treks": assigned_count,
        "open_treks": open_count,
        "total_participants": total_participants,
        "treks": trek_summaries
    }), 200


# ── 2. View Only Assigned Treks ───────────────────────────────────────────────
@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
@role_required("staff")
def get_my_treks():
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    treks = Trek.query.filter_by(staff_id=staff.id).order_by(Trek.start_date.asc()).all()
    result = []
    for t in treks:
        d = t.to_dict()
        d["registered_trekkers"] = Booking.query.filter_by(trek_id=t.id, status="Booked").count()
        result.append(d)
    return jsonify(result), 200


# ── 3. Update Available Slots and Trek Status ─────────────────────────────────
@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
@role_required("staff")
def update_my_trek(trek_id):
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)

    # Strictly ensure only assigned staff can manage their trek
    if trek.staff_id != staff.id:
        return jsonify({"message": "Forbidden: You are only authorized to manage your assigned treks"}), 403

    data = request.get_json() or {}

    # Update available slots
    if "available_slots" in data:
        new_slots = int(data["available_slots"])
        if new_slots < 0:
            return jsonify({"message": "Available slots cannot be negative"}), 400
        if new_slots > trek.total_slots:
            return jsonify({"message": f"Available slots cannot exceed total slots ({trek.total_slots})"}), 400
        trek.available_slots = new_slots

    # Update trek status: Open / Closed / Started / Ongoing / Completed
    if "status" in data:
        valid_statuses = ["Open", "Closed", "Started", "Ongoing", "Completed", "Pending", "Approved"]
        new_status = data["status"]
        if new_status not in valid_statuses:
            return jsonify({"message": f"Invalid status. Allowed: {valid_statuses}"}), 400
        trek.status = new_status
        if new_status == "Completed":
            # Auto-complete active participants on trek completion
            active_bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status.in_(["Booked", "Confirmed"])).all()
            for b in active_bookings:
                b.status = "Completed"

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Trek updated successfully",
        "trek": trek.to_dict()
    }), 200


# ── 4. View Registered Users / Participants for Assigned Trek ─────────────────
@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
@role_required("staff")
def get_trek_participants(trek_id):
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)

    # Ownership check: Ensure only assigned staff can view participants
    if trek.staff_id != staff.id:
        return jsonify({"message": "Forbidden: You are not assigned to this trek"}), 403

    bookings = Booking.query.filter_by(trek_id=trek.id).order_by(Booking.booking_date.asc()).all()
    participants = []
    for b in bookings:
        participants.append({
            "booking_id": b.id,
            "user_id": b.user_id,
            "user_name": b.user.name if b.user else "N/A",
            "user_email": b.user.email if b.user else "N/A",
            "user_username": b.user.username if b.user else "N/A",
            "booking_date": b.booking_date.strftime("%Y-%m-%d %H:%M") if b.booking_date else None,
            "status": b.status,
            "payment_status": b.payment_status
        })

    return jsonify({
        "trek": trek.to_dict(),
        "participants": participants
    }), 200


# ── 5. Manage Participant Status (Booked / Completed / Cancelled) ─────────────
@staff_bp.route("/treks/<int:trek_id>/participants/<int:booking_id>/status", methods=["POST"])
@jwt_required()
@role_required("staff")
def update_participant_status(trek_id, booking_id):
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)
    if trek.staff_id != staff.id:
        return jsonify({"message": "Forbidden: You are not assigned to manage this trek"}), 403

    booking = Booking.query.filter_by(id=booking_id, trek_id=trek.id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["Booked", "Completed", "Cancelled", "Pending"]:
        return jsonify({"message": "Invalid status"}), 400

    # Adjust available slots if booking is cancelled
    if new_status == "Cancelled" and booking.status != "Cancelled":
        trek.available_slots += 1
    elif booking.status == "Cancelled" and new_status in ["Booked", "Pending"]:
        if trek.available_slots > 0:
            trek.available_slots -= 1
        else:
            return jsonify({"message": "Cannot reactivate: Trek slots are full"}), 400

    booking.status = new_status
    db.session.commit()
    cache.clear()
    return jsonify({
        "message": f"Participant status updated to {new_status}",
        "booking": booking.to_dict()
    }), 200


# ── 6. Staff Profile ──────────────────────────────────────────────────────────
@staff_bp.route("/profile", methods=["GET"])
@jwt_required()
@role_required("staff")
def get_profile():
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404
    return jsonify(staff.to_dict()), 200


@staff_bp.route("/profile", methods=["PUT"])
@jwt_required()
@role_required("staff")
def update_profile():
    staff = get_current_staff()
    if not staff:
        return jsonify({"message": "Staff profile not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        staff.name = data["name"].strip()
        if staff.user:
            staff.user.name = data["name"].strip()
    if "phone_number" in data:
        staff.phone_number = data["phone_number"].strip()
    if "specialization" in data:
        staff.specialization = data["specialization"].strip()

    db.session.commit()
    return jsonify({"message": "Profile updated successfully", "staff": staff.to_dict()}), 200
