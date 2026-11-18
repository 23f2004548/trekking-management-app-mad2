from celery import shared_task
from models.models import db, Users, Bookings, Treks
import csv
import os
from datetime import datetime, date, timedelta
from mail import send_email

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

@shared_task(ignore_result=False, name="download_csv")
def download_csv(user_id):
    user = Users.query.get(user_id)
    if not user:
        return "User not found"

    static_folder = os.path.join(BACKEND_DIR, "static", "exports")
    os.makedirs(static_folder, exist_ok=True)
    filename = f"trekking_history_user_{user_id}.csv"
    filepath = os.path.join(static_folder, filename)

    bookings = Bookings.query.filter_by(user_id=user_id).order_by(Bookings.booking_date.desc()).all()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Booking ID", "Trek Name", "Location", "Difficulty", "Price", "Status", "Booking Date"])
        for b in bookings:
            writer.writerow([
                b.id,
                b.trek.name if b.trek else "N/A",
                b.trek.location if b.trek else "N/A",
                b.trek.difficulty if b.trek else "N/A",
                b.trek.price if b.trek else 0.0,
                b.status,
                b.booking_date.strftime("%Y-%m-%d %H:%M") if b.booking_date else "N/A"
            ])
    return filename

@shared_task(name="monthly_report")
def monthly_report():
    admin = Users.query.filter_by(role="admin").first()
    if not admin:
        return "No admin found"

    total_treks = Treks.query.count()
    completed_treks = Treks.query.filter(Treks.status.ilike("completed")).count()
    total_bookings = Bookings.query.count()

    html_content = f"""
    <html>
        <body>
            <h2>Monthly Trekking Activity Report</h2>
            <p>Summary of trekking operations for the month:</p>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px; text-align: left;">Metric</th>
                    <th style="padding: 8px; text-align: left;">Count</th>
                </tr>
                <tr><td style="padding: 8px;">Total Treks Registered</td><td style="padding: 8px;">{total_treks}</td></tr>
                <tr><td style="padding: 8px;">Completed Expeditions</td><td style="padding: 8px;">{completed_treks}</td></tr>
                <tr><td style="padding: 8px;">Total Bookings</td><td style="padding: 8px;">{total_bookings}</td></tr>
            </table>
            <p>Regards,<br>TrekFlow Team</p>
        </body>
    </html>
    """

    reports_folder = os.path.join(BACKEND_DIR, "static", "reports")
    os.makedirs(reports_folder, exist_ok=True)
    report_filename = f"monthly_report_{datetime.now().strftime('%Y_%m')}.html"
    with open(os.path.join(reports_folder, report_filename), "w", encoding="utf-8") as f:
        f.write(html_content)

    send_email(admin.email, "Monthly Trekking Activity Report", html_content, "html")
    return "Monthly Report Sent Successfully"

@shared_task(name="daily_reminders")
def daily_reminders():
    today = date.today()
    window = today + timedelta(days=2)

    upcoming = Treks.query.filter(Treks.start_date >= today, Treks.start_date <= window).all()
    if not upcoming:
        return "No upcoming treks today"

    sent_count = 0
    for trek in upcoming:
        bookings = Bookings.query.filter_by(trek_id=trek.id).filter(Bookings.status.ilike("confirmed")).all()
        for b in bookings:
            if b.user and b.user.email:
                msg = f"Hello {b.user.name}, your trek '{trek.name}' starts on {trek.start_date}. Be prepared!"
                send_email(b.user.email, f"Reminder: Trek {trek.name} Starts Soon!", f"<p>{msg}</p>", "html")
                sent_count += 1

    return f"Sent reminders to {sent_count} trekker(s)"
