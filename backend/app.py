from flask import Flask
from models.db_models import db, User
from werkzeug.security import generate_password_hash
from config import LocalDevelopmentConfig
from flask_cors import CORS
from security import jwt

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

jwt.init_app(app)
db.init_app(app)
CORS(app)

@app.route("/")
def index():
    return "Trekking Management Application V2 API"

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin = User(
            username="admin",
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("Admin123"),
            role="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[SUCCESS] Pre-created default Admin user: admin@gmail.com / Admin123")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
