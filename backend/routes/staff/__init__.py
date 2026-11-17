from flask import Blueprint

staff = Blueprint("staff", __name__, url_prefix="/staff")
staff_bp = staff

from . import routes
