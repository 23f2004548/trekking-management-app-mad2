from flask import Blueprint

auth = Blueprint("auth", __name__)
auth_bp = auth

from . import routes
