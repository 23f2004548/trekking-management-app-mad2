import os
import sys

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from models.db_models import db, User, StaffProfile, Trek, Booking
from werkzeug.security import generate_password_hash

def init_database():
    """
    Programmatic schema initialization and admin seed:
    1. Creates all tables using SQLAlchemy ORM
    2. Pre-creates the default Admin user if not already present
    """
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        admin = User.query.filter_by(role="admin").first()
        if not admin:
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
            print("[SUCCESS] Admin user pre-created successfully:")
            print("          Username: admin")
            print("          Email:    admin@gmail.com")
            print("          Password: Admin123")
            print("          Role:     admin")
        else:
            print("[INFO] Admin user already exists.")

        print("\nDatabase tables in schema:")
        for table in db.metadata.tables.keys():
            print(f"  - {table}")

if __name__ == "__main__":
    init_database()
