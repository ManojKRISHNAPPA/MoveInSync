# 🚗 MoveInSync Clone
**Employee Transportation Management System** – built with Streamlit + Python + SQLite

---

## Features

### Employee Portal
- Self-registration with employee ID, department, home address
- Book cab (Home → Office or Office → Home)
- Select route, shift, and travel date
- View / cancel bookings with real-time status
- Profile page

### Admin Panel
- Live overview dashboard with charts
- View & manage all bookings; update status; assign cabs
- Employee roster
- Fleet management (add cabs, assign drivers)
- Route management (add new routes)
- Driver management (add driver accounts)
- Shift management (configure shift timings & cab times)

### Driver Portal
- View today's assigned trips
- Start trip (`confirmed` → `in_progress`)
- Mark trip as completed (`in_progress` → `completed`)
- Full trip history with filters

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```
The app opens at **http://localhost:8501**

---

## Default Credentials

| Role  | Email                  | Password  |
|-------|------------------------|-----------|
| Admin | admin@company.com      | admin123  |

Employees register themselves. Drivers are added by the admin.

---

## Recommended first-time flow
1. Log in as **Admin**
2. Go to **Drivers** → Add a driver (e.g. DRV001)
3. Go to **Fleet / Cabs** → Add a cab, assign the driver
4. Log out, then **Register** as a new employee
5. Log in as the employee → **Book a Cab**
6. Log back in as Admin → **All Bookings** → confirm / assign cab
7. Log in as Driver → **Dashboard** → Start and complete the trip

---

## Tech Stack
| Layer     | Technology       |
|-----------|-----------------|
| Frontend  | Streamlit        |
| Backend   | Python 3.10+     |
| Database  | SQLite (built-in)|
| Auth      | SHA-256 hashing  |

---

## Project Structure
```
moveinsync_clone/
├── app.py          ← Streamlit UI (all pages & navigation)
├── database.py     ← SQLite data layer (CRUD + analytics)
├── requirements.txt
└── README.md
```
The SQLite database file `moveinsync.db` is created automatically on first run.
