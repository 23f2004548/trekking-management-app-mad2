import sys
from app import app
from models.db_models import db, User, Trek, Booking, StaffProfile
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
import json

client = app.test_client()

def test_user_flow():
    with app.app_context():
        # Setup test trekker user
        test_email = "trekker_m5@test.com"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            user = User(
                username="trekker_m5",
                name="Aman Trekker",
                email=test_email,
                password=generate_password_hash("Secret123"),
                role="user",
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

        # Setup test staff and open trek
        staff_user = User.query.filter_by(email="staff_m5@test.com").first()
        if not staff_user:
            staff_user = User(
                username="staff_m5",
                name="Ramesh Guide",
                email="staff_m5@test.com",
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
                phone_number="9998887776",
                specialization="High Altitude"
            )
            db.session.add(staff_prof)
            db.session.commit()

        # Create Open trek with 2 available slots
        trek = Trek.query.filter_by(name="Rohtang Alpine Pass M5").first()
        if not trek:
            trek = Trek(
                staff_id=staff_prof.id,
                name="Rohtang Alpine Pass M5",
                location="Manali, HP",
                difficulty="Moderate",
                duration=4,
                total_slots=2,
                available_slots=2,
                status="Open",
                start_date=date.today() + timedelta(days=10),
                end_date=date.today() + timedelta(days=14),
                description="Picturesque alpine trail.",
                price=5500.0
            )
            db.session.add(trek)
            db.session.commit()
        else:
            trek.available_slots = 2
            trek.status = "Open"
            # Remove any previous bookings for clean test run
            Booking.query.filter_by(trek_id=trek.id, user_id=user.id).delete()
            db.session.commit()

        trek_id = trek.id

    # 1. Login as trekker
    login_res = client.post("/login", json={"email": test_email, "password": "Secret123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.data}"
    token = login_res.json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] 1. Trekker login successful")

    # 2. Browse treks
    browse_res = client.get("/user/treks?search=Rohtang", headers=headers)
    assert browse_res.status_code == 200
    treks_found = browse_res.json.get("treks", [])
    assert len(treks_found) >= 1
    assert any(t["id"] == trek_id for t in treks_found)
    print(f"[PASS] 2. Browse treks returned {len(treks_found)} matching trek(s)")

    # Filter with difficulty
    diff_res = client.get("/user/treks?difficulty=moderate", headers=headers)
    assert diff_res.status_code == 200
    print(f"[PASS] 2b. Filter treks by difficulty works")

    # 3. Book the trek
    book_res = client.post(f"/user/book/{trek_id}", headers=headers)
    assert book_res.status_code in [200, 201], f"Book trek failed: {book_res.data}"
    booking_id = book_res.json["booking"]["id"]
    print(f"[PASS] 3. Booked trek ID {trek_id}, created Booking ID {booking_id}")

    # Verify slot was decremented
    with app.app_context():
        t = Trek.query.get(trek_id)
        assert t.available_slots == 1, f"Expected 1 slot left, got {t.available_slots}"
    print("[PASS] 3b. Slot decremented from 2 to 1")

    # 4. Duplicate booking attempt -> should return 409
    dup_res = client.post(f"/user/book/{trek_id}", headers=headers)
    assert dup_res.status_code == 409, f"Expected 409 Conflict, got {dup_res.status_code}"
    print("[PASS] 4. Duplicate booking prevented with 409 Conflict")

    # 5. Check user bookings
    bookings_res = client.get("/user/bookings", headers=headers)
    assert bookings_res.status_code == 200
    my_bookings = bookings_res.json["bookings"]
    assert any(b["id"] == booking_id and b["status"] == "Booked" for b in my_bookings)
    print(f"[PASS] 5. Fetched user bookings: found {len(my_bookings)} booking(s)")

    # 6. Check Dashboard stats
    dash_res = client.get("/user/dashboard", headers=headers)
    assert dash_res.status_code == 200
    stats = dash_res.json["stats"]
    assert stats["total_bookings"] >= 1
    assert stats["confirmed_bookings"] >= 1
    print(f"[PASS] 6. User dashboard stats: {stats}")

    # 7. Cancel booking -> slot should be incremented
    cancel_res = client.post(f"/user/bookings/{booking_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200, f"Cancel failed: {cancel_res.data}"
    with app.app_context():
        t = Trek.query.get(trek_id)
        assert t.available_slots == 2, f"Expected 2 slots restored, got {t.available_slots}"
    print("[PASS] 7. Cancelled booking and restored slot to 2")

    # Re-booking after cancellation -> should re-activate and decrement slot
    rebook_res = client.post(f"/user/book/{trek_id}", headers=headers)
    assert rebook_res.status_code == 200
    with app.app_context():
        t = Trek.query.get(trek_id)
        assert t.available_slots == 1
    print("[PASS] 7b. Re-booking previously cancelled trek re-activates and decrements slot")

    # 8. Profile GET & PUT
    prof_res = client.get("/user/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json["user"]["email"] == test_email
    print(f"[PASS] 8a. User profile fetched: {prof_res.json['user']['name']}")

    update_res = client.put("/user/profile", json={"name": "Aman Updated", "email": test_email}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json["user"]["name"] == "Aman Updated"
    print("[PASS] 8b. User profile updated successfully")

    # 9. Trekking history endpoint
    hist_res = client.get("/user/history", headers=headers)
    assert hist_res.status_code == 200
    print(f"[PASS] 9. Trekking history endpoint works (returned {len(hist_res.json['history'])} records)")

    print("\nALL MILESTONE 5 BACKEND TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_user_flow()
