import os
from flask import Flask, send_from_directory
from models.db_models import db, User, Trek, Booking
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

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

jwt.init_app(app)
db.init_app(app)
init_cache(app)
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

@app.route("/public/analytics", methods=["GET"])
def public_analytics():
    from flask import jsonify
    total_open_treks = Trek.query.filter_by(status="Open").count()
    total_completed_expeditions = Trek.query.filter_by(status="Completed").count()
    total_trekkers_served = Booking.query.filter(Booking.status.in_(["Booked", "Completed"])).count()

    easy = Trek.query.filter(Trek.status == "Open", Trek.difficulty.ilike("easy")).count()
    moderate = Trek.query.filter(Trek.status == "Open", Trek.difficulty.ilike("moderate")).count()
    hard = Trek.query.filter(Trek.status == "Open", Trek.difficulty.ilike("hard")).count()

    featured = Trek.query.filter_by(status="Open").order_by(Trek.start_date.asc()).limit(3).all()
    featured_data = [{
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration": t.duration,
        "price": t.price,
        "available_slots": t.available_slots
    } for t in featured]

    all_treks = Trek.query.all()
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
