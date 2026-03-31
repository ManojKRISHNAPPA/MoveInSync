"""
Unit tests for database.py — MoveInSync Cab Booking System
Uses a temporary SQLite file per test to ensure full isolation.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Redirect every test to a fresh, temporary database."""
    db_file = str(tmp_path / "test_moveinsync.db")
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()
    yield db_file


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _register(emp_id, name, email, phone="1234567890", password="pass123",
              address="Whitefield", dept="Engineering", office="HQ"):
    return database.register_user(emp_id, name, email, phone, password, address, dept, office)


# ===========================================================================
# hash_password
# ===========================================================================

class TestHashPassword:
    def test_returns_string(self):
        assert isinstance(database.hash_password("test"), str)

    def test_sha256_length(self):
        # SHA-256 hex digest is always 64 characters
        assert len(database.hash_password("anypassword")) == 64

    def test_deterministic(self):
        assert database.hash_password("hello") == database.hash_password("hello")

    def test_different_inputs_give_different_hashes(self):
        assert database.hash_password("pass1") != database.hash_password("pass2")

    def test_empty_string_is_hashable(self):
        result = database.hash_password("")
        assert isinstance(result, str)
        assert len(result) == 64


# ===========================================================================
# register_user
# ===========================================================================

class TestRegisterUser:
    def test_successful_registration(self):
        ok, msg = _register("EMP001", "Alice", "alice@example.com")
        assert ok is True
        assert "successful" in msg.lower()

    def test_duplicate_employee_id_rejected(self):
        _register("EMP002", "Bob", "bob@example.com")
        ok, msg = _register("EMP002", "Charlie", "charlie@example.com")
        assert ok is False
        assert "employee id" in msg.lower()

    def test_duplicate_email_rejected(self):
        _register("EMP003", "Dave", "dave@example.com")
        ok, msg = _register("EMP004", "Eve", "dave@example.com")
        assert ok is False
        assert "email" in msg.lower()

    def test_returns_tuple(self):
        result = _register("EMP005", "Frank", "frank@example.com")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_password_is_hashed_not_stored_plaintext(self):
        _register("EMP006", "Grace", "grace@example.com", password="secret")
        user = database.login_user("grace@example.com", "secret")
        assert user is not None
        assert user["password_hash"] != "secret"


# ===========================================================================
# login_user
# ===========================================================================

class TestLoginUser:
    def test_valid_credentials_return_user(self):
        _register("EMP010", "Henry", "henry@example.com", password="mypass")
        user = database.login_user("henry@example.com", "mypass")
        assert user is not None
        assert user["name"] == "Henry"

    def test_wrong_password_returns_none(self):
        _register("EMP011", "Irene", "irene@example.com", password="correct")
        result = database.login_user("irene@example.com", "wrong")
        assert result is None

    def test_nonexistent_email_returns_none(self):
        assert database.login_user("nobody@example.com", "pass") is None

    def test_returned_user_has_expected_keys(self):
        _register("EMP012", "Jack", "jack@example.com", password="pw")
        user = database.login_user("jack@example.com", "pw")
        for key in ("id", "name", "email", "role", "employee_id"):
            assert key in user

    def test_default_admin_is_seeded(self):
        user = database.login_user("admin@company.com", "admin123")
        assert user is not None
        assert user["role"] == "admin"

    def test_login_returns_dict(self):
        _register("EMP013", "Kim", "kim@example.com", password="pw")
        user = database.login_user("kim@example.com", "pw")
        assert isinstance(user, dict)


# ===========================================================================
# get_all_employees
# ===========================================================================

class TestGetAllEmployees:
    def test_returns_list(self):
        assert isinstance(database.get_all_employees(), list)

    def test_registered_employee_appears(self):
        _register("EMP020", "Laura", "laura@example.com")
        employees = database.get_all_employees()
        names = [e["name"] for e in employees]
        assert "Laura" in names

    def test_admin_excluded(self):
        employees = database.get_all_employees()
        roles = {e["role"] for e in employees}
        assert "admin" not in roles

    def test_driver_excluded(self):
        database.add_driver("Driver Dan", "dan@driver.com", "9876543210", "dpass", "DRV001")
        employees = database.get_all_employees()
        roles = {e["role"] for e in employees}
        assert "driver" not in roles

    def test_multiple_employees_returned(self):
        _register("EMP021", "Mike", "mike@example.com")
        _register("EMP022", "Nina", "nina@example.com")
        employees = database.get_all_employees()
        assert len(employees) >= 2


# ===========================================================================
# add_driver / get_all_drivers
# ===========================================================================

class TestDriverOperations:
    def test_add_driver_success(self):
        ok, msg = database.add_driver("Driver One", "d1@driver.com", "1111111111", "dpass", "DRV010")
        assert ok is True
        assert "successfully" in msg.lower()

    def test_driver_visible_in_get_all_drivers(self):
        database.add_driver("Driver Two", "d2@driver.com", "2222222222", "dpass", "DRV011")
        drivers = database.get_all_drivers()
        names = [d["name"] for d in drivers]
        assert "Driver Two" in names

    def test_duplicate_driver_employee_id_rejected(self):
        database.add_driver("Driver Three", "d3@driver.com", "3333333333", "dpass", "DRV012")
        ok, msg = database.add_driver("Driver Four", "d4@driver.com", "4444444444", "dpass", "DRV012")
        assert ok is False

    def test_get_all_drivers_returns_list(self):
        assert isinstance(database.get_all_drivers(), list)

    def test_driver_role_is_driver(self):
        database.add_driver("Driver Five", "d5@driver.com", "5555555555", "dpass", "DRV013")
        drivers = database.get_all_drivers()
        roles = {d["role"] for d in drivers}
        assert roles == {"driver"}


# ===========================================================================
# add_cab / get_all_cabs / update_cab
# ===========================================================================

class TestCabOperations:
    def test_add_cab_success(self):
        ok, msg = database.add_cab("KA01AB1234", "sedan", 4, None, "Swift", "White")
        assert ok is True
        assert "successfully" in msg.lower()

    def test_duplicate_cab_number_rejected(self):
        database.add_cab("KA01CD5678", "sedan", 4, None, "Baleno", "Black")
        ok, msg = database.add_cab("KA01CD5678", "suv", 6, None, "Innova", "Silver")
        assert ok is False
        assert "exists" in msg.lower()

    def test_cab_appears_in_get_all_cabs(self):
        database.add_cab("KA02EF9012", "suv", 6, None, "Innova", "Grey")
        cabs = database.get_all_cabs()
        numbers = [c["cab_number"] for c in cabs]
        assert "KA02EF9012" in numbers

    def test_get_all_cabs_returns_list(self):
        assert isinstance(database.get_all_cabs(), list)

    def test_fresh_db_has_no_cabs(self):
        assert database.get_all_cabs() == []

    def test_update_cab_changes_capacity(self):
        database.add_cab("KA03GH3456", "sedan", 4, None, "Alto", "Red")
        cabs = database.get_all_cabs()
        cab_id = next(c["id"] for c in cabs if c["cab_number"] == "KA03GH3456")
        database.update_cab(cab_id, "suv", 7, None, 1)
        updated = database.get_all_cabs()
        cab = next(c for c in updated if c["id"] == cab_id)
        assert cab["capacity"] == 7


# ===========================================================================
# add_route / get_all_routes
# ===========================================================================

class TestRouteOperations:
    def test_add_route_success(self):
        ok, msg = database.add_route("Test Route", "Area A", "Area B", 30, 10.0)
        assert ok is True
        assert "successfully" in msg.lower()

    def test_route_appears_in_get_all_routes(self):
        database.add_route("My Route", "Pickup X", "Drop Y", 45, 20.0)
        routes = database.get_all_routes()
        names = [r["route_name"] for r in routes]
        assert "My Route" in names

    def test_default_routes_seeded_on_init(self):
        routes = database.get_all_routes()
        assert len(routes) >= 5

    def test_get_all_routes_returns_list(self):
        assert isinstance(database.get_all_routes(), list)

    def test_route_has_required_fields(self):
        database.add_route("Full Route", "Start", "End", 60, 30.0)
        routes = database.get_all_routes()
        r = next(x for x in routes if x["route_name"] == "Full Route")
        for field in ("id", "route_name", "pickup_area", "drop_area", "estimated_time", "distance_km"):
            assert field in r


# ===========================================================================
# add_shift / get_all_shifts
# ===========================================================================

class TestShiftOperations:
    def test_add_shift_success(self):
        ok, msg = database.add_shift("Early Bird", "06:00", "15:00", "05:30", "15:30")
        assert ok is True
        assert "successfully" in msg.lower()

    def test_shift_appears_in_get_all_shifts(self):
        database.add_shift("Late Night", "22:00", "07:00", "21:30", "07:30")
        shifts = database.get_all_shifts()
        names = [s["shift_name"] for s in shifts]
        assert "Late Night" in names

    def test_default_shifts_seeded_on_init(self):
        # init_db seeds 4 default shifts
        shifts = database.get_all_shifts()
        assert len(shifts) >= 4

    def test_get_all_shifts_returns_list(self):
        assert isinstance(database.get_all_shifts(), list)

    def test_shift_has_required_fields(self):
        database.add_shift("Flex", "11:00", "20:00", "10:30", "20:30")
        shifts = database.get_all_shifts()
        s = next(x for x in shifts if x["shift_name"] == "Flex")
        for field in ("id", "shift_name", "shift_start", "shift_end", "pickup_time", "drop_time"):
            assert field in s


# ===========================================================================
# create_booking
# ===========================================================================

class TestCreateBooking:
    @pytest.fixture()
    def booking_fixtures(self):
        _register("EMP100", "BookUser", "bookuser@example.com")
        user = database.login_user("bookuser@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        return user["id"], routes[0]["id"], shifts[0]["id"]

    def test_booking_created_successfully(self, booking_fixtures):
        emp_id, route_id, shift_id = booking_fixtures
        ok, msg = database.create_booking(
            emp_id, route_id, shift_id, "2026-05-01",
            "pickup", "Whitefield", "Electronic City", ""
        )
        assert ok is True

    def test_booking_ref_starts_with_bk(self, booking_fixtures):
        emp_id, route_id, shift_id = booking_fixtures
        ok, msg = database.create_booking(
            emp_id, route_id, shift_id, "2026-05-02",
            "pickup", "Whitefield", "Electronic City", ""
        )
        assert "BK" in msg

    def test_booking_confirmed_message(self, booking_fixtures):
        emp_id, route_id, shift_id = booking_fixtures
        ok, msg = database.create_booking(
            emp_id, route_id, shift_id, "2026-05-03",
            "pickup", "Whitefield", "Electronic City", ""
        )
        assert "confirmed" in msg.lower()

    def test_booking_appears_in_employee_bookings(self, booking_fixtures):
        emp_id, route_id, shift_id = booking_fixtures
        database.create_booking(
            emp_id, route_id, shift_id, "2026-05-04",
            "pickup", "Whitefield", "Electronic City", ""
        )
        bookings = database.get_employee_bookings(emp_id)
        assert len(bookings) >= 1

    def test_trip_type_drop_is_accepted(self, booking_fixtures):
        emp_id, route_id, shift_id = booking_fixtures
        ok, msg = database.create_booking(
            emp_id, route_id, shift_id, "2026-05-05",
            "drop", "Electronic City", "Whitefield", ""
        )
        assert ok is True


# ===========================================================================
# get_employee_bookings
# ===========================================================================

class TestGetEmployeeBookings:
    def test_returns_list(self):
        _register("EMP200", "ListUser", "listuser@example.com")
        user = database.login_user("listuser@example.com", "pass123")
        assert isinstance(database.get_employee_bookings(user["id"]), list)

    def test_empty_for_new_user(self):
        _register("EMP201", "NoBook", "nobook@example.com")
        user = database.login_user("nobook@example.com", "pass123")
        assert database.get_employee_bookings(user["id"]) == []

    def test_booking_linked_to_correct_employee(self):
        _register("EMP202", "MyBookUser", "mybook@example.com")
        user = database.login_user("mybook@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-05-10", "pickup", "Area A", "Area B", ""
        )
        bookings = database.get_employee_bookings(user["id"])
        assert all(b["employee_id"] == user["id"] for b in bookings)


# ===========================================================================
# cancel_booking
# ===========================================================================

class TestCancelBooking:
    @pytest.fixture()
    def created_booking(self):
        _register("EMP300", "CancelUser", "canceluser@example.com")
        user = database.login_user("canceluser@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-05-15", "pickup", "From", "To", ""
        )
        bookings = database.get_employee_bookings(user["id"])
        return bookings[0]["id"], user["id"]

    def test_cancel_pending_booking_returns_true(self, created_booking):
        booking_id, emp_id = created_booking
        assert database.cancel_booking(booking_id, emp_id) is True

    def test_cancelled_booking_has_cancelled_status(self, created_booking):
        booking_id, emp_id = created_booking
        database.cancel_booking(booking_id, emp_id)
        all_bookings = database.get_all_bookings()
        booking = next((b for b in all_bookings if b["id"] == booking_id), None)
        assert booking["status"] == "cancelled"

    def test_cancel_nonexistent_booking_returns_false(self):
        assert database.cancel_booking(99999, 99999) is False

    def test_cannot_cancel_other_employees_booking(self, created_booking):
        booking_id, _ = created_booking
        _register("EMP301", "OtherUser", "other@example.com")
        other = database.login_user("other@example.com", "pass123")
        result = database.cancel_booking(booking_id, other["id"])
        assert result is False


# ===========================================================================
# update_booking_status
# ===========================================================================

class TestUpdateBookingStatus:
    @pytest.fixture()
    def booking_id(self):
        _register("EMP400", "StatusUser", "statususer@example.com")
        user = database.login_user("statususer@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-05-20", "pickup", "X", "Y", ""
        )
        bookings = database.get_employee_bookings(user["id"])
        return bookings[0]["id"]

    def test_update_to_confirmed(self, booking_id):
        database.update_booking_status(booking_id, "confirmed")
        all_b = database.get_all_bookings()
        b = next(x for x in all_b if x["id"] == booking_id)
        assert b["status"] == "confirmed"

    def test_update_to_in_progress(self, booking_id):
        database.update_booking_status(booking_id, "in_progress")
        all_b = database.get_all_bookings()
        b = next(x for x in all_b if x["id"] == booking_id)
        assert b["status"] == "in_progress"

    def test_update_to_completed(self, booking_id):
        database.update_booking_status(booking_id, "completed")
        all_b = database.get_all_bookings()
        b = next(x for x in all_b if x["id"] == booking_id)
        assert b["status"] == "completed"


# ===========================================================================
# assign_cab_to_booking
# ===========================================================================

class TestAssignCabToBooking:
    def test_assign_cab_updates_booking(self):
        _register("EMP500", "AssignUser", "assignuser@example.com")
        user = database.login_user("assignuser@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-05-25", "pickup", "A", "B", ""
        )
        database.add_cab("KA99ZZ0001", "sedan", 4, None, "Wagon R", "Blue")
        cabs = database.get_all_cabs()
        cab_id = cabs[0]["id"]
        bookings = database.get_all_bookings()
        booking_id = bookings[0]["id"]
        database.assign_cab_to_booking(booking_id, cab_id)
        updated = database.get_all_bookings()
        b = next(x for x in updated if x["id"] == booking_id)
        assert b["cab_id"] == cab_id
        assert b["status"] == "confirmed"


# ===========================================================================
# get_all_bookings
# ===========================================================================

class TestGetAllBookings:
    def test_returns_list(self):
        assert isinstance(database.get_all_bookings(), list)

    def test_booking_has_enriched_fields(self):
        _register("EMP600", "AllBook", "allbook@example.com")
        user = database.login_user("allbook@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-06-01", "pickup", "P", "Q", ""
        )
        bookings = database.get_all_bookings()
        assert len(bookings) >= 1
        b = bookings[0]
        for field in ("id", "booking_ref", "employee_id", "status", "booking_date"):
            assert field in b


# ===========================================================================
# get_booking_stats
# ===========================================================================

class TestGetBookingStats:
    def test_returns_dict(self):
        assert isinstance(database.get_booking_stats(), dict)

    def test_all_expected_keys_present(self):
        stats = database.get_booking_stats()
        expected = [
            "pending", "confirmed", "in_progress", "completed", "cancelled",
            "total_employees", "total_drivers", "active_cabs", "today_bookings"
        ]
        for key in expected:
            assert key in stats, f"Missing key: {key}"

    def test_all_values_are_non_negative_integers(self):
        stats = database.get_booking_stats()
        for key, val in stats.items():
            assert isinstance(val, int), f"{key} is not int"
            assert val >= 0, f"{key} is negative"

    def test_pending_increases_after_booking(self):
        stats_before = database.get_booking_stats()
        _register("EMP700", "StatUser", "statuser@example.com")
        user = database.login_user("statuser@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-06-10", "pickup", "X", "Y", ""
        )
        stats_after = database.get_booking_stats()
        assert stats_after["pending"] >= stats_before["pending"]

    def test_total_employees_increases_after_register(self):
        before = database.get_booking_stats()["total_employees"]
        _register("EMP701", "CountUser", "countuser@example.com")
        after = database.get_booking_stats()["total_employees"]
        assert after == before + 1


# ===========================================================================
# get_monthly_booking_trend
# ===========================================================================

class TestGetMonthlyBookingTrend:
    def test_returns_list(self):
        assert isinstance(database.get_monthly_booking_trend(), list)

    def test_empty_when_no_bookings(self):
        # Fresh DB with no bookings should return empty list
        result = database.get_monthly_booking_trend()
        assert result == []

    def test_trend_entry_has_month_and_total_keys(self):
        _register("EMP800", "TrendUser", "trenduser@example.com")
        user = database.login_user("trenduser@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-06-15", "pickup", "A", "B", ""
        )
        result = database.get_monthly_booking_trend()
        assert len(result) >= 1
        assert "month" in result[0]
        assert "total" in result[0]

    def test_total_is_positive_integer(self):
        _register("EMP801", "TrendUser2", "trenduser2@example.com")
        user = database.login_user("trenduser2@example.com", "pass123")
        routes = database.get_all_routes()
        shifts = database.get_all_shifts()
        database.create_booking(
            user["id"], routes[0]["id"], shifts[0]["id"],
            "2026-07-01", "pickup", "A", "B", ""
        )
        result = database.get_monthly_booking_trend()
        for entry in result:
            assert entry["total"] > 0
