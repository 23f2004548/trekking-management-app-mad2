import os
import sys
import csv
from app import app
from models.db_models import db, User, Trek, Booking, StaffProfile
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
from task import download_csv, monthly_report, daily_reminders

client = app.test_client()

def test_milestone7():
    with app.app_context():
        # Setup test trekker
        user = User.query.filter_by(email="trekker_m7@test.com").first()
        if not user:
            user = User(
                username="trekker_m7",
                name="Deepak Trekker",
                email="trekker_m7@test.com",
                password=generate_password_hash("Secret123"),
                role="user",
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

        # Setup test staff & trek
        staff = User.query.filter_by(email="staff_m7@test.com").first()
        if not staff:
            staff = User(
                username="staff_m7",
                name="Anil Guide",
                email="staff_m7@test.com",
                password=generate_password_hash("Secret123"),
                role="staff",
                is_active=True
            )
            db.session.add(staff)
            db.session.commit()
            sp = StaffProfile(user_id=staff.id, name=staff.name, email=staff.email, phone_number="9123456789")
            db.session.add(sp)
            db.session.commit()
        else:
            sp = staff.staff_profile

        # Trek starting tomorrow (within daily reminder window)
        trek_soon = Trek.query.filter_by(name="Kudremukh Peak M7").first()
        if not trek_soon:
            trek_soon = Trek(
                staff_id=sp.id,
                name="Kudremukh Peak M7",
                location="Chikmagalur, Karnataka",
                difficulty="Moderate",
                duration=2,
                total_slots=10,
                available_slots=9,
                status="Open",
                start_date=date.today() + timedelta(days=1),
                end_date=date.today() + timedelta(days=3),
                price=3200.0
            )
            db.session.add(trek_soon)
            db.session.commit()

        # Booking for trekker on upcoming trek
        b = Booking.query.filter_by(user_id=user.id, trek_id=trek_soon.id).first()
        if not b:
            b = Booking(user_id=user.id, trek_id=trek_soon.id, status="Booked")
            db.session.add(b)
            db.session.commit()

        user_id = user.id
        admin_user = User.query.filter_by(role="admin").first()
        admin_email = admin_user.email

    # Login
    login_user = client.post("/login", json={"email": "trekker_m7@test.com", "password": "Secret123"})
    assert login_user.status_code == 200
    user_token = login_user.json["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    login_admin = client.post("/login", json={"email": admin_email, "password": "Admin123"})
    assert login_admin.status_code == 200
    admin_token = login_admin.json["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Test CSV Generation Task
    csv_filename = download_csv(user_id)
    assert csv_filename.endswith(".csv"), f"Invalid CSV filename: {csv_filename}"
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(backend_dir, "static", "exports", csv_filename)
    assert os.path.exists(csv_path), f"CSV file not found at: {csv_path}"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert "Trek Name" in headers
        assert "Assigned Guide" in headers
        row = next(reader)
        assert "Deepak Trekker" in row
        assert "Kudremukh Peak M7" in row
    print(f"[PASS] 1. download_csv task created valid CSV with {len(headers)} columns")

    # 2. Test User CSV Export API Endpoint
    export_res = client.post("/user/export/csv", headers=user_headers)
    assert export_res.status_code in [200, 202]
    print(f"[PASS] 2. POST /user/export/csv returned {export_res.status_code} ({export_res.json.get('message')})")

    # 3. Test File Download Route
    download_res = client.get(f"/exports/{csv_filename}")
    assert download_res.status_code == 200
    assert b"Deepak Trekker" in download_res.data
    print(f"[PASS] 3. GET /exports/{csv_filename} served CSV file successfully")

    # 4. Test Monthly Report Generation Task
    report_filename = monthly_report()
    assert report_filename.endswith(".html")
    report_path = os.path.join(backend_dir, "static", "reports", report_filename)
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        report_html = f.read()
        assert "TrekFlow — Monthly Activity Report" in report_html
        assert "Executive Summary" in report_html
    print(f"[PASS] 4. monthly_report task generated HTML report: {report_filename}")

    # 5. Test Daily Reminders Task
    reminders_result = daily_reminders()
    print(f"[PASS] 5. daily_reminders task executed successfully: {reminders_result}")

    # 6. Test Admin Batch Job Endpoints
    m_job_res = client.post("/admin/jobs/monthly-report", headers=admin_headers)
    assert m_job_res.status_code in [200, 202]
    print(f"[PASS] 6a. Admin POST /admin/jobs/monthly-report returned {m_job_res.status_code}")

    d_job_res = client.post("/admin/jobs/daily-reminders", headers=admin_headers)
    assert d_job_res.status_code in [200, 202]
    print(f"[PASS] 6b. Admin POST /admin/jobs/daily-reminders returned {d_job_res.status_code}")

    reports_list_res = client.get("/admin/reports/files", headers=admin_headers)
    assert reports_list_res.status_code == 200
    assert len(reports_list_res.json["reports"]) >= 1
    print(f"[PASS] 7. Admin GET /admin/reports/files listed {len(reports_list_res.json['reports'])} report(s)")

    print("\nALL MILESTONE 7 BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone7()
