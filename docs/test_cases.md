# Software Test Cases & Execution Report
## Smart Lost & Found Portal for Campus

**Test Suite Execution Summary:**
- **Execution Engine**: `pytest 9.1.1` on Python 3.14.5 (Windows 11)
- **Total Test Cases**: 25
- **Passed**: 25 (100%)
- **Failed**: 0
- **Execution Date**: October 2026
- **Test File**: [`tests/test_app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/tests/test_app.py)

---

## Test Cases Specification & Actual Execution Results

### 1. Functional & Positive Testing

#### Test Case: TC-01
- **Requirement ID**: FR-01
- **Test Objective**: Verify that a new student can successfully register an account with valid information.
- **Preconditions**: Email `ananya@campus.edu` is not currently registered.
- **Test Steps**:
  1. Navigate to `/register`.
  2. Enter Name, valid Email, Password, and matching Confirm Password.
  3. Submit registration form.
- **Input Data**:
  - Name: `"Ananya Sen"`
  - Email: `"ananya@campus.edu"`
  - Password: `"Password@123"`
  - Confirm Password: `"Password@123"`
- **Expected Result**: HTTP 200/302; redirected to `/login` with flash message `"Registration successful"`; password stored as salted cryptographic hash (Scrypt/PBKDF2).
- **Actual Result**: User registered successfully; flash message `"Registration successful"` received; database inspection confirmed password hash format `scrypt:32768:8:1$...`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_valid_registration`).

---

#### Test Case: TC-04
- **Requirement ID**: FR-02, FR-03
- **Test Objective**: Verify student login authentication with valid credentials.
- **Preconditions**: User `rahul@campus.edu` exists in database.
- **Test Steps**:
  1. Navigate to `/login`.
  2. Input valid student credentials.
  3. Submit form.
- **Input Data**:
  - Email: `"rahul@campus.edu"`
  - Password: `"Student@123"`
- **Expected Result**: HTTP 200/302; session created with `user_role = 'student'`; redirected to `/dashboard` with greeting `"Welcome back, Rahul Sharma!"`.
- **Actual Result**: Authenticated successfully; session set; redirected to `/dashboard` displaying student metrics and reported items table.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_valid_student_login`).

---

#### Test Case: TC-A1
- **Requirement ID**: FR-02, FR-03
- **Test Objective**: Verify administrator login redirects directly to `/admin`.
- **Preconditions**: User `admin@campus.edu` exists with role `'admin'`.
- **Test Steps**:
  1. Navigate to `/login`.
  2. Enter administrator credentials.
  3. Submit login form.
- **Input Data**:
  - Email: `"admin@campus.edu"`
  - Password: `"Admin@123"`
- **Expected Result**: Authenticated; session created with `user_role = 'admin'`; redirected to `/admin` control center.
- **Actual Result**: User logged in and redirected to `/admin`; Admin Control Panel loaded displaying metrics and moderation tabs.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_valid_admin_login`).

---

#### Test Case: TC-L1
- **Requirement ID**: FR-04
- **Test Objective**: Verify that logging out terminates active session.
- **Preconditions**: User is actively authenticated in session.
- **Test Steps**:
  1. Call `/logout`.
- **Input Data**: N/A (Active session)
- **Expected Result**: Session cleared; redirected to `/login` with message `"You have been logged out successfully."`.
- **Actual Result**: Session cookies destroyed; user redirected to `/login` with success banner.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_logout`).

---

#### Test Case: TC-06
- **Requirement ID**: FR-06, FR-07
- **Test Objective**: Verify that an authenticated student can report a new lost/found item.
- **Preconditions**: Student is logged in (`rahul@campus.edu`).
- **Test Steps**:
  1. Navigate to `/report`.
  2. Fill Title, Category, Location, Date, Type (`Lost`), and Description ($\ge 10$ chars).
  3. Submit report.
- **Input Data**:
  - Title: `"Scientific Calculator"`
  - Description: `"Casio fx-991EX ClassWiz scientific calculator left on desk in Hall 2."`
  - Category: `"Electronics"`
  - Location: `"Lecture Hall 2"`
  - Date: `"2026-10-23"`
  - Item Type: `"Lost"`
- **Expected Result**: Record inserted into `items` table with status `'Pending'`; redirected to dashboard with confirmation.
- **Actual Result**: Item created with `id = 6`, status `'Pending'`; redirected to `/dashboard` with banner `"Your lost item 'Scientific Calculator' has been submitted for admin verification."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_valid_item_report`).

---

#### Test Case: TC-07
- **Requirement ID**: FR-08, FR-09
- **Test Objective**: Verify catalog search returns matching verified items for existing keyword.
- **Preconditions**: Verified item `"Laptop Charger"` exists in database.
- **Test Steps**:
  1. Send GET request to `/items?q=Charger`.
- **Input Data**: `q = "Charger"`
- **Expected Result**: HTTP 200; rendered catalog view contains `"Laptop Charger"` and item location metadata.
- **Actual Result**: HTTP 200; search rendered 1 matching item card with title `"Laptop Charger"`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_search_existing_item`).

---

#### Test Case: TC-08
- **Requirement ID**: FR-08, FR-09
- **Test Objective**: Verify catalog search handles non-existent terms gracefully.
- **Preconditions**: Application running with standard catalog.
- **Test Steps**:
  1. Send GET request to `/items?q=NonExistentItemXYZ12345`.
- **Input Data**: `q = "NonExistentItemXYZ12345"`
- **Expected Result**: HTTP 200; displays friendly empty state `"No matching items found"`.
- **Actual Result**: HTTP 200; zero items rendered; empty state banner displayed with `"Clear All Filters"` link.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_search_nonexistent_item`).

---

#### Test Case: TC-D1
- **Requirement ID**: FR-10
- **Test Objective**: Verify item details view loads complete metadata for valid item ID.
- **Preconditions**: Item `#1` (`College ID Card`) exists in database.
- **Test Steps**:
  1. Navigate to `/items/1`.
- **Input Data**: `item_id = 1`
- **Expected Result**: HTTP 200; displays title, category, location, date, reporter name, and full description.
- **Actual Result**: HTTP 200; page rendered with title `"College ID Card"`, location `"Library 2nd Floor Reading Hall"`, and description.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_view_item_details`).

---

#### Test Case: TC-09
- **Requirement ID**: FR-11
- **Test Objective**: Verify student can submit valid ownership claim on a verified item.
- **Preconditions**: Student `priya@campus.edu` logged in; item `#1` is verified and reported by another student (`rahul@campus.edu`).
- **Test Steps**:
  1. Navigate to `/claim/1`.
  2. Input proof message ($\ge 10$ characters).
  3. Submit claim.
- **Input Data**:
  - Message: `"This is my ID card; Roll number matches CS-2024-042 with my departmental stamp."`
- **Expected Result**: HTTP 200/302; claim inserted with status `'Pending'`; redirected to `/dashboard` with success notification.
- **Actual Result**: Claim recorded in database (`claims` table); redirected to dashboard with flash message `"Your claim has been submitted successfully and is pending admin review."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_submit_valid_claim`).

---

#### Test Case: TC-12
- **Requirement ID**: FR-14
- **Test Objective**: Verify administrator can verify a pending item report.
- **Preconditions**: Administrator logged in; item `#3` has status `'Pending'`.
- **Test Steps**:
  1. POST to `/admin/items/3/status` with `status = 'Verified'`.
- **Input Data**: `status = "Verified"`, `item_id = 3`
- **Expected Result**: Item `#3` status updated to `'Verified'` in database; visible in public catalog.
- **Actual Result**: Item `#3` status updated to `'Verified'`; confirmation flash displayed.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_admin_verifies_item`).

---

#### Test Case: TC-13
- **Requirement ID**: FR-15
- **Test Objective**: Verify administrator can reject an invalid item report.
- **Preconditions**: Administrator logged in; item `#4` has status `'Pending'`.
- **Test Steps**:
  1. POST to `/admin/items/4/status` with `status = 'Rejected'`.
- **Input Data**: `status = "Rejected"`, `item_id = 4`
- **Expected Result**: Item `#4` status updated to `'Rejected'`; excluded from public catalog.
- **Actual Result**: Database confirmed item `#4` status changed to `'Rejected'`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_admin_rejects_item`).

---

#### Test Case: TC-14
- **Requirement ID**: FR-16
- **Test Objective**: Verify administrator can approve an ownership claim and mark the target item returned.
- **Preconditions**: Administrator logged in; claim `#1` on item `#2` is `'Pending'`.
- **Test Steps**:
  1. POST to `/admin/claims/1/status` with `status = 'Approved'` and `mark_returned = 'yes'`.
- **Input Data**: `status = "Approved"`, `mark_returned = "yes"`, `claim_id = 1`
- **Expected Result**: Claim `#1` set to `'Approved'`; item `#2` set to `'Returned'`.
- **Actual Result**: Database query confirmed claim status is `'Approved'` and item status is `'Returned'`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_admin_approves_claim_and_marks_returned`).

---

#### Test Case: TC-15
- **Requirement ID**: FR-16
- **Test Objective**: Verify administrator can reject an unverified claim.
- **Preconditions**: Administrator logged in; claim `#1` is `'Pending'`.
- **Test Steps**:
  1. POST to `/admin/claims/1/status` with `status = 'Rejected'`.
- **Input Data**: `status = "Rejected"`, `claim_id = 1`
- **Expected Result**: Claim `#1` status updated to `'Rejected'`.
- **Actual Result**: Database query confirmed claim `#1` status is `'Rejected'`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_admin_rejects_claim`).

---

#### Test Case: TC-16
- **Requirement ID**: FR-16
- **Test Objective**: Verify administrator can directly mark a verified item as returned.
- **Preconditions**: Administrator logged in; item `#1` is `'Verified'`.
- **Test Steps**:
  1. POST to `/admin/items/1/status` with `status = 'Returned'`.
- **Input Data**: `status = "Returned"`, `item_id = 1`
- **Expected Result**: Item `#1` status updated to `'Returned'`.
- **Actual Result**: Database query confirmed item `#1` status is `'Returned'`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_mark_item_returned`).

---

### 2. Negative & Validation Testing

#### Test Case: TC-02
- **Requirement ID**: FR-01
- **Test Objective**: Verify registration prevents duplicate email addresses.
- **Preconditions**: `rahul@campus.edu` is already registered.
- **Test Steps**:
  1. Submit registration with existing email `rahul@campus.edu`.
- **Input Data**: Email: `"rahul@campus.edu"`, Name: `"Duplicate Rahul"`, Password: `"Pass@123"`
- **Expected Result**: Registration rejected; flash message informs user that account already exists.
- **Actual Result**: Form submission blocked; error message `"An account with this email address already exists. Please log in."` displayed.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_duplicate_email_registration`).

---

#### Test Case: TC-03
- **Requirement ID**: FR-02
- **Test Objective**: Verify login fails when incorrect password is provided.
- **Preconditions**: User `rahul@campus.edu` exists.
- **Test Steps**:
  1. Submit login form with wrong password.
- **Input Data**: Email: `"rahul@campus.edu"`, Password: `"WrongPassword999"`
- **Expected Result**: Login denied; flash message `"Invalid email or password"`.
- **Actual Result**: Authentication failed; user remained on login page with error alert.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_invalid_login`).

---

#### Test Case: TC-05
- **Requirement ID**: FR-06, FR-07
- **Test Objective**: Verify reporting form rejects empty required fields.
- **Preconditions**: Student logged in.
- **Test Steps**:
  1. Submit `/report` with empty title, description, and location.
- **Input Data**: `title = ""`, `description = ""`, `location = ""`
- **Expected Result**: Form rejected; validation error displayed; no database insertion.
- **Actual Result**: HTTP 200; error message `"Item title is required (minimum 3 characters)."` displayed; database unchanged.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_empty_report_form`).

---

#### Test Case: TC-10
- **Requirement ID**: FR-11
- **Test Objective**: Verify claim submission rejects whitespace or empty proof message.
- **Preconditions**: Student logged in; viewing item `#1`.
- **Test Steps**:
  1. Submit claim with whitespace message.
- **Input Data**: `message = "   "`
- **Expected Result**: Claim rejected; error message prompting for sufficient proof ($\ge 10$ chars).
- **Actual Result**: Submission blocked; flash message `"Please provide sufficient proof details in your claim message (minimum 10 characters)."` displayed.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_empty_claim_message`).

---

### 3. Boundary & Security Testing

#### Test Case: TC-11
- **Requirement ID**: NFR-02, FR-13
- **Test Objective**: Verify unauthorized student cannot access protected `/admin` route.
- **Preconditions**: Student `rahul@campus.edu` logged in (`role = 'student'`).
- **Test Steps**:
  1. Navigate directly to `http://127.0.0.1:5000/admin`.
- **Input Data**: Student session
- **Expected Result**: HTTP `403 Forbidden`; custom error template rendered; access denied.
- **Actual Result**: Server returned HTTP 403 status code with `"Access Forbidden: You do not have administrative privileges to access this area."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_unauthorized_admin_access`).

---

#### Test Case: TC-U1
- **Requirement ID**: NFR-02, FR-05
- **Test Objective**: Verify unauthenticated visitor accessing `/dashboard` is redirected to `/login`.
- **Preconditions**: No active session cookie.
- **Test Steps**:
  1. GET `/dashboard`.
- **Input Data**: Unauthenticated request
- **Expected Result**: HTTP 302 Redirect to `/login?next=%2Fdashboard`.
- **Actual Result**: HTTP 302 received; `Location` header points to `/login?next=%2Fdashboard`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_unauthenticated_protected_route_redirect`).

---

#### Test Case: TC-C1
- **Requirement ID**: FR-12
- **Test Objective**: Verify student cannot lodge a claim on an item they reported themselves.
- **Preconditions**: Student `rahul@campus.edu` reported item `#1`.
- **Test Steps**:
  1. Rahul attempts to claim item `#1` via `/claim/1`.
- **Input Data**: `user_id = 2`, `item_id = 1`
- **Expected Result**: System rejects claim attempt with warning message.
- **Actual Result**: Redirected to item details with warning banner `"You cannot submit an ownership claim on an item that you reported."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_cannot_claim_own_item`).

---

#### Test Case: TC-C2
- **Requirement ID**: FR-11
- **Test Objective**: Verify student cannot claim an item that has already been returned.
- **Preconditions**: Item `#5` has status `'Returned'`.
- **Test Steps**:
  1. Student attempts to navigate to `/claim/5`.
- **Input Data**: `item_id = 5`
- **Expected Result**: Claim form denied; notice indicating item is already returned.
- **Actual Result**: Redirected to item details with info banner `"This item has already been marked as returned to its verified owner."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_cannot_claim_returned_item`).

---

#### Test Case: TC-N1
- **Requirement ID**: NFR-03
- **Test Objective**: Verify non-existent item ID returns HTTP 404 rather than unhandled exception.
- **Preconditions**: N/A
- **Test Steps**:
  1. GET `/items/99999`.
- **Input Data**: `item_id = 99999`
- **Expected Result**: HTTP 404 Not Found; clean error page.
- **Actual Result**: HTTP 404 received; rendered `"error.html"` with message `"The requested item could not be found or has been removed."`.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_nonexistent_item_details_404`).

---

#### Test Case: TC-SEC1
- **Requirement ID**: NFR-02
- **Test Objective**: Verify parameterized SQL queries prevent SQL injection payloads in search queries.
- **Preconditions**: Database populated with standard items.
- **Test Steps**:
  1. GET `/items?q=' OR 1=1 --`.
- **Input Data**: `q = "' OR 1=1 --"`
- **Expected Result**: HTTP 200; SQL treated as literal string; no database syntax error or security bypass; 0 matching items returned.
- **Actual Result**: HTTP 200; search executed cleanly without SQL syntax error; returned zero matches.
- **Status**: **PASSED**
- **Remarks**: Verified in test suite (`tests/test_app.py::test_sql_injection_safety`).

---

## 4. Overall Execution Summary

```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\Kalam\OneDrive\Desktop\SE-Micrporject
collected 25 items

tests/test_app.py::test_home_page PASSED                                 [  4%]
tests/test_app.py::test_valid_registration PASSED                        [  8%]
tests/test_app.py::test_valid_student_login PASSED                       [ 12%]
tests/test_app.py::test_valid_admin_login PASSED                         [ 16%]
tests/test_app.py::test_logout PASSED                                    [ 20%]
tests/test_app.py::test_valid_item_report PASSED                         [ 24%]
tests/test_app.py::test_search_existing_item PASSED                      [ 28%]
tests/test_app.py::test_search_nonexistent_item PASSED                   [ 32%]
tests/test_app.py::test_view_item_details PASSED                         [ 36%]
tests/test_app.py::test_submit_valid_claim PASSED                        [ 40%]
tests/test_app.py::test_admin_verifies_item PASSED                       [ 44%]
tests/test_app.py::test_admin_rejects_item PASSED                        [ 48%]
tests/test_app.py::test_admin_approves_claim_and_marks_returned PASSED   [ 52%]
tests/test_app.py::test_admin_rejects_claim PASSED                       [ 56%]
tests/test_app.py::test_mark_item_returned PASSED                        [ 60%]
tests/test_app.py::test_duplicate_email_registration PASSED              [ 64%]
tests/test_app.py::test_invalid_login PASSED                             [ 68%]
tests/test_app.py::test_empty_report_form PASSED                         [ 72%]
tests/test_app.py::test_empty_claim_message PASSED                       [ 76%]
tests/test_app.py::test_unauthorized_admin_access PASSED                 [ 80%]
tests/test_app.py::test_unauthenticated_protected_route_redirect PASSED  [ 84%]
tests/test_app.py::test_cannot_claim_own_item PASSED                     [ 88%]
tests/test_app.py::test_cannot_claim_returned_item PASSED                [ 92%]
tests/test_app.py::test_nonexistent_item_details_404 PASSED              [ 96%]
tests/test_app.py::test_sql_injection_safety PASSED                      [100%]

============================= 25 passed in 20.61s =============================
```
