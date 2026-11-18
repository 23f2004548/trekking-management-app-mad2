from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from models.models import db, Treks, Staff, Bookings
from cache import cache

staff_bp = Blueprint("staff_bp", __name__, url_prefix="/staff")

# ── Staff Required Decorator ──────────────────────────────────────────────────
def staff_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        if not current_user or current_user.role != "staff":
            return jsonify({"message": "Forbidden: Staff access required"}), 403
        return f(*args, **kwargs)
    return decorated


def get_current_staff():
    """Helper to retrieve authenticated staff profile."""
    if not current_user:
        return None
    return Staff.query.filter_by(user_id=current_user.id).first()


# ── 1. Staff Dashboard ────────────────────────────────────────────────────────
@staff_bp.route("/dashboard", methods=["GET"])
@staff_required
@cache.cached(timeout=60)
def dashboard():
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if staff_member.status.lower() == "blacklisted":
        return jsonify({"message": "Your staff account has been blacklisted"}), 403

    if staff_member.status.lower() != "approved":
        return jsonify({"message": "Your staff account is pending admin approval"}), 403

    my_treks = Treks.query.filter_by(staff_id=staff_member.id).all()
    assigned_count = len(my_treks)
    upcoming_count = sum(1 for t in my_treks if t.status.lower() == "upcoming")

    trek_summaries = []
    total_participants = 0
    for t in my_treks:
        active_bookings = Bookings.query.filter_by(trek_id=t.id).filter(Bookings.status.ilike("confirmed")).count()
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
        "open_treks": upcoming_count,
        "total_participants": total_participants,
        "treks": trek_summaries
    }), 200


# ── 2. Assigned Treks ─────────────────────────────────────────────────────────
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
        d["registered_trekkers"] = Bookings.query.filter_by(trek_id=t.id).filter(Bookings.status.ilike("confirmed")).count()
        result.append(d)
    return jsonify(result), 200


# ── 3. Edit Trek ──────────────────────────────────────────────────────────────
@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
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
        st = data["status"].strip().lower()
        if st in ["upcoming", "ongoing", "completed"]:
            trek.status = st

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Trek updated successfully",
        "trek": trek.to_dict()
    }), 200


# ── 4. Participants ───────────────────────────────────────────────────────────
@staff_bp.route("/participants", methods=["GET"])
@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@staff_required
def participants(trek_id=None):
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if trek_id is not None:
        trek = Treks.query.get_or_404(trek_id)
        if trek.staff_id != staff_member.id:
            return jsonify({"message": "Forbidden: You are not assigned to this trek"}), 403
        bookings = Bookings.query.filter_by(trek_id=trek.id).order_by(Bookings.booking_date.asc()).all()
        part_list = [{
            "booking_id": b.id,
            "user_name": b.user.name if b.user else "N/A",
            "user_email": b.user.email if b.user else "N/A",
            "booking_date": b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "N/A",
            "status": b.status
        } for b in bookings]
        return jsonify({"trek": trek.to_dict(), "participants": part_list}), 200

    my_treks = Treks.query.filter_by(staff_id=staff_member.id).order_by(Treks.start_date.asc()).all()
    results = []
    for t in my_treks:
        bookings = Bookings.query.filter_by(trek_id=t.id).order_by(Bookings.booking_date.asc()).all()
        part_list = [{
            "booking_id": b.id,
            "user_name": b.user.name if b.user else "N/A",
            "user_email": b.user.email if b.user else "N/A",
            "booking_date": b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "N/A",
            "status": b.status
        } for b in bookings]
        results.append({
            "trek_id": t.id,
            "trek_name": t.name,
            "participants": part_list
        })
    return jsonify(results), 200


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
    new_status = data.get("status", "").strip().lower()

    if new_status not in ["pending", "confirmed", "cancelled"]:
        return jsonify({"message": "Invalid status. Must be pending, confirmed, or cancelled"}), 400

    if new_status == "cancelled" and booking.status.lower() != "cancelled":
        trek.available_slots += 1
    elif booking.status.lower() == "cancelled" and new_status in ["confirmed", "pending"]:
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
@staff_bp.route("/profile", methods=["GET", "PUT"])
@staff_required
def profile():
    staff_member = get_current_staff()
    if not staff_member:
        return jsonify({"message": "Staff profile not found"}), 404

    if request.method == "PUT":
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
