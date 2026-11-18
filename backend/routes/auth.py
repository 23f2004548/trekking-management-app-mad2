from flask import Blueprint, request, jsonify
from models.models import db, Users, Staff
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth_bp", __name__)

# ── 1. Login ──────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    identifier = data.get("username") or data.get("email")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"message": "Username/Email and password are required"}), 400

    user = Users.query.filter(
        (Users.username == identifier) | (Users.email == identifier)
    ).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    if user.role == "staff":
        staff_profile = Staff.query.filter_by(user_id=user.id).first()
        if staff_profile and staff_profile.status == "pending":
            return jsonify({"message": "Your staff account is pending admin approval. You can only log in once an admin approves it."}), 403
        if staff_profile and staff_profile.status == "blacklisted":
            return jsonify({"message": "Your staff account has been blacklisted."}), 403
        if not user.is_active:
            return jsonify({"message": "Your staff account is pending admin approval."}), 403
    elif not user.is_active:
        return jsonify({"message": "Your account has been deactivated. Please contact support."}), 403

    access_token = create_access_token(identity=user)
    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "user": user.to_dict()
    }), 200


# ── 2. Register (User or Staff) ───────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    username = data.get("username", "").strip() or email
    password = data.get("password", "")
    requested_role = data.get("role", "user").strip().lower()

    if requested_role not in ["user", "staff"]:
        return jsonify({"message": "Please select a valid role (User or Staff)."}), 400

    if not name or not email or not password:
        return jsonify({"message": "All fields (Full Name, Email, Password) are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"message": "Invalid email address format"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters long"}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({"message": "Username / Email already registered"}), 409

    if Users.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    if requested_role == "staff":
        new_user = Users(
            username=username,
            name=name,
            email=email,
            role="staff",
            is_active=False
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        profile = Staff(
            user_id=new_user.id,
            name=name,
            email=email,
            phone_number=data.get("phone_number", "N/A"),
            specialization=data.get("specialization", "General"),
            status="pending"
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({
            "message": "Staff registration submitted! Your account is pending admin approval before you can log in.",
            "user": new_user.to_dict()
        }), 201
    else:
        new_user = Users(
            username=username,
            name=name,
            email=email,
            role="user",
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully! You can now log in.",
            "user": new_user.to_dict()
        }), 201


# ── 3. Logout ─────────────────────────────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Stateless JWT logout endpoint."""
    return jsonify({"message": "Successfully logged out"}), 200
