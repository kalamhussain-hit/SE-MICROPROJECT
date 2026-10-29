import os
import sys
import tempfile
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database.db import init_db, seed_sample_data, get_db_connection


@pytest.fixture
def client():
    """Create and configure a testing client with an isolated temporary SQLite database."""
    db_fd, db_path = tempfile.mkstemp()
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.app_context():
        init_db(db_path)
        seed_sample_data(db_path)

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)


# ---------------------------------------------------------------------------
# Positive Testing
# ---------------------------------------------------------------------------
def test_home_page(client):
    """TC-P1: Landing page loads with status 200 and portal title."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Smart Lost &amp; Found Portal" in response.data or b"CampusLost&amp;Found" in response.data or b"Campus" in response.data


def test_valid_registration(client):
    """TC-01: Valid user registration."""
    response = client.post("/register", data={
        "name": "Ananya Sen",
        "email": "ananya@campus.edu",
        "password": "Password@123",
        "confirm_password": "Password@123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    # Verify user in DB with hashed password
    conn = get_db_connection(app.config["DATABASE"])
    user = conn.execute("SELECT * FROM users WHERE email = 'ananya@campus.edu'").fetchone()
    conn.close()
    assert user is not None
    assert user["name"] == "Ananya Sen"
    assert user["password"] != "Password@123"  # Must be hashed!
    assert user["password"].startswith("scrypt:") or user["password"].startswith("pbkdf2:")


def test_valid_student_login(client):
    """TC-04: Valid student login."""
    response = client.post("/login", data={
        "email": "rahul@campus.edu",
        "password": "Student@123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back, Rahul Sharma" in response.data
    assert b"Student Dashboard" in response.data


def test_valid_admin_login(client):
    """TC-A1: Valid admin login redirects to /admin."""
    response = client.post("/login", data={
        "email": "admin@campus.edu",
        "password": "Admin@123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Campus Lost &amp; Found Control Panel" in response.data


def test_logout(client):
    """TC-L1: User logout clears session."""
    # Login first
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"logged out successfully" in response.data


def test_valid_item_report(client):
    """TC-06: Valid item report creation."""
    # Login as student
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    response = client.post("/report", data={
        "title": "Scientific Calculator",
        "description": "Casio fx-991EX ClassWiz scientific calculator left on desk in Hall 2.",
        "category": "Electronics",
        "location": "Lecture Hall 2",
        "date": "2026-10-23",
        "item_type": "Lost"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"has been submitted for admin verification" in response.data

    # Verify status is 'Pending' in DB
    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute("SELECT * FROM items WHERE title = 'Scientific Calculator'").fetchone()
    conn.close()
    assert item is not None
    assert item["status"] == "Pending"
    assert item["category"] == "Electronics"


def test_search_existing_item(client):
    """TC-07: Search existing item returns matches."""
    response = client.get("/items?q=Charger")
    assert response.status_code == 200
    assert b"Laptop Charger" in response.data


def test_search_nonexistent_item(client):
    """TC-08: Search nonexistent item returns empty state."""
    response = client.get("/items?q=NonExistentItemXYZ12345")
    assert response.status_code == 200
    assert b"No matching items found" in response.data


def test_view_item_details(client):
    """TC-D1: View item details page."""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert b"College ID Card" in response.data
    assert b"Library 2nd Floor Reading Hall" in response.data


def test_submit_valid_claim(client):
    """TC-09: Student submits valid ownership claim."""
    # Login as Priya (user_id 3)
    client.post("/login", data={"email": "priya@campus.edu", "password": "Student@123"})
    # Item 1 was reported by Rahul (user_id 2), status is Verified
    response = client.post("/claim/1", data={
        "message": "This is my ID card; Roll number matches CS-2024-042 with my departmental stamp."
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your claim has been submitted successfully" in response.data


def test_admin_verifies_item(client):
    """TC-12: Admin verifies a pending item."""
    # Login as admin
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    # Item 3 is Pending ("Stainless Steel Water Bottle")
    response = client.post("/admin/items/3/status", data={"status": "Verified"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"updated to &#39;Verified&#39;" in response.data or b"updated to 'Verified'" in response.data

    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute("SELECT status FROM items WHERE id = 3").fetchone()
    conn.close()
    assert item["status"] == "Verified"


def test_admin_rejects_item(client):
    """TC-13: Admin rejects an invalid report."""
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    response = client.post("/admin/items/4/status", data={"status": "Rejected"}, follow_redirects=True)
    assert response.status_code == 200

    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute("SELECT status FROM items WHERE id = 4").fetchone()
    conn.close()
    assert item["status"] == "Rejected"


def test_admin_approves_claim_and_marks_returned(client):
    """TC-14: Admin approves claim and marks item as returned."""
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    # Claim 1 is for item 2
    response = client.post("/admin/claims/1/status", data={
        "status": "Approved",
        "mark_returned": "yes"
    }, follow_redirects=True)
    assert response.status_code == 200

    conn = get_db_connection(app.config["DATABASE"])
    claim = conn.execute("SELECT status FROM claims WHERE id = 1").fetchone()
    item = conn.execute("SELECT status FROM items WHERE id = 2").fetchone()
    conn.close()
    assert claim["status"] == "Approved"
    assert item["status"] == "Returned"


def test_admin_rejects_claim(client):
    """TC-15: Admin rejects a claim."""
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    response = client.post("/admin/claims/1/status", data={"status": "Rejected"}, follow_redirects=True)
    assert response.status_code == 200

    conn = get_db_connection(app.config["DATABASE"])
    claim = conn.execute("SELECT status FROM claims WHERE id = 1").fetchone()
    conn.close()
    assert claim["status"] == "Rejected"


def test_mark_item_returned(client):
    """TC-16: Admin marks item as returned."""
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    response = client.post("/admin/items/1/status", data={"status": "Returned"}, follow_redirects=True)
    assert response.status_code == 200

    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute("SELECT status FROM items WHERE id = 1").fetchone()
    conn.close()
    assert item["status"] == "Returned"


# ---------------------------------------------------------------------------
# Negative Testing & Boundary Testing
# ---------------------------------------------------------------------------
def test_duplicate_email_registration(client):
    """TC-02: Duplicate email registration is blocked."""
    response = client.post("/register", data={
        "name": "Duplicate User",
        "email": "rahul@campus.edu",  # Already exists
        "password": "Password@123",
        "confirm_password": "Password@123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_invalid_login(client):
    """TC-03: Invalid login credentials blocked."""
    response = client.post("/login", data={
        "email": "rahul@campus.edu",
        "password": "WrongPassword999"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_empty_report_form(client):
    """TC-05: Empty report form submission is blocked."""
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    response = client.post("/report", data={
        "title": "",
        "description": "",
        "category": "",
        "location": "",
        "date": "",
        "item_type": ""
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Item title is required" in response.data


def test_empty_claim_message(client):
    """TC-10: Empty claim submission is blocked."""
    client.post("/login", data={"email": "priya@campus.edu", "password": "Student@123"})
    response = client.post("/claim/1", data={"message": "   "}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please provide sufficient proof details" in response.data


def test_unauthorized_admin_access(client):
    """TC-11: Student attempting to access admin route receives 403 Forbidden."""
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    response = client.get("/admin")
    assert response.status_code == 403
    assert b"Access Forbidden" in response.data


def test_unauthenticated_protected_route_redirect(client):
    """TC-U1: Unauthenticated user redirected to login when visiting protected pages."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_cannot_claim_own_item(client):
    """TC-C1: Student cannot submit a claim on their own reported item."""
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    # Item 1 was reported by Rahul
    response = client.get("/claim/1", follow_redirects=True)
    assert response.status_code == 200
    assert b"cannot submit an ownership claim on an item that you reported" in response.data


def test_cannot_claim_returned_item(client):
    """TC-C2: Cannot submit a claim on an already Returned item."""
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    # Item 5 is Returned
    response = client.get("/claim/5", follow_redirects=True)
    assert response.status_code == 200
    assert b"already been marked as returned" in response.data


def test_nonexistent_item_details_404(client):
    """TC-N1: Viewing nonexistent item ID returns 404."""
    response = client.get("/items/99999")
    assert response.status_code == 404
    assert b"Item Not Found" in response.data


def test_sql_injection_safety(client):
    """TC-SEC1: Search query with SQL injection string is safely parameterized."""
    response = client.get("/items?q=' OR 1=1 --")
    assert response.status_code == 200
    # Should not cause error and should safely return 0 results
    assert b"No matching items found" in response.data


# ---------------------------------------------------------------------------
# Smart Lost-Found Matching Tests (Positive, Negative, Boundary, Functional, Integration)
# ---------------------------------------------------------------------------
def test_smart_matching_algorithm_identical_items():
    """TC-SM-01 (Positive): Matching identical category, location, date, and description produces high score (>85%)."""
    from matching import calculate_match_details
    lost = {
        "title": "Casio fx-991EX Scientific Calculator",
        "category": "Electronics",
        "location": "Library 2nd Floor Reading Hall",
        "date": "2026-10-25",
        "description": "Black Casio ClassWiz scientific calculator left on study table with white sticker."
    }
    found = {
        "title": "Casio fx-991EX Scientific Calculator",
        "category": "Electronics",
        "location": "Library 2nd Floor Reading Hall",
        "date": "2026-10-25",
        "description": "Black Casio ClassWiz scientific calculator found on table in library reading hall."
    }
    score, breakdown, reason = calculate_match_details(lost, found)
    assert score >= 85.0
    assert breakdown["category"]["score"] == 100.0
    assert breakdown["location"]["score"] == 100.0
    assert breakdown["date"]["score"] == 100.0
    assert breakdown["description"]["score"] > 60.0


def test_smart_matching_algorithm_different_category():
    """TC-SM-02 (Negative): Different categories severely penalize match score."""
    from matching import calculate_match_details
    lost = {
        "title": "Calculus Textbook",
        "category": "Books & Stationery",
        "location": "Library 2nd Floor",
        "date": "2026-10-25",
        "description": "Thomas Calculus 14th edition hardbound book."
    }
    found = {
        "title": "Bluetooth Speaker",
        "category": "Electronics",
        "location": "Library 2nd Floor",
        "date": "2026-10-25",
        "description": "JBL wireless speaker cylindrical shape."
    }
    score, breakdown, _ = calculate_match_details(lost, found)
    assert breakdown["category"]["score"] == 0.0
    # Should not pass default match threshold of 50.0
    assert score < 50.0


def test_smart_matching_boundary_threshold():
    """TC-SM-03 (Boundary): Score filtering at and around 50.0% threshold."""
    from matching import find_matches_for_item
    item = {
        "id": 100,
        "item_type": "Lost",
        "reported_by": 10,
        "title": "Water Bottle",
        "category": "Personal Belongings",
        "location": "Campus Sports Ground",
        "date": "2026-10-20",
        "description": "Milton stainless steel silver bottle."
    }
    # Candidate with same category and same location and date
    candidate_pass = {
        "id": 101,
        "item_type": "Found",
        "reported_by": 11,
        "title": "Steel Flask Bottle",
        "category": "Personal Belongings",
        "location": "Campus Sports Ground",
        "date": "2026-10-20",
        "description": "Silver stainless flask."
    }
    # Candidate with different category, different location, distant date
    candidate_fail = {
        "id": 102,
        "item_type": "Found",
        "reported_by": 12,
        "title": "Umbrella",
        "category": "Other",
        "location": "Hostel Gate 3",
        "date": "2026-08-01",
        "description": "Black folding umbrella."
    }
    matches = find_matches_for_item(item, [candidate_pass, candidate_fail], threshold=50.0)
    assert len(matches) == 1
    assert matches[0]["candidate_item"]["id"] == 101
    assert matches[0]["score"] >= 50.0


def test_smart_matching_missing_and_invalid_data_handling():
    """TC-SM-04 (Validation/Error Handling): Robust handling of empty fields and malformed dates without crashing."""
    from matching import calculate_match_details
    lost = {
        "title": "",
        "category": None,
        "location": "",
        "date": "invalid-date-format",
        "description": ""
    }
    found = {
        "title": None,
        "category": "",
        "location": None,
        "date": None,
        "description": None
    }
    score, breakdown, reason = calculate_match_details(lost, found)
    assert score == 0.0
    assert breakdown["category"]["score"] == 0.0
    assert breakdown["location"]["score"] == 0.0
    assert breakdown["date"]["score"] == 0.0
    assert breakdown["description"]["score"] == 0.0
    assert "Invalid Date Format" in reason or "Unknown Date" in reason


def test_smart_matching_dashboard_display(client):
    """TC-SM-05 (Functional): Student dashboard renders Smart Matches section with explainable breakdown."""
    # Login as student rahul (id 2) who reported lost item #1 (College ID Card)
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    
    # Create a matching Found report reported by priya (id 3)
    conn = get_db_connection(app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
           VALUES ('College Identity Card', 'Found student ID card on blue lanyard in Library 2nd Floor reading hall.', 'Cards & ID', 'Library 2nd Floor Reading Hall', '2026-10-20', 'Found', 3, 'Verified')"""
    )
    conn.commit()
    conn.close()

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Smart Lost" in response.data or b"Smart Matches" in response.data
    assert b"College Identity Card" in response.data
    assert b"Match" in response.data
    assert b"Category" in response.data
    assert b"Location" in response.data


def test_smart_matching_item_details_display(client):
    """TC-SM-06 (Functional): Item details view displays potential matches of opposite type."""
    # Login as student
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    
    # Insert matching item
    conn = get_db_connection(app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
           VALUES ('Lost Dell Adapter', 'Misplaced 65W Dell Type-C adapter in CS Lab.', 'Electronics', 'Computer Science Lab 3', '2026-10-21', 'Lost', 3, 'Verified')"""
    )
    conn.commit()
    conn.close()

    # View Item #2 (Found Laptop Charger in CS Lab 3)
    response = client.get("/items/2")
    assert response.status_code == 200
    assert b"Potential Smart Matches" in response.data
    assert b"Lost Dell Adapter" in response.data
    assert b"Category" in response.data


def test_smart_matching_admin_visibility(client):
    """TC-SM-07 (Admin Integration): Admin control panel displays smart matches tab with cross-correlated items."""
    # Login as admin
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    
    # Add matching pair
    conn = get_db_connection(app.config["DATABASE"])
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
           VALUES ('Lost Scientific Calculator', 'Casio fx-991EX lost in Hall 2.', 'Electronics', 'Lecture Hall 2', '2026-10-22', 'Lost', 2, 'Verified')"""
    )
    cursor.execute(
        """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
           VALUES ('Found Scientific Calculator', 'Casio fx-991EX found on bench in Hall 2.', 'Electronics', 'Lecture Hall 2', '2026-10-22', 'Found', 3, 'Verified')"""
    )
    conn.commit()
    conn.close()

    response = client.get("/admin")
    assert response.status_code == 200
    assert b"Smart Matches" in response.data
    assert b"Automated Lost-Found Matches" in response.data
    assert b"Scientific Calculator" in response.data


def test_full_integration_flow_with_matching(client):
    """TC-SM-08 (End-to-End Integration): Report Lost -> Admin Verify -> Report Found -> Admin Verify -> Match Generated -> Claim -> Admin Approve & Return."""
    # Step 1: Student A (Rahul) reports Lost item
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    resp_report = client.post("/report", data={
        "title": "Smart Watch",
        "description": "Black silicone strap fitness tracker lost near basketball court.",
        "category": "Electronics",
        "location": "Basketball Court",
        "date": "2026-10-24",
        "item_type": "Lost"
    }, follow_redirects=True)
    assert resp_report.status_code == 200
    client.get("/logout")

    # Step 2: Admin verifies Student A's report
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    conn = get_db_connection(app.config["DATABASE"])
    lost_id = conn.execute("SELECT id FROM items WHERE title = 'Smart Watch'").fetchone()["id"]
    conn.close()
    client.post(f"/admin/items/{lost_id}/status", data={"status": "Verified"}, follow_redirects=True)
    client.get("/logout")

    # Step 3: Student B (Priya) reports matching Found item
    client.post("/login", data={"email": "priya@campus.edu", "password": "Student@123"})
    client.post("/report", data={
        "title": "Black Smart Watch",
        "description": "Black fitness tracker with silicone band picked up near basketball court bleachers.",
        "category": "Electronics",
        "location": "Basketball Court",
        "date": "2026-10-24",
        "item_type": "Found"
    }, follow_redirects=True)
    client.get("/logout")

    # Step 4: Admin verifies Student B's found item
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    conn = get_db_connection(app.config["DATABASE"])
    found_id = conn.execute("SELECT id FROM items WHERE title = 'Black Smart Watch'").fetchone()["id"]
    conn.close()
    client.post(f"/admin/items/{found_id}/status", data={"status": "Verified"}, follow_redirects=True)
    client.get("/logout")

    # Step 5: Student A (Rahul) checks dashboard, sees Smart Match, and claims the Found item
    client.post("/login", data={"email": "rahul@campus.edu", "password": "Student@123"})
    dash_resp = client.get("/dashboard")
    assert dash_resp.status_code == 200
    assert b"Black Smart Watch" in dash_resp.data

    # Step 6: Student A submits claim on found item
    claim_resp = client.post(f"/claim/{found_id}", data={
        "message": "This is my fitness tracker; has a small scratch on bottom left sensor and pin 1234."
    }, follow_redirects=True)
    assert claim_resp.status_code == 200
    assert b"claim has been submitted successfully" in claim_resp.data
    client.get("/logout")

    # Step 7: Admin reviews claim, approves it, and marks item returned
    client.post("/login", data={"email": "admin@campus.edu", "password": "Admin@123"})
    conn = get_db_connection(app.config["DATABASE"])
    claim_id = conn.execute("SELECT id FROM claims WHERE item_id = ? AND user_id = 2", (found_id,)).fetchone()["id"]
    conn.close()
    admin_action_resp = client.post(
        f"/admin/claims/{claim_id}/status",
        data={"status": "Approved", "mark_returned": "yes"},
        follow_redirects=True
    )
    assert admin_action_resp.status_code == 200

    # Step 8: Verify item is marked Returned in DB
    conn = get_db_connection(app.config["DATABASE"])
    item_status = conn.execute("SELECT status FROM items WHERE id = ?", (found_id,)).fetchone()["status"]
    conn.close()
    assert item_status == "Returned"

