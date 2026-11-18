from flask_jwt_extended import JWTManager
from models.models import Users

jwt = JWTManager()

@jwt.user_identity_loader
def load(user):
    return str(user.id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, _jwt_data):
    identity = _jwt_data["sub"]
    return Users.query.filter_by(id=identity).one_or_none()
