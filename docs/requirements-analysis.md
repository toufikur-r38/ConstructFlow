# Requirements Analysis Document

| Document control | Value |
|---|---|
| Project | ConstructFlow — Construction Ledger and Cost Management |
| Author | Toufikur Rahman · ID 2420826 · Section 01 |
| Course / institution | CSE 309 — Web Programming · Independent University, Bangladesh |
| Submitted to | Md Abu Sayed, Lecturer, Department of Computer Science and Engineering |
| Version / date | 1.1 · 16 October 2026 |
| Status | Submission-ready source-based specification; stakeholder approval pending |


## 1. Purpose and analysis boundary

This document transforms the proposal into a prioritized requirement model and reconciles it with the current README. It separates intended business scope, documented capabilities and unverified design decisions. Functional acceptance statements are authoritative in the companion [SRS](software-requirements-specification.md); IDs below refer to the same requirements.

## Source and evidence register

| Code | Source | Authority and limits |
|---|---|---|
| P | *CSE309_project_proposal.pdf*, Toufikur Rahman, submitted 24 September 2026, pp. 1–2 | Primary business scope. Section 1 names cost, budget, stock and bills; sections 2–3 describe operational problems; section 4 identifies roles, archive/history, office separation and mobile use; section 5 describes expected outcomes. |
| R | [Repository README](https://github.com/toufikur-r38/ConstructFlow/blob/f2af045eaea023b78e60110c45085b08eae31d3f/README.md), reviewed 16 October 2026 | Current documented technical/feature baseline. README blob: `4f7e2cb6b09a4f601c511ce4344a04473f17698f`. Descriptions are not proof of successful runtime tests. |

**Evidence labels:** **P** = explicit proposal intent; **R** = README-documented capability or constraint; **D** = derived requirement, unverified and awaiting validation. **P / implementation unverified** preserves a proposal obligation absent from the README. Any detailed behavior beyond the cited source is explicitly labeled D. No interviews, observations, stakeholder approvals, production tests, or performance measurements are claimed.

The proposal governs intended business scope; the README governs the documented implementation baseline. A missing README feature is a gap to resolve, not permission to silently remove it from scope. Priorities are analyst recommendations, not stakeholder decisions.

## 2. Problem, objectives and scope reconciliation

| Business problem / objective | Requirement response | Scope finding |
|---|---|---|
| Scattered ledgers and project records | FR-006–FR-007 | Project/cost baseline documented by R |
| Duplicate/lost entries and overwritten edits | FR-008–FR-009, FR-019; D-12 | History documented; duplicate detection and concurrent edits unverified |
| Difficult cost filtering and limited visibility | FR-011–FR-013 | Dashboards and PDF/Excel/ZIP documented |
| Weak role accountability | FR-001–FR-004, FR-009 | Roles/modules documented; exact action matrix unverified |
| Budget and profitability visibility | FR-006, FR-011, FR-020 | Budget tracking documented; formula/currency rules unverified; profitability is an objective, not a confirmed accounting module |
| Multi-office coordination with separation | FR-016 | Required by P; R does not verify office isolation |
| Stock and missed bills | FR-017–FR-018 | Required by P; distinct stock/bill workflows not verified by R |
| Site-based use | NFR-003, FR-014 | Mobile intent in P; language resources in R; usability not tested |

Stock, bills and office separation remain proposal scope obligations. Their release scheduling requires an explicit stakeholder/supervisor decision; this analysis does not relabel them as completed or discard them.

Scope excludes payroll, banking/payment processing, tax filing, a full ERP suite, unrelated-firm multi-tenancy, native mobile apps and offline synchronization unless separately approved. These are proposed boundaries; neither P nor R defines those capabilities.

## 3. Actors and authorization analysis

| Actor | Source-established basis | Matters requiring confirmation |
|---|---|---|
| Viewer | Named in P and R; viewer dashboard URL in R | Read-only business access, export permission, project/office visibility |
| Operator | Named in P and R; operator dashboard in R | Project creation, correction, late cost and restore authority |
| Admin | Named in P and R; user management and admin dashboard in R | Exact administrative actions and audit visibility |
| Super-admin account | Separate flag in R | System-owner powers and relationship to admin |
| Backup operator | Script in R; human role inferred | Host access, storage access and recovery accountability |
| Store/accounting staff | Business tasks inferred from P | Mapping to existing roles; no new software role assumed |

Module access is an independent documented control, and does not establish office isolation. Do not equate a super-admin flag with unrestricted business-data access without policy approval. Treat the matrix above as questions for D-01/D-08, not a verified permission grant.

## 4. Requirement catalogue and priorities

Must = core business obligation or essential documented baseline; Should = useful documented support. These priorities are proposed. Evidence labels concern source support, not delivery completion.

| ID | Capability | Priority | Evidence |
|---|---|---|---|
| FR-001 | Authentication | Must | P §4; R Features, Main URLs |
| FR-002 | Roles | Must | P §4; R Features |
| FR-003 | Module access | Must | R Features, Structure |
| FR-004 | User administration | Must | R Features, Structure, Main URLs |
| FR-005 | Account maintenance | Should | R Structure, Main URLs |
| FR-006 | Project registry | Must | P §§1–2; R Features |
| FR-007 | Cost entry | Must | P §§1–2; R Features |
| FR-008 | Controlled corrections | Must | P §4; R Features |
| FR-009 | Audit review | Must | P §§2,4; R Features, Main URLs |
| FR-010 | Managed categories | Should | R Features, Main URLs |
| FR-011 | Financial dashboards | Must | P §5; R Features, Main URLs |
| FR-012 | Filtered reporting | Must | P §2; R Features |
| FR-013 | Large exports | Should | R Features |
| FR-014 | Language support | Should | R Features, Structure |
| FR-015 | Database backup | Must | R Database Backups |
| FR-016 | Office separation | Must | P §4; implementation unverified |
| FR-017 | Stock | Must | P §1; implementation unverified |
| FR-018 | Bills | Must | P §§1–2; implementation unverified |
| FR-019 | Input integrity | Must | D; derived from P §§2–3 |
| FR-020 | Summary integrity | Must | D; derived from P §3 |

### Quality requirements

| ID | Attribute | Evidence / decision |
|---|---|---|
| NFR-001 | Security controls | R Features, Production Environment |
| NFR-002 | Deployment configuration | R Production Environment |
| NFR-003 | Mobile usability | P §4; implementation unverified |
| NFR-004 | Operational logging | R Features |
| NFR-005 | Schema maintenance | R Structure, Production Environment |
| NFR-006 | Repository hygiene | R Introduction, Security Note |
| NFR-007 | Performance and availability | D; unverified, blocked by D-11 |
| NFR-008 | Recoverability | D; unverified, blocked by D-07 |
| NFR-009 | Transaction integrity | D; unverified |

## 5. Use cases and exception analysis

| ID / actor | Preconditions and main flow | Exceptions / postcondition | Requirements |
|---|---|---|---|
| UC-01 Authenticate / account holder | Valid account; submit credentials; enter permitted hub/module | Invalid login denied; logout ends access; no role bypass | FR-001–FR-005 |
| UC-02 Maintain project / authorized writer | Module and action permission; enter firm/tender, year, budget, status and completion details; save | Invalid input rejected; mandatory fields D-02; persisted project retrievable | FR-002–FR-003, FR-006, FR-019 |
| UC-03 Enter cost / authorized writer | Existing permitted project; choose running or completed/late workflow; enter details; save | Invalid/unauthorized input rejected; duplicate handling D-12; associated cost retained | FR-007, FR-019 |
| UC-04 Correct/void/restore / authorized reviewer or writer | Permitted record/action; confirm password; apply change; inspect snapshot | Incorrect confirmation or authorization denied; record retained; summary reconciled | FR-008–FR-009, FR-020 |
| UC-05 Review/export / permitted reader | Select supported filters; review dashboard/ledger; export PDF or Excel | Empty data, invalid filters, denied access and large-export threshold require D-04/D-05; no business records changed | FR-011–FR-013, FR-020 |
| UC-06 Recover data / authorized backup operator | PostgreSQL connection and pg_dump; create timestamped dump | Missing client tools, credentials or disk space fail visibly; restore procedure unverified | FR-015, NFR-008 |
| UC-07 Cross-office access / scoped user | Approved office model D-08; request own and other office data | Unauthorized lists/details/exports denied without disclosure; implementation unverified | FR-016 |
| UC-08 Stock/bills / authorized staff | Approved models D-09/D-10; enter, retrieve and correct records | Validation and audit must be defined; implementation unverified | FR-017–FR-019 |

## 6. Conceptual data model

This is a requirements model, not a claim about exact SQL columns.

| Concept | Source-grounded information | Relationship / unresolved detail |
|---|---|---|
| User | Role, module access, separate super-admin flag (R) | Account lifecycle D-01; scope assignments D-08 |
| Project | Firm/tender, work order year, budget, status, completion date (R) | Has project costs; mandatory fields D-02 |
| Cost | Project expenditure and running/late workflow (R) | Amount/date/category rules and precision D-02/D-04 |
| Managed option | Project sector / cost type (R) | Retirement and historical references D-02 |
| Audit snapshot | Edit/void/restore history (R) | Actor, timestamp, fields, retention D-03 |
| Office/site | Separation within centralized operation (P) | Ownership and cross-office model D-08; implementation unverified |
| Stock | Inventory intent (P) | Item/unit/location and movement model D-09; implementation unverified |
| Bill | Bill tracking intent (P) | Project/cost relation and attachments D-10; implementation unverified |

Do not infer a separate Budget database table from project-budget tracking. Reports and backups are generated artifacts, not additional business entities.

## 7. Business rules and state analysis

| Rule | Statement | Evidence |
|---|---|---|
| BR-01 | Access requires authentication, applicable role permission and assigned module access. | FR-001–FR-003, R |
| BR-02 | Running projects use normal cost entry; completed projects have a late-cost workflow. | FR-007, R; exact eligibility D-02 |
| BR-03 | Corrections, voids and restores use password confirmation and retained snapshots. | FR-008, R |
| BR-04 | Ordinary destructive correction preserves traceability rather than hard deletion. | P §4; R edit/void/restore; record coverage D-03 |
| BR-05 | Financial views use one approved inclusion/rounding policy. | FR-020, D; formulas not source-confirmed |
| BR-06 | Scope restrictions must also govern exports and aggregated counts. | FR-016, D operationalization of P §4 |
| BR-07 | Sensitive runtime data and backups are excluded from the public repository. | NFR-006, R |

Conceptual transitions: running project → completed project (exact transition authority/date rules D-02); active record → voided record → restored active record (documented workflow, exact record coverage D-03). Editing preserves history. No approval state machine or permanent purge policy is inferred.

For an agreed example budget B and included expenditure E, a candidate remaining-budget formula is B − E. This formula, the included cost set, negative-balance behavior, currency and rounding are **D-04**, not verified implementation facts. Reconcile with synthetic examples before approval.

## 8. Feasibility and dependencies

The README documents a Flask application factory, SQLAlchemy models, Flask-Login, migrations, templates, JSON translations and construction routes/services/utilities. PostgreSQL is the production-oriented database configuration; SQLite is a development fallback only under the documented development conditions. Redis supports cache/rate-limit storage; a persistent rate-limit backend is required outside development.

Authentication/modules precede protected workflows; projects/categories precede cost entry; approved accounting rules precede reconciled dashboards/exports. Office isolation affects every read/write/report path. Stock and bills require agreed models and cannot be estimated as minor UI additions. No schedule or effort estimate is source-confirmed.

## 9. Gap and decision register

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

## 10. Risk and prioritization decisions

| Risk | Impact | Required disposition |
|---|---|---|
| Office filtering assumed from module access | Confidential data leakage | Resolve D-08 and test every access path |
| Stock/bill scope treated as delivered | Incomplete proposal fulfillment | Explicitly accept implementation work or approve a scope change |
| Financial rules guessed | Incorrect totals and misleading budget comparisons | Resolve D-04 with reconciled examples |
| Unrestricted correction or weak history | Lost accountability | Resolve D-01/D-03 and verify snapshots |
| Manual backup mistaken for recovery guarantee | Unrecoverable data or unacceptable loss | Resolve D-07 and rehearse restore |
| Numeric service promises invented | Unverifiable acceptance | Resolve D-11 before committing service levels |

Recommended sequence: confirm access/accounting policy; validate documented ledger/correction/reporting workflows; close office/stock/bill scope decisions; then approve a complete release baseline. Numerical targets and automated duplicate detection remain unverified.

## 11. Validation and traceability

Every FR has its source, priority and acceptance check in the SRS. Every NFR has evidence and a verification method. UC mappings above connect workflows to requirements. Acceptance must include positive and denied requests, financial reconciliation, history preservation, mobile/bilingual review and an isolated restore exercise where recovery is approved.

Review outcome is **pending**, not passed. No runtime verification occurred during this document analysis. Changes must record requirement ID, reason, evidence, affected tests and reviewer disposition, and update all three documents together.

Related: [Elicitation](requirements-elicitation.md) · [SRS](software-requirements-specification.md).
