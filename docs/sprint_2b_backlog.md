# 🧾 Sprint 2B Backlog — #6 Multi-Objective Optimization

> **Purpose:** The reviewable backlog for Sprint 2B. Defines the user stories, acceptance criteria, and test cases development must satisfy. Per `CLAUDE.md`, Sprint 2B code must implement exactly these stories once locked.
>
> **Split note:** Original Sprint 2 (#1 + #6) was split into **Sprint 2A (#1 Contextual Affinity)** and **Sprint 2B (#6 Multi-Objective Optimization)** per `decision_log.md` D-038. This is the 2B half; it starts after 2A is delivered.
>
> **Review gate:** Reviewed and approved by the owner **before** coding. Post-lock changes require a new `decision_log.md` entry.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Sprint Backlog (User Stories · Acceptance Criteria · Test Cases) |
| **Sprint** | Sprint 2B — Multi-Objective Optimization (#6) |
| **Status** | 🔍 Draft — to be finalized/locked when Sprint 2A completes |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 23 July 2026 |
| **Related Docs** | `architecture.md` §4.1 (optimizer) · `Enhancement_DeepDive` §3.5 · `decision_log.md` D-025, D-038 · `governance_charter.md` POL-001 |

---

## 1. Sprint 2B Scope

Moves ranking from single-objective (lift) to a **multi-objective composite score** (lift + margin + turn − shrink) with fixed, configurable default weights and a visible breakdown. Builds on Sprint 2A's contextual engine; every recommendation still passes through governance (#9).

**In scope:**
1. **Optimization signals** — margin (from `margin_pct`), plus synthesized `turn_rate` and `shrink_rate` in the product master.
2. **Composite scoring** — fixed configurable weights (e.g. `0.4·lift + 0.3·margin + 0.2·turn − 0.1·shrink`) with a per-objective breakdown.
3. **Re-ranking + trade-off visibility** — rank by composite score; show lift vs margin trade-offs.
4. API + UI wiring for the optimization toggle and score breakdown.

**Explicitly OUT of scope for Sprint 2B** (do NOT build):
- ❌ User-adjustable weight sliders — fixed default weights with a visible breakdown (owner-selected).
- ❌ LP/MIP optimization via PuLP — weighted scoring only (PuLP stays a later option).
- ❌ Contextual affinity work — delivered in **Sprint 2A**.
- ❌ #4/#5/#3/#8 (later sprints).

---

## 2. Personas

| Persona | Role in Sprint 2B |
|---------|-------------------|
| **Category Manager** | Reads composite-scored recommendations and the trade-offs |
| **Merchandising Head** | Consumes the lift-vs-margin trade-off view (output consumer) |
| **Data Steward / Admin** | Confirms optimized recommendations remain governed and audited |

## 3. Definition of Ready / Done

As Sprint 2A: acceptance criteria pass; unit + integration tests; `ruff` clean; docstrings + type hints; governance-in-path; CI green; journal entry filed.

---

# 4. User Stories

Story IDs `US-2B.x`; test IDs `TC-2B.x.y` (unit `U`, integration `I`).

### US-2B.1 — Optimization signals in the data

> **As a** Data Steward, **I want** margin, turn, and shrink signals per SKU, **so that** the optimizer has real inputs.

**Acceptance Criteria:**
- **AC1** — Product Master carries **turn_rate** and **shrink_rate** (synthesized, non-null for every SKU, within documented ranges); margin derives from existing `margin_pct`.
- **AC2** — Generation stays deterministic; `data_contract.md` updated for the new fields.
- **AC3** — Signals are read via the data-access layer (no direct file access in services).

**Test Cases:**
- **TC-2B.1.1 (U)** — Every SKU has non-null `turn_rate` and `shrink_rate` in range.
- **TC-2B.1.2 (U)** — Values are deterministic across two seeded runs.

### US-2B.2 — Composite multi-objective score

> **As a** Merchandising Head, **I want** placements scored on lift + margin + turn − shrink, **so that** recommendations reflect profit and operations, not just co-purchase.

**Acceptance Criteria:**
- **AC1** — A composite score uses configurable default weights (`0.4·lift + 0.3·margin + 0.2·turn − 0.1·shrink`, normalized as needed); weights live in config.
- **AC2** — Each recommendation exposes per-objective **components** and the **composite score** (schema extension).
- **AC3** — Objective inputs come from the product master via the data-access layer.
- **AC4** — Scoring is deterministic and unit-tested against hand-computed values.

**Test Cases:**
- **TC-2B.2.1 (U)** — Composite score equals the hand-computed weighted sum for a fixture.
- **TC-2B.2.2 (U)** — Changing weights changes the composite score as expected.
- **TC-2B.2.3 (U)** — Component fields are present and typed.

### US-2B.3 — Re-rank by composite score with trade-off visibility

> **As a** Category Manager, **I want** results ranked by composite score with trade-offs visible, **so that** I see when a high-lift item is displaced by a higher-margin one.

**Acceptance Criteria:**
- **AC1** — Recommendations rank by composite score when optimization is enabled.
- **AC2** — Response/UI shows lift + composite score + component breakdown (the snack-vs-accessory trade-off from the deep-dive).
- **AC3** — Optimization can be toggled; disabled → Sprint 2A/1 lift ranking (backward compatible).

**Test Cases:**
- **TC-2B.3.1 (U)** — A high-lift/low-margin pair ranks below a lower-lift/higher-margin pair once composite scoring is applied.
- **TC-2B.3.2 (I)** — The API response includes lift + composite score + components.

### US-2B.4 — API: optimize flag + composite score

> **As a** UI (via the API), **I want** an optimize flag and composite scores in the response, **so that** screens can drive optimized recommendations.

**Acceptance Criteria:**
- **AC1** — `POST /api/v1/recommendations` accepts an `optimize` flag; response includes composite score + components.
- **AC2** — Backward compatible when omitted; auth + error envelope unchanged.

**Test Cases:**
- **TC-2B.4.1 (I)** — `optimize=true` → 200 with composite scores.
- **TC-2B.4.2 (I)** — Omitted → Sprint 2A/1 behaviour.

### US-2B.5 — UI: optimization view

> **As a** Category Manager, **I want** an optimize toggle and a clear composite-score view, **so that** I can demo business-objective-driven placement.

**Acceptance Criteria:**
- **AC1** — Category Manager mode has an "optimize (multi-objective)" toggle.
- **AC2** — Results show composite score + component breakdown alongside lift.
- **AC3** — UI calls the API only (L1→L2).

**Test Cases:**
- **TC-2B.5.1 (U)** — A formatting helper renders the composite score + components row.
- **TC-2B.5.2 (static)** — `ui/` still imports no services.

---

# 5. Demo-Ready Exit Criteria (Sprint 2B)

1. Enable multi-objective optimization → a high-lift/low-margin pair drops below a higher-margin pair, with the breakdown visible.
2. Every recommendation still shows a rationale and appears in the audit log.
3. All tests green; `ruff` clean; CI passing.

---

*Confidential — Cognizant Internal · Sprint 2B Backlog · Draft · July 2026 · Maintained by Aditya Srivastava*
