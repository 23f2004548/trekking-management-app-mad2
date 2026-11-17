from celery import shared_task
from models.db_models import db, User, Trek, Booking
import csv
import os
from datetime import datetime, date, timedelta
from mail import send_email


# ── 1. User-Triggered CSV Export for Trekking History ─────────────────────────
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

@shared_task(ignore_result=False, name="download_csv")
def download_csv(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found"

    static_folder = os.path.join(BACKEND_DIR, "static", "exports")
    os.makedirs(static_folder, exist_ok=True)

    filename = f"trekking_history_user_{user_id}.csv"
    filepath = os.path.join(static_folder, filename)

    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Booking ID",
            "Trekker Name",
            "Trekker Email",
            "Trek Name",
            "Location",
            "Difficulty",
            "Duration (Days)",
            "Start Date",
            "End Date",
            "Price (INR)",
            "Assigned Guide",
            "Booking Status",
            "Payment Status",
            "Booked On"
        ])
        for b in bookings:
            writer.writerow([
                b.id,
                user.name,
                user.email,
                b.trek.name if b.trek else "N/A",
                b.trek.location if b.trek else "N/A",
                b.trek.difficulty if b.trek else "N/A",
                b.trek.duration if b.trek else "N/A",
                b.trek.start_date.strftime("%Y-%m-%d") if b.trek and b.trek.start_date else "N/A",
                b.trek.end_date.strftime("%Y-%m-%d") if b.trek and b.trek.end_date else "N/A",
                b.trek.price if b.trek else 0.0,
                b.trek.assigned_staff.name if b.trek and b.trek.assigned_staff else "Unassigned",
                b.status,
                b.payment_status,
                b.booking_date.strftime("%Y-%m-%d %H:%M") if b.booking_date else "N/A"
            ])

    print(f"[CELERY] CSV export generated: {filepath}")
    return filename


# ── 2. Monthly Trekking Activity Report for Admin ─────────────────────────────
@shared_task(name="monthly_report")
def monthly_report():
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return "No admin found"

    total_treks = Trek.query.count()
    completed_treks = Trek.query.filter_by(status="Completed").count()
    open_treks = Trek.query.filter_by(status="Open").count()
    total_bookings = Booking.query.count()
    confirmed_trekkers = Booking.query.filter(Booking.status.in_(["Booked", "Confirmed"])).count()
    completed_trekkers = Booking.query.filter_by(status="Completed").count()

    # Popular treks
    treks = Trek.query.all()
    treks_sorted = sorted(treks, key=lambda t: len(t.bookings), reverse=True)
    popular_treks = treks_sorted[:5]

    popular_rows = ""
    for t in popular_treks:
        popular_rows += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{t.name}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{t.location}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{t.difficulty}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{len(t.bookings)}</td>
        </tr>
        """

    now = datetime.now()
    month_str = now.strftime("%B %Y")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Monthly Trekking Activity Report - {month_str}</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #2c3e50; color: white; padding: 15px 20px; border-radius: 5px;">
            <h2 style="margin: 0;">🏔️ TrekFlow — Monthly Activity Report</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Reporting Period: {month_str}</p>
        </div>

        <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 25px;">Executive Summary</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Key Metric</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Count</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Total Treks Registered</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><strong>{total_treks}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Treks Successfully Conducted (Completed)</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green;"><strong>{completed_treks}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Currently Open Treks</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><strong>{open_treks}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Total Bookings Received</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><strong>{total_bookings}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Confirmed Participants</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;"><strong>{confirmed_trekkers}</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Expeditions Completed by Trekkers</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: right; color: green;"><strong>{completed_trekkers}</strong></td>
            </tr>
        </table>

        <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 25px;">Top Popular Trekking Routes</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
            <tr style="background-color: #f8f9fa;">
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Route Name</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Location</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Difficulty</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Total Bookings</th>
            </tr>
            {popular_rows if popular_rows else "<tr><td colspan='4' style='padding: 10px; text-align: center;'>No trek data available</td></tr>"}
        </table>

        <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; font-size: 0.9em; color: #7f8c8d;">
            <p style="margin: 0;">This automated monthly management report was generated by the <strong>TrekFlow Celery Beat</strong> scheduler.</p>
        </div>
    </body>
    </html>
    """

    # Save copy to static/reports
    reports_folder = os.path.join(BACKEND_DIR, "static", "reports")
    os.makedirs(reports_folder, exist_ok=True)
    report_filename = f"monthly_report_{now.strftime('%Y_%m')}.html"
    report_path = os.path.join(reports_folder, report_filename)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    send_email(
        to_address=admin.email,
        subject=f"🏔️ Monthly Trekking Activity Report - {month_str}",
        message=html_content,
        content="html",
        attachment_file=report_path
    )

    print(f"[CELERY] Monthly report generated and sent: {report_path}")
    return report_filename


# ── 3. Daily Reminders for Upcoming Treks ─────────────────────────────────────
@shared_task(name="daily_reminders")
def daily_reminders():
    today = date.today()
    reminder_window = today + timedelta(days=2)

    # Find upcoming active treks starting in next 48 hours
    upcoming_treks = Trek.query.filter(
        Trek.start_date >= today,
        Trek.start_date <= reminder_window,
        Trek.status.in_(["Open", "Approved", "Started"])
    ).all()

    if not upcoming_treks:
        print("[CELERY] No treks starting within the reminder window today.")
        return "No upcoming treks today"

    reminded_count = 0
    for trek in upcoming_treks:
        active_bookings = Booking.query.filter_by(trek_id=trek.id).filter(Booking.status.in_(["Booked", "Confirmed"])).all()
        for b in active_bookings:
            if b.user and b.user.email:
                subject = f"🎒 Reminder: Your Trek '{trek.name}' Starts on {trek.start_date}!"
                message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h3 style="color: #27ae60;">Get Ready for Your Adventure, {b.user.name}!</h3>
                    <p>This is a friendly reminder that your upcoming expedition is starting very soon:</p>
                    <ul>
                        <li><strong>Trek:</strong> {trek.name}</li>
                        <li><strong>Location:</strong> {trek.location}</li>
                        <li><strong>Start Date:</strong> {trek.start_date}</li>
                        <li><strong>Duration:</strong> {trek.duration} Days</li>
                        <li><strong>Assigned Guide:</strong> {trek.assigned_staff.name if trek.assigned_staff else 'To be announced at basecamp'}</li>
                    </ul>
                    <p><strong>Packing Essentials:</strong> Hiking boots, rain poncho, thermal layers, water bottle, and personal first-aid kit.</p>
                    <p>See you on the trail!<br>Team TrekFlow</p>
                </body>
                </html>
                """
                send_email(to_address=b.user.email, subject=subject, message=message, content="html")
                reminded_count += 1

    print(f"[CELERY] Dispatched reminders to {reminded_count} trekker(s).")
    return f"Sent reminders to {reminded_count} trekker(s)"
