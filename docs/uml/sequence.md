# Sequence Diagram
## Workflow: Student Submits Ownership Claim for a Verified Item

This sequence diagram depicts the detailed end-to-end interactions across actors and architectural layers when a registered student discovers their lost item in the catalog and submits an ownership claim with identifying proof.

```mermaid
sequenceDiagram
    autonumber
    actor Student as 👨‍🎓 Student
    participant UI as 🖥️ Web Interface (HTML/CSS/JS)
    participant Backend as ⚙️ Flask Backend (app.py)
    participant Engine as ⚡ Matching Engine (matching.py)
    participant DB as 🗄️ SQLite Database (lost_found.db)

    %% Step 1: Student opens dashboard
    Student ->> UI: Visits Dashboard (/dashboard)
    UI ->> Backend: GET /dashboard (with session cookie)
    Backend ->> DB: Query user's reported items (my_items)
    DB -->> Backend: Returns reported items (e.g., Lost Item #1)
    Backend ->> DB: Query verified opposite-type items (candidate found items)
    DB -->> Backend: Returns verified found catalog items
    
    %% Step 2: Smart Matching Execution
    Backend ->> Engine: find_matches_for_item(my_item, catalog_items, threshold=50.0)
    loop For Each Candidate Found Item
        Engine ->> Engine: calculate_match_details(Category 30%, Location 25%, Date 20%, Description 25%)
    end
    Engine -->> Backend: Returns ranked matches with scores and explainable breakdown
    Backend -->> UI: Renders dashboard.html with "⚡ Smart Lost–Found Matches" section
    UI -->> Student: Displays potential matches, 91.5% score pill, attribute reasons, and "Claim This Item" button

    %% Step 3: Student proceeds to claim from match
    Student ->> UI: Clicks "Claim This Item" on matched Found Item #2
    UI ->> Backend: GET /claim/2
    Backend ->> DB: SELECT * FROM items WHERE id = 2
    DB -->> Backend: Returns Item metadata
    Backend -->> UI: Renders claim.html (pre-linked to matched item)
    UI -->> Student: Displays claim submission form

    %% Step 4: Submit ownership proof
    Student ->> UI: Enters proof message: "Dell 65W charger with blue velcro tie" & submits
    UI ->> Backend: POST /claim/2 (form data: message=...)
    Backend ->> Backend: Check session & validate message >= 10 chars
    Backend ->> DB: INSERT INTO claims (item_id, user_id, message, status) VALUES (2, user_id, message, 'Pending')
    DB -->> Backend: Transaction committed (claim_id=3)
    Backend -->> UI: Redirects to /dashboard with flash("Claim submitted successfully")
    UI -->> Student: Displays updated dashboard with Pending claim
```

### Key Architectural Highlights in Sequence
1. **Security & Session Authentication**: The `@login_required` decorator validates session integrity before exposing the claim submission route.
2. **Business Rule Enforcement**: The backend explicitly verifies that `session['user_id'] != item['reported_by']` and prevents duplicate claims on the same item.
3. **Parameterized SQL Persistence**: The claim message is written safely using parameterized bindings (`?`) preventing SQL injection.
4. **Immediate User Feedback**: The student receives an instant flash confirmation and can track review status directly on their personal dashboard.
