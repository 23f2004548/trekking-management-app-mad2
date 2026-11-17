from flask import Blueprint

user = Blueprint("user", __name__, url_prefix="/user")
user_bp = user

from . import routes
