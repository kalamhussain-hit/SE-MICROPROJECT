# Use Case Diagram
## Smart Lost & Found Portal for Campus

This diagram represents the functional interactions between the two primary actors (**Student / Campus User** and **Campus Administrator**) and the actual implemented use cases within the application.

```mermaid
flowchart LR
    %% Actors
    subgraph Actors [System Actors]
        Student["👨‍🎓 Student / Campus User"]
        Admin["🛡️ Campus Administrator"]
    end

    %% System Boundary
    subgraph Portal [Smart Lost & Found Campus Portal System]
        %% Authentication
        UC1(["UC-01: Register Account"])
        UC2(["UC-02: Authenticate / Log In"])
        UC3(["UC-03: Log Out"])

        %% Student Functions
        UC4(["UC-04: View Student Dashboard"])
        UC5(["UC-05: Report Lost Item"])
        UC6(["UC-06: Report Found Item"])
        UC7(["UC-07: Browse & Search Catalog"])
        UC8(["UC-08: View Item Details"])
        UC9(["UC-09: Submit Ownership Claim"])
        UC10(["UC-10: Track Personal Claims"])
        UC18(["UC-18: View Smart Lost-Found Matches"])

        %% Admin Functions
        UC11(["UC-11: Access Admin Control Panel"])
        UC12(["UC-12: Verify Pending Item Report"])
        UC13(["UC-13: Reject Item Report"])
        UC14(["UC-14: Review Ownership Claims"])
        UC15(["UC-15: Approve Claim & Mark Returned"])
        UC16(["UC-16: Reject Claim"])
        UC17(["UC-17: View User Directory"])
        UC19(["UC-19: Monitor Automated Cross-Matches"])
    end

    %% Student Connections
    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC6
    Student --> UC7
    Student --> UC8
    Student --> UC9
    Student --> UC10
    Student --> UC18

    %% Admin Connections
    Admin --> UC2
    Admin --> UC3
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16
    Admin --> UC17
    Admin --> UC19

    %% Include / Extend relationships
    UC9 -.->|includes| UC8
    UC9 -.->|extends| UC18
    UC15 -.->|includes| UC14
    UC16 -.->|includes| UC14
```

### Actor Description & Responsibilities

| Actor | Description | Key System Operations |
|---|---|---|
| **Student / Campus User** | Enrolled student or university community member | Creates account, logs lost or found items, browses verified listings, views detailed specifications, submits ownership claims with proof, and tracks resolution status in personal dashboard. |
| **Campus Administrator** | Campus security officer, lost & found desk custodian, or system supervisor | Authenticates with administrative role, monitors system metrics, verifies or rejects reported items, evaluates claimant proof descriptions, approves legitimate claims, marks items returned, and reviews registered users. |
