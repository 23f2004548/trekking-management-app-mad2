from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from role_required import role_required
from models.db_models import db, User, StaffProfile, Trek, Booking
from datetime import datetime
from cache import cache
from . import admin_bp

# ── 1. Dashboard Stats ────────────────────────────────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("admin")
@cache.cached(timeout=60)
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="user").count()
    total_staff = StaffProfile.query.count()
    total_bookings = Booking.query.count()
    open_treks = Trek.query.filter_by(status="Open").count()
    active_bookings = Booking.query.filter_by(status="Booked").count()
    blocked_users = User.query.filter_by(is_active=False).count()
    blacklisted_staff = StaffProfile.query.filter_by(status="blacklisted").count()

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


# ── 2. Treks Management (CRUD & Assign Staff) ─────────────────────────────────
@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
@role_required("admin")
@cache.cached(timeout=60)
def get_all_treks():
    treks = Trek.query.order_by(Trek.created_at.desc()).all()
    return jsonify([t.to_dict() for t in treks]), 200


@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
@role_required("admin")
def add_trek():
    data = request.get_json() or {}
    try:
        trek = Trek(
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
@jwt_required()
@role_required("admin")
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
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
                active_bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status.in_(["Booked", "Confirmed"])).all()
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
@jwt_required()
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Trek deleted successfully"}), 200


# ── 3. Staff Management ───────────────────────────────────────────────────────
@admin_bp.route("/staff", methods=["GET"])
@jwt_required()
@role_required("admin")
@cache.cached(timeout=60)
def get_all_staff():
    staff_list = StaffProfile.query.order_by(StaffProfile.created_at.desc()).all()
    return jsonify([s.to_dict() for s in staff_list]), 200


@admin_bp.route("/staff", methods=["POST"])
@jwt_required()
@role_required("admin")
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

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    # Create user credentials with role 'staff'
    staff_user = User(
        username=username,
        name=name,
        email=email,
        role="staff",
        is_active=True
    )
    staff_user.set_password(password)
    db.session.add(staff_user)
    db.session.flush()

    # Create associated StaffProfile
    profile = StaffProfile(
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
@jwt_required()
@role_required("admin")
def toggle_staff_status(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    if staff.status == "active":
        staff.status = "blacklisted"
        if staff.user:
            staff.user.is_active = False
    else:
        staff.status = "active"
        if staff.user:
            staff.user.is_active = True

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": f"Staff status updated to {staff.status}",
        "staff": staff.to_dict()
    }), 200


@admin_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_staff(staff_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    user = User.query.get(staff.user_id)
    db.session.delete(staff)
    if user:
        db.session.delete(user)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Staff member deleted successfully"}), 200


# ── 4. Users Management (Trekkers) ────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
@cache.cached(timeout=60)
def get_all_users():
    users = User.query.filter_by(role="user").order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@jwt_required()
@role_required("admin")
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
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
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"message": "Cannot delete an administrator"}), 403
    db.session.delete(user)
    db.session.commit()
    cache.clear()
    return jsonify({"message": "User deleted successfully"}), 200


# ── 5. Bookings & Trekking History ────────────────────────────────────────────
@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_all_bookings():
    status = request.args.get("status", "all").strip()
    trek_id = request.args.get("trek_id")
    user_id = request.args.get("user_id")
    search = request.args.get("search", "").strip()

    query = Booking.query.join(Trek).join(User)

    if status and status.lower() != "all":
        query = query.filter(Booking.status.ilike(status))
    if trek_id:
        query = query.filter(Booking.trek_id == int(trek_id))
    if user_id:
        query = query.filter(Booking.user_id == int(user_id))
    if search:
        query = query.filter(
            (Trek.name.ilike(f"%{search}%")) |
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    bookings = query.order_by(Booking.booking_date.desc()).all()
    return jsonify([b.to_dict() for b in bookings]), 200


@admin_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@jwt_required()
@role_required("admin")
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["Pending", "Booked", "Cancelled", "Completed"]:
        return jsonify({"message": "Invalid booking status"}), 400

    # If status changes to Cancelled, return the slot to the trek
    if new_status == "Cancelled" and booking.status != "Cancelled":
        booking.trek.available_slots += 1
    elif booking.status == "Cancelled" and new_status in ["Booked", "Pending"]:
        if booking.trek.available_slots > 0:
            booking.trek.available_slots -= 1
        else:
            return jsonify({"message": "Cannot reactivate booking: No available slots on trek"}), 400

    booking.status = new_status
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Booking status updated successfully", "booking": booking.to_dict()}), 200


# ── 6. Search (by Name or ID) ─────────────────────────────────────────────────
@admin_bp.route("/search", methods=["GET"])
@jwt_required()
@role_required("admin")
def search():
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "all").lower()

    treks = []
    users = []
    staff = []

    if not query:
        return jsonify({"treks": [], "users": [], "staff": []}), 200

    # Check if query is an integer ID
    is_id = query.isdigit()

    # Search Treks
    if search_type in ["trek", "all"]:
        trek_q = Trek.query.filter(Trek.name.ilike(f"%{query}%"))
        if is_id:
            trek_q = Trek.query.filter((Trek.id == int(query)) | (Trek.name.ilike(f"%{query}%")))
        treks = [t.to_dict() for t in trek_q.all()]

    # Search Users (Trekkers)
    if search_type in ["user", "all"]:
        user_q = User.query.filter(User.role == "user", (User.name.ilike(f"%{query}%")) | (User.username.ilike(f"%{query}%")))
        if is_id:
            user_q = User.query.filter(User.role == "user", (User.id == int(query)) | (User.name.ilike(f"%{query}%")) | (User.username.ilike(f"%{query}%")))
        users = [u.to_dict() for u in user_q.all()]

    # Search Staff
    if search_type in ["staff", "all"]:
        staff_q = StaffProfile.query.filter(StaffProfile.name.ilike(f"%{query}%"))
        if is_id:
            staff_q = StaffProfile.query.filter((StaffProfile.id == int(query)) | (StaffProfile.name.ilike(f"%{query}%")))
        staff = [s.to_dict() for s in staff_q.all()]

    return jsonify({"treks": treks, "users": users, "staff": staff}), 200


# ── 7. Trekking Statistics & Reports ──────────────────────────────────────────
@admin_bp.route("/reports", methods=["GET"])
@jwt_required()
@role_required("admin")
@cache.cached(timeout=60)
def reports():
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    active_users = User.query.filter_by(role="user", is_active=True).count()
    completed_treks = Trek.query.filter_by(status="Completed").count()

    # Status counts
    booked_count = Booking.query.filter_by(status="Booked").count()
    cancelled_count = Booking.query.filter_by(status="Cancelled").count()
    completed_booking_count = Booking.query.filter_by(status="Completed").count()

    # Difficulty distribution
    easy_count = Trek.query.filter(Trek.difficulty.ilike("easy")).count()
    moderate_count = Trek.query.filter(Trek.difficulty.ilike("moderate")).count()
    hard_count = Trek.query.filter(Trek.difficulty.ilike("hard")).count()

    # Popular treks (by booking count)
    all_treks = Trek.query.all()
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


# ── 8. Celery Batch Jobs (Milestone 7) ─────────────────────────────────────────
@admin_bp.route("/jobs/monthly-report", methods=["POST"])
@jwt_required()
@role_required("admin")
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
@jwt_required()
@role_required("admin")
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
@jwt_required()
@role_required("admin")
def list_generated_reports():
    import os
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


# ── 9. Redis Cache Control (Milestone 8) ───────────────────────────────────────
@admin_bp.route("/cache/clear", methods=["POST"])
@jwt_required()
@role_required("admin")
def clear_api_cache():
    cache.clear()
    return jsonify({"message": "API cache cleared successfully"}), 200

