from functools import wraps
from flask import jsonify
from flask_jwt_extended import current_user

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            if not current_user or current_user.role not in roles:
                return jsonify({"message": "Forbidden: Access denied"}), 403
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper
