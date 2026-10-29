# Class Diagram
## Smart Lost & Found Portal for Campus

This class diagram represents the domain models, database persistence entities, and controller operations of the implemented application, complete with attributes, operational methods, relationships, and multiplicities.

```mermaid
classDiagram
    %% Entities
    class User {
        +int id
        +string name
        +string email
        +string password
        +string role
        +datetime created_at
        +register(name, email, password) bool
        +verify_password(plaintext_password) bool
        +is_admin() bool
        +get_my_items() List~Item~
        +get_my_claims() List~Claim~
    }

    class Item {
        +int id
        +string title
        +string description
        +string category
        +string location
        +string date
        +string item_type
        +int reported_by
        +string status
        +datetime created_at
        +create(title, desc, cat, loc, date, type, user_id) int
        +update_status(new_status) bool
        +is_claimable(user_id) bool
        +get_associated_claims() List~Claim~
    }

    class Claim {
        +int id
        +int item_id
        +int user_id
        +string message
        +string status
        +datetime created_at
        +submit(item_id, user_id, message) int
        +update_status(new_status) bool
    }

    class DatabaseManager {
        +string db_path
        +get_db_connection() sqlite3.Connection
        +init_db() void
        +seed_sample_data() void
    }

    class PortalController {
        +index() Response
        +register() Response
        +login() Response
        +logout() Response
        +dashboard() Response
        +report_item() Response
        +items() Response
        +item_details(item_id) Response
        +submit_claim(item_id) Response
        +admin_dashboard() Response
        +update_item_status(item_id) Response
        +update_claim_status(claim_id) Response
    }

    %% Relationships and Associations
    User "1" --> "0..*" Item : "reports >"
    User "1" --> "0..*" Claim : "submits >"
    Item "1" --> "0..*" Claim : "receives >"
    
    PortalController ..> DatabaseManager : "manages persistence via"
    PortalController ..> User : "authenticates & manages"
    PortalController ..> Item : "queries & creates"
    PortalController ..> Claim : "validates & updates"
```

### Class Specifications & Multiplicities

1. **`User` Entity**:
   - Represents student and administrative actors within the system.
   - Enforces unique email constraints and hashed password verification via Werkzeug.
   - Multiplicity: One `User` can report zero or many (`0..*`) `Item` records and lodge zero or many (`0..*`) `Claim` records.

2. **`Item` Entity**:
   - Represents lost or found physical belongings cataloged on campus.
   - Governed by state enumerations: `Pending`, `Verified`, `Rejected`, and `Returned`.
   - Multiplicity: One `Item` is reported by exactly one (`1`) `User` and can have zero or many (`0..*`) `Claim` submissions.

3. **`Claim` Entity**:
   - Represents an ownership claim submitted by a student.
   - Contains identifying proof message and status enumerations: `Pending`, `Approved`, and `Rejected`.
   - Multiplicity: Associated with exactly one target `Item` and one claimant `User`.

4. **`PortalController` & `DatabaseManager`**:
   - Implements role-based decorators (`@login_required`, `@admin_required`) and parameterized SQL operations with transaction commits.
