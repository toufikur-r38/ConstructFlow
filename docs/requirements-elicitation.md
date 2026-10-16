# ConstructFlow — Requirements Elicitation Document

**Project:** ConstructFlow: A Web-Based Cost Tracking and Management System  
**Course:** CSE 309 — Web Programming  
**Institution:** Independent University, Bangladesh  
**Prepared by:** Toufikur Rahman  
**Status:** Initial draft — validate with stakeholders  
**Version:** 1.0  
**Date:** 16 October 2026

## 1. Purpose

This document describes how requirements for ConstructFlow will be discovered, clarified, recorded, and validated. It includes a selection process for elicitation techniques and explains why the selected approach fits the project.

The source proposal identifies problems in small and mid-sized construction firms that rely on tally books and scattered spreadsheets: duplicate or lost cost entries, accidental overwrites, difficult filtering, poor visibility across sites/offices, and limited accountability for incorrect or missing bills. ConstructFlow is intended to centralize cost, budget, stock, bill, and project records while supporting role-based access, archived records/audit trails, multi-office data separation, and mobile-friendly use.

**Important:** The proposal establishes the project direction, not every detailed requirement. Items marked *to validate* are working assumptions and must be confirmed with representative users or the course supervisor.

## 2. Elicitation objectives

- Understand current cost, budget, stock, bill, and project-record workflows.
- Identify stakeholders, their goals, pain points, access needs, and reporting needs.
- Define how admin, operator, and viewer roles differ.
- Understand multi-office/site separation and what information may be shared.
- Discover audit-history and soft-delete/archive expectations.
- Identify usability, security, data-integrity, and mobile-use expectations.
- Prioritize requirements for a feasible course project and establish acceptance criteria.
- Resolve conflicting needs and obtain stakeholder confirmation.

## 3. Scope and boundaries

### In scope for elicitation
- Project and site records.
- Cost/expense entry, categorization, searching, filtering, and summaries.
- Budgets and comparison of recorded costs against budgets.
- Stock/inventory records and stock movement expectations.
- Bills and supporting information, including missed-bill handling.
- User roles and permissions (admin, operator, viewer).
- Multi-office/site data separation with centralized management.
- Audit history and soft deletion/archive behavior.
- Dashboard/reporting, responsive interface, and data validation.
- Operational constraints, security, and acceptance criteria.

### Out of scope unless stakeholders approve a change
- Full enterprise ERP, payroll, tax filing, banking/payment processing, supplier marketplaces, automated accounting integrations, and native mobile apps.
- Specific technology choices, database design, and deployment architecture are implementation decisions unless they impose a requirement.

## 4. Stakeholders and information needs

| Stakeholder | Likely interests / questions to investigate |
|---|---|
| Firm owner / management | Project cost visibility, budget overruns, cross-site summaries, accountability, reports |
| Administrator | User creation, role assignment, office/site configuration, archive and audit review |
| Operator / accountant / site staff | Fast, low-error entry of costs, bills, and stock activity; corrections; mobile usability |
| Viewer / project manager | Read-only access to permitted projects, dashboards, and reports |
| Store / inventory staff | Stock item records, quantities, receipts/issues, low-stock visibility (to validate) |
| Multiple offices / site representatives | Which records are local, which are shared, and how access is separated |
| Instructor / project supervisor | Academic scope, expected deliverables, feasibility, evaluation criteria |
| Developer / tester | Clear, testable requirements, constraints, edge cases, and priorities |

These roles are inferred from the proposal and are not confirmation that every firm uses these exact job titles.

## 5. Elicitation technique selection process

### 5.1 Candidate techniques

Scores below use a 1–5 scale, where 5 is most favorable for this project. Weighted score = score × weight; maximum total is 500. Scores are a reasoned planning assessment, not results from completed field research.

| Criterion | Weight | Interviews | Questionnaire | Observation / workflow walkthrough | Document analysis | Prototype review |
|---|---:|---:|---:|---:|---:|---:|
| Depth of workflow discovery | 25 | 5 | 2 | 5 | 3 | 4 |
| Ability to clarify ambiguity | 20 | 5 | 2 | 4 | 2 | 4 |
| Reach across roles/sites | 15 | 2 | 5 | 3 | 2 | 3 |
| Low cost / feasibility | 15 | 4 | 5 | 3 | 5 | 3 |
| Evidence of actual work | 15 | 3 | 1 | 5 | 4 | 2 |
| Early usability feedback | 10 | 2 | 1 | 3 | 1 | 5 |
| **Weighted total / 500** | **100** | **390** | **260** | **405** | **285** | **350** |

### 5.2 Selected approach: lightweight triangulation

Select a combination of:
1. **Semi-structured interviews** with representative management, administrator, operator, and viewer users.
2. **Workflow walkthroughs / observation** using a sample or anonymized cost ledger, bill, stock record, and current spreadsheet workflow where access is permitted.
3. **Document analysis** of existing forms, spreadsheets, bill formats, and reports, if stakeholders can share them safely.
4. **Questionnaire** only when input from more users or multiple offices is needed and interviews are impractical.
5. **Low-fidelity prototype review** after initial requirements are drafted, to validate navigation and data-entry assumptions.

The table gives workflow walkthroughs the highest score because the core problem concerns real operational practices and record errors. Interviews score nearly as high because users must explain permissions, exception cases, and accountability needs that may not be visible by observation. Triangulation reduces the risk of relying on one person's recollection or one sample document.

### 5.3 Justification

- **Interviews:** permit follow-up questions about duplicates, corrections, missing bills, approval, and reporting.
- **Walkthroughs:** expose the real sequence of entry, review, correction, and reconciliation tasks.
- **Document analysis:** helps identify actual fields, naming conventions, and report layouts without inventing them.
- **Questionnaire:** efficiently checks whether needs differ across sites, but is weak for exploring complex workflows.
- **Prototype review:** allows non-technical users to react to a concrete screen before implementation.

A full survey-only approach is not recommended: it could miss edge cases and the reasons behind current workarounds. A prototype-only approach is also insufficient because it risks validating a design before the underlying business rules are understood.

## 6. Planned elicitation activities

| Step | Activity | Participants / evidence | Output |
|---|---|---|---|
| 1 | Review proposal and define scope | Project proposal, supervisor | Initial context and scope |
| 2 | Identify and contact representative stakeholders | Management, admin, operators, viewers, site/store staff where available | Stakeholder list |
| 3 | Conduct semi-structured interviews | One representative per available role; record notes with permission | Interview notes and needs |
| 4 | Walk through existing workflows | Anonymized ledger/spreadsheet, bill, stock record, report | Current-state workflow and pain points |
| 5 | Analyze sample documents | Forms and reports supplied voluntarily | Candidate data fields and report needs |
| 6 | Consolidate and classify requirements | All elicitation evidence | Requirement catalogue |
| 7 | Prioritize and resolve conflicts | Stakeholder review / supervisor feedback | Agreed priority and open questions |
| 8 | Review low-fidelity screens and scenarios | Representative users, if available | Usability feedback and revised requirements |
| 9 | Validate the baseline | Stakeholder walkthrough and sign-off where feasible | Approved or provisionally approved baseline |

No stakeholder interviews or observations are claimed to have already occurred. This is the proposed process.

## 7. Interview guide

### Management / owner
1. Which decisions must you make from project cost and budget information?
2. How often do you need project-wise, site-wise, or office-wise summaries?
3. What indicates that a project is over budget?
4. Which reports are needed for internal review or audits?
5. Who may view or correct financial records?

### Administrator
1. How should users, roles, offices, and sites be created and managed?
2. Can a user belong to more than one office or project?
3. Which actions require administrator privileges?
4. Who can view archived records and audit history?
5. What should happen when a user leaves the firm?

### Operator / accountant / site staff
1. Describe a typical cost or bill entry from start to finish.
2. Which fields are essential and which are often unavailable at entry time?
3. How are duplicate entries, mistakes, and missing bills handled today?
4. What supporting documents or references must be retained?
5. What device and network conditions are common at construction sites?
6. Which searches and filters are used most frequently?

### Stock / store staff (to validate)
1. How are stock receipts, issues, adjustments, and balances recorded?
2. Are units, suppliers, item codes, or minimum stock levels needed?
3. Who can authorize or correct a stock adjustment?

### Viewer / project manager
1. What should be visible on a dashboard?
2. Which projects or offices should you be able to access?
3. Which reports should be exportable, if any?
4. Should viewers be completely read-only, including comments or downloads?

## 8. Validation and conflict resolution

- Convert each finding into a uniquely identified, atomic requirement.
- Trace every requirement to a proposal statement, elicitation finding, or explicitly labeled assumption.
- Ask stakeholders to confirm the wording, priority, and acceptance condition.
- Resolve conflicts by considering business risk, accountability, data confidentiality, frequency of use, and implementation feasibility.
- Record unresolved items in an open-questions log rather than silently deciding them.
- Review requirements against representative scenarios: entering a cost, correcting an entry, archiving a record, viewing a budget summary, recording stock movement, and accessing data across offices.

## 9. Expected deliverables

- Stakeholder and role list.
- Interview notes and workflow diagrams, if activities are conducted.
- Current-state problem summary.
- Candidate data fields and reporting needs.
- Prioritized, uniquely identified requirement catalogue.
- Assumptions, constraints, risks, and open questions.
- Reviewed baseline for the Requirements Analysis Document and SRS.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Only one role is consulted | Seek input from different role types; label unavailable perspectives |
| Users describe desired features but omit exceptions | Use workflow walkthroughs and scenario-based follow-up questions |
| Sensitive financial data is shared | Request anonymized examples and collect only necessary information |
| Requirements grow beyond course scope | Prioritize a minimum viable feature set and record later ideas separately |
| Different offices use different processes | Compare workflows and identify configurable versus standardized rules |
| Assumptions are mistaken for confirmed facts | Mark assumptions explicitly and maintain an open-questions log |

## 11. Open questions requiring confirmation

1. Is ConstructFlow intended for one firm with multiple offices, or multiple independent firms?
2. What exact cost categories, budget periods, and budget-overrun rules are required?
3. Does “stock” require only current quantities or full stock movement history?
4. Must bills be uploaded as files, or is recording bill metadata sufficient?
5. Are approval workflows required before costs or stock changes become final?
6. Which reports and export formats are essential?
7. Is offline data entry required at sites with unreliable connectivity?
8. What retention period applies to archived records and audit history?
9. Can records be edited after approval, and who can authorize corrections?
10. What are the expected user volume, data volume, and performance targets?

## 12. Reference

Rahman, Toufikur. *ConstructFlow: A Web-Based Cost Tracking and Management System for a Construction Firm to track their cost, budget, stock and bills.* CSE 309 Web Programming Project Topic Proposal, Independent University, Bangladesh, submitted 24 September 2026.
