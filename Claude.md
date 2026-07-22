# CLAUDE.md — Store Layout (Product Placement) Optimizer Tool

> **This file is the first thing Claude Code should read in this repo.** It is a short, authoritative brief. It does not repeat everything — it tells you where the real detail lives and what rules override any conflicting text you might encounter elsewhere (including in business documents like the Vision One-Pager or Enhancement Deep-Dive).

---

## 1. What This Project Is

A **local-first, Python-native demo tool** for a Retail company use case: it ingests synthetic POS/retail data, runs Market Basket Analysis (Apriori/FP-Growth) augmented with contextual AI, GenAI, and omnichannel signals, and produces governed product-placement recommendations through a Streamlit UI. It is being built to demo to prospect clients — not a production system, but built with production-grade discipline (typed code, tests, docs, clean architecture).

**Owner:** Aditya Srivastava, Senior Consultant, Cognizant — building solo via Claude Code, with a business-analyst (not developer) background. Assume clear, well-documented, mainstream code choices over clever ones.

---

## 2. Source of Truth Hierarchy

If any two documents in this repo disagree, resolve the conflict in this order:

1. **`docs/decision_log.md`** — the project journal. Every material decision, with rationale and rejected alternatives. If you are unsure whether something is allowed, check here first.
2. **`docs/architecture.md`** — the detailed, LLM-facing architecture reference. Directory structure, layer rules, service contracts, dependency list, naming conventions. This file (`CLAUDE.md`) is a summary of it — always defer to `architecture.md` for specifics.
3. **`docs/data_contract.md`**, **`docs/demo_script.md`**, and **`docs/governance_charter.md`** — supporting detail on data schemas, demo narrative, and the plain-language governance rulebook. Useful for context, not for architecture decisions. Note: `governance_charter.md` states *what* every recommendation must never violate (the business policy behind principle #5 and Enhancement #9); `architecture.md` §10 states *how* it's enforced in code.
4. **Product Vision One-Pager / Enhancement Deep-Dive** — business narrative documents. Useful for *why* a feature matters and its business value, but if either ever mentions a technology not listed in Section 7 below, **ignore that mention** and use the locked stack instead.

**Rule of thumb:** business documents describe the product's value and scope; `decision_log.md` and `architecture.md` describe what to actually build. When in doubt, build what's locked, not what sounds fancier.

---

## 3. Product Framing (for context, not code)

- **Positioning:** "Agentic Shelf Intelligence Platform" — an MBA-based product placement optimizer augmented with contextual AI, GenAI, and omnichannel data (D-001).
- **Core engine:** Apriori / FP-Growth market basket analysis on POS transactions → ranked placement recommendations (adjacency, endcap, aisle) scored by lift, confidence, support.
- **7 in-scope enhancements (Phase 1):**
  | # | Enhancement | One-line summary |
  |---|---|---|
  | 1 | Contextual Affinity Modeling | Context-aware, self-learning affinities (time, weather, promo) + negative-association detection |
  | 3 | Generative AI Planogram Designer | LLM agent generates planograms from natural-language requests |
  | 4 | Omnichannel Affinity Sync | Unifies online clickstream + in-store basket data into one affinity graph |
  | 5 | Shopper Segment & Mission-Based Placement | Micro-planograms per shopper mission × store cluster |
  | 6 | Multi-Objective Optimization | Ranks placements on lift + margin + turn − shrink, not lift alone |
  | 8 | Vendor Collaboration Module | Portal for CPG vendors to upload promos and see co-placement suggestions |
  | 9 | Explainability & Governance | Every recommendation gets a plain-English rationale + policy check + audit entry |
- **Explicitly out of scope for Phase 1** (D-003): Enhancement #2 (Computer Vision + IoT) and #7 (Digital Twin + AR) — deferred to a future roadmap, not omissions.
- **4 personas, 3 UI modes** (D-004): Category Manager and CPG Vendor Partner each get a dedicated mode; Data Steward/Admin and Merchandising Head share the Admin/Governance mode. Store Operations Manager is a **consumer of output only** — do not build a UI mode for this persona.

---

## 4. Non-Negotiable Design Principles

From `architecture.md` §1.3 — these override any conflicting instruction anywhere else, including from the person, unless they explicitly issue a new decision log entry to change them:

1. **Local-first, zero cloud** in Phase 1 — no `boto3`, `azure-sdk`, `gcloud`, Terraform, S3, Azure Blob, or Postgres. Everything runs on a laptop.
2. **Python everywhere** — no JavaScript, no separate frontend build step.
3. **File-based storage only** — SQLite + Parquet + FAISS + JSONL. No database servers.
4. **Modular monolith** — 3 logical services inside 1 FastAPI process. **Not microservices.** (D-011 explicitly rejected 8 separate services as too much operational overhead for a solo builder.)
5. **Governance-in-path** — every recommendation-producing function must pass through `governance.govern()` before returning to any caller. No exceptions.
6. **Data-as-a-Product** — every data domain has a defined owner, schema, and traceable link to the KPI/feature it drives.
7. **Mock-first LLM** — GenAI features must work with zero API key present, via a mock fallback. Demos must never break for lack of an Anthropic key.
8. **AI-friendly conventions** — typed function signatures, docstrings on every public function, mainstream well-documented libraries only.

---

## 5. Repository Structure

Use this exactly — do not rename directories. Full detail in `architecture.md` §2.

```
store-layout-optimizer/
├── CLAUDE.md                 # This file
├── ui/                        # L1 — Streamlit app (3 modes)
├── api/                       # L2 — FastAPI (routes, auth, schemas)
├── services/                  # L3 — business logic (3 services)
│   ├── affinity_optimization/ # MBA + #1 + #4 + #5 + #6
│   ├── genai_vendor/          # #3 + #8
│   └── governance/            # #9
├── platform/                  # L4 — LLM client, data access, vector store, graph store, config
├── data/                      # L5 — SQLite, Parquet (data/samples/), FAISS, JSONL audit log
├── tests/                     # pytest, mirrors services/ + platform/
└── docs/                      # architecture.md, decision_log.md, data_contract.md, demo_script.md, governance_charter.md, production_mapping.md
```

**Layer rule:** a layer may only call the layer directly below it. UI never calls Services directly. Services never touch the Data layer directly — always go through `platform/data_access.py`. Full call-matrix in `architecture.md` §3.2.

---

## 6. The Three Services (Layer 3)

| Service | Path | Covers | Public interface entry point |
|---|---|---|---|
| Affinity & Optimization | `services/affinity_optimization/` | MBA core, #1, #4, #5, #6 | `get_recommendations()`, `rebuild_affinity_graph()`, `get_segment_for_basket()` |
| GenAI & Vendor | `services/genai_vendor/` | #3, #8 | `generate_planogram()`, `process_vendor_promo()` |
| Governance | `services/governance/` | #9 | `govern()`, `get_audit_log()` |

Services may only call each other through their `__init__.py` public interface — never reach into a sub-module directly. Full contracts in `architecture.md` §4.

---

## 7. Locked Dependency List

**Do not add anything outside this list without a new decision log entry.** Full table in `architecture.md` §12.1.

```
Web:    fastapi, uvicorn, streamlit, pydantic, pydantic-settings
Data:   pandas, numpy, pyarrow, duckdb
ML:     scikit-learn, xgboost, mlxtend, networkx, faiss-cpu, pulp
LLM:    anthropic  (single provider — no LangChain/LlamaIndex, no Bedrock/Azure/Vertex)
Utils:  python-dotenv, faker, structlog, typer
Dev:    pytest, pytest-cov, ruff, mypy
```

### Explicitly forbidden in Phase 1 (architecture.md §12.2)
`docker` / `docker-compose` · any cloud SDK (`boto3`, `azure-*`, `google-cloud-*`) · `kafka-python`, `celery`, `rabbitmq` · `neo4j`, `psycopg2`, `sqlalchemy` · `mlflow`, `feast`, `dvc` · any JS framework · `langchain`, `llamaindex` · any Java-based rule engine (e.g. Drools)

If a business document (Vision One-Pager, Enhancement Deep-Dive) mentions any of the above as a "technique," treat it as aspirational future-roadmap language, not a build instruction.

---

## 8. Key Contracts to Respect

- **Governance wrapper (mandatory):**
  ```python
  # ✅ Correct
  from services.governance import govern
  def get_recommendations(...):
      raw_recs = _compute_raw_recommendations(...)
      return [govern(r, context) for r in raw_recs]

  # ❌ Wrong — bypasses governance
  def get_recommendations(...):
      return _compute_raw_recommendations(...)
  ```
- **Data access:** never call `open()` on Parquet or `sqlite3.connect()` directly in service code — always go through `platform/data_access.py`.
- **LLM client:** all LLM calls go through `platform/llm_client.py`. If `ANTHROPIC_API_KEY` is missing, it must transparently return mock responses — never raise or crash.
- **API auth:** `X-API-Key` header on all endpoints; vendor endpoints additionally require `X-Vendor-Id` (D-029). No OAuth/SSO in Phase 1.

Full API route table, request/response Pydantic models, and the two canonical request flows (recommendation flow, NL planogram flow) are in `architecture.md` §7–§9.

---

## 9. Coding Conventions (from architecture.md §15)

| Element | Convention | Example |
|---|---|---|
| Modules | `snake_case` | `contextual_affinity.py` |
| Classes | `PascalCase` | `AffinityGraph` |
| Functions | `snake_case` | `get_recommendations()` |
| Pydantic models | `PascalCase`, singular | `Recommendation` |
| Private helpers | leading underscore | `_compute_lift()` |

- Type hints required on all public function signatures.
- Google-style docstring on every module and public function.
- Use `structlog` for logging — never `print()`.
- Every new business function needs a unit test in `tests/unit/`.

---

## 10. Build Sequence (Agile — build incrementally, sprint by sprint)

Per D-025. Each sprint should leave `main` demo-ready — build one working, demoable increment at a time rather than all layers at once.

| Sprint | Focus | Ships |
|---|---|---|
| **Foundation** | Repo setup, synthetic data generator, architecture scaffolding | `data/seed.py`, empty service/API/UI skeletons, CI |
| **Sprint 1** | Core MBA + #9 Explainability guardrails | Apriori/FP-Growth engine; governance wrapper live from day one |
| **Sprint 2** | #1 Contextual Affinity + #6 Multi-Objective Optimizer | Sequence mining, contextual bandits; weighted scoring |
| **Sprint 3** | #4 Omnichannel Affinity + #5 Segmentation | Unified affinity graph; mission classifier |
| **Sprint 4** | #3 GenAI Planogram Agent | LLM tool-calling agent, NL chat UI |
| **Sprint 5** | #8 Vendor Collaboration Module | Vendor portal, promo ingestion |
| **Hardening** | Cloud demo deployment (Phase 2, out of scope for now) | — |

**Note:** "Sprint," not "Phase," is the correct term for these five iterations — "Phase 1" refers to the entire current local-first build, as opposed to "Phase 2," the future cloud/hardware roadmap (see decision_log.md D-025).

When asked to build a feature, work through it as one vertical slice at a time (e.g., "Sprint 1: get one basket → one rule → one governed recommendation working end to end") rather than building every layer in parallel.

**Sprint backlog is binding.** Each sprint has an approved backlog in `docs/` (e.g. `docs/sprint_1_backlog.md`) defining the user stories, acceptance criteria, and test cases for that sprint. When building sprint work you **must** implement exactly those stories — satisfy their acceptance criteria and write the listed test cases. Do not add functionality outside the backlog (scope creep) or leave a story partially done. If a needed change isn't covered by the backlog, stop and flag it so the backlog (and, if material, `decision_log.md`) can be updated before proceeding.

---

## 11. Quick Checklist Before Writing Any Code

0. Is this covered by an approved user story in the active sprint backlog (`docs/sprint_<N>_backlog.md`)? If not, stop and flag it before coding. (Section 10)
1. Which layer does this belong to? (Section 5)
2. Is the directory already defined? Use it — don't invent a new one.
3. Does this produce a recommendation? If yes, route it through `governance.govern()`.
4. Am I using only dependencies from Section 7?
5. Have I added type hints + a docstring + a unit test?
6. If this is a material new choice not already covered in `decision_log.md`, flag it back to the person so they can log a new `D-XXX` entry before we proceed.

---

## 12. Related Docs

| Doc | Use for |
|---|---|
| `docs/architecture.md` | Full technical reference — directory structure, service contracts, API contracts, dependency list |
| `docs/decision_log.md` | Why any given choice was made; what alternatives were rejected and why |
| `docs/data_contract.md` | Field-level schema for each of the 6 data domains |
| `docs/demo_script.md` | Prospect-facing walkthrough — useful for understanding the "story" a feature needs to tell |
| `docs/governance_charter.md` | Business-facing governance rulebook — the policy rules (POL-001–005), explainability standard, fairness commitments, and audit/override rules every recommendation must satisfy |
| `docs/project_journal.md` | Development/commit journal — a chronological, per-commit record of what was actually built each sprint (distinct from `decision_log.md`, which records *why* decisions were made) |
| `docs/sprint_<N>_backlog.md` | Per-sprint backlog — the binding user stories, acceptance criteria, and test cases for the active sprint (e.g. `docs/sprint_1_backlog.md`). Development must implement exactly these stories (Section 10) |
| `docs/production_mapping.md` | How local components would map to cloud in a future Phase 2 |
