from .auth import auth, auth_bp
from .admin import admin, admin_bp
from .staff import staff, staff_bp
from .user import user, user_bp
from .main import main, main_bp

__all__ = [
    "auth", "admin", "staff", "user", "main",
    "auth_bp", "admin_bp", "staff_bp", "user_bp", "main_bp"
]
