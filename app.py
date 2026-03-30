"""
MoveInSync – Employee Transportation Management System
Full-stack Streamlit application (Python + SQLite)
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta

import database as db

# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoveInSync – Microdegree Employee Transportation Management System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Header banner */
    .mis-header {
        background: linear-gradient(135deg, #0d3b6e 0%, #1565C0 60%, #1976D2 100%);
        padding: 22px 30px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(21,101,192,0.35);
    }
    .mis-header h1 { margin: 0; font-size: 2rem; }
    .mis-header h2 { margin: 4px 0 0; font-size: 1.4rem; }
    .mis-header p  { margin: 6px 0 0; opacity: .85; font-size: .95rem; }

    /* Stat / feature cards */
    .card {
        background: #ffffff;
        border-radius: 10px;
        padding: 22px 20px;
        text-align: center;
        border-left: 5px solid #1565C0;
        box-shadow: 0 2px 12px rgba(0,0,0,.08);
        height: 100%;
    }
    .card h3 { margin: 8px 0 4px; font-size: 1.05rem; color: #0d3b6e; }
    .card p  { font-size: .88rem; color: #555; margin: 0; }

    /* Status badges */
    .badge-pending    { color:#FF8F00; font-weight:700; }
    .badge-confirmed  { color:#1565C0; font-weight:700; }
    .badge-in_progress{ color:#2E7D32; font-weight:700; }
    .badge-completed  { color:#424242; font-weight:700; }
    .badge-cancelled  { color:#C62828; font-weight:700; }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] { background: #0d3b6e; }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stRadio label { font-size: .95rem; }

    /* Metric card accent */
    [data-testid="stMetric"] { background:#f0f4ff; border-radius:8px; padding:10px; }

    /* Booking expander */
    .booking-row { padding: 6px 0; }

    /* ── Role selection tiles (home page) ── */
    .role-tile {
        border-radius: 18px;
        padding: 36px 24px 24px;
        text-align: center;
        color: white;
        margin-bottom: 14px;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.22);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    .role-tile:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 32px rgba(0,0,0,0.3);
    }
    .tile-icon { font-size: 3.6rem; margin-bottom: 14px; }
    .role-tile h2 { margin: 0 0 8px; font-size: 1.45rem; font-weight: 700; letter-spacing:.3px; }
    .role-tile p  { margin: 0 0 10px; font-size: .88rem; opacity: .9; line-height: 1.5; }
    .tile-badge {
        display: inline-block;
        background: rgba(255,255,255,.2);
        border-radius: 20px;
        padding: 3px 14px;
        font-size: .78rem;
        margin-top: 6px;
        letter-spacing: .4px;
    }
    .emp-tile    { background: linear-gradient(145deg, #0d3b6e 0%, #1565C0 55%, #1976D2 100%); }
    .admin-tile  { background: linear-gradient(145deg, #1a0033 0%, #4A148C 55%, #6A1B9A 100%); }
    .driver-tile { background: linear-gradient(145deg, #0a2e12 0%, #1B5E20 55%, #2E7D32 100%); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── DB bootstrap ───────────────────────────────────────────────────────────────
db.init_db()

# ── Session-state defaults ─────────────────────────────────────────────────────
for key, default in [("user", None), ("page", "home"), ("login_role", "employee")]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Navigation helpers ─────────────────────────────────────────────────────────
def go(page: str):
    st.session_state.page = page
    st.rerun()


def logout():
    st.session_state.user = None
    st.session_state.page = "home"
    st.rerun()


# ── Shared widget ──────────────────────────────────────────────────────────────
STATUS_ICON = {
    "pending": "🟡", "confirmed": "🔵",
    "in_progress": "🟢", "completed": "⚫", "cancelled": "🔴",
}


def status_badge(status: str) -> str:
    icons = {"pending": "🟡", "confirmed": "🔵", "in_progress": "🟢",
             "completed": "⚫", "cancelled": "🔴"}
    return f"{icons.get(status,'⚪')} {status.replace('_',' ').upper()}"


# ═══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def show_home():
    st.markdown(
        """
        <div class="mis-header">
            <h1>🚗 MoveInSync</h1>
            <p>Manoj testing</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h3 style='text-align:center;color:#444;margin-bottom:6px'>"
        "Select your portal to get started</h3>"
        "<p style='text-align:center;color:#888;margin-bottom:24px'>"
        "Click the tile that matches your role</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3, gap="large")

    # ── Employee tile ──────────────────────────────────────────────────────────
    with c1:
        st.markdown(
            """
            <div class="role-tile emp-tile">
                <div class="tile-icon">🏢</div>
                <h2>Employee</h2>
                <p>Book cab pickups &amp; drops,<br>track rides and manage your schedule</p>
                <span class="tile-badge">Self-registration available</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔐 Login", key="tile_emp_login",
                         use_container_width=True, type="primary"):
                st.session_state.login_role = "employee"
                go("login")
        with b2:
            if st.button("📝 Register", key="tile_emp_reg",
                         use_container_width=True):
                go("register")

    # ── Admin tile ─────────────────────────────────────────────────────────────
    with c2:
        st.markdown(
            """
            <div class="role-tile admin-tile">
                <div class="tile-icon">⚙️</div>
                <h2>Admin</h2>
                <p>Manage fleet, routes, shifts &amp; drivers;<br>monitor every trip from one panel</p>
                <span class="tile-badge">Restricted access</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔐 Admin Login", key="tile_admin_login",
                     use_container_width=True):
            st.session_state.login_role = "admin"
            go("login")

    # ── Driver tile ────────────────────────────────────────────────────────────
    with c3:
        st.markdown(
            """
            <div class="role-tile driver-tile">
                <div class="tile-icon">🚘</div>
                <h2>Driver</h2>
                <p>View assigned trips, start rides<br>and mark them as completed</p>
                <span class="tile-badge">Assigned by admin</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔐 Driver Login", key="tile_driver_login",
                     use_container_width=True):
            st.session_state.login_role = "driver"
            go("login")

    st.markdown("---")
    st.caption("© 2024 MoveInSync Clone · Built with Streamlit & Python")


# Role config used by login page
_ROLE_CFG = {
    "employee": {
        "icon":  "🏢",
        "label": "Employee Portal",
        "grad":  "linear-gradient(135deg, #0d3b6e, #1976D2)",
        "hint":  "Use your registered work email and password.",
        "show_register": True,
    },
    "admin": {
        "icon":  "⚙️",
        "label": "Admin Portal",
        "grad":  "linear-gradient(135deg, #1a0033, #6A1B9A)",
        "hint":  "Demo credentials → admin@company.com  /  admin123",
        "show_register": False,
    },
    "driver": {
        "icon":  "🚘",
        "label": "Driver Portal",
        "grad":  "linear-gradient(135deg, #0a2e12, #2E7D32)",
        "hint":  "Use the credentials provided to you by your admin.",
        "show_register": False,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def show_login():
    role = st.session_state.get("login_role", "employee")
    cfg  = _ROLE_CFG.get(role, _ROLE_CFG["employee"])

    # Role-coloured header
    st.markdown(
        f'<div class="mis-header" style="background:{cfg["grad"]};">' 
        f'<h2>{cfg["icon"]}  {cfg["label"]}</h2>'
        f'<p>Sign in to continue</p></div>',
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            email    = st.text_input("📧 Email Address", placeholder="your.email@company.com")
            password = st.text_input("🔑 Password", type="password")
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col_b:
                back = st.form_submit_button("← Back to Home", use_container_width=True)

            if submit:
                if not (email and password):
                    st.warning("Please fill in both fields.")
                else:
                    user = db.login_user(email, password)
                    if user:
                        # Role mismatch guard
                        if user["role"] != role:
                            st.error(
                                f"❌ This is the **{cfg['label']}**. "
                                f"Your account role is **{user['role']}**. "
                                f"Please go back and choose the correct portal."
                            )
                        else:
                            st.session_state.user = user
                            dest = {"admin": "admin_dashboard",
                                    "driver": "driver_dashboard"}.get(user["role"], "employee_dashboard")
                            go(dest)
                    else:
                        st.error("❌ Invalid email or password.")
            if back:
                go("home")

        st.info(f"💡 {cfg['hint']}")
        if cfg["show_register"]:
            if st.button("Don't have an account? Register here →"):
                go("register")


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════
def show_register():
    st.markdown(
        '<div class="mis-header"><h2>📝 Employee Registration</h2></div>',
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([0.5, 3, 0.5])
    with mid:
        with st.form("register_form"):
            st.subheader("Personal Information")
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                employee_id = st.text_input("👤 Employee ID *", placeholder="EMP001")
                name        = st.text_input("📛 Full Name *", placeholder="Jane Doe")
                email       = st.text_input("📧 Work Email *", placeholder="jane@company.com")
            with r1c2:
                phone       = st.text_input("📱 Phone *", placeholder="9876543210")
                department  = st.selectbox(
                    "🏢 Department",
                    ["Engineering", "Sales", "HR", "Finance",
                     "Marketing", "Operations", "Design", "Other"],
                )
                office_location = st.selectbox(
                    "🏢 Office Location",
                    ["Main Campus – Electronic City",
                     "Manyata Tech Park",
                     "Ecospace"
                     "Whitefield Campus",
                     "Bagmane Tech Park"],
                )

            st.subheader("Address")
            address = st.text_area("🏠 Home / Pickup Address *",
                                   placeholder="Full address used for cab pickup")

            st.subheader("Account Credentials")
            pc1, pc2 = st.columns(2)
            with pc1:
                password  = st.text_input("🔑 Password *", type="password")
            with pc2:
                confirm   = st.text_input("🔑 Confirm Password *", type="password")

            btn_reg, btn_back = st.columns(2)
            with btn_reg:
                submit = st.form_submit_button("Register", use_container_width=True, type="primary")
            with btn_back:
                back = st.form_submit_button("← Back to Login", use_container_width=True)

            if submit:
                fields = [employee_id, name, email, phone, address, password, confirm]
                if not all(fields):
                    st.error("❌ Please fill in all required fields.")
                elif password != confirm:
                    st.error("❌ Passwords do not match.")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    ok, msg = db.register_user(
                        employee_id, name, email, phone,
                        password, address, department, office_location,
                    )
                    if ok:
                        st.success(f"✅ {msg} – You can now log in.")
                        go("login")
                    else:
                        st.error(f"❌ {msg}")
            if back:
                go("login")


# ═══════════════════════════════════════════════════════════════════════════════
# EMPLOYEE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def show_employee_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"## 🚗 MoveInSync")
        st.markdown(f"**{user['name']}**")
        st.caption(f"{user.get('employee_id','')} · {user.get('department','')}")
        st.markdown("---")
        menu = st.radio(
            "Menu",
            ["🏠 Dashboard", "🚗 Book a Cab", "📋 My Bookings", "👤 Profile"],
            key="emp_menu",
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    pages = {
        "🏠 Dashboard": emp_home,
        "🚗 Book a Cab": emp_book_cab,
        "📋 My Bookings": emp_my_bookings,
        "👤 Profile": show_profile,
    }
    pages[menu](user)


# ── Employee: Home ─────────────────────────────────────────────────────────────
def emp_home(user):
    st.markdown(
        f'<div class="mis-header"><h2>🏠 Dashboard</h2>'
        f"<p>Welcome back, {user['name']}!</p></div>",
        unsafe_allow_html=True,
    )

    bookings = db.get_employee_bookings(user["id"])
    today_str = date.today().strftime("%Y-%m-%d")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⏳ Pending",   sum(1 for b in bookings if b["status"] == "pending"))
    m2.metric("✅ Confirmed", sum(1 for b in bookings if b["status"] == "confirmed"))
    m3.metric("🏁 Completed", sum(1 for b in bookings if b["status"] == "completed"))
    m4.metric("📊 Total Rides", len(bookings))

    # Today's bookings
    today_b = [b for b in bookings if b["booking_date"] == today_str]
    st.markdown("---")
    if today_b:
        st.markdown("### 📅 Today's Bookings")
        for b in today_b:
            trip_icon = "🏠→🏢" if b["trip_type"] == "pickup" else "🏢→🏠"
            with st.expander(
                f"{STATUS_ICON.get(b['status'],'⚪')}  {b['booking_ref']}  |  "
                f"{trip_icon}  |  {b['pickup_time']}  |  {b['status'].upper()}"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Route:** {b.get('route_name','N/A')}")
                    st.write(f"**Shift:** {b.get('shift_name','N/A')}")
                    st.write(f"**Pickup:** {b.get('pickup_location','N/A')}")
                with c2:
                    st.write(f"**Cab:** {b.get('cab_number','Not assigned yet')}")
                    st.write(f"**Driver:** {b.get('driver_name','Not assigned yet')}")
                    st.write(f"**Driver Phone:** {b.get('driver_phone','N/A')}")
    else:
        st.info("📭 No bookings for today. Use **Book a Cab** to schedule one!")

    # Upcoming bookings
    upcoming = [
        b for b in bookings
        if b["booking_date"] > today_str and b["status"] not in ("cancelled", "completed")
    ]
    if upcoming:
        st.markdown("### 📆 Upcoming Bookings")
        df = pd.DataFrame(upcoming)[
            ["booking_ref", "booking_date", "pickup_time", "trip_type", "route_name", "status"]
        ]
        df.columns = ["Booking Ref", "Date", "Time", "Trip", "Route", "Status"]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Employee: Book cab ─────────────────────────────────────────────────────────
def emp_book_cab(user):
    st.markdown(
        '<div class="mis-header"><h2>🚗 Book a Cab</h2>'
        "<p>Schedule your pickup or drop in a few clicks</p></div>",
        unsafe_allow_html=True,
    )

    routes = db.get_all_routes()
    shifts = db.get_all_shifts()

    if not routes:
        st.warning("⚠️ No routes configured yet. Please contact your admin.")
        return

    with st.form("book_cab_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            trip_type = st.selectbox(
                "🔄 Trip Type",
                ["pickup", "drop"],
                format_func=lambda x: (
                    "🏠 → 🏢  Home to Office  (Morning Pickup)"
                    if x == "pickup" else
                    "🏢 → 🏠  Office to Home  (Evening Drop)"
                ),
            )
            route_idx = st.selectbox(
                "🗺️ Route",
                range(len(routes)),
                format_func=lambda i: routes[i]["route_name"],
            )
            route = routes[route_idx]
            booking_date = st.date_input(
                "📅 Travel Date",
                min_value=date.today(),
                max_value=date.today() + timedelta(days=30),
            )

        with col2:
            shift_idx = st.selectbox(
                "⏰ Shift",
                range(len(shifts)),
                format_func=lambda i: (
                    f"{shifts[i]['shift_name']}  "
                    f"({shifts[i]['shift_start']} – {shifts[i]['shift_end']})"
                ),
            )
            shift = shifts[shift_idx]
            pickup_location = st.text_input(
                "📍 Pickup Address",
                value=user.get("address", ""),
            )
            drop_location = st.text_input(
                "📍 Drop Address",
                value=user.get("office_location", ""),
            )

        notes = st.text_area("📝 Notes (optional)", placeholder="Anything the driver should know…")

        pickup_time_display = shift["pickup_time"] if trip_type == "pickup" else shift["drop_time"]
        st.info(
            f"**Route:** {route['pickup_area']} ↔ {route['drop_area']}  |  "
            f"Est. {route['estimated_time']} min  |  {route['distance_km']} km  |  "
            f"**Cab time:** {pickup_time_display}"
        )

        submit = st.form_submit_button("🚗  Confirm Booking", type="primary", use_container_width=True)

        if submit:
            date_str = booking_date.strftime("%Y-%m-%d")
            existing = db.get_employee_bookings(user["id"])
            duplicate = any(
                b["booking_date"] == date_str
                and b["trip_type"] == trip_type
                and b["status"] not in ("cancelled",)
                for b in existing
            )
            if duplicate:
                st.error("❌ You already have an active booking for this date and trip type.")
            elif not pickup_location:
                st.error("❌ Please enter a pickup address.")
            else:
                ok, msg = db.create_booking(
                    user["id"], route["id"], shift["id"],
                    date_str, trip_type, pickup_location, drop_location, notes,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.balloons()
                else:
                    st.error(f"❌ {msg}")


# ── Employee: My bookings ──────────────────────────────────────────────────────
def emp_my_bookings(user):
    st.markdown(
        '<div class="mis-header"><h2>📋 My Bookings</h2></div>',
        unsafe_allow_html=True,
    )

    bookings = db.get_employee_bookings(user["id"])
    if not bookings:
        st.info("📭 You have no bookings yet.")
        return

    fc1, fc2 = st.columns(2)
    with fc1:
        sf = st.selectbox("Filter Status",
                          ["All", "pending", "confirmed", "in_progress", "completed", "cancelled"])
    with fc2:
        tf = st.selectbox("Filter Trip", ["All", "pickup", "drop"])

    filtered = [
        b for b in bookings
        if (sf == "All" or b["status"] == sf)
        and (tf == "All" or b["trip_type"] == tf)
    ]
    st.caption(f"{len(filtered)} booking(s) found")

    for b in filtered:
        trip_icon = "🏠→🏢" if b["trip_type"] == "pickup" else "🏢→🏠"
        label = (
            f"{STATUS_ICON.get(b['status'],'⚪')}  {b['booking_ref']}  |  "
            f"{trip_icon}  |  {b['booking_date']}  |  {b['status'].upper()}"
        )
        with st.expander(label):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Ref:** {b['booking_ref']}")
                st.write(f"**Date:** {b['booking_date']}")
                st.write(f"**Time:** {b['pickup_time']}")
                st.write(f"**Trip:** {b['trip_type'].upper()}")
            with c2:
                st.write(f"**Route:** {b.get('route_name','N/A')}")
                st.write(f"**Shift:** {b.get('shift_name','N/A')}")
                st.write(f"**Pickup:** {b.get('pickup_location','N/A')}")
                st.write(f"**Drop:** {b.get('drop_location','N/A')}")
            with c3:
                st.write(f"**Status:** {b['status'].upper()}")
                st.write(f"**Cab:** {b.get('cab_number','Not assigned')}")
                st.write(f"**Driver:** {b.get('driver_name','Not assigned')}")
                if b.get("driver_phone"):
                    st.write(f"**Driver Ph:** {b['driver_phone']}")

            if b["status"] == "pending":
                if st.button("❌ Cancel Booking", key=f"cancel_{b['id']}"):
                    if db.cancel_booking(b["id"], user["id"]):
                        st.success("Booking cancelled.")
                        st.rerun()
                    else:
                        st.error("Could not cancel booking.")


# ── Shared: Profile ────────────────────────────────────────────────────────────
def show_profile(user):
    st.markdown(
        '<div class="mis-header"><h2>👤 My Profile</h2></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 3])
    with c1:
        initial = user["name"][0].upper()
        st.markdown(
            f"""<div style="background:#1565C0;color:#fff;width:90px;height:90px;
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            font-size:2.5rem;margin:10px auto;">{initial}</div>""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='text-align:center;font-weight:bold'>{user['name']}</p>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown("#### Account Details")
        info = {
            "Employee ID": user.get("employee_id", "N/A"),
            "Full Name":   user["name"],
            "Email":       user["email"],
            "Phone":       user.get("phone", "N/A"),
            "Department":  user.get("department", "N/A"),
            "Office":      user.get("office_location", "N/A"),
            "Home Address":user.get("address", "N/A"),
            "Role":        user.get("role", "employee").upper(),
            "Member Since":str(user.get("created_at", "N/A"))[:10],
        }
        for k, v in info.items():
            st.write(f"**{k}:** {v}")


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def show_admin_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown("## ⚙️ Admin Panel")
        st.markdown(f"**{user['name']}**")
        st.caption("Administrator")
        st.markdown("---")
        menu = st.radio(
            "Menu",
            ["📊 Overview",
             "📋 All Bookings",
             "👥 Employees",
             "🚗 Fleet / Cabs",
             "🗺️ Routes",
             "👨‍💼 Drivers",
             "⏰ Shifts"],
            key="admin_menu",
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    pages = {
        "📊 Overview":     admin_overview,
        "📋 All Bookings": admin_all_bookings,
        "👥 Employees":    admin_employees,
        "🚗 Fleet / Cabs": admin_cabs,
        "🗺️ Routes":       admin_routes,
        "👨‍💼 Drivers":     admin_drivers,
        "⏰ Shifts":       admin_shifts,
    }
    pages[menu](user)


# ── Admin: Overview ────────────────────────────────────────────────────────────
def admin_overview(user):
    st.markdown(
        '<div class="mis-header"><h2>📊 Admin Overview</h2>'
        f"<p>Welcome, {user['name']}</p></div>",
        unsafe_allow_html=True,
    )

    s = db.get_booking_stats()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Employees",      s["total_employees"])
    m2.metric("🚗 Active Cabs",    s["active_cabs"])
    m3.metric("👨‍💼 Drivers",       s["total_drivers"])
    m4.metric("📅 Today Bookings", s["today_bookings"])

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Booking Status Breakdown")
        breakdown = pd.DataFrame({
            "Status": ["Pending", "Confirmed", "In Progress", "Completed", "Cancelled"],
            "Count":  [s["pending"], s["confirmed"], s["in_progress"], s["completed"], s["cancelled"]],
        })
        st.bar_chart(breakdown.set_index("Status"), color="#1565C0")

    with c2:
        st.markdown("### Monthly Trend (last 6 months)")
        trend = db.get_monthly_booking_trend()
        if trend:
            df_trend = pd.DataFrame(trend)
            st.line_chart(df_trend.set_index("month"), color="#1565C0")
        else:
            st.info("No booking data yet.")

    st.markdown("---")
    st.markdown("### 🕐 Latest 10 Bookings")
    recent = db.get_all_bookings()[:10]
    if recent:
        df = pd.DataFrame(recent)[
            ["booking_ref", "employee_name", "booking_date", "trip_type", "route_name", "status"]
        ]
        df.columns = ["Ref", "Employee", "Date", "Trip", "Route", "Status"]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Admin: All Bookings ────────────────────────────────────────────────────────
def admin_all_bookings(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>📋 All Bookings</h2></div>',
        unsafe_allow_html=True,
    )

    bookings = db.get_all_bookings()
    if not bookings:
        st.info("No bookings in the system yet.")
        return

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        sf = st.selectbox("Status",
                          ["All", "pending", "confirmed", "in_progress", "completed", "cancelled"])
    with fc2:
        date_f = st.date_input("Date", value=None)
    with fc3:
        search = st.text_input("Search employee name")

    filtered = [
        b for b in bookings
        if (sf == "All" or b["status"] == sf)
        and (not date_f or b["booking_date"] == date_f.strftime("%Y-%m-%d"))
        and (not search or search.lower() in (b.get("employee_name") or "").lower())
    ]
    st.caption(f"{len(filtered)} booking(s)")

    if filtered:
        show_cols = ["booking_ref", "employee_name", "emp_code", "booking_date",
                     "pickup_time", "trip_type", "route_name", "cab_number",
                     "driver_name", "status"]
        avail = [c for c in show_cols if c in filtered[0]]
        df = pd.DataFrame(filtered)[avail]
        df.columns = [c.replace("_", " ").title() for c in avail]
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️ Update Booking Status")
        uc1, uc2, uc3 = st.columns(3)
        with uc1:
            refs = [b["booking_ref"] for b in filtered]
            sel_ref = st.selectbox("Select Booking Ref", refs)
        with uc2:
            new_status = st.selectbox("New Status",
                                      ["pending", "confirmed", "in_progress", "completed", "cancelled"])
        with uc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Update Status", type="primary", use_container_width=True):
                target = next((b for b in filtered if b["booking_ref"] == sel_ref), None)
                if target:
                    db.update_booking_status(target["id"], new_status)
                    st.success(f"✅ {sel_ref} → {new_status}")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 🚗 Assign Cab to Unassigned Booking")
        unassigned = [b for b in filtered if not b.get("cab_number")]
        cabs = db.get_all_cabs()
        active_cabs = [c for c in cabs if c["is_active"]]
        if unassigned and active_cabs:
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                sel_b = st.selectbox("Unassigned Booking", [b["booking_ref"] for b in unassigned])
            with ac2:
                sel_c = st.selectbox("Assign Cab",
                                     [f"{c['cab_number']} – {c['model']} ({c.get('driver_name','No driver')})"
                                      for c in active_cabs])
            with ac3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Assign Cab", type="primary", use_container_width=True):
                    booking = next(b for b in unassigned if b["booking_ref"] == sel_b)
                    cab_idx = [f"{c['cab_number']} – {c['model']} ({c.get('driver_name','No driver')})"
                               for c in active_cabs].index(sel_c)
                    db.assign_cab_to_booking(booking["id"], active_cabs[cab_idx]["id"])
                    st.success("✅ Cab assigned and booking confirmed.")
                    st.rerun()


# ── Admin: Employees ───────────────────────────────────────────────────────────
def admin_employees(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>👥 Employee Management</h2></div>',
        unsafe_allow_html=True,
    )
    employees = db.get_all_employees()
    st.caption(f"{len(employees)} registered employee(s)")
    if employees:
        df = pd.DataFrame(employees)
        cols = ["employee_id", "name", "email", "phone", "department", "office_location", "created_at"]
        avail = [c for c in cols if c in df.columns]
        df_show = df[avail].copy()
        df_show.columns = [c.replace("_", " ").title() for c in avail]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No employees registered yet.")


# ── Admin: Cabs ────────────────────────────────────────────────────────────────
def admin_cabs(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>🚗 Fleet Management</h2></div>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["📋 All Cabs", "➕ Add New Cab"])

    with tab1:
        cabs = db.get_all_cabs()
        if cabs:
            df = pd.DataFrame(cabs)
            cols = ["cab_number", "model", "cab_type", "capacity", "color", "driver_name", "is_active"]
            avail = [c for c in cols if c in df.columns]
            df_show = df[avail].copy()
            df_show.columns = [c.replace("_", " ").title() for c in avail]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("No cabs in the system.")

    with tab2:
        drivers = db.get_all_drivers()
        with st.form("add_cab_form"):
            c1, c2 = st.columns(2)
            with c1:
                cab_number = st.text_input("🔢 License Plate *", placeholder="KA01AB1234")
                cab_type   = st.selectbox("🚗 Type", ["sedan", "suv", "mini", "bus"])
                capacity   = st.number_input("👥 Capacity", 1, 50, 4)
            with c2:
                model = st.text_input("🚘 Model", placeholder="Toyota Innova")
                color = st.text_input("🎨 Color", placeholder="White")
                if drivers:
                    drv_map = {f"{d['name']}  ({d['employee_id']})": d["id"] for d in drivers}
                    drv_map["— No driver assigned —"] = None
                    sel_drv = st.selectbox("👨‍💼 Assign Driver", list(drv_map.keys()))
                    driver_id = drv_map[sel_drv]
                else:
                    st.warning("Add drivers first via Drivers menu.")
                    driver_id = None

            if st.form_submit_button("➕ Add Cab", type="primary", use_container_width=True):
                if not cab_number:
                    st.error("License plate is required.")
                else:
                    ok, msg = db.add_cab(cab_number, cab_type, capacity, driver_id, model, color)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ── Admin: Routes ──────────────────────────────────────────────────────────────
def admin_routes(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>🗺️ Route Management</h2></div>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["📋 All Routes", "➕ Add Route"])

    with tab1:
        routes = db.get_all_routes()
        if routes:
            df = pd.DataFrame(routes)[
                ["route_name", "pickup_area", "drop_area", "estimated_time", "distance_km"]
            ]
            df.columns = ["Route Name", "Pickup Area", "Drop Area", "Est. (min)", "Distance (km)"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No routes configured.")

    with tab2:
        with st.form("add_route_form"):
            c1, c2 = st.columns(2)
            with c1:
                rname   = st.text_input("Route Name *", placeholder="Route 6 – South East")
                pickup  = st.text_input("Pickup Area *", placeholder="Bannerghatta Road")
                drop    = st.text_input("Drop Area *",   placeholder="Electronic City")
            with c2:
                est_time = st.number_input("Est. Time (min)", 5, 300, 30)
                distance = st.number_input("Distance (km)", 0.1, 500.0, 15.0)

            if st.form_submit_button("➕ Add Route", type="primary", use_container_width=True):
                if not all([rname, pickup, drop]):
                    st.error("All fields are required.")
                else:
                    ok, msg = db.add_route(rname, pickup, drop, est_time, distance)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ── Admin: Drivers ─────────────────────────────────────────────────────────────
def admin_drivers(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>👨‍💼 Driver Management</h2></div>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["📋 All Drivers", "➕ Add Driver"])

    with tab1:
        drivers = db.get_all_drivers()
        if drivers:
            df = pd.DataFrame(drivers)
            cols = ["employee_id", "name", "email", "phone", "created_at"]
            avail = [c for c in cols if c in df.columns]
            df_show = df[avail].copy()
            df_show.columns = [c.replace("_", " ").title() for c in avail]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("No drivers added yet.")

    with tab2:
        with st.form("add_driver_form"):
            c1, c2 = st.columns(2)
            with c1:
                did    = st.text_input("Driver ID *", placeholder="DRV001")
                dname  = st.text_input("Full Name *",  placeholder="Rajesh Kumar")
                demail = st.text_input("Email *",      placeholder="rajesh@company.com")
            with c2:
                dphone = st.text_input("Phone *",      placeholder="9876543210")
                dpass  = st.text_input("Password",     type="password", value="driver@123")

            if st.form_submit_button("➕ Add Driver", type="primary", use_container_width=True):
                if not all([did, dname, demail, dphone]):
                    st.error("All fields are required.")
                else:
                    ok, msg = db.add_driver(dname, demail, dphone, dpass, did)
                    if ok:
                        st.success(f"✅ {msg}  (default pwd: driver@123)")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ── Admin: Shifts ──────────────────────────────────────────────────────────────
def admin_shifts(_user=None):
    st.markdown(
        '<div class="mis-header"><h2>⏰ Shift Management</h2></div>',
        unsafe_allow_html=True,
    )

    shifts = db.get_all_shifts()
    if shifts:
        df = pd.DataFrame(shifts)[
            ["shift_name", "shift_start", "shift_end", "pickup_time", "drop_time"]
        ]
        df.columns = ["Shift", "Start", "End", "Pickup Time", "Drop Time"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### ➕ Add Shift")
    with st.form("add_shift_form"):
        c1, c2 = st.columns(2)
        with c1:
            sname  = st.text_input("Shift Name *", placeholder="Evening Shift")
            sstart = st.time_input("Shift Start Time")
            send   = st.time_input("Shift End Time")
        with c2:
            ptime  = st.time_input("Cab Pickup Time (before shift)")
            dtime  = st.time_input("Cab Drop Time (after shift)")

        if st.form_submit_button("➕ Add Shift", type="primary", use_container_width=True):
            if not sname:
                st.error("Shift name is required.")
            else:
                ok, msg = db.add_shift(
                    sname,
                    sstart.strftime("%H:%M"), send.strftime("%H:%M"),
                    ptime.strftime("%H:%M"),  dtime.strftime("%H:%M"),
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# DRIVER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def show_driver_dashboard():
    user = st.session_state.user

    with st.sidebar:
        st.markdown("## 🚘 Driver Panel")
        st.markdown(f"**{user['name']}**")
        st.caption(f"Driver ID: {user.get('employee_id','')}")
        st.markdown("---")
        menu = st.radio(
            "Menu",
            ["📊 Dashboard", "📋 All My Trips", "👤 Profile"],
            key="driver_menu",
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    pages = {
        "📊 Dashboard":   driver_home,
        "📋 All My Trips": driver_all_trips,
        "👤 Profile":     show_profile,
    }
    pages[menu](user)


# ── Driver: Home ───────────────────────────────────────────────────────────────
def driver_home(user):
    st.markdown(
        f'<div class="mis-header"><h2>🚘 Driver Dashboard</h2>'
        f"<p>Welcome, {user['name']}!</p></div>",
        unsafe_allow_html=True,
    )

    trips = db.get_driver_bookings(user["id"])
    today_str = date.today().strftime("%Y-%m-%d")
    today_trips    = [t for t in trips if t["booking_date"] == today_str]
    upcoming_trips = [
        t for t in trips
        if t["booking_date"] > today_str and t["status"] not in ("cancelled", "completed")
    ]

    m1, m2, m3 = st.columns(3)
    m1.metric("📅 Today's Trips", len(today_trips))
    m2.metric("📆 Upcoming",      len(upcoming_trips))
    m3.metric("✅ Completed",     sum(1 for t in trips if t["status"] == "completed"))

    if today_trips:
        st.markdown("---")
        st.markdown("### 📅 Today's Assignments")
        for t in today_trips:
            trip_icon = "🏠→🏢" if t["trip_type"] == "pickup" else "🏢→🏠"
            with st.expander(
                f"{STATUS_ICON.get(t['status'],'⚪')}  {trip_icon}  "
                f"{t.get('employee_name','Passenger')}  |  {t['pickup_time']}  |  {t['status'].upper()}"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Passenger:** {t.get('employee_name','N/A')}")
                    st.write(f"**Phone:** {t.get('employee_phone','N/A')}")
                    st.write(f"**Route:** {t.get('route_name','N/A')}")
                    st.write(f"**Booking Ref:** {t['booking_ref']}")
                with c2:
                    st.write(f"**Pickup:** {t.get('pickup_location') or t.get('pickup_area','N/A')}")
                    st.write(f"**Drop:** {t.get('drop_location') or t.get('drop_area','N/A')}")
                    st.write(f"**Status:** {t['status'].upper()}")

                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if t["status"] == "confirmed":
                        if st.button("🚦 Start Trip", key=f"start_{t['id']}", type="primary"):
                            db.update_booking_status(t["id"], "in_progress")
                            st.success("Trip started! Safe driving 🚗")
                            st.rerun()
                with btn_c2:
                    if t["status"] == "in_progress":
                        if st.button("✅ Mark Completed", key=f"done_{t['id']}", type="primary"):
                            db.update_booking_status(t["id"], "completed")
                            st.success("Trip marked as completed!")
                            st.rerun()
    else:
        st.info("📭 No trips assigned for today.")

    if upcoming_trips:
        st.markdown("---")
        st.markdown("### 📆 Upcoming Trips")
        df = pd.DataFrame(upcoming_trips)[
            ["booking_ref", "employee_name", "booking_date", "pickup_time", "trip_type",
             "route_name", "status"]
        ]
        df.columns = ["Ref", "Passenger", "Date", "Time", "Trip", "Route", "Status"]
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Driver: All Trips ──────────────────────────────────────────────────────────
def driver_all_trips(user):
    st.markdown(
        '<div class="mis-header"><h2>📋 All My Trips</h2></div>',
        unsafe_allow_html=True,
    )

    trips = db.get_driver_bookings(user["id"])
    if not trips:
        st.info("No trips assigned yet.")
        return

    sf = st.selectbox("Filter Status",
                      ["All", "pending", "confirmed", "in_progress", "completed", "cancelled"])
    filtered = trips if sf == "All" else [t for t in trips if t["status"] == sf]
    st.caption(f"{len(filtered)} trip(s)")

    for t in filtered:
        trip_icon = "🏠→🏢" if t["trip_type"] == "pickup" else "🏢→🏠"
        with st.expander(
            f"{STATUS_ICON.get(t['status'],'⚪')}  {t['booking_ref']}  |  "
            f"{trip_icon}  |  {t['booking_date']}  |  {t['status'].upper()}"
        ):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Passenger:** {t.get('employee_name','N/A')}")
                st.write(f"**Date:** {t['booking_date']}")
                st.write(f"**Time:** {t['pickup_time']}")
                st.write(f"**Route:** {t.get('route_name','N/A')}")
            with c2:
                st.write(f"**Pickup:** {t.get('pickup_location') or t.get('pickup_area','N/A')}")
                st.write(f"**Drop:** {t.get('drop_location') or t.get('drop_area','N/A')}")
                st.write(f"**Status:** {t['status'].upper()}")

            bc1, bc2 = st.columns(2)
            with bc1:
                if t["status"] == "confirmed":
                    if st.button("🚦 Start", key=f"s_{t['id']}", type="primary"):
                        db.update_booking_status(t["id"], "in_progress")
                        st.rerun()
            with bc2:
                if t["status"] == "in_progress":
                    if st.button("✅ Complete", key=f"c_{t['id']}", type="primary"):
                        db.update_booking_status(t["id"], "completed")
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    user = st.session_state.user
    page = st.session_state.page

    if user is None:
        route_map = {
            "home":     show_home,
            "login":    show_login,
            "register": show_register,
        }
        route_map.get(page, show_home)()
    else:
        role_map = {
            "admin":  show_admin_dashboard,
            "driver": show_driver_dashboard,
        }
        role_map.get(user["role"], show_employee_dashboard)()


main()
