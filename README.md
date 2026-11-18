# 🏔️ Trekking Management Application (TMA-V2)
**Modern Application Development II (MAD-II) — IIT Madras**

Trekking Management Application V2 is a full-stack web application designed to manage trekking expeditions, participant reservations, staff allocations, and automated reporting.

---

## 🛠️ Tech Stack & Architecture

- **Frontend**: Vue.js 3 (Composition API), Vite, Bootstrap 5, Bootstrap Icons, Chart.js, Axios, Vue Router.
- **Backend API**: Flask 3.1, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Cors, Flask-Caching, Werkzeug.
- **Background Tasks & Jobs**: Celery, Celery Beat, Redis.
- **Email Service**: MailHog (SMTP on port `1025`, Web UI on `http://localhost:8025`).
- **Database**: SQLite with SQLAlchemy ORM.

---

## 📋 Features by Milestones

1. **Milestone 1 — Database Models & Schema**:
   - `Users`: RBAC for Admin, Staff, and Trekkers.
   - `Staff`: Profile information, specialization, status (`pending`, `approved`, `blacklisted`).
   - `Treks`: Route details, difficulty (`Easy`, `Moderate`, `Hard`), slots, status (`upcoming`, `ongoing`, `completed`).
   - `Bookings`: Participant reservations, status (`pending`, `confirmed`, `cancelled`).

2. **Milestone 2 — Authentication & RBAC**:
   - JWT token-based authentication (`/login`, `/register`, `/logout`).
   - Role-based route guards and API decorators (`admin_required`, `staff_required`, `user_required`).

3. **Milestone 3 — Admin Operations**:
   - Route and expedition management (Create, Edit, Delete treks).
   - Staff approvals and blacklisting.
   - User account activation/deactivation.
   - Unified search by Name or ID across Treks, Users, and Staff.

4. **Milestone 4 — Staff Operations**:
   - Dedicated dashboard for assigned expeditions.
   - Participant roster management and attendance confirmation.
   - Expedition status and available slots update.

5. **Milestone 5 — Trekker Dashboard & Booking**:
   - Interactive expedition catalog with real-time slot availability.
   - Filter by name, location, and difficulty level (`Easy`, `Moderate`, `Hard`).
   - Real-time booking with overbooking and duplicate booking prevention.

6. **Milestone 6 — Booking History & Tracking**:
   - Complete booking history and status monitoring.
   - Cancellation with automatic slot recovery.
   - Historical records of completed mountain journeys.

7. **Milestone 7 — Celery Background Jobs**:
   - **Daily Reminders**: Automated email reminders sent to trekkers with expeditions starting within 48 hours.
   - **Monthly Activity Report**: Automated HTML report generation summarizing monthly operational metrics.
   - **User CSV Export**: Asynchronous export of user booking and trekking history.

8. **Milestone 8 — Redis Caching**:
   - Caching on frequently accessed read endpoints (`/admin/dashboard`, `/admin/reports`, `/staff/dashboard`).
   - Instant cache invalidation on mutations and on-demand cache flush.

9. **Enhancements**:
   - Interactive Chart.js analytics for System Overview, Booking Status Distribution, and Treks by Difficulty Level.
   - Public pre-login analytics landing page.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Redis Server (listening on `localhost:6379`)
- MailHog (listening on `localhost:1025` SMTP, `localhost:8025` HTTP)

### 2. Backend Setup
```bash
cd backend
python -m venv env
# On Windows:
.\env\Scripts\activate
# On Linux/macOS:
source env/bin/activate

pip install -r requirements.txt
python app.py
```
*Backend runs on `http://localhost:5000`.*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

### 4. Background Workers (Celery & Celery Beat)
```bash
# Terminal 1: Celery Worker
cd backend
celery -A app.celery worker --loglevel=info -P solo

# Terminal 2: Celery Beat Scheduler
cd backend
celery -A app.celery beat --loglevel=info
```

### 5. Email Testing with MailHog
1. Run `MailHog_windows_amd64.exe` (or `mailhog` on Linux).
2. Open `http://localhost:8025` in your browser to view all dispatched reminder and monthly report emails.

---

## 👤 Default Admin Credentials
- **Email**: `admin@gmail.com`
- **Password**: `Admin123`
