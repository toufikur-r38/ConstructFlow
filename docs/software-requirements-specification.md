# Software Requirements Specification (SRS)
## ConstructFlow: A Web-Based Cost Tracking and Management System

| Document field | Value |
|---|---|
| Project | ConstructFlow |
| Course | CSE 309 — Web Programming |
| Department / institution | Department of Computer Science and Engineering, Independent University, Bangladesh |
| Prepared by | Toufikur Rahman |
| Proposal submission date | 24 September 2026 |
| SRS version | 1.0 — Initial draft |
| Date | 16 October 2026 |
| Status | Proposed baseline; stakeholder and supervisor validation required |

> **Document status note:** This SRS follows a conventional IEEE-style organization for software requirements. It is not claimed to be formally certified against a particular IEEE edition. The project proposal is the primary source. Requirements added to make the specification testable are marked as proposed or subject to validation.

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification defines the intended behavior, interfaces, constraints, and quality expectations for ConstructFlow. It is intended for the student developer, project supervisor, testers, and representative users who review the proposed system.

The SRS establishes a baseline for design, implementation, and acceptance testing. Unresolved business rules must be decided before the related features are considered final.

### 1.2 Document conventions
- **Shall** indicates a requirement proposed as mandatory for the defined baseline.
- **Should** indicates an important requirement that may be negotiated.
- **May** indicates an optional capability.
- **TBD** indicates a detail that has not been established and requires a decision.
- Requirement identifiers (FR, NFR, IR, and BR) support traceability.
- “Proposed / validate” means the requirement is a reasonable operationalization of the proposal, but has not been explicitly confirmed by stakeholders.

### 1.3 Intended audience
- Project author and implementation team.
- Course instructor / project supervisor.
- Testers and reviewers.
- Construction-firm representatives, if available for validation.

### 1.4 Product scope
ConstructFlow is a web-based system intended to help small and mid-sized construction firms centralize information about projects, costs, budgets, stock, and bills. The system aims to reduce reliance on separate tally books and spreadsheets, improve cost retrieval and visibility, support coordination across offices/sites, and improve accountability through role-based permissions and record history.

The initial role model includes administrator, operator, and viewer. The interface should be usable on mobile devices because data entry may occur at construction sites.

### 1.5 References
1. Rahman, Toufikur. *ConstructFlow: A Web-Based Cost Tracking and Management System for a Construction Firm to track their cost, budget, stock and bills.* CSE 309 Web Programming Project Topic Proposal, Independent University, Bangladesh, submitted 24 September 2026.
2. *ConstructFlow Requirements Elicitation Document*, `docs/requirements-elicitation.md`.
3. *ConstructFlow Requirements Analysis Document*, `docs/requirements-analysis.md`.

## 2. Overall description

### 2.1 Product perspective
ConstructFlow is planned as a centralized web application. Authorized users will access shared system services through a browser, while the system limits which functions and records each user can access. The proposal does not specify a required technology stack, hosting platform, database, or external integration.

### 2.2 Product functions
At a high level, the system is expected to:
- Maintain project/site information.
- Record, list, search, and filter project costs.
- Store budget information and show a basic comparison with recorded costs.
- Maintain stock information.
- Record and retrieve bill information.
- Authenticate users and enforce admin/operator/viewer permissions.
- Separate data according to authorized office/site scope while keeping the system centralized.
- Archive records rather than permanently delete them through normal user workflows.
- Retain traceability for relevant edits and archive actions.
- Provide dashboard or summary views for permitted users.
- Support common workflows on mobile-sized screens.

### 2.3 User classes and characteristics

| User class | Expected capability | Notes |
|---|---|---|
| Administrator | Manage accounts, roles, access scope, and approved administrative operations | Exact archive and audit privileges are TBD |
| Operator | Enter and maintain permitted project, cost, bill, and stock records | Exact correction and approval privileges are TBD |
| Viewer | View permitted records and summaries | Read-only interpretation is proposed and requires confirmation |
| Management / project manager | Review project cost and budget summaries | May use an admin or viewer role; mapping TBD |
| Site / office staff | Use permitted functions from site/office locations | Mobile usability is important |

The proposal explicitly names admin, operator, and viewer. Additional descriptions are analysis-level actor groupings, not confirmed job titles.

### 2.4 Operating environment
- Web browser on desktop, tablet, or mobile device.
- Network access to the hosted application is assumed for the initial release.
- Supported browser versions and hosting requirements: TBD.
- Offline operation is not included unless separately approved.

### 2.5 Design and implementation constraints
- The project is being developed for the CSE 309 Web Programming course.
- The application must address the stated construction cost-tracking problem.
- Role-based access, office/site data separation, soft deletion/archive, and mobile-friendly use are core design concerns.
- No programming language, framework, database, or deployment platform is mandated by the proposal.

### 2.6 User documentation
At minimum, the release should include brief instructions for login, role permissions, creating and finding records, reviewing summaries, and archiving/correcting records. The exact format is an implementation decision.

### 2.7 Assumptions and dependencies
- The initial system is assumed to support one construction firm operating across multiple offices/sites; confirm this assumption.
- Users are assumed to have individual accounts.
- Users are assumed to have network access while using the application.
- Required cost categories, bill fields, stock rules, and budget calculations will be confirmed before implementation.
- Access to sample forms or workflows depends on stakeholders making non-sensitive examples available.

## 3. External interface requirements

### 3.1 User interface
**UIR-01:** The system shall provide a consistent navigation structure for the main project, cost, budget, stock, bill, and account functions.

**UIR-02:** The system shall provide forms with clearly labeled fields and identify required inputs.

**UIR-03:** The system shall display understandable validation and operation-result messages.

**UIR-04:** The interface shall adapt to common mobile, tablet, and desktop viewport sizes and keep core workflows usable on mobile screens.

**UIR-05:** The system shall visually distinguish active records from archived records where both are shown.

**UIR-06:** Controls and views shall be shown or enabled according to the user's permissions, while server-side authorization remains the enforcement mechanism.

Detailed wireframes, color palette, accessibility conformance target, and exact navigation labels are TBD.

### 3.2 Hardware interfaces
No direct hardware interface is specified. The system is expected to run in a browser on ordinary user devices. Any printer, barcode scanner, or other peripheral integration is out of scope unless approved.

### 3.3 Software interfaces
- A supported web browser is required.
- The application will use a persistent data store, but its product and version are TBD.
- No external accounting, banking, payment, or inventory integration is specified.
- File upload for bill images or documents is TBD and must not be assumed as required.

### 3.4 Communications interfaces
The application will communicate over a network using standard web communication mechanisms selected during design. Production deployment should use encrypted transport (HTTPS). Exact hosting, domain, and deployment configuration are TBD.

## 4. System features and functional requirements

### 4.1 Authentication and access control

**FR-001 — User authentication (proposed baseline).** The system shall require a user to authenticate before accessing protected records or functions.

**FR-002 — Role-based authorization.** The system shall support the roles administrator, operator, and viewer.

**FR-003 — Permission enforcement.** The system shall authorize each protected operation according to the user's role and assigned scope. Enforcement shall not rely only on hiding interface controls.

**FR-004 — Viewer restriction (proposed; validate).** A viewer shall be able to view permitted records but shall not create, edit, archive, or delete business records.

**FR-005 — User administration (proposed; validate).** An authorized administrator shall be able to create or update user accounts and assign a role and permitted office/site scope.

**FR-006 — Access denial.** When a user attempts an operation or record access they are not authorized to perform, the system shall deny the request and shall not disclose the protected record contents.

Acceptance checks:
- An unauthenticated user cannot access protected pages or data operations.
- A viewer cannot modify a record by using a direct request.
- A user cannot retrieve a record outside their authorized office/site scope.
- Only authorized administrators can change user roles or access scope.

### 4.2 Project and site records

**FR-010 — Project record management (proposed).** The system shall allow authorized users to create and view project records.

**FR-011 — Project record updates (proposed).** The system shall allow updates to project details only to roles permitted by the access policy.

**FR-012 — Project/site association (proposed).** Project records shall be associated with an office or site according to the agreed organizational model.

**FR-013 — Project retrieval.** The system shall allow authorized users to find projects they are permitted to access.

Acceptance checks:
- A permitted user can create and retrieve a valid project record.
- An unauthorized user cannot view or update a project outside their scope.
- Mandatory project fields and the office/site relationship are confirmed before implementation.

### 4.3 Cost tracking

**FR-020 — Cost entry.** The system shall allow authorized users to record project-related costs.

**FR-021 — Cost validation.** The system shall validate required cost fields and reject invalid entries with a clear explanation.

**FR-022 — Cost listing.** The system shall display cost records that the user is authorized to access.

**FR-023 — Cost search and filtering.** The system shall allow users to search or filter cost records using agreed criteria, including cost type/category if that field is adopted.

**FR-024 — Cost correction.** The system shall support corrections only according to the agreed role and audit policy. Corrections to existing records shall not silently erase required history.

**FR-025 — Duplicate-entry assistance (proposed).** The system should warn users when a new cost entry appears to match an existing entry according to matching rules agreed during analysis. The system shall not silently discard a legitimate entry solely because it resembles another entry.

Acceptance checks:
- A valid cost entry can be saved and retrieved by an authorized user.
- Missing or invalid required data is rejected.
- A user can narrow results using confirmed filter fields.
- Relevant edits are traceable according to Section 4.8.
- Duplicate matching fields and warning behavior are specified before testing.

### 4.4 Budget and cost summaries

**FR-030 — Budget record management (proposed).** The system shall allow authorized users to record and retrieve budget information for the agreed project scope and period.

**FR-031 — Cost-versus-budget view.** The system shall present recorded costs and the applicable budget together when sufficient valid data exists.

**FR-032 — Missing budget state.** If no applicable budget exists, the system shall clearly indicate that a budget comparison is unavailable rather than presenting a misleading result.

**FR-033 — Summary scope.** Budget and cost summaries shall include only records that the user is authorized to access and that satisfy the agreed date, status, and calculation rules.

Acceptance checks:
- An authorized user can save and retrieve a budget.
- Given a defined budget and defined included costs, the displayed comparison matches the agreed calculation rule.
- If no budget exists, the UI communicates the missing state.
- Currency, time period, and treatment of archived/corrected records are agreed before implementation.

### 4.5 Stock management

**FR-040 — Stock records.** The system shall allow authorized users to maintain stock information.

**FR-041 — Stock validation.** The system shall validate required stock fields and reject invalid values according to the confirmed unit and quantity rules.

**FR-042 — Stock visibility.** Users shall only view stock information within their permitted access scope.

**FR-043 — Stock transaction model (TBD).** Whether the first release records only current quantities or records receipts, issues, adjustments, and transaction history must be decided before implementation.

Acceptance checks:
- Authorized users can create and retrieve agreed stock records.
- Invalid required fields are rejected.
- Stock access respects office/site permissions.
- Stock balance calculations are tested only after the transaction model is confirmed.

### 4.6 Bill management

**FR-050 — Bill record entry.** The system shall allow authorized users to record bill information using fields agreed during requirements validation.

**FR-051 — Bill retrieval.** The system shall allow authorized users to search for and retrieve bill records.

**FR-052 — Bill association (proposed).** Where applicable, a bill record shall be associated with a project and/or cost record according to the agreed data model.

**FR-053 — Bill supporting files (TBD).** Whether the system stores uploaded bill images/documents or only bill metadata must be confirmed.

**FR-054 — Bill auditability.** Relevant bill-record changes and archive actions shall be traceable according to Section 4.8.

Acceptance checks:
- An authorized user can create and retrieve a valid bill record.
- Required bill fields and duplicate-warning rules are documented.
- A bill is visible only to authorized users.
- File handling is tested only if attachment support is approved.

### 4.7 Office/site separation and centralized access

**FR-060 — Centralized system.** The system shall provide a centralized application for permitted records from multiple offices/sites.

**FR-061 — Scope-based access.** The system shall restrict users to the offices, sites, projects, and records assigned by the approved access policy.

**FR-062 — Cross-site summaries.** Cross-site or cross-office summaries shall be shown only to roles explicitly authorized to see them.

**FR-063 — Scope consistency.** Search, list, detail, and summary functions shall apply the same access restrictions.

Acceptance checks:
- Test users with different scopes see only their authorized records.
- Search and dashboard functions do not reveal restricted record names, counts, or details unless explicitly permitted.
- Management's cross-site access rules are agreed and tested.

### 4.8 Archive and audit history

**FR-070 — Soft deletion/archive.** The system shall support archiving or soft-deleting records instead of permanently deleting them through ordinary application workflows.

**FR-071 — Edit history.** The system shall preserve traceability for relevant record edits as defined by the audit policy.

**FR-072 — Action attribution (proposed).** Audit entries shall identify the authenticated actor, action type, affected record, and timestamp for relevant create/edit/archive actions.

**FR-073 — Audit access.** Audit history shall be visible only to authorized roles.

**FR-074 — Archived-record handling.** Archived records shall be distinguishable from active records and shall not appear in ordinary active lists unless the user selects an approved archived-record view.

**FR-075 — Restore and retention policy (TBD).** Permissions for restoring records, retention duration, and any permanent purge process must be defined before implementation.

Acceptance checks:
- Archiving a record does not remove it permanently from the underlying retained record history.
- A permitted reviewer can identify who performed a relevant action and when.
- Unauthorized users cannot inspect audit history.
- Restore and retention behavior follows the approved policy.

### 4.9 Dashboard and reporting

**FR-080 — Dashboard summary (proposed).** The system should provide a summary of project costs and related information appropriate to the user's permissions.

**FR-081 — Consistent totals.** Dashboard figures shall use the same approved calculation rules as detailed records and budget comparisons.

**FR-082 — Report export (optional/TBD).** Export to CSV, PDF, or other formats may be added if stakeholders specify the needed formats and permissions.

Acceptance checks:
- Dashboard information reflects the underlying authorized records.
- Totals match agreed test data and calculation rules.
- Export is not considered part of the baseline until explicitly approved.

### 4.10 Usability and feedback

**FR-090 — Responsive interface.** Core data-entry and record-review workflows shall remain usable on common mobile-sized screens.

**FR-091 — Operation feedback.** The system shall communicate whether a save, update, archive, or other operation succeeded or failed.

**FR-092 — Form feedback.** Validation messages shall identify the field or issue requiring attention where practicable.

**FR-093 — Consistent navigation.** The main system modules shall use consistent navigation and terminology.

Acceptance checks:
- Test the core workflows on agreed mobile and desktop viewport sizes.
- Users can distinguish successful save from validation or server failure.
- Common forms expose required fields and actionable errors.

## 5. Non-functional requirements

The original proposal does not specify numerical performance, uptime, recovery, or accessibility targets. Proposed measurable targets below must be reviewed for feasibility and formally agreed before being treated as contractual acceptance criteria.

### 5.1 Security

**NFR-001:** The application shall enforce authentication for protected operations.

**NFR-002:** Authorization shall be checked on the server for each protected read or write operation.

**NFR-003:** The application shall use HTTPS in a production deployment.

**NFR-004:** Passwords, if locally managed, shall not be stored as plaintext; an established password-hashing mechanism shall be used.

**NFR-005:** Error messages shall not expose secrets, credentials, or unauthorized record contents.

### 5.2 Data integrity and auditability

**NFR-010:** Required fields and data types shall be validated before records are accepted.

**NFR-011:** Relevant create/edit/archive events shall be traceable according to the approved audit policy.

**NFR-012:** Financial and stock calculations shall follow documented rules and be tested against known examples.

**NFR-013:** The application shall prevent unauthorized changes to records and permissions.

### 5.3 Usability and responsiveness

**NFR-020:** Core workflows shall be usable on agreed mobile, tablet, and desktop viewport sizes without requiring desktop-only interactions.

**NFR-021:** Forms shall use readable labels, clear validation messages, and consistent interaction patterns.

**NFR-022:** The system should minimize unnecessary steps for common cost and bill entry; final usability criteria should be checked with representative users if available.

### 5.4 Performance

**NFR-030 — Candidate response-time target:** Common list and search operations should complete within 3 seconds under a representative test dataset and agreed test environment. This is a proposed target, not a value supplied by the project proposal.

**NFR-031:** The test report shall state the test dataset, environment, and operation measured when performance is evaluated.

### 5.5 Reliability, backup, and recovery

**NFR-040:** Backup frequency, backup storage, restoration procedure, and recovery targets shall be defined before any production use.

**NFR-041:** The system shall provide understandable failure feedback and shall avoid reporting a failed save as successful.

**NFR-042:** Availability and uptime targets are TBD because the proposal does not define hosting or service expectations.

### 5.6 Maintainability and compatibility

**NFR-050:** The implementation should use consistent naming, modular organization, and version control suitable for a course project.

**NFR-051:** The application shall be tested in the browsers and versions agreed for demonstration.

**NFR-052:** Dependencies, setup instructions, and required environment configuration should be documented in the repository.

### 5.7 Privacy

**NFR-060:** Access to financial and audit information shall be restricted to authorized users.

**NFR-061:** Development and testing should use anonymized sample records rather than unnecessary real financial or personal information.

## 6. Data requirements

### 6.1 Conceptual data entities
The following entities describe the conceptual information that may be required. This section is not a final database schema.

| Entity | Description | Candidate data (validate) |
|---|---|---|
| User | Account and assigned permissions | User ID, display name, login, role, status |
| Office/Site | Organizational access boundary | ID, name, parent relationship if needed |
| Project | Project identity and status | ID, name, site/office, dates, status |
| Cost record | A recorded project cost | ID, project, category, date, amount, description, creator |
| Budget | Budget for a defined project scope/period | ID, project/scope, period, amount, status |
| Stock item / stock record | Item and its stock information | ID, item name/code, unit, quantity, location |
| Bill record | Bill information | ID/reference, date, amount, project/cost association, attachment reference if approved |
| Audit event | Trace of relevant user actions | ID, actor, action, target record, timestamp, change summary |
| Archive state | Active/archive status | Status, archived by, archived at, reason if required |

### 6.2 Data validation
- Mandatory fields must be identified for each entity before implementation.
- Amount and quantity fields must use agreed numeric precision and validation rules.
- Date formats and timezone behavior must be consistent.
- Currency and rounding rules must be confirmed.
- Referential integrity between projects, costs, bills, and sites must be enforced where relationships are adopted.
- Duplicate detection criteria must be defined without assuming that similar values always indicate a duplicate.

### 6.3 Data retention
Archived-record retention, backup retention, and permanent deletion rules are TBD. Ordinary user workflows shall not permanently erase records where the archive requirement applies.

## 7. Business rules

**BR-001:** Access to protected functions shall be based on the user's assigned role.

**BR-002:** Access to records shall respect the user's authorized office/site scope.

**BR-003:** The viewer role is intended to be read-only; confirm the exact restrictions before implementation.

**BR-004:** Ordinary record removal shall use archive/soft-delete behavior rather than permanent deletion.

**BR-005:** Relevant edits and archive actions shall be traceable.

**BR-006:** Cost and budget summaries shall use approved rules for date range, currency, record status, and inclusion of corrected or archived records.

**BR-007:** Stock balances shall follow the confirmed stock transaction model.

**BR-008:** Bill fields, bill-to-cost relationships, and supporting-file behavior shall follow the approved bill workflow.

**BR-009:** The system shall not show cross-site summaries to users unless their permissions explicitly allow it.

## 8. Use cases

### UC-01: Enter a cost
- **Actor:** Operator.
- **Precondition:** Authenticated user has permission for the project/site.
- **Trigger:** User selects the cost-entry function.
- **Main flow:** Select project/site; enter required cost details; validate; save; show confirmation.
- **Alternatives:** Invalid fields are explained; unauthorized scope is rejected; suspected duplicate warning is displayed if implemented.
- **Postcondition:** Cost record is stored and relevant action history is retained.
- **Related requirements:** FR-020 to FR-025, FR-060 to FR-063, FR-070 to FR-072.

### UC-02: Review budget and cost
- **Actor:** Authorized management user or viewer.
- **Precondition:** User can view the selected project.
- **Main flow:** Select project and agreed period; view budget and recorded cost summary.
- **Alternatives:** If no budget exists, the system indicates that comparison is unavailable.
- **Postcondition:** No record is changed.
- **Related requirements:** FR-030 to FR-033, FR-080 to FR-081.

### UC-03: Record and retrieve a bill
- **Actor:** Operator.
- **Precondition:** User has permission for the relevant project/site.
- **Main flow:** Enter required bill information; validate; save; search and retrieve the record later.
- **Alternatives:** Invalid fields are rejected; duplicate-warning behavior follows the approved rule.
- **Postcondition:** Bill record is available to authorized users and relevant changes are traceable.
- **Related requirements:** FR-050 to FR-054.

### UC-04: Maintain stock information
- **Actor:** Authorized operator or stock staff.
- **Precondition:** User has access to the relevant site.
- **Main flow:** View or enter the agreed stock record/transaction; validate; save; review updated information.
- **Alternatives:** Invalid quantity or unauthorized site access is rejected.
- **Postcondition:** Stock information is stored according to the confirmed stock model.
- **Related requirements:** FR-040 to FR-043.

### UC-05: Archive a record
- **Actor:** Role authorized by the final policy.
- **Precondition:** User is authenticated and permitted to archive the record.
- **Main flow:** Select record; request archive; system records the action and marks the record archived; show confirmation.
- **Alternatives:** Unauthorized action is rejected; repeated requests are handled safely.
- **Postcondition:** Record is retained and distinguishable from active records.
- **Related requirements:** FR-070 to FR-075.

### UC-06: Administer user access
- **Actor:** Administrator.
- **Precondition:** Administrator is authenticated.
- **Main flow:** Create or update account; assign role and office/site scope; save; system enforces the new permissions.
- **Alternatives:** Invalid or unauthorized permission changes are rejected.
- **Postcondition:** Account permissions reflect the saved configuration.
- **Related requirements:** FR-001 to FR-006.

## 9. Acceptance criteria overview

The release should not be accepted until the agreed test cases demonstrate at least the following:

1. Authentication protects all restricted functions.
2. Admin, operator, and viewer permissions behave according to an approved permission matrix.
3. Office/site restrictions apply consistently to direct record views, searches, and summaries.
4. Authorized users can create and retrieve project, cost, budget, stock, and bill records included in the release.
5. Invalid required fields are rejected with clear messages.
6. Cost search and filtering work for the confirmed criteria.
7. Budget comparisons match agreed calculations using a known test dataset.
8. Archive behavior retains records and relevant history instead of permanently deleting them through ordinary workflows.
9. Audit history identifies the actor, action, target, and timestamp for agreed event types.
10. Core workflows remain usable at the agreed mobile and desktop viewport sizes.
11. Any agreed performance target is verified in a documented test environment.
12. Unresolved TBD items that affect released functionality are decided or explicitly excluded.

## 10. Traceability matrix

| Proposal statement / concern | SRS coverage |
|---|---|
| Track costs, budgets, stock, and bills | FR-020–025, FR-030–033, FR-040–043, FR-050–054 |
| Multiple tally books and spreadsheets | Section 1.4, FR-010–013, FR-020–023 |
| Duplicate or lost cost entries | FR-021, FR-025, NFR-010 |
| Editing overwrites prior information | FR-024, FR-070–075, NFR-011 |
| Difficult cost filtering | FR-023 |
| No real-time picture across offices/sites | FR-060–063, FR-080–081 |
| Missed bills and unclear responsibility | FR-050–054, FR-070–073 |
| Admin/operator/viewer access | FR-001–006 |
| Soft deletion/archive | FR-070–075, BR-004 |
| Multi-office data separation | FR-060–063, BR-002, BR-009 |
| Mobile-friendly site use | UIR-04, FR-090–093, NFR-020–022 |

## 11. Open issues and TBD register

| ID | Decision required | Why it matters |
|---|---|---|
| TBD-01 | Confirm one firm/multiple offices versus multi-firm tenancy | Determines data model and access boundaries |
| TBD-02 | Define project, cost, budget, stock, and bill mandatory fields | Needed for forms, validation, and testing |
| TBD-03 | Define cost categories, currency, tax, and rounding rules | Needed for accurate totals |
| TBD-04 | Define budget scope, period, and comparison formula | Needed for budget summaries |
| TBD-05 | Decide stock current-balance versus transaction-history model | Affects stock behavior and integrity |
| TBD-06 | Decide bill attachments versus metadata-only records | Affects storage and interface requirements |
| TBD-07 | Approve role-permission matrix, including edit/archive/restore/audit permissions | Required for security testing |
| TBD-08 | Define office/site sharing and management visibility | Required for cross-site access |
| TBD-09 | Define audit events, change detail, and retention period | Required for accountability |
| TBD-10 | Decide duplicate matching rules | Prevents both duplicates and false warnings |
| TBD-11 | Confirm reports, filters, and export formats | Determines dashboard/report scope |
| TBD-12 | Confirm offline use, performance, availability, backup, and recovery expectations | Not specified in proposal |
| TBD-13 | Confirm browser support and accessibility target | Needed for compatibility and UI testing |

## 12. Appendices

### Appendix A — Suggested minimum role matrix (proposed; approval required)

| Operation | Administrator | Operator | Viewer |
|---|---|---|---|
| View records within authorized scope | Yes | Yes | Yes |
| Create cost/bill/stock records | Configurable | Yes, within scope | No |
| Edit business records | Configurable | Within approved policy | No |
| Archive records | Yes, proposed | TBD | No |
| Manage users and roles | Yes | No | No |
| View audit history | Yes, proposed | TBD | No by default |
| View cross-office summaries | Only if authorized | Only if authorized | Only if authorized |

This is a starting proposal, not a confirmed authorization policy. The final matrix must be approved before implementation.

### Appendix B — Suggested test data
Use fictional project names, dates, amounts, stock items, bills, users, and offices. Include:
- Two offices/sites with different user permissions.
- At least two projects with separate budgets.
- Several cost categories and dates.
- One missing-budget case.
- Active and archived records.
- A suspected duplicate and a legitimate similar transaction.
- Stock records with valid and invalid quantities.
- Bill records with complete and incomplete required fields.

### Appendix C — Change history

| Version | Date | Description |
|---|---|---|
| 1.0 | 16 October 2026 | Initial SRS draft based on the ConstructFlow project proposal; assumptions and open issues identified |

## 13. Approval

This document is a proposed requirements baseline and requires review. Approval should be recorded after the project supervisor and, if available, representative stakeholders validate the scope, priorities, and TBD decisions.

| Reviewer | Name / role | Status / date |
|---|---|---|
| Project author | Toufikur Rahman | Pending |
| Course instructor / supervisor | Md Abu Sayed, Lecturer, CSE Department | Pending |
| Representative user / stakeholder | TBD | Pending |
