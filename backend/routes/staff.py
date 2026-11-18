from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from models.models import db, Users, Treks, Staff, Bookings, User, Trek, StaffProfile, Booking
from cache import cache

staff_bp = Blueprint("staff_bp", __name__, url_prefix="/staff")

# ── Staff Required Decorator (MAD 1: staff_required) ──────────────────────────
def staff_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        if not current_user or current_user.role != "staff":
            return jsonify({"message": "Forbidden: Staff access required"}), 403
        return f(*args, **kwargs)
    return decorated


def get_current_staff():
    """Helper to retrieve the authenticated staff profile."""
    if not current_user:
        return None
    return Staff.query.filter_by(user_id=current_user.id).first()


# ── 1. Staff Dashboard (MAD 1: dashboard) ──────────────────────────────────────
@staff_bp.route("/dashboard", methods=["GET"])
@staff_required
@cache.cached(timeout=60)
def dashboard():
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if staff_member.status == "blacklisted":
        return jsonify({"message": "Your staff account has been blacklisted"}), 403

    my_treks = Treks.query.filter_by(staff_id=staff_member.id).all()
    assigned_count = len(my_treks)
    open_count = sum(1 for t in my_treks if t.status == "Open")

    trek_summaries = []
    total_participants = 0
    for t in my_treks:
        active_bookings = Bookings.query.filter_by(trek_id=t.id, status="Booked").count()
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
        "staff": staff_member.to_dict(),
        "assigned_treks": assigned_count,
        "open_treks": open_count,
        "total_participants": total_participants,
        "treks": trek_summaries
    }), 200


# ── 2. Assigned Treks (MAD 1: treks) ──────────────────────────────────────────
@staff_bp.route("/treks", methods=["GET"])
@staff_required
def treks():
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    my_treks = Treks.query.filter_by(staff_id=staff_member.id).order_by(Treks.start_date.asc()).all()
    result = []
    for t in my_treks:
        d = t.to_dict()
        d["registered_trekkers"] = Bookings.query.filter_by(trek_id=t.id, status="Booked").count()
        result.append(d)
    return jsonify(result), 200

# Alias for backwards compatibility
get_my_treks = treks


# ── 3. Edit Trek (MAD 1: edit_trek) ───────────────────────────────────────────
@staff_bp.route("/treks/<int:trek_id>", methods=["PUT", "POST"])
@staff_bp.route("/treks/edit/<int:trek_id>", methods=["PUT", "POST"])
@staff_required
def edit_trek(trek_id):
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Treks.query.get_or_404(trek_id)

    if trek.staff_id != staff_member.id:
        return jsonify({"message": "Forbidden: You are only authorized to manage your assigned treks"}), 403

    data = request.get_json() or {}

    if "available_slots" in data:
        new_slots = int(data["available_slots"])
        if new_slots < 0:
            return jsonify({"message": "Available slots cannot be negative"}), 400
        if new_slots > trek.total_slots:
            return jsonify({"message": f"Available slots cannot exceed total slots ({trek.total_slots})"}), 400
        trek.available_slots = new_slots

    if "status" in data:
        valid_statuses = ["Open", "Closed", "Started", "Ongoing", "Completed", "Pending", "Approved"]
        new_status = data["status"]
        if new_status not in valid_statuses:
            return jsonify({"message": f"Invalid status. Allowed: {valid_statuses}"}), 400
        trek.status = new_status
        if new_status == "Completed":
            active_bookings = Bookings.query.filter_by(trek_id=trek.id).filter(Bookings.status.in_(["Booked", "Confirmed"])).all()
            for b in active_bookings:
                b.status = "Completed"

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Trek updated successfully",
        "trek": trek.to_dict()
    }), 200

# Alias for backwards compatibility
update_my_trek = edit_trek


# ── 4. Participants (MAD 1: participants) ──────────────────────────────────────
@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@staff_bp.route("/participants", methods=["GET"])
@staff_required
def participants(trek_id=None):
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if trek_id is None:
        t_id = request.args.get("trek_id")
        if t_id:
            trek_id = int(t_id)

    if trek_id:
        trek = Treks.query.get_or_404(trek_id)
        if trek.staff_id != staff_member.id:
            return jsonify({"message": "Forbidden: You are not assigned to this trek"}), 403

        trek_bookings = Bookings.query.filter_by(trek_id=trek.id).order_by(Bookings.booking_date.asc()).all()
        part_list = []
        for b in trek_bookings:
            part_list.append({
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
            "participants": part_list
        }), 200
    else:
        # Return all assigned treks with their participant lists
        my_treks = Treks.query.filter_by(staff_id=staff_member.id).all()
        return jsonify({"treks": [t.to_dict() for t in my_treks]}), 200

# Alias for backwards compatibility
get_trek_participants = participants


# ── 5. Manage Participant Status ──────────────────────────────────────────────
@staff_bp.route("/treks/<int:trek_id>/participants/<int:booking_id>/status", methods=["POST"])
@staff_required
def update_participant_status(trek_id, booking_id):
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Treks.query.get_or_404(trek_id)
    if trek.staff_id != staff_member.id:
        return jsonify({"message": "Forbidden: You are not assigned to manage this trek"}), 403

    booking = Bookings.query.filter_by(id=booking_id, trek_id=trek.id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["Booked", "Completed", "Cancelled", "Pending"]:
        return jsonify({"message": "Invalid status"}), 400

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


# ── 6. Staff Profile (MAD 1: profile) ──────────────────────────────────────────
@staff_bp.route("/profile", methods=["GET", "POST", "PUT"])
@staff_required
def profile():
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if request.method in ["POST", "PUT"]:
        data = request.get_json() or {}
        if "name" in data:
            staff_member.name = data["name"].strip()
            if staff_member.user:
                staff_member.user.name = data["name"].strip()
        if "phone_number" in data:
            staff_member.phone_number = data["phone_number"].strip()
        if "specialization" in data:
            staff_member.specialization = data["specialization"].strip()

        db.session.commit()
        return jsonify({"message": "Profile updated successfully", "staff": staff_member.to_dict()}), 200

    return jsonify(staff_member.to_dict()), 200

# Aliases for backwards compatibility
get_profile = profile
update_profile = profile
