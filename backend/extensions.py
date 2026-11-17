from models.models import db
from security import jwt

# Compatibility with MAD 1 syntax
login_manager = jwt

__all__ = ["db", "jwt", "login_manager"]
