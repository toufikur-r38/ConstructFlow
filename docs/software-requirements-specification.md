# Software Requirements Specification

| Document control | Value |
|---|---|
| Project | ConstructFlow — Construction Ledger and Cost Management |
| Author | Toufikur Rahman · ID 2420826 · Section 01 |
| Course / institution | CSE 309 — Web Programming · Independent University, Bangladesh |
| Submitted to | Md Abu Sayed, Lecturer, Department of Computer Science and Engineering |
| Version / date | 1.1 · 16 October 2026 |
| Status | Submission-ready source-based specification; stakeholder approval pending |


## 1. Introduction

### 1.1 Purpose and audience

This specification defines ConstructFlow's intended behavior and acceptance basis for the student developer, supervisor, testers and construction-firm representatives. It uses a conventional IEEE-style SRS organization: introduction, overall description, interfaces, functional requirements, data, quality attributes and verification. Formal compliance with a specific standard edition is not claimed.

### 1.2 Scope

ConstructFlow centralizes construction project costs and budgets to reduce fragmented records, difficult retrieval and untraceable changes. The proposal additionally requires stock, bill tracking, office/site separation and mobile usability. The README documents the present ledger, authentication, correction, reporting and operational baseline. Proposal obligations absent from R remain explicit implementation gaps.

Payroll, banking/payment processing, tax filing, full ERP, external accounting integrations, native mobile apps, unrelated-firm multi-tenancy and offline synchronization are excluded from this specification unless approved through change control. These boundaries are analyst proposals.

### 1.3 Conventions

“Shall” identifies a required outcome for the proposed baseline. FR and NFR IDs are stable across the companion documents. Must/Should priorities are analyst recommendations. A source-supported requirement is not a claim that implementation passes acceptance. D requirements and unresolved details require validation before baseline approval; a TBD is not a completed, testable commitment.

## Source and evidence register

| Code | Source | Authority and limits |
|---|---|---|
| P | *CSE309_project_proposal.pdf*, Toufikur Rahman, submitted 24 September 2026, pp. 1–2 | Primary business scope. Section 1 names cost, budget, stock and bills; sections 2–3 describe operational problems; section 4 identifies roles, archive/history, office separation and mobile use; section 5 describes expected outcomes. |
| R | [Repository README](https://github.com/toufikur-r38/ConstructFlow/blob/f2af045eaea023b78e60110c45085b08eae31d3f/README.md), reviewed 16 October 2026 | Current documented technical/feature baseline. README blob: `4f7e2cb6b09a4f601c511ce4344a04473f17698f`. Descriptions are not proof of successful runtime tests. |

**Evidence labels:** **P** = explicit proposal intent; **R** = README-documented capability or constraint; **D** = derived requirement, unverified and awaiting validation. **P / implementation unverified** preserves a proposal obligation absent from the README. Any detailed behavior beyond the cited source is explicitly labeled D. No interviews, observations, stakeholder approvals, production tests, or performance measurements are claimed.

The proposal governs intended business scope; the README governs the documented implementation baseline. A missing README feature is a gap to resolve, not permission to silently remove it from scope. Priorities are analyst recommendations, not stakeholder decisions.

### 1.4 Related documents and glossary

- [Requirements Elicitation Document](requirements-elicitation.md): method selection, planned consultation and evidence limits.
- [Requirements Analysis Document](requirements-analysis.md): scope reconciliation, use cases, data concepts and dependencies.

| Term | Meaning |
|---|---|
| Project ledger | Central records of projects, budgets and related expenditure |
| Late cost | Cost entered using the completed-project workflow documented in R |
| Void / restore | Retain an inactive record / return it through a controlled workflow |
| Audit snapshot | Preserved record information supporting review of a change |
| Module access | Assignment to a workspace; does not itself establish office isolation |
| Super-admin | Separate system-owner flag documented by R; exact powers unverified |
| RPO / RTO | Maximum acceptable data-loss interval / recovery-time objective; values TBD |

## 2. Overall description

### 2.1 Product perspective and functions

ConstructFlow is a centralized browser-based Flask application. The README documents an app factory, environment configuration, SQLAlchemy models, account/admin/auth modules, and Construction routes, services, templates and utilities. Shared templates and English/Bangla JSON resources support the UI. The module hub allows assignment to Construction and future extensibility; future modules are not specified requirements.

The documented functions cover authentication, role and module authorization, project registration, running and late costs, edit/void/restore with snapshots, managed categories, financial dashboards, filtered PDF/Excel reports, large ZIP exports, account maintenance, logs and manual database backup.

### 2.2 Users

Viewer, operator and admin are named roles. Super-admin is a separate flag rather than an assumed fourth role. Management, accountants, site/store staff and backup operators are stakeholder categories to map to accounts and permissions during D-01/D-08. Their names do not grant additional privileges.

### 2.3 Operating environment and constraints

| Area | Documented baseline R |
|---|---|
| Application | Python / Flask; Flask-Login; SQLAlchemy; Flask-Migrate/Alembic |
| Data | PostgreSQL-ready configuration; DATABASE_URL required outside development |
| Local fallback | SQLite when DATABASE_URL is absent and FLASK_ENV=development or FLASK_DEBUG=1 |
| Cache / rate limits | Redis support; Redis or another persistent rate-limit backend required outside development |
| Security configuration | SECRET_KEY required outside development; secure production cookies; CSRF, rate limiting and security headers |
| CSRF lifetime | README example WTF_CSRF_TIME_LIMIT=3600 means one hour; not a claimed mandatory immutable value |
| Backup tooling | DATABASE_URL and PostgreSQL client tools including pg_dump |
| Client | Browser and network access; device/browser versions D-06 |

Runtime dependency versions are maintained in requirements.txt, not invented here. Hosting provider, server sizing, domain, network architecture and workload limits are unverified. Production transport shall use HTTPS (**D**, derived security requirement; deployment verification pending).

### 2.4 Assumptions, dependencies and documentation

One firm with multiple offices/sites is the working interpretation of P; unrelated-firm tenancy is not established. Individual accounts and online access are proposed assumptions. Availability of staff and anonymized examples affects validation. User documentation should explain login, permissions, entry, correction, reports and recovery responsibilities (**D**); the README already supplies setup and backup commands.

## 3. External interface requirements

### 3.1 User interfaces

| Entry point documented in R | Purpose / linked requirements |
|---|---|
| /login, /modules, /construction/ | Authentication and module entry; FR-001–FR-003 |
| /construction/admin-dashboard, /construction/operator-dashboard, /construction/viewer-dashboard | Role dashboards; FR-011 |
| /construction/add-project, /construction/view-projects | Project ledger; FR-006 |
| /construction/add-cost, /construction/view-costs | Cost entry, review and report/export workflow; FR-007, FR-012 |
| /construction/dropdown-options, /construction/audit-log | Category administration and history; FR-009–FR-010 |
| /register, /account/profile, /account/change-password | User/account management; FR-004–FR-005 |

These URLs describe navigation, not a public API or permission matrix. The system shall use clear field labels, actionable validation feedback and distinguishable operation results (**D**, FR-019). Core mobile use is required by P; exact viewports and accessibility target are D-06. No accessibility certification is asserted.

### 3.2 Software, communications and hardware interfaces

The browser communicates with the Flask application over web requests. SQLAlchemy/database configuration and migrations support persistence. Redis can support cache/rate-limit storage. The backup script invokes PostgreSQL tooling. Reports produce PDF/Excel and, for large exports, ZIP files. No REST API contract, banking/accounting integration, scanner, specialized device or bill-upload interface is source-confirmed.

The system shall apply the same approved authorization rules to UI and direct requests (**D** operationalization of FR-002/FR-016). Security controls must remain effective when controls are hidden in the UI.

## 4. Functional requirements

Each acceptance check is a planned verification scenario, not a reported result. “Authorized” depends on D-01 and, for office scope, D-08. Features marked “implementation unverified” must not be represented as delivered.

### FR-001 — Authentication

**Requirement:** The system shall authenticate users before access to protected functions and provide logout.

**Evidence:** P §4; R Features, Main URLs. **Priority:** Must.

**Acceptance:** Valid login grants a session; invalid login does not; a logged-out request cannot access protected records.

### FR-002 — Roles

**Requirement:** The system shall enforce viewer, operator and admin authorization on protected operations.

**Evidence:** P §4; R Features. **Priority:** Must.

**Acceptance:** Attempt permitted and forbidden operations using each role; forbidden direct requests cause no data change.

### FR-003 — Module access

**Requirement:** The system shall enforce assigned Construction module access through the module hub.

**Evidence:** R Features, Structure. **Priority:** Must.

**Acceptance:** An assigned user enters Construction; an unassigned user is denied both hub entry and a direct module request.

### FR-004 — User administration

**Requirement:** The system shall provide authorized user management and module assignment, retaining a separate super-admin flag.

**Evidence:** R Features, Structure, Main URLs. **Priority:** Must.

**Acceptance:** An authorized administrator changes a test assignment; access follows it. Exact admin versus super-admin powers require D-01.

### FR-005 — Account maintenance

**Requirement:** The system shall provide profile and password-change functions for authenticated users.

**Evidence:** R Structure, Main URLs. **Priority:** Should.

**Acceptance:** A user accesses their profile and changes their password; password policy and reset flow require D-01.

### FR-006 — Project registry

**Requirement:** The system shall maintain project records with firm/tender details, work order year, budget, status and completion date.

**Evidence:** P §§1–2; R Features. **Priority:** Must.

**Acceptance:** Create and retrieve a project with those fields; validate mandatory-field rules after D-02 is resolved.

### FR-007 — Cost entry

**Requirement:** The system shall support cost entry for running projects and a late-cost workflow for completed projects.

**Evidence:** P §§1–2; R Features. **Priority:** Must.

**Acceptance:** Record a running-project cost and a completed-project late cost; verify the workflow distinction and saved project association.

### FR-008 — Controlled corrections

**Requirement:** The system shall support edit, void and restore workflows with password confirmation and audit snapshots.

**Evidence:** P §4; R Features. **Priority:** Must.

**Acceptance:** Correct, void and restore a test record; check password confirmation, retained snapshots and resulting active record state.

### FR-009 — Audit review

**Requirement:** The system shall provide authorized review of record history through the audit hub.

**Evidence:** P §§2,4; R Features, Main URLs. **Priority:** Must.

**Acceptance:** A permitted reviewer finds a correction and its snapshot; an unauthorized request cannot retrieve history. Audit fields require D-03.

### FR-010 — Managed categories

**Requirement:** The system shall provide managed project-sector and cost-type dropdown options.

**Evidence:** R Features, Main URLs. **Priority:** Should.

**Acceptance:** An authorized change appears in the relevant form; behavior for options already in use requires D-02.

### FR-011 — Financial dashboards

**Requirement:** The system shall provide financial dashboards for the documented roles.

**Evidence:** P §5; R Features, Main URLs. **Priority:** Must.

**Acceptance:** Compare each role dashboard against a known authorized dataset. Exact financial formulas require D-04.

### FR-012 — Filtered reporting

**Requirement:** The system shall provide filtered cost reporting and PDF/Excel exports.

**Evidence:** P §2; R Features. **Priority:** Must.

**Acceptance:** Export a known filtered dataset in both formats and reconcile its included rows and totals. Filter set requires D-04.

### FR-013 — Large exports

**Requirement:** The system shall support ZIP packaging for very large report exports.

**Evidence:** R Features. **Priority:** Should.

**Acceptance:** Exercise the configured large-export threshold and inspect the ZIP. Threshold and resource limits require D-05.

### FR-014 — Language support

**Requirement:** The system shall provide English and Bangla UI translations using the documented JSON resources.

**Evidence:** R Features, Structure. **Priority:** Should.

**Acceptance:** Review core screens in both languages; translation completeness and export language expectations require D-06.

### FR-015 — Database backup

**Requirement:** The system shall provide manual timestamped PostgreSQL custom-format dumps under backups/database/ using the backup script.

**Evidence:** R Database Backups. **Priority:** Must.

**Acceptance:** Run the script against a disposable PostgreSQL instance with pg_dump available and verify a readable dump; restoration acceptance requires D-07.

### FR-016 — Office separation

**Requirement:** The system shall separate office/site data within centralized access according to an approved organizational access policy.

**Evidence:** P §4; implementation unverified. **Priority:** Must.

**Acceptance:** After D-08, test two office-scoped accounts against list, detail, update, summary and export requests; no unauthorized records may leak.

### FR-017 — Stock

**Requirement:** The system shall track stock according to an approved inventory model.

**Evidence:** P §1; implementation unverified. **Priority:** Must.

**Acceptance:** Blocked by D-09: agree item, unit, location and movement rules, then demonstrate entry, retrieval and balance reconciliation.

### FR-018 — Bills

**Requirement:** The system shall track bill records according to an approved bill lifecycle and project/cost relationship.

**Evidence:** P §§1–2; implementation unverified. **Priority:** Must.

**Acceptance:** Blocked by D-10: agree fields and lifecycle, then create and retrieve a bill and trace a correction.

### FR-019 — Input integrity

**Requirement:** The system shall reject invalid required input without partially saving the requested business change.

**Evidence:** D; derived from P §§2–3. **Priority:** Must.

**Acceptance:** Submit missing, malformed and inconsistent values; verify actionable feedback and unchanged persistent business data.

### FR-020 — Summary integrity

**Requirement:** The system shall apply approved cost-inclusion and rounding rules consistently to ledgers, dashboards and exports.

**Evidence:** D; derived from P §3. **Priority:** Must.

**Acceptance:** Use the same known fixture before and after edit/void/restore; reconcile every affected total using D-04 rules.

## 5. Data requirements and business rules

### 5.1 Logical information

| Information | Required / documented basis | Unverified details |
|---|---|---|
| Account | Roles, assigned modules, super-admin flag (R) | Login constraints, lifecycle, reset and office membership D-01/D-08 |
| Project | Firm/tender details, work order year, budget, status, completion date (R) | Required fields, field types/limits and transitions D-02 |
| Cost | Project expenditure, running and late entry (R) | Mandatory fields, date/amount/category constraints and duplicate criteria D-02/D-12 |
| Categories | Sector and cost-type dropdowns (R) | Deactivation and historical usage D-02 |
| History | Audit snapshots and edit/void/restore (R) | Exact event coverage, actor/time metadata, retention D-03 |
| Office/site | Separated centralized records (P) | Data ownership and sharing D-08; implementation unverified |
| Stock | Tracking intent (P) | Units, locations, movement/balance rules D-09; implementation unverified |
| Bill | Tracking intent (P) | Metadata, attachment and lifecycle D-10; implementation unverified |

This table specifies information needs rather than a physical schema. It does not assert an existing Office, Stock, Bill or separate Budget table.

### 5.2 Integrity and lifecycle rules

- BR-01: Authenticate and check role/module permissions before protected access (R).
- BR-02: Distinguish running-project entry from completed-project late costs (R); exact transition/eligibility rules D-02.
- BR-03: Preserve controlled edit/void/restore history with password confirmation (P/R); record coverage and retention D-03.
- BR-04: Apply office scope consistently across detail, list, update, aggregate and export paths (P intent; detailed rule D).
- BR-05: Reconcile ledger/dashboard/export calculations using one approved policy (D, FR-020).
- BR-06: Exclude private runtime data and generated artifacts from Git (R).

Currency, monetary precision, rounding, date inclusivity, timezone presentation, null/zero budgets, negative amounts, void inclusion, duplicate criteria and conflicting-edit rules are unresolved. They require D-02/D-04/D-12 and must not be inferred from the author's location.

### 5.3 Retention, migration and recovery

Ordinary business correction shall preserve traceability consistent with FR-008. No permanent-purge permission or legal retention period is established. Migrations govern schema changes. Manual backups are documented; automation, encryption, retention, offsite storage and successful restoration are not verified. Those recovery controls require D-07 rather than an assumed guarantee.

## 6. Non-functional requirements

### NFR-001 — Security controls

**Requirement:** The system shall provide CSRF protection, login rate limiting, secure production cookie settings and security headers.

**Evidence:** R Features, Production Environment.

**Verification:** Verify CSRF rejection, configured rate-limit enforcement, production cookie flags and response headers.

### NFR-002 — Deployment configuration

**Requirement:** Production shall require SECRET_KEY, DATABASE_URL and Redis or another persistent rate-limit backend; secrets shall be supplied outside source control.

**Evidence:** R Production Environment.

**Verification:** Start without required values and check safe rejection; start with a valid isolated environment. Do not expose secret values.

### NFR-003 — Mobile usability

**Requirement:** Core entry and review workflows shall remain usable on mobile devices.

**Evidence:** P §4; implementation unverified.

**Verification:** D-06: choose devices/viewports and complete login, entry, filtering and correction without inaccessible controls.

### NFR-004 — Operational logging

**Requirement:** The system shall maintain separate app, access, security, audit and error logging.

**Evidence:** R Features.

**Verification:** Trigger representative events in a disposable environment and inspect their intended destinations; log retention/redaction policy is D-03/D-07.

### NFR-005 — Schema maintenance

**Requirement:** Database schema changes shall use Flask-Migrate/Alembic migrations.

**Evidence:** R Structure, Production Environment.

**Verification:** Upgrade a disposable database using documented migration commands and verify expected schema.

### NFR-006 — Repository hygiene

**Requirement:** The public repository shall exclude secrets, private databases, logs, uploads, generated reports, backups and real project data.

**Evidence:** R Introduction, Security Note.

**Verification:** Review tracked changes and ignore rules before publication; fixtures must be synthetic.

### NFR-007 — Performance and availability

**Requirement:** The system shall meet agreed response-time, capacity and availability targets.

**Evidence:** D; unverified, blocked by D-11.

**Verification:** No numerical target is source-confirmed. Agree dataset, concurrency, measurement method, percentile and limit before load testing.

### NFR-008 — Recoverability

**Requirement:** The system shall meet agreed recovery-point and recovery-time objectives.

**Evidence:** D; unverified, blocked by D-07.

**Verification:** Restore a test dump and measure recovered completeness and elapsed recovery time against approved objectives.

### NFR-009 — Transaction integrity

**Requirement:** A rejected business operation shall not leave a partial change or inconsistent financial summary.

**Evidence:** D; unverified.

**Verification:** Inject a controlled save failure and verify rollback and summary consistency; concurrent-edit policy requires D-12.

### 6.1 Additional unverified quality decisions

No source defines response-time seconds, uptime percentage, concurrent-user count, recovery interval, supported browser versions or accessibility level. These are pending decisions rather than numerical promises. Performance acceptance must define workload and dataset before limits. Bilingual UI resources do not establish translated exports or full translation coverage.

## 7. Verification and acceptance plan

| Test group | Requirement coverage | Planned method / required evidence |
|---|---|---|
| V-01 Access | FR-001–FR-005, FR-016 | Role/module/office fixtures; positive and denied direct requests; no unauthorized changes or disclosure |
| V-02 Ledger | FR-006–FR-007, FR-010, FR-019 | Synthetic project/cost examples, running/late flow and invalid inputs |
| V-03 Accountability | FR-008–FR-009, FR-020 | Password-confirmed edit/void/restore; preserved history; reconciled totals |
| V-04 Reporting | FR-011–FR-013, FR-020 | Known filtered dataset; PDF/Excel rows/totals; configured ZIP boundary |
| V-05 Language/device | FR-014, NFR-003 | English/Bangla core-task review on approved devices |
| V-06 Operations | FR-015, NFR-001–NFR-002, NFR-004–NFR-006, NFR-008–NFR-009 | Safe configuration checks, logs, migrations, backup/restore and failure rollback |
| V-07 Proposal gaps | FR-016–FR-018 | Approved scope/stock/bill models; isolation and lifecycle scenarios |
| V-08 Service levels | NFR-007 | Agreed workload and measured targets after D-11 |

Unit/integration tests, scenario demonstrations and document inspections may provide evidence; no test pass is asserted here. Stock/bill acceptance and numerical service-level tests are blocked until their requirements are elaborated. R-only documentation cannot substitute for implementation testing.

Release acceptance requires approved scope, resolved critical decisions, passing agreed tests, documented exceptions and reviewer approval. A partial ledger demonstration cannot by itself close proposal obligations for stock, bills and office separation.

## 8. Requirements traceability and unresolved issues

### 8.1 Source-to-requirement map

| Source concern | Requirements |
|---|---|
| P §1 cost, budget, stock, bills | FR-006–FR-007, FR-011, FR-017–FR-018 |
| P §§2–3 filtering, mistakes and accountability | FR-008–FR-009, FR-012, FR-019–FR-020 |
| P §4 roles and archived history | FR-001–FR-002, FR-008–FR-009 |
| P §4 office separation and mobile use | FR-016, NFR-003 |
| P §5 centralized project visibility | FR-006, FR-011, FR-016 |
| R Features / Main URLs / Structure | FR-001–FR-014, NFR-001, NFR-004–NFR-005 |
| R Production Environment / Backups / Security Note | FR-015, NFR-002, NFR-005–NFR-006 |
| Derived controls / unverified quality targets | FR-019–FR-020, NFR-007–NFR-009 |

Functional sections provide item-level sources, including R subsection and proposal section. Analysis use cases provide scenario-level mappings.

### 8.2 Decision register

| Decision | Unverified detail / scope gap | Proposed decision owner | Resolution evidence |
|---|---|---|---|
| D-01 | Exact role/action matrix, super-admin powers, account lifecycle and password policy | Owner / administrator | Approved permission matrix and account scenarios |
| D-02 | Mandatory fields, validation limits, project states, completion-date rules and category retirement | Operator / administrator | Reviewed field catalogue and state transitions |
| D-03 | Audit event coverage, actor/time fields, history retention and restore permissions | Owner / administrator | Audit policy and sample history |
| D-04 | Currency, precision, rounding, budget formula, void inclusion, report filters and cache freshness | Accountant / management | Hand-calculated reconciled examples |
| D-05 | Large-export threshold, chunking, maximum size and timeout behavior | Developer / supervisor | Configuration and representative export test |
| D-06 | Supported browsers, mobile viewports, language selection and translation coverage | Site staff / supervisor | Reviewed device and language checklist |
| D-07 | Backup frequency, retention, storage protection, restore process, RPO and RTO | System owner | Approved recovery policy and restore rehearsal |
| D-08 | Office/site model, assignments and authorized cross-office visibility | Firm owner | Approved scope matrix; isolation tests |
| D-09 | Stock quantities versus movement ledger, units, locations and adjustments | Store staff / owner | Approved inventory scenarios and data model |
| D-10 | Bill metadata, attachments, statuses, duplication and project/cost links | Accountant / owner | Approved bill lifecycle and sample records |
| D-11 | Concurrency, workload, response-time and availability targets | Owner / developer | Agreed workload and measurable acceptance limits |
| D-12 | Duplicate warning and conflicting-update strategy | Operator / developer | Approved duplicate/concurrent-edit scenarios |

All owners above are proposed stakeholder categories; no consultation or approval is implied.

## 9. Change control and approval

A change proposal shall identify affected IDs, source/rationale, priority, scope and security/accounting impacts, revised acceptance checks and approving reviewer (**D**, proposed governance). Update the elicitation findings, analysis and SRS together. Preserve proposal gaps until explicit acceptance or approved scope change.

| Reviewer category | Decision | Status |
|---|---|---|
| Firm representative | Business policy, office boundaries, stock/bills and financial rules | Pending; representative not identified |
| Supervisor | Academic scope and assessment suitability | Pending |
| Student developer | Feasibility, implementation mapping and test evidence | Prepared; validation pending |

**Version history:** 1.0 — initial proposal-based draft. 1.1 — reconciled with README, unified requirement IDs, preserved proposal gaps, added source/evidence labels and planned verification. No stakeholder sign-off or implementation verification is implied.
