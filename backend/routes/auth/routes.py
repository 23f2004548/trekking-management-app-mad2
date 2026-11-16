from flask import request, jsonify
from models.db_models import db, User, StaffProfile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, current_user
from . import auth_bp

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login endpoint for all roles (Admin, Trek Staff, Trekkers).
    Accepts username or email and password.
    Returns JWT access token, role, and user profile data.
    """
    data = request.get_json() or {}
    identifier = data.get("username") or data.get("email")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"message": "Username/Email and password are required"}), 400

    # Match by either username or email
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"message": "Your account has been deactivated. Please contact support."}), 403

    # Additional check for staff blacklist status
    if user.role == "staff":
        staff_profile = StaffProfile.query.filter_by(user_id=user.id).first()
        if staff_profile and staff_profile.status == "blacklisted":
            return jsonify({"message": "Your staff account has been blacklisted."}), 403

    access_token = create_access_token(identity=user)
    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "user": user.to_dict()
    }), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Self-registration endpoint:
    - Allowed ONLY for Users (Trekkers).
    - Trek Staff accounts are created by Admin only.
    - Admin account is pre-created only.
    """
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    requested_role = data.get("role", "user").strip().lower()

    # Rule enforcement: Only trekkers ('user') can self-register
    if requested_role in ["admin", "staff"]:
        return jsonify({
            "message": "Registration restricted: Staff accounts must be created by Admin, and Admin accounts cannot be registered."
        }), 403

    if not username or not name or not email or not password:
        return jsonify({"message": "All fields (username, name, email, password) are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"message": "Invalid email address format"}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already taken"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    new_user = User(
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


@auth_bp.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    """Returns the current authenticated user's details."""
    if not current_user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(current_user.to_dict()), 200
