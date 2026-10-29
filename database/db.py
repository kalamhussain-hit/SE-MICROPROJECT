import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "lost_found.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db_connection(db_path=None):
    """Establish and return an active SQLite database connection with row access."""
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path=None):
    """Initialize database tables using schema.sql."""
    conn = get_db_connection(db_path)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def seed_sample_data(db_path=None):
    """Seed the database with initial users, items, and claims for testing."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Check if users already exist
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    if cursor.fetchone()["count"] > 0:
        print("Database already contains data. Skipping sample seeding.")
        conn.close()
        return

    # Seed Users
    users_data = [
        ("Campus Administrator", "admin@campus.edu", generate_password_hash("Admin@123"), "admin"),
        ("Rahul Sharma", "rahul@campus.edu", generate_password_hash("Student@123"), "student"),
        ("Priya Patel", "priya@campus.edu", generate_password_hash("Student@123"), "student")
    ]
    cursor.executemany(
        "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        users_data
    )
    admin_id = 1
    rahul_id = 2
    priya_id = 3

    # Seed Items
    items_data = [
        (
            "College ID Card",
            "Blue ribbon lanyard with HIT student ID card in transparent holder. Roll No: CS-2024-042.",
            "Cards & ID",
            "Library 2nd Floor Reading Hall",
            "2026-10-20",
            "Lost",
            rahul_id,
            "Verified"
        ),
        (
            "Laptop Charger",
            "Black 65W Dell Type-C adapter with blue Velcro cable tie found plugged near station 14.",
            "Electronics",
            "Computer Science Lab 3",
            "2026-10-21",
            "Found",
            rahul_id,
            "Verified"
        ),
        (
            "Stainless Steel Water Bottle",
            "Milton 750ml silver stainless steel water bottle with slight dent on the base.",
            "Personal Belongings",
            "Cafeteria Ground Floor Table 5",
            "2026-10-22",
            "Lost",
            priya_id,
            "Pending"
        ),
        (
            "Software Engineering Notebook",
            "Spiral-bound Classmate notebook containing handwritten notes on SDLC and UML diagrams.",
            "Books & Stationery",
            "Seminar Hall B Row 4",
            "2026-10-23",
            "Found",
            priya_id,
            "Pending"
        ),
        (
            "Wireless Earphones",
            "White AirPods Pro in black silicone protective case with small silver carabiner.",
            "Electronics",
            "Campus Sports Ground Bleachers",
            "2026-10-24",
            "Found",
            priya_id,
            "Returned"
        )
    ]
    cursor.executemany(
        """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        items_data
    )

    # Seed Claims
    claims_data = [
        (2, rahul_id, "This is my Dell 65W adapter; I misplaced it during the afternoon lab session on Tuesday.", "Pending"),
        (5, priya_id, "These AirPods Pro match my lost pair; the black silicone case has my initials engraved inside.", "Approved")
    ]
    cursor.executemany(
        """INSERT INTO claims (item_id, user_id, message, status)
           VALUES (?, ?, ?, ?)""",
        claims_data
    )

    conn.commit()
    conn.close()
    print("Sample data seeded successfully.")


if __name__ == "__main__":
    init_db()
    seed_sample_data()
