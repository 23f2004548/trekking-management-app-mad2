from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from models.models import db, Users, Treks, Staff, Bookings
from datetime import datetime
import os
from cache import cache

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# ── Admin Required Decorator ──────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        if not current_user or current_user.role != "admin":
            return jsonify({"message": "Forbidden: Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


# ── 1. Dashboard Stats ────────────────────────────────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
@cache.cached(timeout=60)
def dashboard():
    total_treks = Treks.query.count()
    total_users = Users.query.filter_by(role="user").count()
    total_staff = Staff.query.count()
    total_bookings = Bookings.query.count()
    open_treks = Treks.query.filter_by(status="Open").count()
    active_bookings = Bookings.query.filter_by(status="Booked").count()
    blocked_users = Users.query.filter_by(is_active=False).count()
    blacklisted_staff = Staff.query.filter_by(status="blacklisted").count()

    return jsonify({
        "total_treks": total_treks,
        "total_users": total_users,
        "total_staff": total_staff,
        "total_bookings": total_bookings,
        "open_treks": open_treks,
        "active_bookings": active_bookings,
        "blocked_users": blocked_users,
        "blacklisted_staff": blacklisted_staff
    }), 200


# ── 2. Treks Management ───────────────────────────────────────────────────────
@admin_bp.route("/treks", methods=["GET"])
@admin_required
@cache.cached(timeout=60)
def treks():
    all_treks = Treks.query.order_by(Treks.created_at.desc()).all()
    return jsonify([t.to_dict() for t in all_treks]), 200


@admin_bp.route("/treks", methods=["POST"])
@admin_required
def add_trek():
    data = request.get_json() or {}
    try:
        trek = Treks(
            name=data["name"].strip(),
            location=data["location"].strip(),
            difficulty=data.get("difficulty", "Easy"),
            duration=int(data["duration"]),
            total_slots=int(data["total_slots"]),
            available_slots=int(data.get("available_slots", data["total_slots"])),
            status=data.get("status", "Pending"),
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
            staff_id=int(data["staff_id"]) if data.get("staff_id") else None,
            description=data.get("description", ""),
            price=float(data.get("price", 0.0))
        )
        db.session.add(trek)
        db.session.commit()
        cache.clear()
        return jsonify({"message": "Trek created successfully", "trek": trek.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@admin_required
def edit_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    data = request.get_json() or {}
    try:
        if "name" in data: trek.name = data["name"].strip()
        if "location" in data: trek.location = data["location"].strip()
        if "difficulty" in data: trek.difficulty = data["difficulty"]
        if "duration" in data: trek.duration = int(data["duration"])
        if "total_slots" in data: trek.total_slots = int(data["total_slots"])
        if "available_slots" in data: trek.available_slots = int(data["available_slots"])
        if "status" in data:
            trek.status = data["status"]
            if trek.status == "Completed":
                active_bookings = Bookings.query.filter_by(trek_id=trek.id).filter(Bookings.status.in_(["Booked", "Confirmed"])).all()
                for b in active_bookings:
                    b.status = "Completed"
        if "description" in data: trek.description = data["description"]
        if "price" in data: trek.price = float(data["price"])
        if "staff_id" in data:
            trek.staff_id = int(data["staff_id"]) if data["staff_id"] else None
        if data.get("start_date"):
            trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        db.session.commit()
        cache.clear()
        return jsonify({"message": "Trek updated successfully", "trek": trek.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@admin_required
def delete_trek(trek_id):
    trek = Treks.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek deleted successfully"}), 200


# ── 3. Staff Management ───────────────────────────────────────────────────────
@admin_bp.route("/staff", methods=["GET"])
@admin_required
@cache.cached(timeout=60)
def staff():
    status = request.args.get("status")
    query = Staff.query
    if status:
        query = query.filter_by(status=status)
    staff_list = query.order_by(Staff.created_at.desc()).all()
    return jsonify([s.to_dict() for s in staff_list]), 200


@admin_bp.route("/staff", methods=["POST"])
@admin_required
def add_staff():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "Staff123")
    phone_number = data.get("phone_number", "N/A").strip()
    specialization = data.get("specialization", "").strip()

    if not username or not name or not email:
        return jsonify({"message": "Username, name, and email are required"}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if Users.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    staff_user = Users(
        username=username,
        name=name,
        email=email,
        role="staff",
        is_active=True
    )
    staff_user.set_password(password)
    db.session.add(staff_user)
    db.session.flush()

    profile = Staff(
        user_id=staff_user.id,
        name=name,
        email=email,
        phone_number=phone_number,
        specialization=specialization,
        status="active"
    )
    db.session.add(profile)
    db.session.commit()
    cache.clear()

    return jsonify({"message": "Staff member created successfully", "staff": profile.to_dict()}), 201


@admin_bp.route("/staff/<int:staff_id>/toggle-status", methods=["POST"])
@admin_required
def change_staff_status(staff_id):
    staff_member = Staff.query.get_or_404(staff_id)
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    if new_status:
        staff_member.status = new_status
        if staff_member.user:
            staff_member.user.is_active = (new_status.lower() in ["active", "approved"])
    else:
        if staff_member.status == "pending":
            staff_member.status = "active"
            if staff_member.user:
                staff_member.user.is_active = True
        elif staff_member.status == "active":
            staff_member.status = "blacklisted"
            if staff_member.user:
                staff_member.user.is_active = False
        else:
            staff_member.status = "active"
            if staff_member.user:
                staff_member.user.is_active = True

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": f"Staff status updated to {staff_member.status}",
        "staff": staff_member.to_dict()
    }), 200


@admin_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
@admin_required
def delete_staff(staff_id):
    staff_member = Staff.query.get_or_404(staff_id)
    user = Users.query.get(staff_member.user_id)
    db.session.delete(staff_member)
    if user:
        db.session.delete(user)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Staff member deleted successfully"}), 200


# ── 4. Users Management ───────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@admin_required
@cache.cached(timeout=60)
def users():
    all_users = Users.query.filter_by(role="user").order_by(Users.created_at.desc()).all()
    return jsonify([u.to_dict() for u in all_users]), 200


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    user = Users.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"message": "Cannot deactivate an administrator"}), 403

    user.is_active = not user.is_active
    db.session.commit()
    cache.clear()
    return jsonify({
        "message": f"User {'activated' if user.is_active else 'deactivated'} successfully",
        "user": user.to_dict()
    }), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"message": "Cannot delete an administrator"}), 403
    db.session.delete(user)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "User deleted successfully"}), 200


# ── 5. Bookings Management ────────────────────────────────────────────────────
@admin_bp.route("/bookings", methods=["GET"])
@admin_required
def bookings():
    status = request.args.get("status", "all").strip()
    trek_id = request.args.get("trek_id")
    user_id = request.args.get("user_id")
    search_term = request.args.get("search", "").strip()

    query = Bookings.query.join(Treks).join(Users)

    if status and status.lower() != "all":
        query = query.filter(Bookings.status.ilike(status))
    if trek_id:
        query = query.filter(Bookings.trek_id == int(trek_id))
    if user_id:
        query = query.filter(Bookings.user_id == int(user_id))
    if search_term:
        query = query.filter(
            (Treks.name.ilike(f"%{search_term}%")) |
            (Users.name.ilike(f"%{search_term}%")) |
            (Users.email.ilike(f"%{search_term}%"))
        )

    all_bookings = query.order_by(Bookings.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in all_bookings]), 200


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@admin_required
def change_booking_status(booking_id):
    booking = Bookings.query.get_or_404(booking_id)
    data = request.get_json() or {}
    new_status = data.get("status", "").capitalize()

    if new_status not in ["Pending", "Booked", "Confirmed", "Cancelled", "Completed"]:
        return jsonify({"message": "Invalid booking status"}), 400

    if new_status == "Cancelled" and booking.status != "Cancelled":
        booking.trek.available_slots += 1
    elif booking.status == "Cancelled" and new_status in ["Booked", "Pending", "Confirmed"]:
        if booking.trek.available_slots > 0:
            booking.trek.available_slots -= 1
        else:
            return jsonify({"message": "Cannot reactivate booking: No available slots on trek"}), 400

    booking.status = new_status
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Booking status updated successfully", "booking": booking.to_dict()}), 200


# ── 6. Search ─────────────────────────────────────────────────────────────────
@admin_bp.route("/search", methods=["GET"])
@admin_required
def search():
    query_str = (request.args.get("search") or request.args.get("q") or "").strip()
    search_type = request.args.get("type", "all").lower()

    treks_res = []
    users_res = []
    staff_res = []

    if not query_str:
        return jsonify({"treks": [], "users": [], "staff": []}), 200

    is_id = query_str.isdigit()

    if search_type in ["trek", "all"]:
        trek_q = Treks.query.filter(Treks.name.ilike(f"%{query_str}%"))
        if is_id:
            trek_q = Treks.query.filter((Treks.id == int(query_str)) | (Treks.name.ilike(f"%{query_str}%")))
        treks_res = [t.to_dict() for t in trek_q.all()]

    if search_type in ["user", "all"]:
        user_q = Users.query.filter(Users.role == "user", (Users.name.ilike(f"%{query_str}%")) | (Users.username.ilike(f"%{query_str}%")))
        if is_id:
            user_q = Users.query.filter(Users.role == "user", (Users.id == int(query_str)) | (Users.name.ilike(f"%{query_str}%")) | (Users.username.ilike(f"%{query_str}%")))
        users_res = [u.to_dict() for u in user_q.all()]

    if search_type in ["staff", "all"]:
        staff_q = Staff.query.filter(Staff.name.ilike(f"%{query_str}%"))
        if is_id:
            staff_q = Staff.query.filter((Staff.id == int(query_str)) | (Staff.name.ilike(f"%{query_str}%")))
        staff_res = [s.to_dict() for s in staff_q.all()]

    return jsonify({"treks": treks_res, "users": users_res, "staff": staff_res}), 200


# ── 7. Reports ────────────────────────────────────────────────────────────────
@admin_bp.route("/reports", methods=["GET"])
@admin_required
@cache.cached(timeout=60)
def reports():
    total_treks = Treks.query.count()
    total_bookings = Bookings.query.count()
    active_users = Users.query.filter_by(role="user", is_active=True).count()
    completed_treks = Treks.query.filter_by(status="Completed").count()

    booked_count = Bookings.query.filter_by(status="Booked").count()
    cancelled_count = Bookings.query.filter_by(status="Cancelled").count()
    completed_booking_count = Bookings.query.filter_by(status="Completed").count()

    easy_count = Treks.query.filter(Treks.difficulty.ilike("easy")).count()
    moderate_count = Treks.query.filter(Treks.difficulty.ilike("moderate")).count()
    hard_count = Treks.query.filter(Treks.difficulty.ilike("hard")).count()

    all_treks = Treks.query.all()
    popular_treks = []
    for t in all_treks:
        b_count = len(t.bookings)
        popular_treks.append({
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "difficulty": t.difficulty,
            "booking_count": b_count,
            "status": t.status
        })
    popular_treks.sort(key=lambda x: x["booking_count"], reverse=True)

    return jsonify({
        "total_treks": total_treks,
        "total_bookings": total_bookings,
        "active_users": active_users,
        "completed_treks": completed_treks,
        "booking_stats": {
            "booked": booked_count,
            "cancelled": cancelled_count,
            "completed": completed_booking_count
        },
        "difficulty_distribution": {
            "Easy": easy_count,
            "Moderate": moderate_count,
            "Hard": hard_count
        },
        "popular_treks": popular_treks[:5]
    }), 200


# ── 8. Celery Batch Jobs ──────────────────────────────────────────────────────
@admin_bp.route("/jobs/monthly-report", methods=["POST"])
@admin_required
def trigger_monthly_report():
    try:
        from task import monthly_report
        task = monthly_report.delay()
        return jsonify({
            "message": "Monthly activity report generation initiated in background",
            "task_id": task.id
        }), 202
    except Exception:
        from task import monthly_report
        result = monthly_report()
        return jsonify({
            "message": "Monthly activity report generated successfully",
            "filename": result,
            "report_url": f"/reports/file/{result}"
        }), 200


@admin_bp.route("/jobs/daily-reminders", methods=["POST"])
@admin_required
def trigger_daily_reminders():
    try:
        from task import daily_reminders
        task = daily_reminders.delay()
        return jsonify({
            "message": "Daily trek reminders initiated in background",
            "task_id": task.id
        }), 202
    except Exception:
        from task import daily_reminders
        result = daily_reminders()
        return jsonify({
            "message": "Daily trek reminders dispatched successfully",
            "result": result
        }), 200


@admin_bp.route("/reports/files", methods=["GET"])
@admin_required
def list_generated_reports():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_folder = os.path.join(backend_dir, "static", "reports")
    files = []
    if os.path.exists(reports_folder):
        for f in os.listdir(reports_folder):
            if f.endswith(".html"):
                files.append({
                    "filename": f,
                    "url": f"/reports/file/{f}"
                })
    return jsonify({"reports": files}), 200


# ── 9. Cache Control ──────────────────────────────────────────────────────────
@admin_bp.route("/cache/clear", methods=["POST"])
@admin_required
def clear_api_cache():
    cache.clear()
    return jsonify({"message": "API cache cleared successfully"}), 200
