from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Users Model (MAD 1 Class: Users, table: 'user') ───────────────────────────
class Users(BaseModel):
    __tablename__ = 'user'

    username = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, staff, user
    is_active = db.Column(db.Boolean, default=True)

    # 1-to-1 relationship with Staff
    staff = db.relationship("Staff", backref="user", uselist=False, cascade="all,delete-orphan")
    # 1-to-many relationship with Bookings
    bookings = db.relationship("Bookings", backref="user", cascade="all,delete-orphan")

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }


# ── Staff Model (MAD 1 Class: Staff, table: 'staff_profile') ──────────────────
class Staff(BaseModel):
    __tablename__ = 'staff_profile'

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, default="N/A")
    specialization = db.Column(db.String(100))
    status = db.Column(db.String(20), default="pending")  # pending, approved, blacklisted

    @property
    def role(self):
        return "staff"

    # 1-to-many relationship with Treks
    treks = db.relationship("Treks", backref="assigned_staff", cascade="all,delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "specialization": self.specialization,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }


# ── Treks Model (MAD 1 Class: Treks, table: 'trek') ───────────────────────────
class Treks(BaseModel):
    __tablename__ = 'trek'

    staff_id = db.Column(db.Integer, db.ForeignKey("staff_profile.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy, Moderate, Hard
    duration = db.Column(db.Integer, nullable=False)  # Duration in days
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="upcoming")  # upcoming, ongoing, completed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)

    # 1-to-many relationship with Bookings
    bookings = db.relationship("Bookings", backref="trek", cascade="all,delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.assigned_staff.name if self.assigned_staff else "Unassigned",
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration": self.duration,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "status": self.status,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "description": self.description,
            "price": self.price,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }


# ── Bookings Model (MAD 1 Class: Bookings, table: 'booking') ───────────────────
class Bookings(BaseModel):
    __tablename__ = 'booking'

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="confirmed")  # pending, confirmed, cancelled
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending, Paid, Refunded

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.name if self.trek else None,
            "trek_location": self.trek.location if self.trek else None,
            "trek_difficulty": self.trek.difficulty if self.trek else None,
            "trek_status": self.trek.status if self.trek else None,
            "trek_start_date": self.trek.start_date.strftime("%Y-%m-%d") if self.trek and self.trek.start_date else None,
            "trek_end_date": self.trek.end_date.strftime("%Y-%m-%d") if self.trek and self.trek.end_date else None,
            "trek_price": self.trek.price if self.trek else 0.0,
            "trek_duration": self.trek.duration if self.trek else 0,
            "staff_name": self.trek.assigned_staff.name if self.trek and self.trek.assigned_staff else "Unassigned",
            "staff_email": self.trek.assigned_staff.email if self.trek and self.trek.assigned_staff else None,
            "staff_phone": self.trek.assigned_staff.phone_number if self.trek and self.trek.assigned_staff else None,
            "booking_date": self.booking_date.strftime("%Y-%m-%d %H:%M") if self.booking_date else None,
            "status": self.status,
            "payment_status": self.payment_status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }
