from .admin import admin_bp, admin
from .admin.routes import *

__all__ = [
    "admin", "admin_bp", "admin_required", "dashboard", "treks", "add_trek",
    "edit_trek", "delete_trek", "staff", "add_staff", "change_staff_status",
    "delete_staff", "users", "delete_user", "bookings", "change_booking_status",
    "search", "reports", "profile"
]
