# 📔 Project Journal — Store Layout (Product Placement) Optimizer

> **Purpose of this document:** A chronological development journal recording *what was actually built and committed* to the repository, sprint by sprint. It is the running narrative of the build itself.
>
> **How this differs from `decision_log.md`:** `decision_log.md` records **decisions** — *why* choices were made and what alternatives were rejected. This journal records **development activity** — *what code and docs actually changed*, tied to every git commit. Decisions are logged before they are executed; journal entries are logged after work lands on `main`.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Development / Commit Journal (Living Document) |
| **Status** | Living Document (updated continuously) |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 20 July 2026 |
| **Related Documents** | `decision_log.md` · `architecture.md` · `demo_script.md` · `governance_charter.md` |

---

## 🔧 Maintenance Rule (Read Before Committing)

**Every commit pushed to the repository must be recorded in this journal**, in Section "Commit Log" below, with all of the following:

1. **Short SHA** and full commit subject line
2. **Date** (author date, `YYYY-MM-DD`)
3. **Author**
4. **Sprint / phase** the work belongs to
5. **Files changed** with insertion/deletion counts
6. **Plain-English summary** of what changed and why it mattered

**Process:** After a commit lands on `main`, add its entry to the Commit Log before starting the next unit of work. Keep the newest entry at the bottom of its sprint section (chronological order). Update the **Last Updated** date in the metadata block whenever you add an entry.

> **Enforcement:** A version-controlled `post-commit` hook (`.githooks/post-commit`, activated via `git config core.hooksPath .githooks`) **auto-captures every commit** into the "Auto-Captured Commits" section below — SHA, date, author, subject, and files changed. Your job after a commit is to **file** each auto-captured entry into the correct sprint section under Commit Log and replace the auto-note with a plain-English summary. Because a commit cannot contain its own final hash, the most recent commit's entry always lands in Auto-Captured first and is filed on the next commit (the journal lags the tip by one commit — this is expected).

---

## 🗺️ Sprint Roadmap (from `decision_log.md` D-025)

| Sprint | Focus | Status |
|--------|-------|--------|
| **Foundation** | Vision, Data Contract, Architecture, Repo/CI setup, documentation | ✅ Complete |
| **Sprint 1** | Core MBA + #9 Explainability & Governance | 🔄 In review (US-1.1–US-1.11 done; awaiting sign-off) |
| **Sprint 2** | #1 Contextual Affinity + #6 Multi-Objective Optimizer | ⏳ Not started |
| **Sprint 3** | #4 Omnichannel Affinity + #5 Segmentation | ⏳ Not started |
| **Sprint 4** | #3 GenAI Planogram Agent | ⏳ Not started |
| **Sprint 5** | #8 Vendor Collaboration Module | ⏳ Not started |
| **Hardening** | Cloud demo deployment (Phase 2) | ⏳ Deferred |

---

# AUTO-CAPTURED COMMITS (UNFILED)

The `post-commit` hook appends each new commit here automatically. File each entry into the correct sprint section under **Commit Log** below, replace the auto-note with a plain-English summary, then commit the journal update.

<!-- JOURNAL:AUTO -->

---

# COMMIT LOG

## Foundation Sprint

Focus: establish the repository, the authoritative documentation set, and the source-of-truth hierarchy that all subsequent code will follow. No application code yet — this sprint deliberately front-loads documentation and project scaffolding per D-026 (documentation discipline).

---

### `52d356b` — README for Store Layout Optimizer demo

| Field | Value |
|-------|-------|
| **Date** | 2026-07-17 |
| **Author** | adisri94 &lt;Aditya.Srivastava2@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `README.md` — new file (+105)

**Summary:** Initial human-facing README establishing the project name, demo positioning, prerequisites (Python 3.11+, `uv`, 16 GB RAM, optional Anthropic key), the 3-command setup flow (`make setup` / `seed` / `demo`), the 3 UI modes, and the top-level project structure. First content committed to the repo.

---

### `c3e62a2` — Create CLAUDE.md for project overview and guidelines

| Field | Value |
|-------|-------|
| **Date** | 2026-07-17 |
| **Author** | adisri94 &lt;Aditya.Srivastava2@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `Claude.md` — new file (+195)

**Summary:** Added the LLM-facing project brief (`CLAUDE.md`) — the authoritative entry point for Claude Code. Defines the source-of-truth hierarchy, the 8 non-negotiable design principles, repository structure, the 3 services, the locked dependency list, key contracts (governance wrapper, data access, LLM client), coding conventions, and the sprint build sequence. At this point it referenced several docs (`architecture.md`, `decision_log.md`, etc.) that did not yet exist in the repo.

---

### `1100972` — Add project docs: architecture, decision log, data contract, business docs

| Field | Value |
|-------|-------|
| **Date** | 2026-07-17 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `docs/Data_Product_Contract_Store_Layout_Optimizer_1.1.md` — new file (+663)
- `docs/Enhancement_DeepDive_Store_Layout_Optimizer1.1.md` — new file (+431)
- `docs/Product_Vision_OnePager_v2.1_Store_Layout_Optimizer.md` — new file (+134)
- `docs/architecture.md` — new file (+1009)
- `docs/decision_log.md` — new file (+912)
- **Total:** 5 files, +3149

**Summary:** Populated the `docs/` reference set that the `CLAUDE.md` source-of-truth hierarchy depends on. Placed `architecture.md` and `decision_log.md` at their canonical paths so the existing `CLAUDE.md` references resolve. Added the three supporting business/data documents (Data Product Contract v1.1, Product Vision One-Pager v2.1, Enhancement Deep-Dive v1.1). This closed the gap where `CLAUDE.md` referenced the two top source-of-truth documents that were previously missing.

---

### `f9a5ddc` — Add demo script and governance charter docs; wire up references

| Field | Value |
|-------|-------|
| **Date** | 2026-07-20 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `Claude.md` — modified (+3 / −2 net; 5 lines touched)
- `docs/architecture.md` — modified (+3 / −1; doc listings)
- `docs/demo_script.md` — new file (+139)
- `docs/governance_charter.md` — new file (+148)
- **Total:** 4 files, +293 / −3

**Summary:** Added two new docs — `demo_script.md` (Sprint 1 presenter walkthrough) and `governance_charter.md` (business-facing governance rulebook covering POL-001–005, the explainability standard, fairness commitments, and audit/override rules). Fixed broken `demo_script.txt` → `demo_script.md` links inside the charter. Wired `governance_charter.md` into `CLAUDE.md` (source-of-truth hierarchy, repo tree, and Related Docs table) and updated `architecture.md`'s three doc listings (metadata, §2 repo tree, Related Documents table) for consistency across the doc set.

---

### `0ca715b` — Add project journal and post-commit journaling hook

| Field | Value |
|-------|-------|
| **Date** | 2026-07-20 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `.githooks/post-commit` — new file (+65)
- `Claude.md` — modified (+1)
- `docs/architecture.md` — modified (+2)
- `docs/project_journal.md` — new file (+181)
- **Total:** 4 files, +249

**Summary:** Created this development/commit journal documenting all Foundation-sprint commits to date, with a maintenance rule and empty Sprint 1–5 sections. Added the `post-commit` hook (`.githooks/post-commit`, activated via `core.hooksPath`) that auto-captures every commit's SHA, date, author, subject, and file stats into the Auto-Captured section for filing. Registered `project_journal.md` in the `CLAUDE.md` and `architecture.md` doc listings. This commit was itself auto-captured by the hook it introduced, then filed here.

---

### `76982a6` — Journal: file 0ca715b entry into Foundation sprint

| Field | Value |
|-------|-------|
| **Date** | 2026-07-20 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `docs/project_journal.md` — modified (+19)

**Summary:** Housekeeping commit that moved the auto-captured entry for `0ca715b` out of the Auto-Captured zone and into the Foundation Commit Log with a written summary — the first exercise of the filing half of the journaling workflow.

---

### `cc41d59` — Journal: file 76982a6 entry into Foundation sprint

| Field | Value |
|-------|-------|
| **Date** | 2026-07-20 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `docs/project_journal.md` — modified (+15)

**Summary:** Housekeeping commit that filed the auto-captured entry for `76982a6` into the Foundation Commit Log — the lag-by-one filing step for the previous journal-sync commit.

---

### `8d1b55a` — Add Windows task runner (tasks.ps1) and log D-031

| Field | Value |
|-------|-------|
| **Date** | 2026-07-20 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation |

**Files changed:**
- `tasks.ps1` — new file (+124)
- `README.md` — modified (+16)
- `docs/decision_log.md` — modified (+26; D-031)
- `docs/architecture.md` — modified (+2)
- `docs/project_journal.md` — modified (+15)
- **Total:** 5 files, +183

**Summary:** Added `tasks.ps1`, a Windows-native PowerShell task runner mirroring the Makefile verbs (`setup`/`seed`/`demo`/`test`/`reset`/`clean`) with a `uv` resolver that falls back to `python -m uv`. Logged D-031 and documented the PyPI `pip install --user uv` route in the README for proxy-restricted environments where the astral install script is blocked. Closes the Foundation-sprint toolchain gap (no `make` required on Windows).

---

### `388c3bc` — Lock Sprint 1 backlog for development (D-032)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-22 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Foundation → Sprint 1 boundary |

**Files changed:**
- `docs/sprint_1_backlog.md` — new file (+347)
- `docs/decision_log.md` — modified (+31; D-032)
- `Claude.md` — modified (+4)
- `docs/project_journal.md` — modified (+22 / −1)
- **Total:** 4 files, +403 / −1

**Summary:** Created and locked the Sprint 1 backlog (11 user stories US-1.1–US-1.11 with acceptance criteria and test cases), logged D-032, and bound development to the active sprint backlog in CLAUDE.md (Section 10 rule, Section 11 checklist step 0, Section 12 listing). Marks the transition from Foundation planning to Sprint 1 coding.

---

## Sprint 1 — Core MBA + #9 Explainability & Governance

_Backlog locked 22 Jul 2026 (D-032, `sprint_1_backlog.md`). Entries are added here as Sprint 1 work lands on `main`._

Planned scope: Apriori/FP-Growth engine over synthetic POS baskets, the governance wrapper (`services/governance/`) live from day one, and the first end-to-end vertical slice (one basket → one rule → one governed recommendation).

---

### `57da34b` — Sprint 1 slice 1: project scaffolding + US-1.1 data generator + US-1.2 data access

| Field | Value |
|-------|-------|
| **Date** | 2026-07-22 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Sprint 1 (US-1.1, US-1.2) |

**Files changed:** 24 files, +3921 / −27 — key additions:
- `pyproject.toml`, `uv.lock`, `.gitignore`, `.env.example`, `.python-version`
- `data/seed.py` (+361) — US-1.1 deterministic synthetic data generator
- `platform_services/{config,data_access,exceptions}.py` — US-1.2 data-access layer
- `tests/` — 13 tests (US-1.1, US-1.2, layer-boundary guard)

**Summary:** First Sprint 1 code slice. Delivered US-1.1 (synthetic Product Master + POS generator, deterministic, schema-faithful, affinity-seeded) and US-1.2 (data-access layer: `load_parquet`, `duckdb_query`, `get_sqlite_conn` with typed errors). Established `pyproject.toml` with the locked dependency set (verified installing on Python 3.13) and ruff/pytest config. Renamed Layer 4 package to `platform_services/` (D-033). Sample Parquet intentionally not committed until the schema settles.

---

### `9fee04d` — Sprint 1 US-1.3: Market Basket Analysis engine

| Field | Value |
|-------|-------|
| **Date** | 2026-07-22 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Sprint 1 (US-1.3) |

**Files changed:**
- `api/schemas.py` — new (+40); the `Recommendation` model (§9)
- `services/affinity_optimization/mba_core/engine.py` — new (+127)
- service/test scaffolding — **Total:** 10 files, +295

**Summary:** Implemented the MBA engine (US-1.3): mines association rules via mlxtend (FP-Growth default, Apriori selectable), scored by lift/confidence/support, mapped to ranked `Recommendation` objects. Exposes raw mining only — no user-facing entry point, so nothing bypasses governance. Added `Recommendation` to `api/schemas.py` (with a `contributing_baskets` evidence field). Tests TC-1.3.1–1.3.6.

---

### `9c196f2` — Sprint 1 US-1.4–1.7: Explainability & Governance (#9)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-22 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Sprint 1 (US-1.4–US-1.7) |

**Files changed:** 14 files, +777 / −4 — `services/governance/{explainability,policy_engine,audit_writer,__init__}.py`, `services/affinity_optimization/service.py`, `api/schemas.py`, governance tests.

**Summary:** Built the governance epic. US-1.4 template rationale (no LLM, flag-gated seam). US-1.5 policy engine POL-001–005 (POL-003/004 return `not_evaluated`, never a false pass). US-1.6 append-only JSONL audit log with a sole writer. US-1.7 `govern()`/`get_audit_log()` and a governed `get_recommendations()` that returns only `GovernedRecommendation` (governance-in-path). 35 tests total.

---

### `75368f2` — Sprint 1 US-1.8–1.9: API layer (recommendations + audit endpoints)

| Field | Value |
|-------|-------|
| **Date** | 2026-07-22 |
| **Author** | Srivastava &lt;2271124@cognizant.com&gt; |
| **Sprint** | Sprint 1 (US-1.8, US-1.9) |

**Files changed:** 12 files, +356 / −1 — `api/auth.py`, `api/main.py`, `api/routes/{health,recommendations,audit}.py`, `api/schemas.py`, `tests/integration/test_api.py`, `pyproject.toml` (+httpx).

**Summary:** Added the FastAPI layer. `X-API-Key` auth (D-029), a standard error envelope, and endpoints `POST /api/v1/recommendations`, `GET /api/v1/audit/log`, `GET /api/v1/audit/{recommendation_id}`, `GET /health`. Added `httpx` as a test-only dev dependency for TestClient (D-034). 42 tests total (TC-1.8.x, TC-1.9.x).

---

## Sprint 2 — #1 Contextual Affinity + #6 Multi-Objective Optimizer

_No commits yet._

---

## Sprint 3 — #4 Omnichannel Affinity + #5 Segmentation

_No commits yet._

---

## Sprint 4 — #3 GenAI Planogram Agent

_No commits yet._

---

## Sprint 5 — #8 Vendor Collaboration Module

_No commits yet._

---

# OPEN FOLLOW-UPS

Items noted during development that are not yet resolved:

- **Doc filename consistency:** `data_contract.md` is referenced by canonical name in `CLAUDE.md`/`architecture.md`, but the actual file is `docs/Data_Product_Contract_Store_Layout_Optimizer_1.1.md` (likewise the Product Vision One-Pager and Enhancement Deep-Dive use long versioned names). Decide whether to rename files to canonical names or repoint the references.
- **Missing doc:** `docs/production_mapping.md` is referenced across the doc set but does not yet exist.
- **Commit identity:** Commits from this machine are attributed to `Srivastava <2271124@cognizant.com>` (auto-configured). Confirm the intended `git config user.name` / `user.email`.
- **Journal automation:** ✅ Done — `.githooks/post-commit` auto-captures every commit; `core.hooksPath` must be set to `.githooks` on each clone (the hook is version-controlled, but the config pointer is per-clone).

---

*Confidential — Cognizant Internal · Project Journal · Maintained by Aditya Srivastava*
