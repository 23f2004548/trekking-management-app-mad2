import os
from flask import Flask, send_from_directory, jsonify
from models.models import db, Users, Treks, Staff, Bookings, User, Trek, StaffProfile, Booking
from werkzeug.security import generate_password_hash
from config import LocalDevelopmentConfig
from flask_cors import CORS
from security import jwt
from cache import cache, init_cache
from celery_init_app import celery_init_app
from celery.schedules import crontab
from task import monthly_report, daily_reminders

# Blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

def create_app(config_class=LocalDevelopmentConfig):
    application = Flask(__name__)
    application.config.from_object(config_class)

    jwt.init_app(application)
    db.init_app(application)
    init_cache(application)
    CORS(application)

    # Register blueprints matching Placement Portal architecture
    application.register_blueprint(auth_bp)
    application.register_blueprint(admin_bp)
    application.register_blueprint(staff_bp)
    application.register_blueprint(user_bp)

    # File downloads
    @application.route("/exports/<filename>")
    def download_export(filename):
        exports_dir = os.path.join(application.root_path, "static", "exports")
        return send_from_directory(exports_dir, filename, as_attachment=True)

    @application.route("/reports/file/<filename>")
    def download_report_file(filename):
        reports_dir = os.path.join(application.root_path, "static", "reports")
        return send_from_directory(reports_dir, filename)

    @application.route("/public/analytics", methods=["GET"])
    def public_analytics():
        total_open_treks = Treks.query.filter_by(status="Open").count()
        total_completed_expeditions = Treks.query.filter_by(status="Completed").count()
        total_trekkers_served = Bookings.query.filter(Bookings.status.in_(["Booked", "Completed"])).count()

        easy = Treks.query.filter(Treks.status == "Open", Treks.difficulty.ilike("easy")).count()
        moderate = Treks.query.filter(Treks.status == "Open", Treks.difficulty.ilike("moderate")).count()
        hard = Treks.query.filter(Treks.status == "Open", Treks.difficulty.ilike("hard")).count()

        featured = Treks.query.filter_by(status="Open").order_by(Treks.start_date.asc()).limit(3).all()
        featured_data = [{
            "id": t.id,
            "name": t.name,
            "location": t.location,
            "difficulty": t.difficulty,
            "duration": t.duration,
            "price": t.price,
            "available_slots": t.available_slots
        } for t in featured]

        all_treks = Treks.query.all()
        treks_sorted = sorted(all_treks, key=lambda t: len(t.bookings), reverse=True)[:5]
        popular_data = [{
            "name": t.name,
            "bookings": len(t.bookings)
        } for t in treks_sorted]

        return jsonify({
            "metrics": {
                "open_treks": total_open_treks,
                "completed_expeditions": total_completed_expeditions,
                "trekkers_served": total_trekkers_served
            },
            "difficulty_breakdown": {
                "labels": ["Easy", "Moderate", "Hard"],
                "counts": [easy, moderate, hard]
            },
            "featured_treks": featured_data,
            "popular_treks": popular_data
        }), 200

    @application.route("/api/ping", methods=["GET"])
    def ping():
        return jsonify({"status": "ok", "app": "TMA-V2"}), 200

    return application

# Default global app instance for wsgi / celery / dev server
app = create_app()

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

def create_admin():
    admin_user = Users.query.filter_by(role="admin").first()
    if not admin_user:
        admin_user = Users(
            username="admin",
            name="Admin",
            email="admin@gmail.com",
            password=generate_password_hash("Admin123"),
            role="admin",
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("[SUCCESS] Pre-created default Admin user: admin@gmail.com / Admin123")

with app.app_context():
    db.create_all()
    create_admin()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
