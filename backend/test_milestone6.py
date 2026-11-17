import sys
from app import app
from models.db_models import db, User, Trek, Booking, StaffProfile
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

client = app.test_client()

def test_milestone6_flow():
    with app.app_context():
        # 1. Setup Admin
        admin = User.query.filter_by(role="admin").first()
        if not admin:
            admin = User(
                username="admin_m6",
                name="Admin M6",
                email="admin_m6@gmail.com",
                password=generate_password_hash("Admin123"),
                role="admin",
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()

        # 2. Setup Staff
        staff_user = User.query.filter_by(email="staff_m6@test.com").first()
        if not staff_user:
            staff_user = User(
                username="staff_m6",
                name="Tenzing Guide",
                email="staff_m6@test.com",
                password=generate_password_hash("Secret123"),
                role="staff",
                is_active=True
            )
            db.session.add(staff_user)
            db.session.commit()

        staff_prof = StaffProfile.query.filter_by(user_id=staff_user.id).first()
        if not staff_prof:
            staff_prof = StaffProfile(
                user_id=staff_user.id,
                name=staff_user.name,
                email=staff_user.email,
                phone_number="9876543210",
                specialization="High Mountain Expedition"
            )
            db.session.add(staff_prof)
            db.session.commit()

        # 3. Setup Two Trekker Users (to test isolation)
        trekker1 = User.query.filter_by(email="trekker1_m6@test.com").first()
        if not trekker1:
            trekker1 = User(
                username="trekker1_m6",
                name="Trekker One",
                email="trekker1_m6@test.com",
                password=generate_password_hash("Secret123"),
                role="user",
                is_active=True
            )
            db.session.add(trekker1)

        trekker2 = User.query.filter_by(email="trekker2_m6@test.com").first()
        if not trekker2:
            trekker2 = User(
                username="trekker2_m6",
                name="Trekker Two",
                email="trekker2_m6@test.com",
                password=generate_password_hash("Secret123"),
                role="user",
                is_active=True
            )
            db.session.add(trekker2)
        db.session.commit()

        # 4. Create Trek with status = 'Closed'
        closed_trek = Trek.query.filter_by(name="Kanchenjunga High Pass M6").first()
        if not closed_trek:
            closed_trek = Trek(
                staff_id=staff_prof.id,
                name="Kanchenjunga High Pass M6",
                location="Sikkim",
                difficulty="Hard",
                duration=8,
                total_slots=5,
                available_slots=5,
                status="Closed",
                start_date=date.today() + timedelta(days=20),
                end_date=date.today() + timedelta(days=28),
                price=12000.0
            )
            db.session.add(closed_trek)
            db.session.commit()

        # 5. Create Trek with status = 'Open' and slots = 1
        open_trek = Trek.query.filter_by(name="Valley of Flowers M6").first()
        if not open_trek:
            open_trek = Trek(
                staff_id=staff_prof.id,
                name="Valley of Flowers M6",
                location="Uttarakhand",
                difficulty="Easy",
                duration=3,
                total_slots=1,
                available_slots=1,
                status="Open",
                start_date=date.today() + timedelta(days=5),
                end_date=date.today() + timedelta(days=8),
                price=4000.0
            )
            db.session.add(open_trek)
            db.session.commit()
        else:
            open_trek.available_slots = 1
            open_trek.status = "Open"
            Booking.query.filter_by(trek_id=open_trek.id).delete()
            db.session.commit()

        closed_trek_id = closed_trek.id
        open_trek_id = open_trek.id
        staff_prof_id = staff_prof.id
        admin_email = admin.email

    # Tokens
    def get_token(email, pw="Secret123"):
        res = client.post("/login", json={"email": email, "password": pw})
        assert res.status_code == 200, f"Login failed for {email}: {res.data}"
        return res.json["access_token"]

    t1_token = get_token("trekker1_m6@test.com")
    t2_token = get_token("trekker2_m6@test.com")
    staff_token = get_token("staff_m6@test.com")
    admin_token = get_token(admin_email, "Admin123")

    h1 = {"Authorization": f"Bearer {t1_token}"}
    h2 = {"Authorization": f"Bearer {t2_token}"}
    h_staff = {"Authorization": f"Bearer {staff_token}"}
    h_admin = {"Authorization": f"Bearer {admin_token}"}

    # TEST A: Cannot book if status != 'Open' (Closed trek)
    res_closed = client.post(f"/user/book/{closed_trek_id}", headers=h1)
    assert res_closed.status_code == 400, f"Expected 400 for booking closed trek, got {res_closed.status_code}"
    print("[PASS] Test A: Booking rejected when trek status != 'Open'")

    # TEST B: Book open trek with slots=1 (Trekker 1)
    res_book = client.post(f"/user/book/{open_trek_id}", headers=h1)
    assert res_book.status_code in [200, 201]
    b1_id = res_book.json["booking"]["id"]
    print(f"[PASS] Test B: Trekker 1 successfully booked slot (Booking #{b1_id})")

    # TEST C: Overbooking prevention (Trekker 2 tries to book full trek)
    res_overbook = client.post(f"/user/book/{open_trek_id}", headers=h2)
    assert res_overbook.status_code == 400, f"Expected 400 for full trek, got {res_overbook.status_code}"
    print("[PASS] Test C: Prevented overbooking beyond available slots (400 returned)")

    # TEST D: User isolation - Trekker 2 cannot view or cancel Trekker 1's booking
    res_cancel_unauth = client.post(f"/user/bookings/{b1_id}/cancel", headers=h2)
    assert res_cancel_unauth.status_code == 403, f"Expected 403, got {res_cancel_unauth.status_code}"
    res_view_unauth = client.get(f"/user/bookings/{b1_id}", headers=h2)
    assert res_view_unauth.status_code == 403, f"Expected 403, got {res_view_unauth.status_code}"
    print("[PASS] Test D: User isolation enforced (403 for unauthorized booking access)")

    # TEST E: Trekker 1 status tracking shows 'Confirmed & Scheduled' (Stage 1)
    res_track1 = client.get(f"/user/bookings/{b1_id}", headers=h1)
    assert res_track1.status_code == 200
    assert res_track1.json["booking"]["tracking_stage"] == 1
    print(f"[PASS] Test E: Trek status tracking at Stage 1: {res_track1.json['booking']['tracking_label']}")

    # TEST F: Staff updates trek status to 'Ongoing' -> stage updates to 3
    res_staff_update = client.put(f"/staff/treks/{open_trek_id}", json={"status": "Ongoing"}, headers=h_staff)
    assert res_staff_update.status_code == 200
    res_track3 = client.get(f"/user/bookings/{b1_id}", headers=h1)
    assert res_track3.json["booking"]["tracking_stage"] == 3
    print(f"[PASS] Test F: Live trek progress reflected: Stage 3 ({res_track3.json['booking']['tracking_label']})")

    # TEST G: Staff marks trek as 'Completed' -> auto-completes participant bookings
    res_staff_comp = client.put(f"/staff/treks/{open_trek_id}", json={"status": "Completed"}, headers=h_staff)
    assert res_staff_comp.status_code == 200
    with app.app_context():
        b = Booking.query.get(b1_id)
        assert b.status == "Completed", f"Expected booking status 'Completed', got '{b.status}'"
    print("[PASS] Test G: Trek completion auto-transitions active bookings to 'Completed'")

    # TEST H: Completed booking cannot be cancelled
    res_cancel_comp = client.post(f"/user/bookings/{b1_id}/cancel", headers=h1)
    assert res_cancel_comp.status_code == 400
    print("[PASS] Test H: Completed booking protected from cancellation (400 returned)")

    # TEST I: Completed expedition appears in user history
    res_hist = client.get("/user/history", headers=h1)
    assert res_hist.status_code == 200
    hist_items = res_hist.json["history"]
    assert any(h["id"] == b1_id for h in hist_items)
    assert res_hist.json["summary"]["total_completed"] >= 1
    print(f"[PASS] Test I: Completed trek verified in Trekker 1 history (Total completed: {res_hist.json['summary']['total_completed']})")

    # TEST J: Admin can view all bookings and filter by status
    res_admin_b = client.get("/admin/bookings?status=Completed", headers=h_admin)
    assert res_admin_b.status_code == 200
    assert any(b["id"] == b1_id for b in res_admin_b.json)
    print(f"[PASS] Test J: Admin booking search & status filter working (found {len(res_admin_b.json)} completed bookings)")

    print("\nALL MILESTONE 6 REQUIREMENTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_milestone6_flow()
