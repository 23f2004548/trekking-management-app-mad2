import time
from app import app
from cache import cache
from models.db_models import db, User, Trek, Booking
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

client = app.test_client()

def test_caching_and_invalidation():
    with app.app_context():
        # Setup Admin
        admin = User.query.filter_by(role="admin").first()
        admin_email = admin.email

        # Setup test trekker
        trekker = User.query.filter_by(email="trekker_m8@test.com").first()
        if not trekker:
            trekker = User(
                username="trekker_m8",
                name="Sunita Trekker",
                email="trekker_m8@test.com",
                password=generate_password_hash("Secret123"),
                role="user",
                is_active=True
            )
            db.session.add(trekker)
            db.session.commit()

        # Setup initial trek
        test_trek = Trek.query.filter_by(name="Bhrigu Lake M8").first()
        if not test_trek:
            test_trek = Trek(
                name="Bhrigu Lake M8",
                location="Manali, HP",
                difficulty="Easy",
                duration=3,
                total_slots=4,
                available_slots=4,
                status="Open",
                start_date=date.today() + timedelta(days=12),
                end_date=date.today() + timedelta(days=15),
                price=4200.0
            )
            db.session.add(test_trek)
            db.session.commit()
        else:
            test_trek.available_slots = 4
            test_trek.status = "Open"
            Booking.query.filter_by(trek_id=test_trek.id, user_id=trekker.id).delete()
            db.session.commit()

        test_trek_id = test_trek.id

    # 1. Login
    admin_login = client.post("/login", json={"email": admin_email, "password": "Admin123"})
    admin_token = admin_login.json["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    user_login = client.post("/login", json={"email": "trekker_m8@test.com", "password": "Secret123"})
    user_token = user_login.json["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Clear cache before starting test
    with app.app_context():
        cache.clear()

    # 2. Benchmark response time on cached endpoint: GET /admin/dashboard
    t0 = time.perf_counter()
    res1 = client.get("/admin/dashboard", headers=admin_headers)
    t1 = time.perf_counter()
    first_call_duration = (t1 - t0) * 1000

    assert res1.status_code == 200
    data1 = res1.json

    t2 = time.perf_counter()
    res2 = client.get("/admin/dashboard", headers=admin_headers)
    t3 = time.perf_counter()
    cached_call_duration = (t3 - t2) * 1000

    assert res2.status_code == 200
    data2 = res2.json
    assert data1["total_treks"] == data2["total_treks"]

    print(f"[PASS] 1. Cached /admin/dashboard call succeeded. Initial: {first_call_duration:.2f}ms, Cached: {cached_call_duration:.2f}ms")

    # 3. Test Cache Invalidation on Trek Creation
    treks_res1 = client.get("/admin/treks", headers=admin_headers)
    assert treks_res1.status_code == 200
    initial_count = len(treks_res1.json)

    # Create new trek -> must trigger cache.clear()
    new_trek_data = {
        "name": f"Hampta Pass Invalidation Test {int(time.time())}",
        "location": "Manali",
        "difficulty": "Moderate",
        "duration": 5,
        "total_slots": 10,
        "available_slots": 10,
        "status": "Open",
        "start_date": (date.today() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "end_date": (date.today() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "price": 8500.0
    }
    create_res = client.post("/admin/treks", json=new_trek_data, headers=admin_headers)
    assert create_res.status_code == 201

    # Fetch treks immediately after creation -> cache must be fresh
    treks_res2 = client.get("/admin/treks", headers=admin_headers)
    assert treks_res2.status_code == 200
    new_count = len(treks_res2.json)
    assert new_count == initial_count + 1, f"Expected {initial_count + 1} treks, got {new_count}"
    print(f"[PASS] 2. Cache invalidation on Trek creation verified (Treks count: {initial_count} -> {new_count})")

    # 4. Test Cache Invalidation on User Booking
    # Fetch reports before booking (cached)
    rep1 = client.get("/admin/reports", headers=admin_headers)
    assert rep1.status_code == 200
    b_count_before = rep1.json["total_bookings"]

    # User books a trek -> triggers cache.clear()
    book_res = client.post(f"/user/book/{test_trek_id}", headers=user_headers)
    assert book_res.status_code in [200, 201]

    # Fetch reports immediately -> cache must be invalidated and updated
    rep2 = client.get("/admin/reports", headers=admin_headers)
    assert rep2.status_code == 200
    b_count_after = rep2.json["total_bookings"]
    assert b_count_after == b_count_before + 1, f"Expected {b_count_before + 1} bookings, got {b_count_after}"
    print(f"[PASS] 3. Cache invalidation on User Booking verified (Reports booking count: {b_count_before} -> {b_count_after})")

    # 5. Test Manual Admin Cache Flush Endpoint
    clear_res = client.post("/admin/cache/clear", headers=admin_headers)
    assert clear_res.status_code == 200
    assert "cleared successfully" in clear_res.json["message"]
    print("[PASS] 4. Admin manual cache flush endpoint POST /admin/cache/clear verified")

    print("\nALL MILESTONE 8 CACHING & PERFORMANCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_caching_and_invalidation()
