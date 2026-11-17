import os
from flask import Flask, send_from_directory
from models.db_models import db, User
from werkzeug.security import generate_password_hash
from config import LocalDevelopmentConfig
from flask_cors import CORS
from security import jwt
from celery_init_app import celery_init_app
from celery.schedules import crontab
from task import monthly_report, daily_reminders

# Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

jwt.init_app(app)
db.init_app(app)
CORS(app)

# Celery Initialization
celery = celery_init_app(app)
celery.autodiscover_tasks()

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Monthly trekking activity report on 1st of every month
    sender.add_periodic_task(
        crontab(day_of_month="1", hour="0", minute="0"),
        monthly_report.s(),
        name="monthly-trekking-report"
    )
    # Daily reminders for upcoming treks every morning at 8:00 AM
    sender.add_periodic_task(
        crontab(hour="8", minute="0"),
        daily_reminders.s(),
        name="daily-trek-reminders"
    )

# Register routes
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)

@app.route("/exports/<filename>")
def download_export(filename):
    exports_dir = os.path.join(app.root_path, "static", "exports")
    return send_from_directory(exports_dir, filename, as_attachment=True)

@app.route("/reports/file/<filename>")
def download_report_file(filename):
    reports_dir = os.path.join(app.root_path, "static", "reports")
    return send_from_directory(reports_dir, filename)

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
