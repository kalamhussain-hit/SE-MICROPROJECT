import os
import re
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection, init_db, seed_sample_data, DEFAULT_DB_PATH
from matching import (
    calculate_match_details,
    find_matches_for_item,
    DEFAULT_MATCH_THRESHOLD
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campus-lost-found-secret-key-se2026")
app.config["DATABASE"] = DEFAULT_DB_PATH

# ---------------------------------------------------------------------------
# Categories and Constants
# ---------------------------------------------------------------------------
VALID_CATEGORIES = [
    "Electronics",
    "Cards & ID",
    "Books & Stationery",
    "Personal Belongings",
    "Clothing",
    "Keys",
    "Other"
]

ITEM_STATUSES = ["Pending", "Verified", "Rejected", "Returned"]
CLAIM_STATUSES = ["Pending", "Approved", "Rejected"]


# ---------------------------------------------------------------------------
# Authentication & Authorization Helpers
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Administrator login required.", "warning")
            return redirect(url_for("login", next=request.path))
        if session.get("user_role") != "admin":
            return render_template(
                "error.html",
                error_code=403,
                error_title="Access Forbidden",
                error_message="You do not have administrative privileges to access this area."
            ), 403
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Retrieve current logged in user dict or None."""
    if "user_id" not in session:
        return None
    conn = get_db_connection(app.config["DATABASE"])
    user = conn.execute(
        "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()
    return user


@app.context_processor
def inject_global_data():
    """Inject categories and current user into all Jinja templates."""
    return {
        "categories": VALID_CATEGORIES,
        "current_user_id": session.get("user_id"),
        "current_user_name": session.get("user_name"),
        "current_user_role": session.get("user_role"),
        "now": datetime.now()
    }


# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def is_valid_email(email):
    return bool(email and EMAIL_REGEX.match(email.strip()))


# ---------------------------------------------------------------------------
# Public & Authentication Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Landing page showing portal highlights and recent verified items."""
    conn = get_db_connection(app.config["DATABASE"])
    recent_items = conn.execute(
        """SELECT i.*, u.name AS reporter_name
           FROM items i
           JOIN users u ON i.reported_by = u.id
           WHERE i.status IN ('Verified', 'Returned')
           ORDER BY i.created_at DESC LIMIT 6"""
    ).fetchall()

    stats = {
        "verified_items": conn.execute("SELECT COUNT(*) FROM items WHERE status = 'Verified'").fetchone()[0],
        "returned_items": conn.execute("SELECT COUNT(*) FROM items WHERE status = 'Returned'").fetchone()[0],
        "active_claims": conn.execute("SELECT COUNT(*) FROM claims WHERE status = 'Approved'").fetchone()[0],
    }
    conn.close()
    return render_template("index.html", recent_items=recent_items, stats=stats)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle student registration."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append("Please enter your full name (minimum 2 characters).")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", name=name, email=email)

        conn = get_db_connection(app.config["DATABASE"])
        cursor = conn.cursor()

        # Check duplicate email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash("An account with this email address already exists. Please log in.", "danger")
            return render_template("register.html", name=name, email=email)

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, 'student')",
            (name, email, hashed_password)
        )
        conn.commit()
        conn.close()

        flash("Registration successful! You may now log in with your credentials.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login for both students and administrators."""
    if "user_id" in session:
        if session.get("user_role") == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email address and password.", "danger")
            return render_template("login.html", email=email)

        conn = get_db_connection(app.config["DATABASE"])
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]

            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))

        flash("Invalid email or password. Please try again.", "danger")
        return render_template("login.html", email=email)

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out current user and clear session."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Student Dashboard & Reporting
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard displaying personal reported items, claims, smart matches, and status."""
    user_id = session["user_id"]
    conn = get_db_connection(app.config["DATABASE"])

    # Items reported by current user
    my_items = conn.execute(
        """SELECT * FROM items
           WHERE reported_by = ?
           ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()

    # Claims submitted by current user with item information
    my_claims = conn.execute(
        """SELECT c.id AS claim_id, c.message, c.status AS claim_status, c.created_at AS claim_date,
                  i.id AS item_id, i.title AS item_title, i.category, i.location, i.item_type,
                  i.status AS item_status
           FROM claims c
           JOIN items i ON c.item_id = i.id
           WHERE c.user_id = ?
           ORDER BY c.created_at DESC""",
        (user_id,)
    ).fetchall()

    # Smart Lost-Found Matches for current user's reported items
    # Fetch all verified items in catalog that can act as candidate matches
    catalog_items = conn.execute(
        """SELECT i.*, u.name AS reporter_name
           FROM items i
           JOIN users u ON i.reported_by = u.id
           WHERE i.status = 'Verified'"""
    ).fetchall()
    catalog_dicts = [dict(it) for it in catalog_items]

    user_matches = []
    # For each item reported by user that is Verified or Pending, see if matching candidate exists
    for my_item in my_items:
        if my_item["status"] in ["Verified", "Pending"]:
            my_item_dict = dict(my_item)
            matches = find_matches_for_item(my_item_dict, catalog_dicts, threshold=DEFAULT_MATCH_THRESHOLD)
            for m in matches:
                # Add my_item reference for UI display
                user_matches.append({
                    "my_item": my_item_dict,
                    "matched_item": m["candidate_item"],
                    "score": m["score"],
                    "breakdown": m["breakdown"],
                    "reason": m["reason"]
                })

    # Sort user matches by score descending
    user_matches.sort(key=lambda x: x["score"], reverse=True)

    stats = {
        "total_reported": len(my_items),
        "verified_reported": sum(1 for item in my_items if item["status"] == "Verified"),
        "total_claims": len(my_claims),
        "approved_claims": sum(1 for claim in my_claims if claim["claim_status"] == "Approved"),
        "total_matches": len(user_matches)
    }

    conn.close()
    return render_template(
        "dashboard.html",
        my_items=my_items,
        my_claims=my_claims,
        user_matches=user_matches,
        stats=stats
    )


@app.route("/report", methods=["GET", "POST"])
@login_required
def report_item():
    """Report a new lost or found item."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        date_str = request.form.get("date", "").strip()
        item_type = request.form.get("item_type", "").strip()

        errors = []
        if not title or len(title) < 3:
            errors.append("Item title is required (minimum 3 characters).")
        if not description or len(description) < 10:
            errors.append("Please provide a descriptive explanation (minimum 10 characters).")
        if category not in VALID_CATEGORIES:
            errors.append("Please select a valid category from the list.")
        if not location or len(location) < 3:
            errors.append("Campus location is required (e.g. Library 2nd Floor).")
        if item_type not in ["Lost", "Found"]:
            errors.append("Item type must be either 'Lost' or 'Found'.")

        if not date_str:
            errors.append("Date is required.")
        else:
            try:
                item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if item_date > datetime.now().date():
                    errors.append("The report date cannot be in the future.")
            except ValueError:
                errors.append("Invalid date format. Please use YYYY-MM-DD.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "report.html",
                title=title,
                description=description,
                category=category,
                location=location,
                date=date_str,
                item_type=item_type
            )

        conn = get_db_connection(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO items (title, description, category, location, date, item_type, reported_by, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')""",
            (title, description, category, location, date_str, item_type, session["user_id"])
        )
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()

        flash(
            f"Your {item_type.lower()} item '{title}' has been submitted for admin verification.",
            "success"
        )
        return redirect(url_for("dashboard"))

    return render_template("report.html")


# ---------------------------------------------------------------------------
# Browse & Search Items
# ---------------------------------------------------------------------------
@app.route("/items")
def items():
    """Browse and search items with filters for keyword, category, type, and status."""
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    item_type = request.args.get("type", "").strip()
    status = request.args.get("status", "").strip()

    sql = """
        SELECT i.*, u.name AS reporter_name
        FROM items i
        JOIN users u ON i.reported_by = u.id
        WHERE 1=1
    """
    params = []

    # If user is not admin, only show Verified or Returned items by default
    if session.get("user_role") != "admin":
        if status in ["Verified", "Returned"]:
            sql += " AND i.status = ?"
            params.append(status)
        else:
            sql += " AND i.status IN ('Verified', 'Returned')"
    elif status and status in ITEM_STATUSES:
        sql += " AND i.status = ?"
        params.append(status)

    if query:
        sql += " AND (i.title LIKE ? OR i.description LIKE ? OR i.location LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if category and category in VALID_CATEGORIES:
        sql += " AND i.category = ?"
        params.append(category)

    if item_type in ["Lost", "Found"]:
        sql += " AND i.item_type = ?"
        params.append(item_type)

    sql += " ORDER BY i.created_at DESC"

    conn = get_db_connection(app.config["DATABASE"])
    items_list = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template(
        "items.html",
        items=items_list,
        query=query,
        selected_category=category,
        selected_type=item_type,
        selected_status=status
    )


@app.route("/items/<int:item_id>")
def item_details(item_id):
    """View detailed information about a single reported item."""
    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute(
        """SELECT i.*, u.name AS reporter_name, u.email AS reporter_email
           FROM items i
           JOIN users u ON i.reported_by = u.id
           WHERE i.id = ?""",
        (item_id,)
    ).fetchone()

    if not item:
        conn.close()
        return render_template(
            "error.html",
            error_code=404,
            error_title="Item Not Found",
            error_message="The requested item could not be found or has been removed."
        ), 404

    # Fetch claims if the current user is admin or the reporter
    claims = []
    user_has_claimed = False
    if "user_id" in session:
        if session.get("user_role") == "admin" or session["user_id"] == item["reported_by"]:
            claims = conn.execute(
                """SELECT c.*, u.name AS claimant_name, u.email AS claimant_email
                   FROM claims c
                   JOIN users u ON c.user_id = u.id
                   WHERE c.item_id = ?
                   ORDER BY c.created_at DESC""",
                (item_id,)
            ).fetchall()

        # Check if current user already submitted a claim
        existing_claim = conn.execute(
            "SELECT id, status FROM claims WHERE item_id = ? AND user_id = ?",
            (item_id, session["user_id"])
        ).fetchone()
        if existing_claim:
            user_has_claimed = True

    # Smart Matches for this item
    # If this item is Lost, find matching Verified Found items.
    # If this item is Found, find matching Verified Lost items.
    matches = []
    if item["status"] in ["Verified", "Pending"]:
        opposite_type = "Found" if item["item_type"] == "Lost" else "Lost"
        candidate_rows = conn.execute(
            """SELECT i.*, u.name AS reporter_name
               FROM items i
               JOIN users u ON i.reported_by = u.id
               WHERE i.item_type = ? AND i.status = 'Verified' AND i.id != ?""",
            (opposite_type, item_id)
        ).fetchall()
        candidate_dicts = [dict(c) for c in candidate_rows]
        matches = find_matches_for_item(dict(item), candidate_dicts, threshold=DEFAULT_MATCH_THRESHOLD)

    conn.close()
    return render_template(
        "item_details.html",
        item=item,
        claims=claims,
        user_has_claimed=user_has_claimed,
        potential_matches=matches
    )


# ---------------------------------------------------------------------------
# Claim Submission
# ---------------------------------------------------------------------------
@app.route("/claim/<int:item_id>", methods=["GET", "POST"])
@login_required
def submit_claim(item_id):
    """Submit an ownership verification claim for a reported item."""
    conn = get_db_connection(app.config["DATABASE"])
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()

    if not item:
        conn.close()
        return render_template(
            "error.html",
            error_code=404,
            error_title="Item Not Found",
            error_message="Cannot submit claim on an invalid or non-existent item."
        ), 404

    # Prevent user claiming their own reported item
    if item["reported_by"] == session["user_id"]:
        conn.close()
        flash("You cannot submit an ownership claim on an item that you reported.", "warning")
        return redirect(url_for("item_details", item_id=item_id))

    # Check if item is already Returned or Rejected
    if item["status"] == "Returned":
        conn.close()
        flash("This item has already been marked as returned to its verified owner.", "info")
        return redirect(url_for("item_details", item_id=item_id))

    if item["status"] == "Rejected":
        conn.close()
        flash("This item report has been rejected by administration and cannot be claimed.", "danger")
        return redirect(url_for("item_details", item_id=item_id))

    # Check if user already claimed this item
    existing_claim = conn.execute(
        "SELECT id, status FROM claims WHERE item_id = ? AND user_id = ?",
        (item_id, session["user_id"])
    ).fetchone()

    if existing_claim:
        conn.close()
        flash(f"You have already submitted a claim for this item (Status: {existing_claim['status']}).", "warning")
        return redirect(url_for("item_details", item_id=item_id))

    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if not message or len(message) < 10:
            flash("Please provide sufficient proof details in your claim message (minimum 10 characters).", "danger")
            conn.close()
            return render_template("claim.html", item=item, message=message)

        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO claims (item_id, user_id, message, status)
               VALUES (?, ?, ?, 'Pending')""",
            (item_id, session["user_id"], message)
        )
        conn.commit()
        conn.close()

        flash("Your claim has been submitted successfully and is pending admin review.", "success")
        return redirect(url_for("dashboard"))

    conn.close()
    return render_template("claim.html", item=item)


# ---------------------------------------------------------------------------
# Administrator Management Routes
# ---------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    """Administrator control center to review items and claims."""
    conn = get_db_connection(app.config["DATABASE"])

    items_list = conn.execute(
        """SELECT i.*, u.name AS reporter_name, u.email AS reporter_email
           FROM items i
           JOIN users u ON i.reported_by = u.id
           ORDER BY i.created_at DESC"""
    ).fetchall()

    claims_list = conn.execute(
        """SELECT c.*, u.name AS claimant_name, u.email AS claimant_email,
                  i.title AS item_title, i.category, i.status AS item_status, i.item_type
           FROM claims c
           JOIN users u ON c.user_id = u.id
           JOIN items i ON c.item_id = i.id
           ORDER BY c.created_at DESC"""
    ).fetchall()

    users_list = conn.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()

    # Precalculate global active matches between all Verified Lost and Found items for Admin monitoring
    verified_lost = [dict(it) for it in items_list if it["item_type"] == "Lost" and it["status"] == "Verified"]
    verified_found = [dict(it) for it in items_list if it["item_type"] == "Found" and it["status"] == "Verified"]
    admin_matches = []
    for l_item in verified_lost:
        found_matches = find_matches_for_item(l_item, verified_found, threshold=DEFAULT_MATCH_THRESHOLD)
        for m in found_matches:
            admin_matches.append({
                "lost_item": m["lost_item"],
                "found_item": m["found_item"],
                "score": m["score"],
                "breakdown": m["breakdown"],
                "reason": m["reason"]
            })
    admin_matches.sort(key=lambda x: x["score"], reverse=True)

    stats = {
        "total_items": len(items_list),
        "pending_items": sum(1 for i in items_list if i["status"] == "Pending"),
        "verified_items": sum(1 for i in items_list if i["status"] == "Verified"),
        "rejected_items": sum(1 for i in items_list if i["status"] == "Rejected"),
        "returned_items": sum(1 for i in items_list if i["status"] == "Returned"),
        "total_claims": len(claims_list),
        "pending_claims": sum(1 for c in claims_list if c["status"] == "Pending"),
        "approved_claims": sum(1 for c in claims_list if c["status"] == "Approved"),
        "total_matches": len(admin_matches),
        "total_users": len(users_list)
    }

    conn.close()
    return render_template(
        "admin.html",
        items=items_list,
        claims=claims_list,
        users=users_list,
        admin_matches=admin_matches,
        stats=stats
    )


@app.route("/admin/items/<int:item_id>/status", methods=["POST"])
@admin_required
def update_item_status(item_id):
    """Admin updates item status: 'Verified', 'Rejected', or 'Returned'."""
    new_status = request.form.get("status", "").strip()

    if new_status not in ITEM_STATUSES:
        flash("Invalid item status specified.", "danger")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection(app.config["DATABASE"])
    cursor = conn.cursor()

    item = cursor.execute("SELECT id, title FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        flash("Target item does not exist.", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor.execute(
        "UPDATE items SET status = ? WHERE id = ?",
        (new_status, item_id)
    )
    conn.commit()
    conn.close()

    flash(f"Status of '{item['title']}' updated to '{new_status}'.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/claims/<int:claim_id>/status", methods=["POST"])
@admin_required
def update_claim_status(claim_id):
    """Admin updates claim status: 'Approved' or 'Rejected'."""
    new_status = request.form.get("status", "").strip()

    if new_status not in CLAIM_STATUSES:
        flash("Invalid claim status specified.", "danger")
        return redirect(url_for("admin_dashboard"))

    conn = get_db_connection(app.config["DATABASE"])
    cursor = conn.cursor()

    claim = cursor.execute(
        """SELECT c.id, c.item_id, i.title AS item_title
           FROM claims c
           JOIN items i ON c.item_id = i.id
           WHERE c.id = ?""",
        (claim_id,)
    ).fetchone()

    if not claim:
        conn.close()
        flash("Claim record not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    cursor.execute(
        "UPDATE claims SET status = ? WHERE id = ?",
        (new_status, claim_id)
    )

    # If a claim is approved, optionally offer or set item to Returned if requested
    if new_status == "Approved" and request.form.get("mark_returned") == "yes":
        cursor.execute("UPDATE items SET status = 'Returned' WHERE id = ?", (claim["item_id"],))

    conn.commit()
    conn.close()

    flash(f"Claim #{claim_id} for '{claim['item_title']}' has been set to '{new_status}'.", "success")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template(
        "error.html",
        error_code=404,
        error_title="Page Not Found",
        error_message="The requested campus portal page could not be located."
    ), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template(
        "error.html",
        error_code=403,
        error_title="Access Forbidden",
        error_message="You do not have the required permissions to perform this action."
    ), 403


@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "error.html",
        error_code=500,
        error_title="Internal Server Error",
        error_message="An unexpected system error occurred. Please try again later."
    ), 500


# ---------------------------------------------------------------------------
# CLI / Startup
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists(app.config["DATABASE"]):
        init_db(app.config["DATABASE"])
        seed_sample_data(app.config["DATABASE"])
    app.run(debug=True, host="127.0.0.1", port=5000)
