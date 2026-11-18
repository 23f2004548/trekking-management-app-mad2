from flask import Blueprint

staff_bp = Blueprint("staff_bp", __name__, url_prefix="/staff")

from . import routes
