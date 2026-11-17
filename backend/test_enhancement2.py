"""
Automated Verification Suite for Enhancement 2 (E2):
- Interactive Reports, Charts & Analytics (Chart.js integration)
- Pre-login Public Analytics Endpoint (GET /public/analytics)
- Mock Payment Processing Simulation (POST /user/bookings/<id>/pay)
"""

from app import app
from models.db_models import db, User, Trek, Booking
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

client = app.test_client()

def test_enhancement_2():
    with app.app_context():
        # 1. Verify Public Analytics Endpoint (Pre-login, unauthenticated)
        print("--> Testing GET /public/analytics (Unauthenticated)")
        pub_res = client.get("/public/analytics")
        assert pub_res.status_code == 200, f"Expected 200, got {pub_res.status_code}: {pub_res.data}"
        pub_data = pub_res.json
        print(f"Public analytics returned keys: {list(pub_data.keys())}")
        
        assert "metrics" in pub_data
        metrics = pub_data["metrics"]
        assert "open_treks" in metrics
        assert "completed_expeditions" in metrics
        assert "trekkers_served" in metrics
        print(f"Community Metrics: {metrics}")

        assert "difficulty_breakdown" in pub_data
        assert "labels" in pub_data["difficulty_breakdown"]
        assert "counts" in pub_data["difficulty_breakdown"]
        assert "popular_treks" in pub_data
        assert "featured_treks" in pub_data
        print("✓ Pre-login Public Analytics verified successfully!")

        # 2. Setup a test user and booking for Payment simulation
        user = User.query.filter_by(email="trekker_e2@test.com").first()
        if not user:
            user = User(
                username="trekker_e2",
                name="Aakash Verma",
                email="trekker_e2@test.com",
                password=generate_password_hash("Password123"),
                role="user",
                is_active=True
            )
            db.session.add(user)
            db.session.commit()

        trek = Trek.query.filter_by(name="Kashmir Great Lakes E2").first()
        if not trek:
            trek = Trek(
                name="Kashmir Great Lakes E2",
                location="Sonamarg, J&K",
                difficulty="Challenging",
                duration=7,
                total_slots=10,
                available_slots=10,
                status="Open",
                start_date=date.today() + timedelta(days=20),
                end_date=date.today() + timedelta(days=27),
                price=14500.0
            )
            db.session.add(trek)
            db.session.commit()

        # Clean existing booking if any
        Booking.query.filter_by(user_id=user.id, trek_id=trek.id).delete()
        db.session.commit()

        # Login as user
        login_res = client.post("/login", json={"email": "trekker_e2@test.com", "password": "Password123"})
        assert login_res.status_code == 200, f"Login failed: {login_res.data}"
        token = login_res.json["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create booking
        book_res = client.post(f"/user/book/{trek.id}", headers=headers)
        assert book_res.status_code == 201, f"Booking creation failed: {book_res.data}"
        booking_id = book_res.json["booking"]["id"]
        assert book_res.json["booking"]["payment_status"] == "Pending"
        print(f"Created booking ID {booking_id} with payment_status='Pending'")

        # 3. Simulate Payment
        print("--> Testing POST /user/bookings/<id>/pay (Payment Simulation)")
        pay_res = client.post(f"/user/bookings/{booking_id}/pay", json={"method": "UPI"}, headers=headers)
        assert pay_res.status_code == 200, f"Payment simulation failed: {pay_res.data}"
        pay_data = pay_res.json
        assert pay_data["booking"]["payment_status"] == "Paid"
        print("✓ Payment simulation succeeded!")

        # 4. Verify idempotent / duplicate payment prevention
        dup_pay_res = client.post(f"/user/bookings/{booking_id}/pay", json={"method": "Card"}, headers=headers)
        assert dup_pay_res.status_code == 400, "Expected 400 for already paid booking"
        print("✓ Duplicate payment prevention verified!")

        # 5. Verify booking in GET /user/bookings reflects Paid
        list_res = client.get("/user/bookings", headers=headers)
        assert list_res.status_code == 200
        found = next((b for b in list_res.json["bookings"] if b["id"] == booking_id), None)
        assert found is not None
        assert found["payment_status"] == "Paid"
        print("✓ GET /user/bookings reflects updated payment_status='Paid'!")

    print("\n==========================================")
    print("ALL ENHANCEMENT 2 TESTS PASSED SUCCESSFULLY!")
    print("==========================================\n")

if __name__ == "__main__":
    test_enhancement_2()
