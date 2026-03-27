import sqlite3
import hashlib
import random
from datetime import datetime

DB_PATH = "moveinsync.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users: employees, admins, drivers
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id      TEXT    UNIQUE NOT NULL,
            name             TEXT    NOT NULL,
            email            TEXT    UNIQUE NOT NULL,
            phone            TEXT,
            password_hash    TEXT    NOT NULL,
            role             TEXT    DEFAULT 'employee',
            address          TEXT,
            office_location  TEXT,
            department       TEXT,
            is_active        INTEGER DEFAULT 1,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Cabs / Fleet
    c.execute("""
        CREATE TABLE IF NOT EXISTS cabs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cab_number  TEXT    UNIQUE NOT NULL,
            model       TEXT,
            cab_type    TEXT    DEFAULT 'sedan',
            capacity    INTEGER DEFAULT 4,
            color       TEXT,
            driver_id   INTEGER REFERENCES users(id),
            is_active   INTEGER DEFAULT 1
        )
    """)

    # Routes
    c.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name     TEXT    NOT NULL,
            pickup_area    TEXT    NOT NULL,
            drop_area      TEXT    NOT NULL,
            estimated_time INTEGER DEFAULT 30,
            distance_km    REAL    DEFAULT 0,
            is_active      INTEGER DEFAULT 1
        )
    """)

    # Work shifts
    c.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_name  TEXT NOT NULL,
            shift_start TEXT NOT NULL,
            shift_end   TEXT NOT NULL,
            pickup_time TEXT,
            drop_time   TEXT
        )
    """)

    # Cab bookings
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_ref      TEXT    UNIQUE NOT NULL,
            employee_id      INTEGER REFERENCES users(id),
            cab_id           INTEGER REFERENCES cabs(id),
            route_id         INTEGER REFERENCES routes(id),
            shift_id         INTEGER REFERENCES shifts(id),
            booking_date     TEXT    NOT NULL,
            pickup_time      TEXT    NOT NULL,
            pickup_location  TEXT,
            drop_location    TEXT,
            trip_type        TEXT    DEFAULT 'pickup',
            status           TEXT    DEFAULT 'pending',
            notes            TEXT,
            created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # ── Seed data ──────────────────────────────────────────────────────────────
    # Default admin
    c.execute(
        """INSERT OR IGNORE INTO users
           (employee_id, name, email, phone, password_hash, role, department)
           VALUES (?,?,?,?,?,?,?)""",
        ("ADMIN001", "System Admin", "admin@company.com", "9999999999",
         hash_password("admin123"), "admin", "IT"),
    )

    # Default shifts
    default_shifts = [
        ("Morning Shift",   "09:00", "18:00", "08:00", "19:00"),
        ("Afternoon Shift", "13:00", "22:00", "12:00", "23:00"),
        ("Night Shift",     "21:00", "06:00", "20:00", "07:00"),
        ("General Shift",   "10:00", "19:00", "09:00", "20:00"),
    ]
    for s in default_shifts:
        c.execute(
            """INSERT OR IGNORE INTO shifts
               (shift_name, shift_start, shift_end, pickup_time, drop_time)
               VALUES (?,?,?,?,?)""",
            s,
        )

    # Default routes
    default_routes = [
        ("Route 1 – North Zone", "Whitefield",  "Electronic City",    45, 25.0),
        ("Route 2 – South Zone", "Koramangala", "Manyata Tech Park",   40, 20.0),
        ("Route 3 – East Zone",  "Indiranagar",  "Bagmane Tech Park",  30, 15.0),
        ("Route 4 – West Zone",  "Rajajinagar",  "EGL Tech Park",      50, 28.0),
        ("Route 5 – Central",    "HSR Layout",   "UB City",            35, 18.0),
    ]
    for r in default_routes:
        c.execute(
            """INSERT OR IGNORE INTO routes
               (route_name, pickup_area, drop_area, estimated_time, distance_km)
               VALUES (?,?,?,?,?)""",
            r,
        )

    conn.commit()
    conn.close()


# ── User operations ────────────────────────────────────────────────────────────

def register_user(employee_id, name, email, phone, password, address, department, office_location):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO users
               (employee_id, name, email, phone, password_hash, address, department, office_location)
               VALUES (?,?,?,?,?,?,?,?)""",
            (employee_id, name, email, phone, hash_password(password),
             address, department, office_location),
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        err = str(e).lower()
        if "employee_id" in err:
            return False, "Employee ID already exists."
        if "email" in err:
            return False, "Email is already registered."
        return False, str(e)
    finally:
        conn.close()


def login_user(email: str, password: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE email=? AND password_hash=? AND is_active=1",
        (email, hash_password(password)),
    )
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_employees():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='employee' ORDER BY name")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_all_drivers():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE role='driver' ORDER BY name")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_driver(name, email, phone, password, employee_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO users
               (employee_id, name, email, phone, password_hash, role)
               VALUES (?,?,?,?,?,?)""",
            (employee_id, name, email, phone, hash_password(password), "driver"),
        )
        conn.commit()
        return True, "Driver added successfully!"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


# ── Cab operations ─────────────────────────────────────────────────────────────

def get_all_cabs():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT c.*, u.name AS driver_name
           FROM cabs c
           LEFT JOIN users u ON c.driver_id = u.id
           ORDER BY c.cab_number"""
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_cab(cab_number, cab_type, capacity, driver_id, model, color):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO cabs (cab_number, cab_type, capacity, driver_id, model, color)
               VALUES (?,?,?,?,?,?)""",
            (cab_number, cab_type, capacity, driver_id or None, model, color),
        )
        conn.commit()
        return True, "Cab added successfully!"
    except sqlite3.IntegrityError:
        return False, "Cab number already exists."
    finally:
        conn.close()


def update_cab(cab_id, cab_type, capacity, driver_id, is_active):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE cabs SET cab_type=?, capacity=?, driver_id=?, is_active=? WHERE id=?",
        (cab_type, capacity, driver_id or None, is_active, cab_id),
    )
    conn.commit()
    conn.close()


# ── Route operations ───────────────────────────────────────────────────────────

def get_all_routes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM routes WHERE is_active=1 ORDER BY route_name")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_route(route_name, pickup_area, drop_area, estimated_time, distance_km):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO routes (route_name, pickup_area, drop_area, estimated_time, distance_km)
               VALUES (?,?,?,?,?)""",
            (route_name, pickup_area, drop_area, estimated_time, distance_km),
        )
        conn.commit()
        return True, "Route added successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# ── Shift operations ───────────────────────────────────────────────────────────

def get_all_shifts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM shifts ORDER BY shift_start")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_shift(shift_name, shift_start, shift_end, pickup_time, drop_time):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """INSERT INTO shifts (shift_name, shift_start, shift_end, pickup_time, drop_time)
               VALUES (?,?,?,?,?)""",
            (shift_name, shift_start, shift_end, pickup_time, drop_time),
        )
        conn.commit()
        return True, "Shift added successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# ── Booking operations ─────────────────────────────────────────────────────────

def create_booking(employee_id, route_id, shift_id, booking_date,
                   trip_type, pickup_location, drop_location, notes=""):
    conn = get_connection()
    c = conn.cursor()

    # Determine pickup/drop time from shift
    c.execute("SELECT * FROM shifts WHERE id=?", (shift_id,))
    shift = c.fetchone()
    pickup_time = (
        (shift["pickup_time"] if trip_type == "pickup" else shift["drop_time"])
        if shift else "09:00"
    )

    # Try to find an available cab for this date/time
    c.execute(
        """SELECT c.id FROM cabs c
           WHERE c.is_active=1 AND c.driver_id IS NOT NULL
             AND c.id NOT IN (
                 SELECT cab_id FROM bookings
                 WHERE booking_date=? AND pickup_time=?
                   AND status NOT IN ('cancelled','completed')
                   AND cab_id IS NOT NULL
             )
           LIMIT 1""",
        (booking_date, pickup_time),
    )
    row = c.fetchone()
    cab_id = row["id"] if row else None

    booking_ref = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    try:
        c.execute(
            """INSERT INTO bookings
               (booking_ref, employee_id, cab_id, route_id, shift_id, booking_date,
                pickup_time, pickup_location, drop_location, trip_type, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (booking_ref, employee_id, cab_id, route_id, shift_id, booking_date,
             pickup_time, pickup_location, drop_location, trip_type, notes),
        )
        conn.commit()
        cab_msg = "" if cab_id else " (Cab will be assigned shortly)"
        return True, f"Booking confirmed! Ref: {booking_ref}{cab_msg}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_employee_bookings(employee_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT b.*,
                  r.route_name, r.pickup_area, r.drop_area,
                  s.shift_name,
                  cb.cab_number, cb.model,
                  u.name  AS driver_name,
                  u.phone AS driver_phone
           FROM bookings b
           LEFT JOIN routes r  ON b.route_id  = r.id
           LEFT JOIN shifts s  ON b.shift_id  = s.id
           LEFT JOIN cabs   cb ON b.cab_id    = cb.id
           LEFT JOIN users  u  ON cb.driver_id = u.id
           WHERE b.employee_id=?
           ORDER BY b.booking_date DESC, b.pickup_time DESC""",
        (employee_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_all_bookings():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT b.*,
                  emp.name        AS employee_name,
                  emp.employee_id AS emp_code,
                  r.route_name,
                  s.shift_name,
                  cb.cab_number,
                  drv.name        AS driver_name
           FROM bookings b
           LEFT JOIN users  emp ON b.employee_id = emp.id
           LEFT JOIN routes r   ON b.route_id    = r.id
           LEFT JOIN shifts s   ON b.shift_id    = s.id
           LEFT JOIN cabs   cb  ON b.cab_id      = cb.id
           LEFT JOIN users  drv ON cb.driver_id  = drv.id
           ORDER BY b.booking_date DESC, b.created_at DESC"""
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def cancel_booking(booking_id: int, employee_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """UPDATE bookings SET status='cancelled'
           WHERE id=? AND employee_id=? AND status='pending'""",
        (booking_id, employee_id),
    )
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def update_booking_status(booking_id: int, status: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()


def get_driver_bookings(driver_id: int):
    """Return all bookings assigned to cabs driven by this driver."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT b.*,
                  emp.name  AS employee_name,
                  emp.phone AS employee_phone,
                  r.route_name, r.pickup_area, r.drop_area
           FROM bookings b
           LEFT JOIN users  emp ON b.employee_id = emp.id
           LEFT JOIN routes r   ON b.route_id    = r.id
           LEFT JOIN cabs   cb  ON b.cab_id      = cb.id
           WHERE cb.driver_id=? AND b.status NOT IN ('cancelled')
           ORDER BY b.booking_date DESC, b.pickup_time""",
        (driver_id,),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def assign_cab_to_booking(booking_id: int, cab_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bookings SET cab_id=?, status='confirmed' WHERE id=?",
              (cab_id, booking_id))
    conn.commit()
    conn.close()


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_booking_stats() -> dict:
    conn = get_connection()
    c = conn.cursor()

    def scalar(sql, params=()):
        c.execute(sql, params)
        return c.fetchone()[0]

    stats = {
        "pending":          scalar("SELECT COUNT(*) FROM bookings WHERE status='pending'"),
        "confirmed":        scalar("SELECT COUNT(*) FROM bookings WHERE status='confirmed'"),
        "in_progress":      scalar("SELECT COUNT(*) FROM bookings WHERE status='in_progress'"),
        "completed":        scalar("SELECT COUNT(*) FROM bookings WHERE status='completed'"),
        "cancelled":        scalar("SELECT COUNT(*) FROM bookings WHERE status='cancelled'"),
        "total_employees":  scalar("SELECT COUNT(*) FROM users WHERE role='employee' AND is_active=1"),
        "total_drivers":    scalar("SELECT COUNT(*) FROM users WHERE role='driver' AND is_active=1"),
        "active_cabs":      scalar("SELECT COUNT(*) FROM cabs WHERE is_active=1"),
        "today_bookings":   scalar("SELECT COUNT(*) FROM bookings WHERE booking_date=date('now')"),
    }
    conn.close()
    return stats


def get_monthly_booking_trend():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """SELECT strftime('%Y-%m', booking_date) AS month, COUNT(*) AS total
           FROM bookings
           GROUP BY month
           ORDER BY month DESC
           LIMIT 6"""
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
