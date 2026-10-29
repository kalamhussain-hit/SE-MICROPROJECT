# Requirement Traceability Matrix (RTM)
## Smart Lost & Found Portal for Campus

The Requirement Traceability Matrix (RTM) tracks the lifecycle of every specified Functional Requirement (FR) and Non-Functional Requirement (NFR) from the IEEE 830 SRS through its corresponding source code implementation and automated test verification.

---

## 1. Functional Requirements Traceability

| Requirement ID | Requirement Description | Implementation Module | Source File & Route / Method | Verification Test Case ID | Test Execution Status |
|---|---|---|---|---|---|
| **FR-01** | Student Account Registration with Validation | Authentication Module | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/register`) | **TC-01, TC-02** | **PASSED** (100%) |
| **FR-02** | User Login with Password Verification | Authentication Module | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/login`) | **TC-03, TC-04** | **PASSED** (100%) |
| **FR-03** | Role-Based Post-Login Routing | Session Controller | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/login`) | **TC-04, TC-A1** | **PASSED** (100%) |
| **FR-04** | User Session Termination / Logout | Authentication Module | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/logout`) | **TC-L1** | **PASSED** (100%) |
| **FR-05** | Student Personal Dashboard | Student Portal | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/dashboard`) | **TC-04, TC-U1** | **PASSED** (100%) |
| **FR-06** | Report Lost Campus Belonging | Item Management | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/report`) | **TC-05, TC-06** | **PASSED** (100%) |
| **FR-07** | Report Found Campus Belonging | Item Management | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/report`) | **TC-06** | **PASSED** (100%) |
| **FR-08** | Browse Public Verified Catalog | Item Discovery | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/items`) | **TC-P1, TC-07** | **PASSED** (100%) |
| **FR-09** | Multi-Criteria Catalog Search & Filter | Item Discovery | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/items`) | **TC-07, TC-08, TC-SEC1** | **PASSED** (100%) |
| **FR-10** | Item Specification Details View | Item Discovery | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/items/<id>`) | **TC-D1, TC-N1** | **PASSED** (100%) |
| **FR-11** | Submit Ownership Claim with Proof | Claims Module | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/claim/<id>`) | **TC-09, TC-10, TC-C2** | **PASSED** (100%) |
| **FR-12** | Prohibit Self-Reporting Claims | Business Logic Guard | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/claim/<id>`) | **TC-C1** | **PASSED** (100%) |
| **FR-13** | Admin Dashboard & Live Metrics | Administrative Center | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/admin`) | **TC-A1, TC-11** | **PASSED** (100%) |
| **FR-14** | Admin Verify Item Report | Moderation Controller | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/admin/items/<id>/status`) | **TC-12** | **PASSED** (100%) |
| **FR-15** | Admin Reject Invalid Item Report | Moderation Controller | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/admin/items/<id>/status`) | **TC-13** | **PASSED** (100%) |
| **FR-16** | Admin Claim Review & Return Marking | Claims Resolution | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/admin/claims/<id>/status`) | **TC-14, TC-15, TC-16** | **PASSED** (100%) |
| **FR-17** | Automated Smart Lost-Found Candidate Correlation | Smart Matching Engine | [`matching.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/matching.py) (`find_matches_for_item`) | **TC-SM-01, TC-SM-02, TC-SM-03** | **PASSED** (100%) |
| **FR-18** | Explainable Weighted Multi-Attribute Match Scoring | Smart Matching Engine | [`matching.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/matching.py) (`calculate_match_details`) | **TC-SM-01, TC-SM-04, TC-SM-05** | **PASSED** (100%) |
| **FR-19** | Smart Match Presentation & Claim Integration | Student Portal & Claims | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/dashboard`, `/items/<id>`) | **TC-SM-05, TC-SM-06, TC-SM-08** | **PASSED** (100%) |
| **FR-20** | Administrative Smart Match Oversight | Administrative Center | [`app.py`](file:///c:/Users/Kalam/OneDrive/Desktop/SE-Micrporject/app.py) (`/admin`) | **TC-SM-07, TC-SM-08** | **PASSED** (100%) |

---

## 2. Non-Functional Requirements Traceability

| Requirement ID | Metric Category | System Implementation Mechanism | Verification Test Case ID | Test Execution Status |
|---|---|---|---|---|
| **NFR-01** | Performance | Sub-millisecond SQLite indexes on `status`, `item_type`, `category` | **TC-07, TC-08** | **PASSED** (100%) |
| **NFR-02** | Security | Scrypt / PBKDF2 password hashing, RBAC `@admin_required`, parameterized SQL | **TC-01, TC-11, TC-SEC1** | **PASSED** (100%) |
| **NFR-03** | Usability | Responsive HTML5/CSS3 layout, color-coded status badges, custom error pages | **TC-P1, TC-N1** | **PASSED** (100%) |
| **NFR-04** | Reliability | SQLite ACID enforcement (`PRAGMA foreign_keys = ON;`, `ON DELETE CASCADE`) | **TC-06, TC-09, TC-14** | **PASSED** (100%) |

---

## 3. Coverage Analysis
- **Total Functional Requirements Tracked**: 20 / 20 (100%)
- **Total Non-Functional Requirements Tracked**: 4 / 4 (100%)
- **Total Associated Test Cases**: 33 / 33 Passing (100%)
- **Defects Found / Open**: 0
