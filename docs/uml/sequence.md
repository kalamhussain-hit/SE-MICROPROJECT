# Sequence Diagram
## Workflow: Student Submits Ownership Claim for a Verified Item

This sequence diagram depicts the detailed end-to-end interactions across actors and architectural layers when a registered student discovers their lost item in the catalog and submits an ownership claim with identifying proof.

```mermaid
sequenceDiagram
    autonumber
    actor Student as 👨‍🎓 Student
    participant UI as 🖥️ Web Interface (HTML/CSS/JS)
    participant Backend as ⚙️ Flask Backend (app.py)
    participant DB as 🗄️ SQLite Database (lost_found.db)

    %% Step 1: Browse to item details
    Student ->> UI: Clicks "View Details" on item #2 (Laptop Charger)
    UI ->> Backend: GET /items/2
    Backend ->> DB: SELECT * FROM items WHERE id = 2 (parameterized query)
    DB -->> Backend: Returns Item row (status='Verified', reported_by=1)
    Backend ->> DB: SELECT * FROM claims WHERE item_id=2 AND user_id=student_id
    DB -->> Backend: Returns empty (no previous claim)
    Backend -->> UI: Renders item_details.html with "Submit Ownership Claim" button
    UI -->> Student: Displays item specifications & claim callout

    %% Step 2: Open claim form
    Student ->> UI: Clicks "Submit Ownership Claim" button
    UI ->> Backend: GET /claim/2 (with session cookie)
    Backend ->> Backend: Verify @login_required & user_id != reported_by
    Backend ->> DB: SELECT * FROM items WHERE id = 2
    DB -->> Backend: Returns Item metadata
    Backend -->> UI: Renders claim.html (item summary & proof textarea)
    UI -->> Student: Displays claim submission form

    %% Step 3: Enter proof and submit
    Student ->> UI: Enters proof message: "Dell 65W charger with blue velcro tie" & clicks Submit
    UI ->> UI: Validates message length >= 10 chars (script.js)
    UI ->> Backend: POST /claim/2 (form data: message=...)
    
    %% Step 4: Backend validation & persistence
    Backend ->> Backend: Check session & validate message >= 10 chars
    Backend ->> DB: Check existing claims for item_id=2 and user_id
    DB -->> Backend: No active claim found
    Backend ->> DB: INSERT INTO claims (item_id, user_id, message, status) VALUES (2, user_id, message, 'Pending')
    DB -->> Backend: Transaction committed (claim_id=3)
    
    %% Step 5: Response & redirection
    Backend -->> UI: HTTP 302 Redirect to /dashboard with flash("Claim submitted successfully")
    UI ->> Backend: GET /dashboard
    Backend ->> DB: Query user items & user claims
    DB -->> Backend: Returns updated user claims list
    Backend -->> UI: Renders dashboard.html
    UI -->> Student: Displays Student Dashboard showing Claim #CLM-3 with status "Pending"
```

### Key Architectural Highlights in Sequence
1. **Security & Session Authentication**: The `@login_required` decorator validates session integrity before exposing the claim submission route.
2. **Business Rule Enforcement**: The backend explicitly verifies that `session['user_id'] != item['reported_by']` and prevents duplicate claims on the same item.
3. **Parameterized SQL Persistence**: The claim message is written safely using parameterized bindings (`?`) preventing SQL injection.
4. **Immediate User Feedback**: The student receives an instant flash confirmation and can track review status directly on their personal dashboard.
