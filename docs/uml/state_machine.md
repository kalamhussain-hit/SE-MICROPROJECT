# State Machine Diagram
## Entity Lifecycle: Item Entity

This state machine diagram models the distinct operational states, triggering events, guard conditions, and transitions of the central **Item** entity from initial creation through resolution.

```mermaid
stateDiagram-v2
    [*] --> Pending : Student submits Lost or Found report via /report

    state Pending {
        [*] --> AwaitingAdminReview
        AwaitingAdminReview : Report logged in database
        AwaitingAdminReview : Hidden from public catalog
        AwaitingAdminReview : Displayed in student's dashboard
    }

    Pending --> Verified : Admin approves report [Valid campus report]
    Pending --> Rejected : Admin declines report [Spam, duplicate, or inappropriate]

    state Verified {
        [*] --> CatalogPublished
        CatalogPublished : Visible in public search catalog (/items)
        CatalogPublished : Open for ownership claims by other students
        CatalogPublished : Visible on portal home feed
        CatalogPublished : Automatically evaluated by Smart Matching Engine against opposite-type items
    }

    Verified --> Returned : Claim approved & handover confirmed
    Verified --> Returned : Admin directly marks item as returned
    Verified --> Rejected : Admin revokes listing upon investigation

    state Rejected {
        [*] --> ReportArchived
        ReportArchived : Excluded from public catalog
        ReportArchived : Ineligible for claims
        ReportArchived : Marked rejected in student dashboard
    }

    Rejected --> Verified : Admin re-verifies after student clarification

    state Returned {
        [*] --> HandoverFinalized
        HandoverFinalized : Belonging returned to verified owner
        HandoverFinalized : Item tagged 'Returned' in public directory
        HandoverFinalized : No further claims accepted
    }

    Returned --> [*] : Lifecycle Complete
```

### State Transition Matrix

| Current State | Triggering Event | Guard Condition | Target State | Operational Effect |
|---|---|---|---|---|
| **`[*]` (None)** | Student submits report | Form valid (Title $\ge 3$, Desc $\ge 10$, Date $\le$ Today) | **`Pending`** | Item saved with `status = 'Pending'`; awaits administrative queue review. |
| **`Pending`** | Administrator clicks "Verify" | Report is genuine, appropriate, and relevant | **`Verified`** | Item is published to `/items` catalog; eligible for ownership claims. |
| **`Pending`** | Administrator clicks "Reject" | Report is duplicate, spam, or fails campus criteria | **`Rejected`** | Report disabled; student sees rejection notice in dashboard. |
| **`Verified`** | Administrator approves claim | Ownership proof confirmed & handover authorized | **`Returned`** | Target item marked `Returned`; claim marked `Approved`. |
| **`Verified`** | Administrator clicks "Mark Returned" | Physical owner claimed item in-person at campus desk | **`Returned`** | Item status updated to `Returned`; public notified of successful return. |
| **`Verified`** | Administrator clicks "Reject" | Report flagged as inaccurate post-publication | **`Rejected`** | Item removed from active public claims pool. |
| **`Rejected`** | Administrator clicks "Re-verify" | Reporter provides missing clarification | **`Verified`** | Item restored to active catalog. |
| **`Returned`** | Lifecycle termination | Handover complete | **`[*]`** | Final state; item preserved for campus audit metrics. |
