# ConstructFlow — Requirements Analysis Document

**Project:** ConstructFlow: A Web-Based Cost Tracking and Management System  
**Course:** CSE 309 — Web Programming  
**Institution:** Independent University, Bangladesh  
**Prepared by:** Toufikur Rahman  
**Version:** 1.0 — Initial analysis draft  
**Date:** 16 October 2026  
**Status:** Proposed baseline; stakeholder validation required

## 1. Introduction

### 1.1 Purpose
This document analyzes the needs stated in the ConstructFlow project proposal and translates them into organized, prioritized, testable requirements. It provides a bridge between requirements elicitation and the formal Software Requirements Specification (SRS).

### 1.2 Source and evidence
The primary source is the project proposal submitted on 24 September 2026. It describes manual recordkeeping through tally books and scattered spreadsheets, leading to duplicate or lost cost entries, overwrites, difficult cost filtering, limited cross-office visibility, and weak accountability for false entries or missing bills.

The proposal explicitly identifies role-based access (admin/operator/viewer), soft deletion or archiving, multi-office data separation in a centralized system, and a mobile-friendly interface as design challenges. Detailed workflows, exact fields, approval rules, performance targets, and integrations are not defined in the proposal and remain open for validation.

### 1.3 Analysis method
Requirements are grouped into business goals, functional requirements, non-functional requirements, data concepts, business rules, use cases, priorities, constraints, and unresolved questions. IDs are assigned for traceability. MoSCoW priorities are provisional:
- **Must:** essential to the problem and proposed project identity.
- **Should:** important but may be negotiated if scope or time is limited.
- **Could:** useful enhancement.
- **TBD:** insufficient evidence to set a final priority.

## 2. Problem analysis

### 2.1 Current-state problems
| ID | Problem from proposal | Likely impact |
|---|---|---|
| P-01 | Records are spread across tally books and spreadsheets | Fragmented information and reconciliation effort |
| P-02 | Cost entries can be duplicated or lost | Inaccurate project cost totals |
| P-03 | Editing can overwrite prior information | Weak history and difficult error investigation |
| P-04 | Finding a specific type of cost is stressful | Slow retrieval and reporting |
| P-05 | Offices/sites lack a real-time shared picture of costs | Delayed decisions and inconsistent information |
| P-06 | False entries or missed bills lack clear accountability | Audit and trust risks |
| P-07 | Site staff need a usable interface | Poor adoption if entry is difficult on mobile devices |

### 2.2 Desired future state
ConstructFlow should provide a centralized web system for project-related cost, budget, stock, and bill information. It should support authorized access across offices/sites, allow users to find relevant records efficiently, retain an audit trail of edits and archived records, and offer a mobile-friendly interface.

## 3. System context and stakeholders

| Stakeholder / actor | Goal | Primary interactions |
|---|---|---|
| Administrator | Manage users, permissions, and access boundaries | User/role management; office/site configuration; audit/archive review |
| Operator | Record and maintain operational information | Cost, bill, stock, and project record entry; correction requests/actions as authorized |
| Viewer | Inspect permitted information without changing it | Dashboard, searches, summaries, reports |
| Management / owner | Monitor costs, budgets, and project performance | Cross-project summaries and reports (details to validate) |
| Site / office staff | Enter or consult site-specific records | Mobile-friendly record entry and site-scoped searches |
| Developer / tester | Implement and verify agreed requirements | Requirements, test scenarios, and defect resolution |

Admin, operator, and viewer are explicitly mentioned in the proposal. Management, site staff, and developer/tester are analysis-level actor groupings inferred from the stated use case; their exact permissions need confirmation.

## 4. Scope analysis

### 4.1 Included
- Centralized web-based project records.
- Cost tracking and cost categorization/search/filtering.
- Budget records and cost visibility.
- Stock information.
- Bill records.
- Admin/operator/viewer access roles.
- Office/site data separation.
- Soft deletion or archiving and traceability of edits.
- Dashboard or summary views.
- Responsive/mobile-friendly user interface.
- Data validation and protection against accidental duplicate or destructive changes.

### 4.2 Excluded unless approved
- Full ERP/accounting suite.
- Payroll, tax submission, bank/payment processing, or procurement marketplace.
- Automated integration with external accounting tools.
- Native Android/iOS applications.
- Offline synchronization.
- Multi-tenant support for unrelated firms.
- Formal electronic signatures or legally compliant document retention.

These exclusions are scope-control proposals, not statements from the original proposal that such features are impossible.

## 5. Functional requirements

Requirement statements use “The system shall” to make them testable. Requirements derived directly from the proposal are marked **Source-aligned**; details added to make them actionable are marked **Proposed / validate**.

| ID | Requirement | Priority | Basis |
|---|---|---|---|
| FR-01 | The system shall allow an authorized user to create and maintain project records. | Must | Proposed / validate |
| FR-02 | The system shall allow authorized users to record project-related costs with agreed fields. | Must | Source-aligned; fields TBD |
| FR-03 | The system shall allow users to search, filter, and retrieve cost records by agreed criteria. | Must | Source-aligned |
| FR-04 | The system shall support recording budget information for a project or agreed project scope. | Must | Source-aligned; budget rules TBD |
| FR-05 | The system shall present recorded costs in a way that supports comparison with the applicable budget. | Should | Source-aligned goal; calculation rules TBD |
| FR-06 | The system shall maintain stock records. | Must | Source-aligned; exact workflow TBD |
| FR-07 | The system shall maintain bill records and their association with relevant projects/costs where applicable. | Must | Source-aligned; association rules TBD |
| FR-08 | The system shall authenticate users before granting access to protected system functions. | Must | Proposed security baseline |
| FR-09 | The system shall enforce role-based permissions for administrator, operator, and viewer roles. | Must | Source-aligned |
| FR-10 | The viewer role shall not modify business records. | Must | Proposed interpretation of “viewer”; validate |
| FR-11 | The system shall restrict records according to the user's authorized office/site scope. | Must | Source-aligned intent; exact sharing rules TBD |
| FR-12 | The system shall support centralized access to permitted records across multiple offices/sites. | Must | Source-aligned |
| FR-13 | The system shall archive or soft-delete records instead of permanently removing them through ordinary user actions. | Must | Source-aligned |
| FR-14 | The system shall retain a history of relevant edits and archive actions sufficient to support accountability. | Must | Source-aligned; exact audit fields TBD |
| FR-15 | The system shall provide dashboard or summary views of project costs and related records to authorized users. | Should | Source-aligned outcome |
| FR-16 | The interface shall support mobile-sized screens for common site workflows. | Must | Source-aligned |
| FR-17 | The system shall validate required fields and reject invalid data before saving. | Must | Proposed data-integrity control |
| FR-18 | The system should warn about likely duplicate cost/bill entries based on agreed matching fields. | Should | Proposed response to duplicate-entry problem |
| FR-19 | The system shall identify the user and timestamp associated with relevant create/edit/archive actions. | Must | Proposed audit detail; validate |
| FR-20 | The system shall allow authorized users to review archived records and audit history. | Should | Proposed; access policy TBD |
| FR-21 | The system may provide exportable reports if stakeholders confirm the required formats and permissions. | Could | TBD |
| FR-22 | The system shall display clear feedback when a record is saved or an operation fails. | Should | Proposed usability requirement |

## 6. Non-functional requirements

The proposal identifies security, accountability, centralized information, and mobile usability as important concerns, but does not specify numerical service levels. The measurable targets below are candidates for stakeholder agreement, not confirmed commitments.

| ID | Quality attribute | Requirement / candidate acceptance measure | Priority |
|---|---|---|---|
| NFR-01 | Security | Protected pages and data operations shall require authentication. | Must |
| NFR-02 | Authorization | Server-side access checks shall enforce role and office/site permissions; hiding UI controls alone is insufficient. | Must |
| NFR-03 | Auditability | Relevant record changes and archive actions shall be traceable to an authenticated user and timestamp. | Must |
| NFR-04 | Data integrity | Invalid required fields shall not be saved; concurrent updates and duplicate prevention strategy require design validation. | Must |
| NFR-05 | Usability | Common tasks shall use clear labels, understandable validation messages, and consistent navigation. | Should |
| NFR-06 | Responsiveness | Core workflows shall remain usable on common mobile, tablet, and desktop viewport sizes. | Must |
| NFR-07 | Performance | Candidate target: common list/search requests complete within 3 seconds under an agreed representative test load. Confirm feasibility and test environment. | TBD |
| NFR-08 | Availability | Hosting and availability expectations must be agreed; no uptime percentage is defined in the proposal. | TBD |
| NFR-09 | Recoverability | Backup frequency, restore procedure, and recovery targets must be agreed before production use. | TBD |
| NFR-10 | Maintainability | Code and requirements shall use consistent naming and modular organization appropriate for a course project. | Should |
| NFR-11 | Compatibility | The web interface should be tested in current mainstream browsers selected for the course demonstration. | Should |
| NFR-12 | Privacy | Use only necessary personal data; access to financial and audit information shall be limited to authorized roles. | Must |

## 7. Use-case analysis

### UC-01: Record a project cost
- **Primary actor:** Operator
- **Preconditions:** User is authenticated and has permission for the selected project/site.
- **Main flow:** Open cost entry; select project/site; enter agreed cost details; validate input; save; show confirmation.
- **Alternate flows:** Missing/invalid fields produce actionable errors; unauthorized project selection is rejected; suspected duplicate prompts a warning if duplicate detection is implemented.
- **Postconditions:** A valid cost record exists and the action is traceable according to the audit policy.
- **Requirements:** FR-02, FR-03, FR-09, FR-11, FR-14, FR-17, FR-19.

### UC-02: Review project cost against budget
- **Primary actor:** Management or authorized viewer
- **Preconditions:** User has permission to view the project and budget.
- **Main flow:** Select project and period; system displays recorded cost and applicable budget; user reviews the summary.
- **Alternate flows:** If no budget exists, system clearly indicates that comparison is unavailable; unauthorized projects are not disclosed.
- **Postconditions:** No business record is changed.
- **Requirements:** FR-04, FR-05, FR-15, FR-11.

### UC-03: Record or review a bill
- **Primary actor:** Operator
- **Preconditions:** User is authorized for the relevant project/site.
- **Main flow:** Enter bill details and agreed references; validate; save; retrieve it through search when needed.
- **Alternate flows:** Missing mandatory information is rejected; duplicate warning behavior follows the agreed policy.
- **Postconditions:** Bill information is stored and traceable.
- **Requirements:** FR-07, FR-03, FR-09, FR-14, FR-17, FR-18.

### UC-04: Maintain stock information
- **Primary actor:** Authorized operator / stock staff
- **Preconditions:** User has permission to access the selected site or stock record.
- **Main flow:** Open stock module; view or enter an agreed stock record/transaction; validate; save; view updated information.
- **Alternate flows:** Invalid quantity or unauthorized site is rejected.
- **Postconditions:** Stock information reflects the accepted transaction according to confirmed stock rules.
- **Requirements:** FR-06, FR-09, FR-11, FR-17.
- **Open issue:** The proposal does not specify whether full receipt/issue/adjustment history is required.

### UC-05: Archive a record and inspect history
- **Primary actor:** Authorized administrator or other role approved by policy
- **Preconditions:** User is authenticated and permitted to archive or inspect the record.
- **Main flow:** Select record; request archive; system records the action; record is removed from ordinary active views but remains retrievable to authorized users; history is reviewed if permitted.
- **Alternate flows:** Unauthorized requests are rejected; repeated archive requests are handled safely.
- **Postconditions:** Record is retained rather than permanently erased through ordinary workflow, and the action is traceable.
- **Requirements:** FR-13, FR-14, FR-19, FR-20.
- **Open issue:** Exact restore permissions and retention rules require confirmation.

### UC-06: Administer user access
- **Primary actor:** Administrator
- **Preconditions:** Administrator is authenticated.
- **Main flow:** Create or update a user; assign role and permitted office/site scope; save; system enforces the resulting permissions.
- **Alternate flows:** Invalid role/scope is rejected; an unauthorized user cannot perform administration.
- **Postconditions:** Access policy reflects the saved configuration.
- **Requirements:** FR-08, FR-09, FR-11.
- **Open issue:** Password reset, account deactivation, and multi-factor authentication requirements are not specified in the proposal.

## 8. Data concept analysis

The following are conceptual entities, not a finalized database schema.

| Entity | Purpose | Candidate attributes to validate |
|---|---|---|
| User | Represents a system account | Identifier, name, login, role, status |
| Office / Site | Defines organizational access scope | Identifier, name, parent office if applicable |
| Project | Groups project work and records | Identifier, name, site/office, status, dates |
| Cost record | Records a cost entry | Identifier, project, category, amount, date, description, creator |
| Budget | Stores approved or planned budget information | Project/scope, period, amount, status |
| Stock item / stock record | Represents inventory information | Item code/name, unit, quantity, location |
| Bill record | Captures bill information | Reference, date, amount, project, attachment/metadata (TBD) |
| Audit event | Supports accountability | Actor, action, target record, timestamp, change summary |
| Archive state | Indicates archived versus active record | Status, archived by, archived at, reason (TBD) |

Amounts, currencies, tax, bill attachments, approval status, and required fields must be confirmed before the SRS baseline is finalized.

## 9. Business rules

| ID | Rule | Status |
|---|---|---|
| BR-01 | A user may access only functions allowed by their assigned role. | Required by proposed role-based access |
| BR-02 | Access to records shall respect office/site scope. | Required in principle; cross-site exceptions TBD |
| BR-03 | Viewer accounts shall not change business records. | Proposed; confirm |
| BR-04 | Ordinary deletion shall archive/soft-delete rather than permanently erase a record. | Source-aligned |
| BR-05 | Relevant create, edit, and archive actions shall be traceable. | Source-aligned intent; exact event types TBD |
| BR-06 | Cost totals and budget comparisons shall use agreed date, currency, and inclusion rules. | TBD |
| BR-07 | Duplicate detection must not silently discard legitimate similar transactions. | Proposed safeguard |
| BR-08 | A record correction policy shall specify who may edit, restore, or reverse archived records. | TBD |

## 10. Requirement prioritization and release recommendation

### Minimum viable course-project baseline
1. Authentication and role permissions.
2. Project/site records and access boundaries.
3. Cost entry, list, search, and filtering.
4. Budget entry and basic cost-versus-budget summary.
5. Bill record management.
6. Basic stock records.
7. Soft deletion/archive and audit history.
8. Responsive interface and input validation.

### Secondary enhancements
- Duplicate-entry warning.
- Richer dashboards and report filters.
- Exportable reports.
- More advanced audit-history viewing and record restoration.
- Low-stock alerts or approval workflows, only if confirmed by stakeholders.

Priorities should be reviewed after elicitation. This proposed ordering favors the core problems described in the proposal and should not be treated as stakeholder-approved scope.

## 11. Risks, assumptions, and constraints

### Assumptions to validate
- The first release serves one construction firm with multiple offices/sites.
- Users have individual accounts rather than sharing credentials.
- Web access is available during normal use; offline support is not assumed.
- Admin/operator/viewer are the initial role set.
- Costs, budgets, stock, and bills are the central record categories.

### Risks
- Unclear permissions may expose sensitive financial information.
- Missing business rules may cause inconsistent totals or stock balances.
- Poorly designed archive behavior may undermine accountability.
- Scope expansion may exceed course time.
- Mobile connectivity and device constraints may affect field usage.

### Constraints
- Academic project scope and schedule.
- Requirements must be feasible for a web programming course.
- No specific technology stack or numerical service-level target is provided by the proposal.

## 12. Traceability to proposal

| Proposal concern | Analysis response |
|---|---|
| Tally books and scattered spreadsheets | Centralized project, cost, budget, stock, and bill records |
| Duplicate/lost entries and overwrites | Validation, duplicate warning proposal, audit history |
| Difficult cost filtering | Search/filter requirements |
| No real-time multi-office picture | Centralized summaries with access boundaries |
| Missed bills and unclear responsibility | Bill records and traceable actions |
| Admin/operator/viewer challenge | Role-based authorization |
| Soft delete/archive challenge | Archive and history requirements |
| Multi-office data separation | Office/site access scope |
| Mobile-friendly interface | Responsive usability requirement |

## 13. Open questions

1. Which cost fields and categories are mandatory?
2. Are budgets assigned per project, phase, category, or time period?
3. Which costs count toward budget totals, and how are corrections handled?
4. Does stock require transaction-level history and automatic balance calculations?
5. Are bill images/files required, or are reference details enough?
6. Which roles can create, edit, archive, restore, or view audit history?
7. Can a user access multiple sites, and what information can management see across them?
8. Are approvals, comments, exports, or notifications needed?
9. What data backup, retention, and performance expectations apply?
10. What browser/device support will be used for acceptance testing?

## 14. Conclusion

The proposal supports a clear core: centralized construction project records, cost and budget visibility, stock and bill tracking, role-based access, office/site separation, auditability, and mobile usability. The largest remaining analysis gaps are detailed data fields, permission matrices, stock and bill workflows, budget calculations, and measurable quality targets. These must be validated before implementation requirements are considered final.

## 15. Reference

Rahman, Toufikur. *ConstructFlow: A Web-Based Cost Tracking and Management System for a Construction Firm to track their cost, budget, stock and bills.* CSE 309 Web Programming Project Topic Proposal, Independent University, Bangladesh, submitted 24 September 2026.
