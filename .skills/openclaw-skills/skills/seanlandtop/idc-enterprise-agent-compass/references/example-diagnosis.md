# Example Diagnosis: Manufacturing Enterprise Order Processing

Complete worked example demonstrating the seven-step COMPASS diagnostic process. Use as an anchor when users struggle to self-identify their scenarios.

---

## Scenario Description

A mid-size manufacturing enterprise receives orders via email attachments, chat files, and an ERP external portal — formats are inconsistent. After an order arrives, staff must:

1. Find customer records in CRM
2. Check inventory and delivery dates in ERP
3. Compare prices in the quotation system
4. Verify production capacity in the production system

When any step is blocked, sales, customer service, and production scheduling must repeatedly align — consuming significant time and causing delays.

**Company profile:** Mid-size manufacturing, ~500 employees, ERP and CRM deployed, no prior Agent/RPA experience, IT maturity moderate.

---

## Step 1: Current State

- **Industry & Scale:** Manufacturing, ~500 employees, moderate IT maturity
- **Core Pain Points:**
  1. Order processing takes 2-4 hours per order due to multi-system data gathering
  2. Cross-department alignment (sales ↔ production ↔ customer service) causes frequent delays
- **Existing Systems:** ERP (SAP), CRM (Salesforce), Quotation system (custom), Production scheduling (MES)
- **Agent Experience:** None; some RPA discussion but no pilot

→ All three required items collected. Proceed to Step 2.

---

## Step 2: Three-Question Screening

**Q1: "In the order processing task, what action consumes the most human time?"**

User answer: "Moving between systems — pulling data from CRM, then ERP, then quotation system, then MES. And when something doesn't match, going back and forth."

→ Maps to **Orchestration** (cross-system data movement) and **Collaboration** (cross-department alignment when things don't match)

**Q2: "Where does the knowledge and judgment logic primarily reside?"**

User answer: "Our senior order managers know all the tricks — which supplier to use as backup, how to handle partial shipments, when to push production vs. find alternatives. When they're on vacation, things slow down significantly."

→ Maps to **Sedimentation** (knowledge concentrated in individuals)

**Q3: "How do you currently measure the quality of order processing?"**

User answer: "We track order completion time and error rate, but it's manual — someone enters it in a spreadsheet at the end of the month."

→ Partial baseline exists (processing time, error rate) but collection is manual and infrequent. Flag: baseline data collection should be automated before Agent introduction for accurate ROI measurement.

**Screening result:** Primary dimensions: **Orchestration**, **Collaboration**. Secondary: **Sedimentation**. Baseline data: partially available, needs improvement.

---

## Step 3: Constraint Layer

The primary bottleneck is in **Layer 2: Information Processing**.

- Orders have already entered the enterprise (Perception is a secondary issue)
- The core pain is in how information flows between systems and roles after entry
- Knowledge retention (Layer 3) is important but secondary to the immediate processing bottleneck

---

## Step 4: Specific Dimensions

**Orchestration (Primary):**
- Evidence: "Moving between 4 systems for each order, manually pulling data"
- Judgment signal confirmed: Cross-system process relies on manual triggers, API connections are hard-coded or non-existent

**Collaboration (Primary):**
- Evidence: "When any step is blocked, sales, customer service, and production must repeatedly align"
- Judgment signal confirmed: Significant time spent in coordination meetings and status chasing

**Sedimentation (Secondary):**
- Evidence: "Senior order managers hold all the judgment logic; things slow down when they're away"
- Judgment signal confirmed: Key personnel departure would significantly impact operations

**Perception (Tertiary — pre-requisite):**
- Evidence: "Orders come via email attachments, chat files, portal — formats inconsistent"
- Note: This is a prerequisite issue but has lower complexity than the processing layer bottleneck

---

## Step 5: System Readiness

| Dimension | Assessment | Notes |
|-----------|-----------|-------|
| Interface Capability | **Partial** | SAP and Salesforce have APIs; quotation system and MES have limited API access |
| Permission Model | **Partial** | Service accounts exist for SAP; no Agent-specific permission design |
| Operation Traceability | **Partial** | SAP has audit logs; other systems have inconsistent logging |
| Data Semantics | **To-Build** | Field meanings and business rules exist mainly in experienced staff's knowledge |

**Priority actions:**
1. API enablement for quotation system and MES (directly enables Orchestration scenario)
2. Data dictionary creation for order-related fields across all four systems
3. Agent-specific permission model design (can proceed in parallel with pilot)

---

## Step 6: Supplier Direction

Based on the diagnosis:

| Dimension | Supplier Type | Role |
|-----------|--------------|------|
| **Orchestration** | Agent Development Platform Vendors + Enterprise Scenario Vendors (APA) | Platform provides cross-system orchestration backbone; APA vendor provides process automation upgrade path from current manual workflows |
| **Collaboration** | Enterprise Scenario Vendors (Operations/Collaboration) | Proven solutions for internal coordination, status tracking, and cross-department alignment |
| **Sedimentation** | Agent Development Platform Vendors | Platform provides memory storage and knowledge base infrastructure for capturing senior order managers' judgment logic |
| **Industry semantics** (BOM, scheduling rules) | Industry Scenario Vendors (Manufacturing) | Deep manufacturing domain knowledge for encoding industry-specific rules |

**Recommended combination:** Platform + APA + Operations + Manufacturing Industry

**Phase guidance:**
- Phase 1 pilot: Start with APA vendor's proven order processing template on Platform
- Phase 2 scaling: Add Operations vendor for collaboration layer
- Phase 3 depth: Engage Manufacturing Industry vendor for domain-specific knowledge encoding

---

## Step 7: Output Summary

### 1. COMPASS Diagnosis Result
- **Primary constraint layer:** Information Processing (Layer 2)
- **Core bottleneck dimensions:** Orchestration (cross-system data movement), Collaboration (cross-department alignment)
- **Secondary dimension:** Sedimentation (knowledge concentration in individuals)

### 2. Recommended Entry Scenarios
- **Phase 1 pilot:** "Order intake → Inventory & delivery verification → Exception escalation" closed-loop. Covers Orchestration + Monitoring. Cross-system characteristics are clear, manual handoff cost is high, results are easily measurable.
- **Phase 2:** Expand to sales-production-customer service collaboration layer (Collaboration)
- **Phase 3:** Capture senior order managers' judgment logic (Sedimentation)

### 3. Supplier Direction
- **Platform base:** Agent Development Platform Vendor (cross-system orchestration, governance)
- **Process automation:** Enterprise Scenario Vendor — APA (proven order processing patterns)
- **Collaboration:** Enterprise Scenario Vendor — Operations (internal coordination)
- **Industry depth:** Industry Scenario Vendor — Manufacturing (BOM, scheduling rules)

### 4. Implementation Roadmap
- **Month 1-2:** Automate baseline data collection; enable APIs for quotation system and MES
- **Month 2-4:** Phase 1 pilot — order intake to exception escalation closed-loop
- **Month 4-6:** Evaluate pilot results; begin Phase 2 collaboration layer
- **Month 6-9:** Phase 3 — knowledge capture from senior order managers
- **Parallel throughout:** Permission model design, audit logging enhancement, data dictionary creation

### 5. Human-Agent Boundary
- **Agent analyzes:** Order data extraction from multi-format inputs, cross-system data comparison, exception identification
- **Agent executes:** Data validation, inventory queries, price matching, status updates, notification distribution
- **Human decides:** Exception order approval (e.g., non-standard delivery, credit limit override), major customer communication, production scheduling conflicts, new supplier selection
- **Escalation rules:** Any order exceeding credit limit → human approval; any delivery date conflict → human decision; any new customer first order → human confirmation
