# Requirements Elicitation Document

| Document control | Value |
|---|---|
| Project | ConstructFlow — Construction Ledger and Cost Management |
| Author | Toufikur Rahman · ID 2420826 · Section 01 |
| Course / institution | CSE 309 — Web Programming · Independent University, Bangladesh |
| Submitted to | Md Abu Sayed, Lecturer, Department of Computer Science and Engineering |
| Version / date | 1.1 · 16 October 2026 |
| Status | Submission-ready source-based specification; stakeholder approval pending |


## 1. Purpose and problem context

This document records the evidence available for ConstructFlow and defines the selection, execution and validation process for further elicitation. The proposal describes scattered tally books/spreadsheets, duplicate or lost costs, overwritten edits, difficult filtering, missed bills, and weak accountability across offices. The objective is reliable centralized construction records with controlled access and traceable changes.

## Source and evidence register

| Code | Source | Authority and limits |
|---|---|---|
| P | *CSE309_project_proposal.pdf*, Toufikur Rahman, submitted 24 September 2026, pp. 1–2 | Primary business scope. Section 1 names cost, budget, stock and bills; sections 2–3 describe operational problems; section 4 identifies roles, archive/history, office separation and mobile use; section 5 describes expected outcomes. |
| R | [Repository README](https://github.com/toufikur-r38/ConstructFlow/blob/f2af045eaea023b78e60110c45085b08eae31d3f/README.md), reviewed 16 October 2026 | Current documented technical/feature baseline. README blob: `4f7e2cb6b09a4f601c511ce4344a04473f17698f`. Descriptions are not proof of successful runtime tests. |

**Evidence labels:** **P** = explicit proposal intent; **R** = README-documented capability or constraint; **D** = derived requirement, unverified and awaiting validation. **P / implementation unverified** preserves a proposal obligation absent from the README. Any detailed behavior beyond the cited source is explicitly labeled D. No interviews, observations, stakeholder approvals, production tests, or performance measurements are claimed.

The proposal governs intended business scope; the README governs the documented implementation baseline. A missing README feature is a gap to resolve, not permission to silently remove it from scope. Priorities are analyst recommendations, not stakeholder decisions.

## 2. Stakeholders and information needs

| Stakeholder category | Needed information | Evidence status |
|---|---|---|
| Firm owner / management | Cost visibility, budgets, office boundaries, reporting priorities | Inferred from P §§2–5; representative not yet consulted |
| Admin / system owner | Roles, module assignment, super-admin limits, audit and recovery | Roles in P; technical distinctions in R; policy unverified |
| Operator / accountant | Entry fields, late costs, correction, bills and reconciliation | Role in P; specific job mapping unverified |
| Viewer / project manager | Permitted summaries and exports | Viewer role in P; job mapping unverified |
| Site / store staff | Mobile conditions, stock units and movement | Site use in P; store role inferred |
| Course supervisor / developer | Scope feasibility and review criteria | Academic context in P; acceptance approval pending |

## 3. Elicitation approach selection

### 3.1 Selection process

1. Identify uncertainty from P and compare it with R.
2. Evaluate candidate methods for workflow depth, clarification, feasibility and mobile-usability feedback.
3. Select complementary methods rather than interpret a single score as the entire process.
4. Reassess after initial sessions; retain the source and decision for every requirement.

The following 1–5 ratings are analyst planning judgments, not research results. Weights total 100%; higher scores are better. Weighted score = sum(weight × rating) / 100.

| Method | Workflow depth 35% | Clarification 30% | Feasibility 20% | Usability feedback 15% | Score / 5 |
|---|---:|---:|---:|---:|---:|
| Semi-structured interview | 5 | 5 | 4 | 3 | 4.50 |
| Guided workflow observation | 5 | 4 | 3 | 4 | 4.15 |
| Proposal / README / form analysis | 3 | 2 | 5 | 1 | 2.80 |
| Prototype review | 3 | 4 | 3 | 5 | 3.60 |
| Questionnaire | 2 | 2 | 5 | 2 | 2.60 |

### 3.2 Selection and justification

Use document analysis first, then semi-structured interviews and guided workflow walkthroughs, followed by prototype review. Interviews rank highest because permission exceptions, missing bills and correction authority need follow-up discussion. Walkthroughs expose actual entry/reconciliation steps that recall may omit. Document analysis is immediately available and establishes evidence without inventing business rules. Prototype review makes mobile and bilingual interaction concrete for non-technical staff.

Use a questionnaire only to compare practices across additional offices after terminology is established. It provides reach but cannot alone resolve accounting or access-policy ambiguity. Observation depends on permission and access to anonymized examples; if unavailable, record the limitation and use scenario walkthroughs without presenting them as observed work.

## 4. Activities, completion status and outputs

| Activity | Status | Output / next step |
|---|---|---|
| Read complete two-page proposal | Completed | Business scope and problem statements P |
| Read current repository README | Completed | Feature/technology baseline R |
| Compare proposal and README | Completed | Stock, bills and office-isolation gaps; decision register below |
| Interview representative roles | Planned; not conducted | Notes with participant role, date, consent and unresolved questions |
| Walk through ledger, correction, bill and stock examples | Planned; not conducted | Anonymized workflow and field catalogue |
| Review mobile/bilingual screens | Planned; not conducted | Usability observations and revised requirements |
| Resolve conflicts and validate specification | Pending | Decisions, priorities and approval record |

## 5. Interview and walkthrough protocol

Use one representative per available role, including two office/site perspectives where feasible. Record unavailable perspectives. Begin with the last real task rather than a feature wish list; request anonymized examples and obtain permission before recording.

| Audience | Questions and evidence to request |
|---|---|
| Management | Which figures drive decisions? What defines budget overrun? Which offices may see each other? Reconcile a sample project summary. |
| Admin | Who creates users and grants modules? How does super-admin differ? Who can edit, void, restore or inspect history? Demonstrate a disputed correction. |
| Operator / accountant | Walk through a running cost and a late completed-project cost. Which fields are mandatory? What happens for a duplicate or missed bill? |
| Viewer | Which details and exports are required? Is download allowed? What should a restricted user see? |
| Store staff | Trace receipt, issue, adjustment and balance. Which units and locations matter? Are negative balances valid? |
| Site staff | Demonstrate entry on the normal phone and connection. Which English/Bangla labels are unclear? |
| System owner | Who performs and verifies backups? What loss and downtime are acceptable? Demonstrate recovery in a safe environment. |

Walkthrough cases: add project → enter cost → filter/export → correct → void → restore → reconcile totals. Separately examine bill and stock scenarios and cross-office denied access; their implementation is unverified.

## 6. Recording and validation method

For each finding record an evidence ID, source/section or participant/date, original need, normalized requirement ID, priority, assumptions, acceptance check and decision owner. Never record a planned interview as a completed source.

Review each requirement for necessity, atomic wording, consistency, feasibility and verifiability. Use the same FR/NFR IDs in the analysis and SRS. Resolve conflicts using confidentiality, accountability, operational frequency and course feasibility; management decides business policy and the supervisor reviews academic scope. Preserve unresolved disagreements in the decision log.

## 7. Open decisions

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

## 8. Risks and controls

| Risk | Control |
|---|---|
| README claims treated as tested behavior | Keep R evidence distinct from implementation verification |
| Proposal features omitted because not documented in code baseline | Retain FR-016–FR-018 as explicit gaps |
| One stakeholder represents every office | Compare roles/sites and label missing perspectives |
| Sensitive bills or project data collected | Use anonymized examples and restrict notes |
| Scope grows beyond course feasibility | Record release decisions; preserve proposal obligations pending explicit change |
| Inconsistent terms or requirements | Shared identifiers, glossary and cross-document review |

## 9. Exit and approval criteria

Elicitation is complete when critical decisions D-01–D-04 and D-08–D-10 have documented dispositions, role representatives have reviewed relevant scenarios, every accepted requirement has a source and acceptance check, and unresolved release risks have an accountable owner. No fixed interview count constitutes validation.

| Reviewer | Responsibility | Approval |
|---|---|---|
| Firm representative (to be identified) | Business scope, permissions and calculations | Pending |
| Course supervisor | Academic scope and submission requirements | Pending |
| Student developer | Feasibility and traceability | Prepared; approval not asserted |

Related documents: [Requirements Analysis](requirements-analysis.md) and [SRS](software-requirements-specification.md).
