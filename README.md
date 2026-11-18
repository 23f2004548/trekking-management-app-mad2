# Trekking Management Application (MAD-2)

A comprehensive, role-based web application for managing wilderness trekking expeditions, participant reservations, guide assignments, automated email alerts, and administrative analytics.

---

## Prerequisites

Make sure you have the following installed on your machine:
- **Python 3.10+** (with `pip` and `venv`)
- **Node.js 18+** & **npm**
- **Redis Server** (running on default port `6379`)
- **MailHog** (SMTP on port `1025`, Web UI on port `8025`)
- **Git**

---

## 1. Clone the Repository

```bash
git clone https://github.com/23f2004548/trekking-management-app-mad2.git
cd trekking-management-app-mad2
```

---

## 2. Backend Setup & Installation

### Windows (PowerShell):
```powershell
cd backend
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

### Linux / macOS / WSL (bash):
```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cd ..
```

---

## 3. Frontend Setup & Installation

Open a terminal and install frontend dependencies:

### Windows:
```powershell
cd frontend
npm.cmd install
cd ..
```

### Linux / macOS / WSL:
```bash
cd frontend
npm install
cd ..
```

---

## 4. Running the Servers (Step-by-Step)

To run the complete application with all background workers and services, open **6 separate terminal windows** (or tabs):

### Terminal 1: Redis Server
Start Redis on port `6379`.
- **WSL / Linux / macOS**:
  ```bash
  redis-server
  ```
- **Windows (if installed via Memurai or native Redis)**:
  ```powershell
  redis-server
  ```
- *Verify Redis is active*:
  ```bash
  redis-cli ping
  # Expected output: PONG
  ```

---

### Terminal 2: MailHog (Email Service)
Runs the SMTP server on port `1025` and the Web UI on port `8025`.
- **Windows**:
  Run the MailHog executable:
  ```powershell
  MailHog_windows_amd64.exe
  ```
- **Linux / macOS**:
  ```bash
  mailhog
  ```
- *Web UI*: Access emails in browser at [http://localhost:8025](http://localhost:8025)

---

### Terminal 3: Flask Backend Server
Runs the REST API on port `5000`.

- **Windows (PowerShell)**:
  ```powershell
  .\backend\env\Scripts\python backend\app.py
  ```
- **Linux / macOS / WSL**:
  ```bash
  cd backend
  source env/bin/activate
  python app.py
  ```
- *API URL*: [http://localhost:5000](http://localhost:5000)

> **Note**: On the first start, Flask automatically creates the database tables and initializes the default admin account:
> - **Username**: `admin`
> - **Password**: `Admin123`

---

### Terminal 4: Celery Worker
Processes background tasks (CSV booking exports, monthly reports, email dispatches).

- **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="backend"
  .\backend\env\Scripts\celery.exe -A app:celery worker --loglevel=info -P solo
  ```
- **Linux / macOS / WSL**:
  ```bash
  cd backend
  source env/bin/activate
  celery -A app:celery worker --loglevel=info
  ```

---

### Terminal 5: Celery Beat (Periodic Scheduler)
Triggers scheduled jobs (e.g., daily 8:00 AM reminders, monthly reports on the 1st of each month).

- **Windows (PowerShell)**:
  ```powershell
  $env:PYTHONPATH="backend"
  .\backend\env\Scripts\celery.exe -A app:celery beat --loglevel=info
  ```
- **Linux / macOS / WSL**:
  ```bash
  cd backend
  source env/bin/activate
  celery -A app:celery beat --loglevel=info
  ```

---

### Terminal 6: Vite Frontend Server
Runs the Vue 3 single page application on port `5173`.

- **Windows**:
  ```powershell
  cd frontend
  npm.cmd run dev
  ```
- **Linux / macOS / WSL**:
  ```bash
  cd frontend
  npm run dev
  ```
- *App URL*: Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 5. Summary of Service URLs & Ports

| Service | Address | Description |
|---|---|---|
| **Frontend UI** | [http://localhost:5173](http://localhost:5173) | Vue 3 Single Page Application |
| **Backend API** | [http://localhost:5000](http://localhost:5000) | Flask REST API Server |
| **MailHog Web UI** | [http://localhost:8025](http://localhost:8025) | View sent test emails & reminders |
| **MailHog SMTP** | `localhost:1025` | Local SMTP relay |
| **Redis** | `localhost:6379` | Message broker & cache |
| **API Definition** | `api.yaml` | OpenAPI 3.0 specification file |

---

## 6. Default Credentials

- **Admin Account**:
  - **Username**: `admin`
  - **Password**: `Admin123`
- **Trekker / Staff**:
  - Click **Register as Trekker** on the homepage to create a user account.
  - Or select **Role: Staff** during registration to create a guide profile (requires admin approval in the Admin Staff panel).
