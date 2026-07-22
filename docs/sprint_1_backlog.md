# 🧾 Sprint 1 Backlog — Core MBA + #9 Explainability & Governance

> **Purpose of this document:** The authoritative, reviewable backlog for Sprint 1. It defines the **user stories**, **acceptance criteria**, and **test cases** that development must satisfy. Per `CLAUDE.md`, Sprint 1 code must implement exactly these stories — no more (scope creep), no less (partial delivery). Anything not listed here is out of scope for Sprint 1.
>
> **Review gate:** This backlog is to be reviewed and approved by the owner **before** coding begins. Changes to scope after approval require a new `decision_log.md` entry.
>
> **🔒 LOCKED (22 Jul 2026, D-032):** Approved by the owner. The user stories, acceptance criteria, and test cases below are frozen for Sprint 1 development. Any addition, removal, or material change requires a new `decision_log.md` entry before it is implemented.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Sprint Backlog (User Stories · Acceptance Criteria · Test Cases) |
| **Sprint** | Sprint 1 — Core MBA + #9 Explainability & Governance |
| **Status** | 🔒 Approved & Locked for Development (22 Jul 2026) — see `decision_log.md` D-032 |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 22 July 2026 |
| **Related Docs** | `architecture.md` §4, §7, §9, §10, §14 · `decision_log.md` D-025, D-012 · `governance_charter.md` POL-001–005 · `demo_script.md` (Sprint 1 scenes) · `data_contract.md` |

---

## 1. Sprint 1 Scope (Confirmed)

Sprint 1 delivers the **first end-to-end vertical slice**: synthetic POS data → market-basket rule mining → a governed, explainable, audited recommendation surfaced in the UI.

**In scope:**
1. Synthetic data generator for the POS + product master domains (minimum needed to mine baskets).
2. Data-access layer (`platform/data_access.py`) — DuckDB over Parquet + SQLite connection.
3. Market Basket Analysis engine (Apriori / FP-Growth via `mlxtend`) producing raw recommendations scored by **lift, confidence, support**.
4. Governance service (#9): plain-English rationale, policy checks (POL-001–005), append-only JSONL audit log — **in the path of every recommendation** (D-012, principle #5).
5. FastAPI endpoints: `POST /api/v1/recommendations`, `GET /api/v1/audit/log`, `GET /api/v1/audit/{recommendation_id}`, `GET /health`, with `X-API-Key` auth.
6. Minimal Streamlit UI: **Category Manager** mode (get recommendations + "Why this recommendation?" panel) and **Admin/Governance** mode (audit log view).

**Explicitly OUT of scope for Sprint 1** (deferred to later sprints — do NOT build):
- ❌ Contextual signals: time-of-day, weather, promo (#1 — Sprint 2)
- ❌ Multi-objective scoring: margin/turn/shrink (#6 — Sprint 2)
- ❌ Omnichannel/clickstream, segmentation (#4/#5 — Sprint 3)
- ❌ GenAI planogram chat (#3 — Sprint 4)
- ❌ Vendor portal / promo ingestion (#8 — Sprint 5)
- ❌ FAISS vector store, NetworkX graph store (not needed for baseline MBA)
- ❌ Live Anthropic API calls (rationale uses template generation in Sprint 1; LLM narrative is additive later — mock-first, principle #7)

---

## 2. Personas Involved (D-004)

| Persona | Role in Sprint 1 |
|---------|------------------|
| **Category Manager** | Requests recommendations; reads the plain-English rationale |
| **Data Steward / Admin** | Reviews the audit log; confirms every recommendation was governed |

(CPG Vendor Partner and Merchandising Head are not exercised until later sprints.)

---

## 3. Definition of Ready (per story)

- Story has a persona, a value statement, acceptance criteria in Given/When/Then form, and at least one test case.
- Referenced schema/contract exists in `architecture.md` (§9 data contracts, §7 API).
- No dependency on an out-of-scope enhancement.

## 4. Definition of Done (Sprint 1)

- All acceptance criteria for the story pass.
- Unit tests written in `tests/unit/` mirroring the module path; integration tests in `tests/integration/`.
- `ruff check .` clean; type hints + Google-style docstrings on all public functions (§15).
- Every recommendation-producing path routes through `governance.govern()` (§4.4) — verified by test.
- CI (`.github/workflows/ci.yml`) green.
- Journal entry filed after commit; docs updated if contracts changed.

---

# 5. Epics & User Stories

Story IDs: `US-1.x`. Test IDs: `TC-1.x.y` (unit `U`, integration `I`).

---

## EPIC A — Data Foundation

### US-1.1 — Generate synthetic POS & product data

> **As a** Data Steward, **I want** a deterministic synthetic-data generator, **so that** every teammate can mine the same baskets and reproduce the same recommendations.

**Scope note:** Sprint 1 needs only the domains required to mine baskets: **POS Transactions** and **Product Master**. Other four domains are generated in later sprints.

**Acceptance Criteria:**
- **AC1** — Given a clean checkout, when I run `data/seed.py` (`./tasks.ps1 seed`), then `data/samples/pos_transactions.parquet` and `data/samples/product_master.parquet` are created.
- **AC2** — Given the generator runs twice with the fixed seed (`random.seed(42)`, D per §6.3), then both runs produce byte-identical row counts and identical basket contents.
- **AC3** — Given the generated data, then POS transactions conform to the `data_contract.md` POS schema (transaction_id, basket/line linkage, sku_id, store_id, timestamp) and product master to its schema (sku_id, product_name, category, margin fields).
- **AC4** — Given the generated data, then at least some SKU pairs co-occur frequently enough to produce non-trivial rules (support high enough that Apriori returns ≥ 1 itemset at min_support=0.01).
- **AC5** — Volumes are demo-appropriate but test-friendly: full generation targets D-009 volumes; a `--sample` / small-mode flag produces a tiny deterministic set for tests.

**Test Cases:**
- **TC-1.1.1 (U)** — Seed twice in small-mode; assert identical DataFrame shapes and identical sorted basket tuples.
- **TC-1.1.2 (U)** — Assert generated POS columns exactly match the POS schema field names/types from `data_contract.md`.
- **TC-1.1.3 (U)** — Assert product master `category` and margin fields are populated (no nulls) for every `sku_id` referenced in POS.
- **TC-1.1.4 (U)** — Assert referential integrity: every `sku_id` in POS exists in product master.

---

### US-1.2 — Read data through the data-access layer

> **As a** developer (enabler), **I want** all data reads to go through `platform/data_access.py`, **so that** services never touch Parquet/SQLite directly (§5.2, principle: layer boundaries).

**Acceptance Criteria:**
- **AC1** — `data_access.load_parquet(domain)` returns a DataFrame for `"pos_transactions"` and `"product_master"`.
- **AC2** — `data_access.duckdb_query(sql)` executes SQL over the Parquet files and returns a DataFrame.
- **AC3** — `data_access.get_sqlite_conn()` returns a connection to `data/app.db`, auto-creating the schema on first call.
- **AC4** — Calling with an unknown domain raises a clear, typed error (not a bare `KeyError`/`FileNotFoundError`).
- **AC5** — No service module imports `sqlite3`, `pyarrow`, or calls `open()` on a data file directly (enforced by a lint/grep test).

**Test Cases:**
- **TC-1.2.1 (U)** — `load_parquet("product_master")` returns non-empty DataFrame with expected columns.
- **TC-1.2.2 (U)** — `duckdb_query` with a simple COUNT returns the correct row count.
- **TC-1.2.3 (U)** — Unknown domain raises the defined custom exception with a helpful message.
- **TC-1.2.4 (I)** — Repo scan test: assert no file under `services/` references `sqlite3.connect(` or `open(` on `data/`.

---

## EPIC B — Market Basket Analysis Core

### US-1.3 — Mine association rules from baskets

> **As a** Category Manager, **I want** the tool to find product pairs frequently bought together with lift/confidence/support, **so that** placement suggestions are grounded in real transaction patterns (not guesses).

**Acceptance Criteria:**
- **AC1** — Given POS baskets, when the engine runs, then it returns association rules each carrying **lift**, **confidence**, and **support** (matching the `Recommendation` fields in §9).
- **AC2** — Engine supports both **Apriori** and **FP-Growth** (`mlxtend`); algorithm is selectable via a parameter, default **FP-Growth**; both return equivalent rule sets on the same data.
- **AC3** — Results are ranked by lift descending; `top_k` limits the count (default 20).
- **AC4** — Support/confidence/lift thresholds are parameters with sensible defaults; no rule below `min_support` is returned.
- **AC5** — Each rule maps to a `Recommendation` with `sku_a`, `sku_b`, a `placement_type` (default `"adjacency"` for Sprint 1), and a generated `recommendation_id`.
- **AC6** — Lift is computed correctly: for an independent pair (co-occurrence = product of marginals) lift ≈ 1.0 (±tolerance).

**Test Cases:**
- **TC-1.3.1 (U)** — Hand-built basket fixture with a known pair; assert support/confidence/lift equal manually-computed values within tolerance.
- **TC-1.3.2 (U)** — Independent pair fixture → lift ≈ 1.0.
- **TC-1.3.3 (U)** — Apriori and FP-Growth return the same rule set (same pairs, same metrics) on the fixture.
- **TC-1.3.4 (U)** — `top_k=5` returns exactly 5 rules, sorted by lift descending.
- **TC-1.3.5 (U)** — Rules below `min_support` are excluded.
- **TC-1.3.6 (U)** — Output objects validate against the `Recommendation` Pydantic model.

---

## EPIC C — Explainability & Governance (#9) — the differentiator

### US-1.4 — Attach a plain-English rationale to every recommendation

> **As a** Category Manager, **I want** each recommendation to include a one-sentence plain-English reason, **so that** I can trust and act on it without a data-science background (governance_charter §4).

**Acceptance Criteria:**
- **AC1** — `governance.govern(recommendation, context)` returns a `GovernedRecommendation` (§9) with a non-empty `rationale`.
- **AC2** — The rationale names both SKUs, references the lift in plain language, and cites the supporting transaction count (e.g. *"Customers who buy X are 2.1× more likely to also buy Y, based on 3,200 comparable transactions."*).
- **AC3** — Sprint 1 generates the rationale from a **template** (no LLM call); the design leaves a seam for an LLM narrative later (principle #7, mock-first).
- **AC4** — A recommendation that cannot be explained in one sentence is not returned (charter §4 "no black box").

**Test Cases:**
- **TC-1.4.1 (U)** — `govern()` output has a non-empty rationale containing both SKU names and the lift value.
- **TC-1.4.2 (U)** — Rationale is deterministic for the same input (template, not random).
- **TC-1.4.3 (U)** — Output validates against `GovernedRecommendation`.

---

### US-1.5 — Enforce policy rules on every recommendation

> **As a** Data Steward, **I want** policy checks POL-001–005 applied to every recommendation, **so that** nothing non-compliant reaches a user (governance_charter §3, architecture §10.3).

**Acceptance Criteria:**
- **AC1** — Each of POL-001…POL-005 is a small pure function in `policy_engine.py` returning a `PolicyResult` (pass/fail/warning + message).
- **AC2** — **POL-002** (confidence ≥ 0.1): a recommendation below threshold is flagged/blocked; this is the primary Sprint 1 gate.
- **AC3** — **POL-005** (regulated categories alcohol/tobacco): recommendations touching a regulated category are flagged.
- **AC4** — **POL-001** (high-margin ≤ 40% of an endcap): evaluated where placement/margin context is available; documented as partial if endcap composition isn't modelled yet.
- **AC5** — **POL-003 / POL-004** (brand mandate / vendor equity): config-driven; where the config/data is absent they pass with a "not-evaluated" note rather than silently — never a false pass.
- **AC6** — `policy_warnings` on the `GovernedRecommendation` lists any triggered rule; the recommendation still carries the result transparently.

**Test Cases:**
- **TC-1.5.1 (U)** — POL-002: confidence 0.05 → fail/flag; confidence 0.5 → pass.
- **TC-1.5.2 (U)** — POL-005: a SKU in a regulated category → flagged with the correct message.
- **TC-1.5.3 (U)** — POL-001: synthetic endcap at 45% high-margin → fail; at 35% → pass.
- **TC-1.5.4 (U)** — Every policy function returns a well-formed `PolicyResult` (schema test).
- **TC-1.5.5 (U)** — When brand/vendor config is absent, POL-003/POL-004 return "not-evaluated", never "pass".

---

### US-1.6 — Write an append-only audit entry for every recommendation

> **As a** Data Steward, **I want** every recommendation permanently recorded, **so that** any recommendation can be justified after the fact (charter §6, D-021).

**Acceptance Criteria:**
- **AC1** — Every `govern()` call writes exactly one JSONL line to `data/audit.jsonl` via `audit_writer.py`.
- **AC2** — The line conforms to the `AuditEntry` schema (§9): `audit_id`, ISO-8601 UTC `timestamp`, `recommendation_id`, `policy_result`, `evidence` (lift/confidence/support).
- **AC3** — The log is **append-only**: existing lines are never modified or removed; a second recommendation adds a line without touching the first.
- **AC4** — Only `audit_writer.py` writes to `audit.jsonl` (§6.3) — enforced by test.
- **AC5** — The `GovernedRecommendation.audit_id` matches the written entry's `audit_id`.

**Test Cases:**
- **TC-1.6.1 (U)** — After one `govern()`, `audit.jsonl` has exactly one parseable JSON line matching `AuditEntry`.
- **TC-1.6.2 (U)** — After two `govern()` calls, line count increases by exactly 1 each; the first line is byte-identical before/after the second call.
- **TC-1.6.3 (U)** — `timestamp` parses as ISO-8601 UTC.
- **TC-1.6.4 (I)** — Repo scan: no module other than `audit_writer.py` opens `audit.jsonl` for writing.

---

### US-1.7 — Governance is unavoidable (governance-in-path)

> **As a** Data Steward, **I want** it to be impossible to return a recommendation without governing it, **so that** the compliance guarantee holds structurally, not by convention (principle #5, D-012, §4.4).

**Acceptance Criteria:**
- **AC1** — The public `get_recommendations()` returns only `GovernedRecommendation` objects — never raw `Recommendation`.
- **AC2** — There is no public code path that returns raw recommendations to a caller.
- **AC3** — For N recommendations returned, exactly N audit lines are written.

**Test Cases:**
- **TC-1.7.1 (I)** — Call `get_recommendations()`; assert every element is a `GovernedRecommendation` with a rationale and an `audit_id`.
- **TC-1.7.2 (I)** — Assert audit line count increased by exactly the number of recommendations returned.
- **TC-1.7.3 (U)** — Type/contract test: `get_recommendations` return annotation is `list[GovernedRecommendation]`.

---

## EPIC D — API Layer

### US-1.8 — Get recommendations over HTTP

> **As a** Category Manager (via the UI), **I want** a recommendations endpoint, **so that** the UI can fetch governed suggestions.

**Acceptance Criteria:**
- **AC1** — `POST /api/v1/recommendations` with `{store_id, category?, top_k?}` returns a list of governed recommendations (§7.3).
- **AC2** — Request/response bodies are Pydantic models from `api/schemas.py`; timestamps ISO-8601 UTC (§7.4).
- **AC3** — Missing/invalid `X-API-Key` → 401/403; valid key → 200.
- **AC4** — Invalid body (e.g. missing `store_id`) → 422 with the standard error shape `{"error": {"code", "message"}}`.
- **AC5** — `GET /health` returns 200 with a liveness payload.

**Test Cases:**
- **TC-1.8.1 (I)** — Valid key + valid body → 200; response items validate against `GovernedRecommendation`.
- **TC-1.8.2 (I)** — No `X-API-Key` → 401/403.
- **TC-1.8.3 (I)** — Missing `store_id` → 422 with standard error shape.
- **TC-1.8.4 (I)** — `GET /health` → 200.

---

### US-1.9 — Inspect the audit trail over HTTP

> **As a** Data Steward, **I want** audit endpoints, **so that** the Admin UI can display the governance record.

**Acceptance Criteria:**
- **AC1** — `GET /api/v1/audit/log?limit=` returns recent `AuditEntry` items, newest first.
- **AC2** — `GET /api/v1/audit/{recommendation_id}` returns the audit entry/entries for that recommendation, or 404 if none.
- **AC3** — Both endpoints require `X-API-Key`.

**Test Cases:**
- **TC-1.9.1 (I)** — After generating recommendations, `GET /audit/log` returns ≥ that many entries, newest first.
- **TC-1.9.2 (I)** — `GET /audit/{known_id}` returns the matching entry; unknown id → 404.
- **TC-1.9.3 (I)** — Missing key → 401/403.

---

## EPIC E — UI

### US-1.10 — Category Manager: see recommendations and why

> **As a** Category Manager, **I want** to pick a category, get recommendations, and open a "Why this recommendation?" panel, **so that** I can act on transparent suggestions (demo_script Scenes 2–3).

**Acceptance Criteria:**
- **AC1** — The Category Manager mode lets me select a category/store and click "Get Recommendations".
- **AC2** — Results show each pairing with its lift, confidence, and support.
- **AC3** — A "Why this recommendation?" control reveals the plain-English rationale and any policy warnings.
- **AC4** — The UI calls the API over HTTP (never imports services directly — L1→L2 only, §3.2).

**Test Cases:**
- **TC-1.10.1 (I)** — With the API running, the UI request returns and renders ≥ 1 recommendation with all three scores. *(May be validated via the API integration test that the UI calls; UI smoke-tested manually and via the `verify` skill.)*
- **TC-1.10.2 (U)** — UI data-formatting helper turns a `GovernedRecommendation` payload into the display row correctly.
- **TC-1.10.3 (static)** — Assert `ui/` modules make HTTP calls and do not `import services...`.

---

### US-1.11 — Admin/Governance: view the audit log

> **As a** Data Steward, **I want** an Admin mode that lists audit entries for recommendations, **so that** I can demonstrate the governance trail (demo_script Scene 3).

**Acceptance Criteria:**
- **AC1** — Admin/Governance mode lists recent audit entries with timestamp, recommendation id, evidence, and policy result.
- **AC2** — I can find the audit entry corresponding to a recommendation shown in Category Manager mode.
- **AC3** — Data is fetched via the audit API (L1→L2).

**Test Cases:**
- **TC-1.11.1 (I)** — Admin view fetches `/audit/log` and renders ≥ 1 entry with all fields.
- **TC-1.11.2 (U)** — Audit-row formatting helper renders an `AuditEntry` correctly.

---

# 6. Traceability Matrix

| Story | Enhancement | Architecture ref | Decision / Policy |
|-------|-------------|------------------|-------------------|
| US-1.1 | Data foundation | §2, §6.2, data_contract | D-006, D-008, D-009 |
| US-1.2 | Platform enabler | §5.2 | principle: layer boundaries |
| US-1.3 | MBA core | §4.1 | D-025 (Sprint 1) |
| US-1.4 | #9 Explainability | §10.1, charter §4 | D-012 |
| US-1.5 | #9 Governance | §10.3, charter §3 | POL-001–005 |
| US-1.6 | #9 Audit | §10.2, charter §6 | D-021 |
| US-1.7 | #9 Governance-in-path | §4.4 | principle #5, D-012 |
| US-1.8 | API | §7.3 | D-029 (auth) |
| US-1.9 | API (audit) | §7.3 | D-021 |
| US-1.10 | UI (Category Mgr) | §3.2, demo_script | D-004 |
| US-1.11 | UI (Admin/Gov) | §3.2, demo_script | D-004 |

---

# 7. Test Strategy Summary (per §14)

- **Unit tests** (`tests/unit/`) mirror `services/` + `platform/` structure; every public function ≥ 1 test.
- **Integration tests** (`tests/integration/`) cover the recommendation flow (Flow A, §8.1) end to end using small synthetic data and **no live LLM**.
- **Every policy rule** (POL-001–005) has a dedicated test (§14.2).
- **Every audit write** has a format test (§14.2).
- **Governance-in-path** is asserted structurally (US-1.7).
- No test hits the real Anthropic API.
- Ordinarily-green **CI** runs `ruff` + `pytest` on every PR (D-028, §14.3).

---

# 8. Sprint 1 Definition of Demo-Ready (exit criteria)

Maps to `demo_script.md` Scenes 2–3:
1. `./tasks.ps1 seed` produces data; `./tasks.ps1 demo` starts API + UI.
2. In Category Manager mode, selecting a category returns ≥ 1 recommendation with lift/confidence/support and a plain-English rationale.
3. In Admin/Governance mode, the corresponding audit entry is visible.
4. All tests green; `ruff` clean; CI passing.

---

## 🔗 Related Documents

| Doc | Use for |
|-----|---------|
| `architecture.md` | Contracts, layer rules, schemas, policy implementation locations |
| `governance_charter.md` | The policy rules these stories enforce |
| `demo_script.md` | The Sprint 1 narrative these stories must make demoable |
| `decision_log.md` | Why Sprint 1 is scoped this way (D-025) |
| `data_contract.md` | Field-level schemas for US-1.1 |
| `project_journal.md` | Where completed Sprint 1 commits are recorded |

---

*Confidential — Cognizant Internal · Sprint 1 Backlog · Draft for Review · July 2026 · Maintained by Aditya Srivastava*
