from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from role_required import role_required
from models.models import db, Users, Treks, Staff, Bookings, User, Trek, StaffProfile, Booking
from cache import cache
from . import user_bp


# ── User Required Decorator (MAD 1: user_required) ────────────────────────────
def user_required(f):
    @wraps(f)
    @jwt_required()
    @role_required("user")
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated


# ── 1. User Dashboard (MAD 1: dashboard) ──────────────────────────────────────
@user_bp.route("/dashboard", methods=["GET"])
@user_required
def dashboard():
    total_bookings = Bookings.query.filter_by(user_id=current_user.id).count()
    confirmed_bookings = Bookings.query.filter_by(user_id=current_user.id).filter(
        Bookings.status.in_(["Booked", "Confirmed"])
    ).count()
    completed_bookings = Bookings.query.filter_by(user_id=current_user.id, status="Completed").count()
    cancelled_bookings = Bookings.query.filter_by(user_id=current_user.id, status="Cancelled").count()
    pending_bookings = Bookings.query.filter_by(user_id=current_user.id, status="Pending").count()

    all_user_bookings = Bookings.query.filter_by(user_id=current_user.id).all()
    easy, moderate, hard = 0, 0, 0
    for b in all_user_bookings:
        if b.trek and b.trek.difficulty:
            diff = b.trek.difficulty.lower()
            if diff == "easy":
                easy += 1
            elif diff == "moderate":
                moderate += 1
            elif diff == "hard":
                hard += 1

    recent = Bookings.query.filter_by(user_id=current_user.id).order_by(Bookings.booking_date.desc()).limit(5).all()
    recent_bookings = [b.to_dict() for b in recent]

    return jsonify({
        "stats": {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "pending_bookings": pending_bookings,
            "diff_labels": ["Easy", "Moderate", "Hard"],
            "diff_counts": [easy, moderate, hard]
        },
        "recent_bookings": recent_bookings,
        "user_name": current_user.name
    }), 200


# ── 2. Browse Treks (MAD 1: browse) ───────────────────────────────────────────
@user_bp.route("/browse", methods=["GET"])
@user_bp.route("/treks", methods=["GET"])
@user_required
def browse():
    search = (request.args.get("search") or request.args.get("search_word") or "").strip()
    location = request.args.get("location", "").strip()
    difficulty = request.args.get("difficulty", "all").strip().lower()

    query = Treks.query.filter(Treks.status == "Open")

    if search:
        query = query.filter(Treks.name.ilike(f"%{search}%"))
    if location:
        query = query.filter(Treks.location.ilike(f"%{location}%"))
    if difficulty and difficulty != "all":
        query = query.filter(Treks.difficulty.ilike(f"%{difficulty}%"))

    open_treks = query.order_by(Treks.start_date.asc()).all()

    active_booked_trek_ids = [
        b.trek_id for b in Bookings.query.filter_by(user_id=current_user.id)
        .filter(Bookings.status.in_(["Booked", "Confirmed", "Pending"])).all()
    ]

    trek_list = []
    for t in open_treks:
        d = t.to_dict()
        d["is_booked_by_user"] = t.id in active_booked_trek_ids
        trek_list.append(d)

    return jsonify({"treks": trek_list}), 200

# Alias for backwards compatibility
browse_treks = browse


# ── 3. Book Trek (MAD 1: book_trek) ───────────────────────────────────────────
@user_bp.route("/book/<int:trek_id>", methods=["POST"])
@user_required
def book_trek(trek_id):
    trek = Treks.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status != "Open":
        return jsonify({"message": f"Trek is currently '{trek.status}' and not open for bookings"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available for this trek"}), 400

    existing_booking = Bookings.query.filter_by(user_id=current_user.id, trek_id=trek_id).first()

    if existing_booking:
        if existing_booking.status in ["Booked", "Confirmed", "Pending"]:
            return jsonify({"message": "You have already booked this trek"}), 409
        elif existing_booking.status == "Cancelled":
            existing_booking.status = "Booked"
            trek.available_slots -= 1
            db.session.commit()
            cache.clear()
            return jsonify({
                "message": "Booking re-submitted successfully!",
                "booking": existing_booking.to_dict()
            }), 200

    booking = Bookings(user_id=current_user.id, trek_id=trek.id, status="Booked")
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": "Trek booked successfully!",
        "booking": booking.to_dict()
    }), 201


def serialize_booking_with_tracking(b):
    d = b.to_dict()
    if b.status == "Cancelled":
        d["tracking_stage"] = 0
        d["tracking_label"] = "Cancelled"
    elif b.status == "Completed" or (b.trek and b.trek.status == "Completed"):
        d["tracking_stage"] = 4
        d["tracking_label"] = "Completed / Summit Achieved"
    elif b.trek and b.trek.status == "Ongoing":
        d["tracking_stage"] = 3
        d["tracking_label"] = "Ongoing Expedition"
    elif b.trek and b.trek.status == "Started":
        d["tracking_stage"] = 2
        d["tracking_label"] = "Expedition Started"
    else:
        d["tracking_stage"] = 1
        d["tracking_label"] = "Confirmed & Scheduled"
    return d


# ── 4. My Bookings (MAD 1: bookings) ──────────────────────────────────────────
@user_bp.route("/bookings", methods=["GET"])
@user_required
def bookings():
    status_filter = request.args.get("status", "all").strip()
    query = Bookings.query.filter_by(user_id=current_user.id)

    if status_filter and status_filter.lower() != "all":
        query = query.filter(Bookings.status.ilike(status_filter))

    user_bookings = query.order_by(Bookings.booking_date.desc()).all()
    return jsonify({"bookings": [serialize_booking_with_tracking(b) for b in user_bookings]}), 200

# Alias for backwards compatibility
get_user_bookings = bookings


@user_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@user_required
def get_booking_detail(booking_id):
    booking = Bookings.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Booking not found"}), 404

    if booking.user_id != current_user.id:
        return jsonify({"message": "Forbidden: You can only view your own bookings"}), 403

    return jsonify({"booking": serialize_booking_with_tracking(booking)}), 200


# ── 5. Cancel Booking (MAD 1: cancel_booking) ─────────────────────────────────
@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@user_bp.route("/bookings/cancel/<int:booking_id>", methods=["POST"])
@user_required
def cancel_booking(booking_id):
    booking = Bookings.query.get(booking_id)
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
    cache.clear()

    return jsonify({
        "message": "Booking cancelled successfully",
        "booking": serialize_booking_with_tracking(booking)
    }), 200


# ── 6. Payment Simulation (Enhancement 2) ─────────────────────────────────────
@user_bp.route("/bookings/<int:booking_id>/pay", methods=["POST"])
@user_required
def simulate_payment(booking_id):
    booking = Bookings.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Booking not found"}), 404

    if booking.user_id != current_user.id:
        return jsonify({"message": "Forbidden"}), 403

    if booking.status == "Cancelled":
        return jsonify({"message": "Cannot pay for a cancelled booking"}), 400

    if booking.payment_status == "Paid":
        return jsonify({"message": "Booking is already paid"}), 400

    data = request.get_json() or {}
    payment_method = data.get("method", "UPI")

    booking.payment_status = "Paid"
    db.session.commit()
    cache.clear()

    return jsonify({
        "message": f"Payment simulated successfully via {payment_method}! Booking confirmed.",
        "booking": serialize_booking_with_tracking(booking)
    }), 200


# ── 7. Trekking History (MAD 1: history) ───────────────────────────────────────
@user_bp.route("/history", methods=["GET"])
@user_required
def history():
    history_bookings = (
        Bookings.query
        .join(Treks)
        .filter(Bookings.user_id == current_user.id)
        .filter(
            (Bookings.status == "Completed") |
            (Treks.status == "Completed")
        )
        .order_by(Bookings.booking_date.desc())
        .all()
    )

    records = []
    total_kms = 0
    total_days = 0

    for b in history_bookings:
        t = b.trek
        d_val = t.duration if (t and t.duration) else 0
        est_km = d_val * 12
        total_days += d_val
        total_kms += est_km

        records.append({
            "id": b.id,
            "booking_id": b.id,
            "trek_id": b.trek_id,
            "trek_name": t.name if t else "Unknown",
            "location": t.location if t else "N/A",
            "trek_location": t.location if t else "N/A",
            "difficulty": t.difficulty if t else "Moderate",
            "trek_difficulty": t.difficulty if t else "Moderate",
            "price": t.price if t else 0.0,
            "trek_price": t.price if t else 0.0,
            "duration": d_val,
            "estimated_km": est_km,
            "trek_start_date": t.start_date.strftime("%Y-%m-%d") if (t and t.start_date) else None,
            "trek_end_date": t.end_date.strftime("%Y-%m-%d") if (t and t.end_date) else None,
            "completion_date": t.end_date.strftime("%Y-%m-%d") if (t and t.end_date) else (b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "N/A"),
            "staff_name": t.assigned_staff.name if (t and t.assigned_staff) else "Unassigned",
            "status": "Completed"
        })

    return jsonify({
        "history": records,
        "summary": {
            "total_completed": len(records),
            "total_days_trekked": total_days,
            "estimated_distance_km": total_kms
        }
    }), 200


# ── 8. Profile Management (MAD 1: profile) ────────────────────────────────────
@user_bp.route("/profile", methods=["GET", "POST", "PUT"])
@user_required
def profile():
    if request.method in ["POST", "PUT"]:
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()

        if email and email != current_user.email:
            existing = Users.query.filter_by(email=email).first()
            if existing and existing.id != current_user.id:
                return jsonify({"message": "Email is already taken"}), 409
            current_user.email = email

        if name:
            current_user.name = name

        db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "user": current_user.to_dict()
        }), 200

    total_bookings = Bookings.query.filter_by(user_id=current_user.id).count()
    completed = Bookings.query.filter_by(user_id=current_user.id, status="Completed").count()

    d = current_user.to_dict()
    d["total_bookings"] = total_bookings
    d["completed_treks"] = completed
    return jsonify({"user": d}), 200

# Aliases for backwards compatibility
get_profile = profile
update_profile = profile


# ── 9. Celery CSV Export (Milestone 7) ─────────────────────────────────────────
@user_bp.route("/export/csv", methods=["POST"])
@user_required
def trigger_csv_export():
    try:
        from task import download_csv
        task = download_csv.delay(current_user.id)
        return jsonify({
            "message": "CSV export initiated in background",
            "task_id": task.id
        }), 202
    except Exception:
        from task import download_csv
        filename = download_csv(current_user.id)
        return jsonify({
            "message": "CSV export generated successfully",
            "filename": filename,
            "download_url": f"/exports/{filename}"
        }), 200


@user_bp.route("/export/status/<task_id>", methods=["GET"])
@user_required
def check_export_status(task_id):
    try:
        from celery.result import AsyncResult
        res = AsyncResult(task_id)
        if res.state == "SUCCESS":
            filename = res.result
            return jsonify({
                "status": "SUCCESS",
                "filename": filename,
                "download_url": f"/exports/{filename}"
            }), 200
        elif res.state == "FAILURE":
            return jsonify({"status": "FAILURE", "error": str(res.info)}), 500
        else:
            return jsonify({"status": res.state}), 202
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500
