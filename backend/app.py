import os
from flask import Flask, send_from_directory, jsonify
from models.models import db, Users, Treks, Bookings
from werkzeug.security import generate_password_hash
from config import LocalDevelopmentConfig
from flask_cors import CORS
from security import jwt
from cache import cache
from celery_init_app import celery_init_app
from celery.schedules import crontab
from task import monthly_report, daily_reminders

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

jwt.init_app(app)
cache.init_app(app)
db.init_app(app)

celery = celery_init_app(app)
celery.autodiscover_tasks()

@celery.on_after_finalize.connect 
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(day_of_month="1", hour="0", minute="0"), monthly_report.s())
    sender.add_periodic_task(crontab(hour="8", minute="0"), daily_reminders.s())

CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)

@app.route("/exports/<filename>")
def download_export(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'exports'), filename, as_attachment=True)

@app.route("/reports/file/<filename>")
def download_report(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'reports'), filename)

@app.route("/public/analytics")
def public_analytics():
    treks = Treks.query.all()
    upcoming_count = Treks.query.filter(Treks.status.ilike("upcoming")).count()
    completed_count = Treks.query.filter(Treks.status.ilike("completed")).count()
    trekkers = Bookings.query.filter(Bookings.status.ilike("confirmed")).count()
    counts = [Treks.query.filter(Treks.status.ilike("upcoming"), Treks.difficulty.ilike(d)).count() for d in ["Easy", "Moderate", "Hard"]]
    featured = [t.to_dict() for t in Treks.query.filter(Treks.status.ilike("upcoming")).limit(3)]
    popular = [{"name": t.name, "bookings": len(t.bookings)} for t in sorted(treks, key=lambda t: len(t.bookings), reverse=True)[:5]]
    return jsonify({
        "metrics": {"open_treks": upcoming_count, "completed_expeditions": completed_count, "trekkers_served": trekkers},
        "difficulty_breakdown": {"labels": ["Easy", "Moderate", "Hard"], "counts": counts},
        "featured_treks": featured,
        "popular_treks": popular
    })

with app.app_context():
    db.create_all()
    if not Users.query.filter_by(role="admin").first():
        admin = Users(username="admin", name="Admin", email="admin@gmail.com", password=generate_password_hash("Admin123"), role="admin", is_active=True)
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
