# 📓 Decision Log — Store Layout (Product Placement) Optimizer Tool

> **Project Journal** capturing every material decision taken during the design and build of the demo tool, aligned with the objectives laid out in *"Objectives For Store – Layout (Product Placement) Optimizer Tool"*.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Decision Log / Project Journal |
| **Version** | 1.0 |
| **Status** | Living Document (updated continuously) |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Location** | Noida / Gurgaon, India |
| **Last Updated** | 07 July 2026 |
| **Related Documents** | Product Vision One-Pager v2 · Enhancement Deep-Dive v1.0 · Data Product Contract v1.0 · Phase 1 Solution Architecture |

---

## 🎯 Purpose of This Document

This is the **single source of truth** for every decision taken during the design, planning, and build of the demo tool. It exists to:

1. Preserve context for future team members joining the project
2. Explain **why** choices were made, not just what was chosen
3. Document alternatives that were evaluated and rejected
4. Support future audits, retrospectives, and Phase 2 planning
5. Satisfy the SDLC discipline mandated in the project objectives

**Rule:** Every material decision — technical, product, or process — must be logged here **before** it is executed in code or documentation.

---

## 📚 How to Read This Log

Each decision entry follows this structure:

- **Decision ID** — Unique identifier (e.g., `D-001`)
- **Date** — When the decision was taken
- **Category** — Product · Data · Architecture · Technology · Process · Governance
- **Status** — Proposed · Accepted · Superseded · Deferred
- **Decision** — The chosen path in one sentence
- **Rationale** — Why this choice was made
- **Alternatives Considered** — What else was evaluated and why rejected
- **Impact** — Downstream implications
- **Owner** — Who owns the decision

---

# PART 1 — PRODUCT DECISIONS

## D-001 · Product Positioning

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Product |
| **Status** | ✅ Accepted |

**Decision:** Position the tool as an *"Agentic Shelf Intelligence Platform"* — an MBA-based product placement optimizer augmented with contextual AI, GenAI, and omnichannel data.

**Rationale:**
- Pure MBA-based placement tools have existed since the 1990s and are undifferentiated
- Positioning as an AI-augmented intelligence platform aligns with 2026 buying signals
- Fits into the broader Agentic AI narrative already being developed for Cognizant offerings

**Alternatives Considered:**
- *"Planogram Optimization Tool"* — rejected: too generic, sounds like Blue Yonder / Nielsen Spaceman
- *"Retail Analytics Platform"* — rejected: too broad, loses the placement-specific focus

**Impact:** Shapes marketing, demo script, and prospect conversations.

**Owner:** Aditya Srivastava

---

## D-002 · Enhancement Scope for Phase 1

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Product |
| **Status** | ✅ Accepted |

**Decision:** Include **7 of 9** identified enhancements in Phase 1 scope — all Low, Low-Med, and Medium complexity items:
- #1 Contextual Affinity Modeling (Medium)
- #3 Generative AI Planogram Designer (Medium)
- #4 Omnichannel Affinity Sync (Medium)
- #5 Shopper Segment & Mission-Based Placement (Medium)
- #6 Multi-Objective Optimization (Low-Med)
- #8 Vendor Collaboration Module (Low-Med)
- #9 Explainability & Governance (Low)

**Rationale:**
- Delivers a differentiated, credible offering
- All included enhancements have well-understood algorithms and libraries
- Defers heavy infrastructure investments to Phase 2

**Alternatives Considered:**
- *All 9 enhancements* — rejected: adds #2 Computer Vision/IoT and #7 Digital Twin/AR which require hardware/3D expertise beyond current scope
- *Only Low complexity (5 items)* — rejected: loses the differentiators (#1, #3, #4)

**Impact:** Defines the entire Phase 1 build backlog.

**Owner:** Aditya Srivastava

---

## D-003 · Explicit Non-Goals for Phase 1

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Product |
| **Status** | ✅ Accepted |

**Decision:** Explicitly defer #2 Computer Vision + IoT Integration and #7 Digital Twin + AR to Phase 2 roadmap; document them as *conscious deferrals*, not omissions.

**Rationale:**
- Both require specialized hardware (shelf cameras, 3D scanners) and skills (CV, AR development)
- Not achievable in a laptop-based demo tool
- Documented as v2 roadmap items to preserve the prospect story

**Impact:** Documented in `docs/production_mapping.md` and Product Vision One-Pager.

**Owner:** Aditya Srivastava

---

## D-004 · Target Personas (Phase 1)

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Product |
| **Status** | ✅ Accepted |

**Decision:** Design UI and workflows for **4 primary personas**:
1. Category Manager
2. CPG Vendor Partner
3. Data Steward / Admin
4. Merchandising Head

**Rationale:** These 4 cover the entire lifecycle of a placement recommendation — from creation, to vendor collaboration, to governance, to executive review.

**Alternatives Considered:**
- *Category Manager only* — rejected: loses the vendor collaboration and governance narratives
- *Adding Store Ops Manager as 5th* — deferred: they are consumers of the output, not primary users of the tool

**Impact:** Streamlit UI will have 3 modes covering these personas.

**Owner:** Aditya Srivastava

---

# PART 2 — DATA DECISIONS

## D-005 · Data-as-a-Product Principle

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Data |
| **Status** | ✅ Accepted |

**Decision:** Adopt **Data-as-a-Product** as the guiding principle — every data domain has a defined owner, schema, quality gates, SLAs, and traceability from data element → KPI/feature.

**Rationale:**
- Explicitly called out in the project objectives
- Enables clear ownership and reduces integration friction
- Sets the demo apart from ad-hoc analytics tools

**Impact:** Drives the structure of the Data Product Contract document and API design.

**Owner:** Aditya Srivastava

---

## D-006 · Data Domains for Phase 1

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Data |
| **Status** | ✅ Accepted |

**Decision:** Phase 1 covers **6 data domains** (plus a system-generated Audit Log):
1. POS Transactions
2. Product Master
3. Store Master
4. E-commerce Clickstream
5. Loyalty & Customer Segmentation
6. Vendor Trade Promo

**Rationale:** These 6 domains collectively feed every one of the 7 enhancements, per the Enhancement Deep-Dive document. Adding more would inflate scope without unlocking new capabilities.

**Impact:** Determines the synthetic data generator, ingestion APIs, and storage layout.

**Owner:** Aditya Srivastava

---

## D-007 · Mimicked Industry System Schemas

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Data |
| **Status** | ✅ Accepted |

**Decision:** Each data domain will **mimic the schema of a leading industry system** so the demo mirrors real prospect data landscapes:

| Domain | Mimicked Source System |
|--------|------------------------|
| POS Transactions | Oracle Retail Xstore / SAP CAR (ARTS ODM-aligned) |
| Product Master | SAP MDG-M / Stibo STEP |
| Store Master | SAP Retail / Oracle Retail Merchandising |
| Clickstream | Adobe Analytics / GA4 / SF Commerce Cloud |
| Loyalty | Salesforce Marketing Cloud / Adobe Experience Platform |
| Vendor Promo | SAP TPM / Blue Yonder TPO |

**Rationale:**
- Makes the demo instantly recognizable to prospects using these systems
- Reduces "would this work with my SAP?" objections during demos
- Positions Cognizant as system-aware, not just tool-aware

**Alternatives Considered:**
- *Custom simplified schemas* — rejected: cheapens the demo, loses the recognition factor

**Impact:** Detailed in the Data Product Contract v1.0.

**Owner:** Aditya Srivastava

---

## D-008 · Synthetic Data Generation Strategy

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Data |
| **Status** | ✅ Accepted |

**Decision:** Generate synthetic data using **Python + Faker + realistic distributions** for a *global sports apparel retailer* context. Data written to Parquet files, checked into repo via **Git LFS**.

**Rationale:**
- No real customer data → no PII / compliance risk
- Sports apparel context aligns with Aditya's Nike consulting experience → richer demo storytelling
- Parquet + LFS gives fast load times and reproducible demos across team laptops

**Alternatives Considered:**
- *Real anonymized retail data* — rejected: procurement + legal effort not justified for a demo
- *Data generated on-the-fly at demo time* — rejected: unreliable, adds startup latency

**Impact:** `data/seed.py` script + `data/samples/*.parquet` files (LFS-tracked).

**Owner:** Aditya Srivastava

---

## D-009 · Data Volumes for Demo

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Data |
| **Status** | ✅ Accepted |

**Decision:** Target volumes:
- POS Transactions: ~500K
- Product Master: ~10K SKUs
- Store Master: ~50 stores
- Clickstream: ~2M events
- Loyalty Profiles: ~100K
- Vendor Promo Events: ~200

**Rationale:** Large enough to make MBA, segmentation, and affinity graph outputs *look real*; small enough to load fully into memory on a mid-tier laptop (16 GB RAM).

**Impact:** Sets the design boundary for choosing NetworkX (in-memory) over Neo4j.

**Owner:** Aditya Srivastava

---

# PART 3 — ARCHITECTURE DECISIONS

## D-010 · Local-First Deployment Model

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Architecture |
| **Status** | ✅ Accepted |

**Decision:** Design the tool as a **laptop-hosted, local-first demo** that any team member can `git clone` and run locally. No cloud dependency for Phase 1.

**Rationale:**
- Zero cloud cost during Phase 1
- Team members can demo offline (travel, client sites without VPN)
- Removes credential-sharing and cloud setup friction

**Alternatives Considered:**
- *Cloud-hosted demo (AWS/Azure)* — deferred: adds hosting cost, requires managing credentials for team access, forces cloud vendor lock-in decision early
- *Docker Compose from Day 1* — deferred to Phase 2: adds a debugging layer for a solo non-technical builder

**Impact:** Completely reshapes the technology stack toward embeddable, file-based components.

**Owner:** Aditya Srivastava

---

## D-011 · Layered Architecture with Consolidated Services

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Architecture |
| **Status** | ✅ Accepted |

**Decision:** 7-layer architecture:
- **L1** Presentation UI (Streamlit)
- **L2** API Layer (FastAPI)
- **L3** Consolidated Services (3 logical services in 1 Python process)
- **L4** Local Platform Services
- **L5** Data Layer
- **L6** Local Runtime & Tooling
- **L7** (Documented but deferred) Cloud & Enterprise Services

The 3 consolidated services are:
1. **Affinity & Optimization Service** (MBA + #1 + #4 + #5 + #6)
2. **GenAI & Vendor Service** (#3 + #8)
3. **Governance Service** (#9)

**Rationale:**
- Running 8 microservices on a laptop is impractical for a solo builder
- Modular Python packages within one process preserve the *"in production, these become separate services"* narrative
- Governance stays separate because it sits *in the request path* of all recommendations

**Alternatives Considered:**
- *8 separate microservices* — rejected: operational overhead too high for demo
- *Single monolithic module* — rejected: destroys the microservice story

**Impact:** Defines the code organization under `services/`.

**Owner:** Aditya Srivastava

---

## D-012 · Governance-in-the-Path Design

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Architecture · Governance |
| **Status** | ✅ Accepted |

**Decision:** The Governance Service (#9) **intercepts every recommendation** before it reaches the user, attaching explainability narrative, running policy checks, and writing to the audit log.

**Rationale:**
- Explainability is a top adoption blocker for AI-based retail tools — cannot be a bolt-on
- Positions the demo as governance-first, differentiating from competitors
- Aligns with Cognizant's Responsible AI narrative

**Impact:** All service outputs must pass through a common Governance wrapper before response.

**Owner:** Aditya Srivastava

---

# PART 4 — TECHNOLOGY DECISIONS (LOCKED CORE ELEMENTS)

## D-013 · Programming Language

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **Python 3.11+** end-to-end (UI, API, services, data layer).

**Rationale:**
- Single language reduces cognitive load for a solo non-technical builder
- Claude Code (the vibe-coding environment) is strongest with Python
- Native to the data science / ML ecosystem being used

**Alternatives Considered:**
- *Python backend + React frontend* — rejected: JS toolchain (npm, bundlers) is a nightmare without dev experience
- *Node.js full stack* — rejected: weaker ML/analytics ecosystem

**Impact:** All code is Python; no separate frontend build step.

**Owner:** Aditya Srivastava

---

## D-014 · UI Framework

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **Streamlit** — single app with 3 modes (Category Manager, Vendor Portal, Admin/Governance).

**Rationale:**
- Zero build step, zero HTML/CSS/JS knowledge required
- Python-native — Claude Code can extend it easily
- Looks polished enough for prospect demos out of the box

**Alternatives Considered:**
- *React* — rejected: requires JS toolchain, steep learning curve
- *Gradio* — rejected: more ML-demo oriented, less polished for business demos
- *Flask + Jinja templates* — rejected: still requires HTML skills

**Impact:** UI code lives in `ui/streamlit_app.py` with mode-specific modules.

**Owner:** Aditya Srivastava

---

## D-015 · API Framework

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **FastAPI** for the API layer.

**Rationale:**
- Industry standard, huge Claude Code training coverage
- Auto-generated OpenAPI docs at `/docs` — itself becomes a demo asset
- Pydantic contracts give type safety without the builder needing to understand types deeply

**Alternatives Considered:**
- *Flask* — rejected: no auto-docs, less type-safe
- *Django REST Framework* — rejected: overkill for a demo

**Impact:** API code lives in `api/main.py` with route modules.

**Owner:** Aditya Srivastava

---

## D-016 · Operational Database

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **SQLite** as the operational database.

**Rationale:**
- Single file, zero setup, zero admin
- Built into Python's standard library
- Handles demo volumes trivially

**Alternatives Considered:**
- *Postgres in Docker* — deferred to Phase 2 (T3): adds a container to manage
- *DuckDB for everything* — rejected: DuckDB is analytical, weaker for transactional writes

**Impact:** Operational state stored in `data/app.db`.

**Owner:** Aditya Srivastava

---

## D-017 · Analytical Engine

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **DuckDB + Parquet** for analytical queries.

**Rationale:**
- DuckDB is "SQLite for analytics" — no server needed
- Runs SQL over Parquet files at near-Snowflake speed
- Prospects instantly recognize the pattern (Parquet is standard in modern data lakes)

**Alternatives Considered:**
- *Pandas only* — rejected: SQL queries make demo more relatable to prospect analysts
- *Cloud data warehouse* — deferred to Phase 2

**Impact:** Analytical data in `data/samples/*.parquet`; DuckDB queries them directly.

**Owner:** Aditya Srivastava

---

## D-018 · LLM Provider

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **Anthropic Claude API** as the primary LLM. Config-driven via `.env` (`ANTHROPIC_API_KEY`). If key missing, GenAI features fall back to a **mocked response** so demos never break.

**Rationale:**
- Same ecosystem as Claude Code being used to build — familiar behavior
- Strong reasoning + tool-calling capability for the GenAI Planogram Agent (#3)
- Mock fallback ensures every team member can demo regardless of API access

**Alternatives Considered:**
- *OpenAI API* — rejected: extra vendor to manage
- *Ollama local models* — deferred to Phase 2 (T1): valuable but adds complexity
- *Azure OpenAI* — deferred: requires Azure tenant setup

**Impact:** `platform/llm_client.py` implements a clean adapter with mock fallback.

**Owner:** Aditya Srivastava

---

## D-019 · Vector Search

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **FAISS** (local, file-backed) for product embeddings and RAG context.

**Rationale:**
- In-process, no server needed
- Meta's proven library, well-documented
- Handles demo scale (10K SKUs) with sub-millisecond retrieval

**Alternatives Considered:**
- *Pinecone / Weaviate* — rejected: cloud dependency
- *pgvector on Postgres* — deferred to Phase 2

**Impact:** `platform/vector_store.py` wraps FAISS with save/load helpers.

**Owner:** Aditya Srivastava

---

## D-020 · Affinity Graph

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **NetworkX** (in-memory Python graph library) for the unified affinity graph (#4).

**Rationale:**
- In-process, zero infrastructure
- Sufficient for demo volumes
- Rebuilt from Parquet on service startup

**Alternatives Considered:**
- *Neo4j in Docker* — deferred to Phase 2 (T8): only if NetworkX proves insufficient
- *Amazon Neptune* — rejected: cloud dependency

**Impact:** Affinity graph loaded on startup, cached in memory.

**Owner:** Aditya Srivastava

---

## D-021 · Audit Log Storage

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology · Governance |
| **Status** | 🔒 Locked |

**Decision:** **JSONL append-only file** (`data/audit.jsonl`) for the audit log.

**Rationale:**
- Simplest possible immutable-by-convention log
- Human-readable and easily queried with DuckDB or `jq`
- Supports the Explainability & Governance narrative

**Alternatives Considered:**
- *SQLite table* — rejected: less obviously "append-only"
- *Cloud immutable storage (S3 with object lock)* — deferred to Phase 2

**Impact:** All Governance decisions written to this file.

**Owner:** Aditya Srivastava

---

## D-022 · Package Manager

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked |

**Decision:** **`uv`** (by Astral) as the Python package manager.

**Rationale:**
- Dramatically faster than pip/poetry
- Simpler config (`pyproject.toml`)
- Excellent Claude Code support

**Alternatives Considered:**
- *pip + requirements.txt* — rejected: dated, no lockfile
- *Poetry* — rejected: slower, more complex than `uv`

**Impact:** Dependencies in `pyproject.toml`; installed via `uv sync`.

**Owner:** Aditya Srivastava

---

## D-023 · Containerization

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology |
| **Status** | 🔒 Locked (deferred to Phase 2) |

**Decision:** **No Docker in Phase 1.** Direct Python execution via `uv` and `Makefile`.

**Rationale:**
- Docker adds a debugging layer that a solo non-technical builder doesn't need yet
- Cloning + running Python directly is more transparent
- Docker Compose is documented in the Phase 2 roadmap (T2)

**Impact:** No `Dockerfile` or `docker-compose.yml` in Phase 1 repo.

**Owner:** Aditya Srivastava

---

## D-024 · Repository Hosting

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Technology · Process |
| **Status** | 🔒 Locked |

**Decision:** **GitHub (private repo)** for the codebase. Repo name TBD.

**Rationale:**
- Industry standard, familiar to any team member
- Private during development; can flip to public later if needed
- Git LFS supported for seed data files

**Alternatives Considered:**
- *Azure DevOps* — deferred: Cognizant enterprise instance can be used if mandated
- *GitLab* — rejected: no organizational preference for it

**Impact:** Repo bootstrapping starts once name is finalized.

**Owner:** Aditya Srivastava

---

# PART 5 — PROCESS & GOVERNANCE DECISIONS

## D-025 · SDLC Approach

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:** **Agile / Sprint-based** SDLC with 6 planned sprints:
- **Foundation Sprint** (2–3 wks) — Vision, Data Contract, Architecture, Repo/CI setup
- **Sprint 1** — Core MBA + #9 Explainability guardrails
- **Sprint 2** — #1 Contextual Affinity + #6 Multi-Objective Optimizer
- **Sprint 3** — #4 Omnichannel Affinity + #5 Segmentation
- **Sprint 4** — #3 GenAI Planogram Agent
- **Sprint 5** — #8 Vendor Collaboration Module
- **Sprint H** — Hardening + Cloud Demo Deployment (deferred to Phase 2)

**Rationale:**
- #9 first as guardrails — every subsequent enhancement passes through it
- Analytical core (#1, #6) before data breadth (#4, #5)
- GenAI (#3) after analytical foundations are stable
- Vendor Portal (#8) last, as it depends on the analytical outputs

**Impact:** Drives backlog structure and milestone tags.

**Owner:** Aditya Srivastava

---

## D-026 · Documentation Discipline

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:** Maintain **6 markdown documents** in `docs/`:
1. `architecture.md` — layered architecture and design rationale
2. `data_contract.md` — links to full Data Product Contract
3. `decision_log.md` — this document (living)
4. `demo_script.md` — prospect-facing walkthrough with talking points
5. `production_mapping.md` — local → cloud equivalents (turns demo into a sales conversation)
6. `README.md` (root-level) — setup in 3 commands

**Rationale:**
- Solo non-technical builder needs docs as a safety net
- Each doc has a distinct audience (dev vs. prospect vs. business)
- Aligns with the *"well documented"* objective

**Impact:** Every sprint must update relevant docs before merge.

**Owner:** Aditya Srivastava

---

## D-027 · Version Control Discipline

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:**
- **Feature branches** per enhancement (`feature/#1-contextual-affinity`, etc.)
- **Frequent commits** with meaningful messages (Claude Code assists)
- **Tagged milestones** per sprint (`v0.1-mba-core`, `v0.2-contextual-affinity`, etc.)
- **Main branch** always demo-ready

**Rationale:** Protects demo readiness during half-broken feature work; enables rollback if a demo goes wrong.

**Impact:** Branch protection rules to be set on `main`.

**Owner:** Aditya Srivastava

---

## D-028 · Testing & Linting

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:** Use **`pytest`** for tests, **`ruff`** for linting/formatting. Basic CI on GitHub Actions for lint + test only (no deploy).

**Rationale:**
- Both are Python-native, low-config
- Catches obvious bugs before demo
- CI runs on every PR

**Impact:** `pytest.ini`, `ruff` config in `pyproject.toml`, `.github/workflows/ci.yml`.

**Owner:** Aditya Srivastava

---

## D-029 · Security & Privacy Posture (Demo)

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Governance |
| **Status** | ✅ Accepted |

**Decision:** Demo-appropriate security posture:
- **API Key auth** on FastAPI (env-var based)
- **Vendor scope isolation** enforced at API level (`vendor_id` header check)
- **PII fields hashed** in synthetic data (email, phone)
- **Consent flags** honored in loyalty data
- **Secrets via `.env`** (never committed)

**Rationale:** Demonstrates production-grade thinking without enterprise-grade complexity.

**Impact:** Documented in `docs/architecture.md`; full enterprise security deferred to Phase 2 (T4).

**Owner:** Aditya Srivastava

---

## D-030 · Vibe-Coding via Claude Code

| Field | Value |
|-------|-------|
| **Date** | 07 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:** Build the entire codebase via **Claude Code** (AI-assisted development), given the builder has no prior development experience.

**Rationale:**
- Builder has business analyst background, not developer background
- Claude Code excels at the chosen Python stack
- All stack choices were optimized for AI-assisted coding compatibility

**Impact:**
- Every architectural decision favored well-documented, mainstream libraries
- Kickoff Bundle will include a first prompt for Claude Code

**Owner:** Aditya Srivastava

---

## D-031 · Windows-Native Task Runner (`tasks.ps1`)

| Field | Value |
|-------|-------|
| **Date** | 20 Jul 2026 |
| **Category** | Technology · Process |
| **Status** | ✅ Accepted |

**Decision:** Add a PowerShell task runner (`tasks.ps1`) at the repo root that mirrors the six canonical Makefile targets (`setup`, `seed`, `demo`, `test`, `reset`, `clean`), invoked as `./tasks.ps1 <verb>`. The Makefile contract (`architecture.md` §16) is **augmented, not replaced** — the verb names remain identical across both entry points.

**Rationale:**
- The builder's environment is Windows, where `make` is not installed by default; installing GnuWin32/Chocolatey `make` adds a tool to obtain for no functional gain.
- A PowerShell script requires **zero extra installs** — `powershell.exe` ships with Windows.
- Keeping the same verb names preserves the muscle-memory contract; only the invocation prefix differs (`./tasks.ps1 setup` vs `make setup`).

**Alternatives Considered:**
- *Install `make` on Windows* — rejected: an extra dependency to obtain and document, contrary to the low-friction, laptop-first posture (D-010).
- *Drop the Makefile, keep only `tasks.ps1`* — rejected: the Makefile stays as the cross-platform/CI reference and the documented contract; this is an additive convenience for Windows.
- *Run raw `uv` commands each time* — rejected: loses the memorable, documented command names.

**Impact:** New `tasks.ps1` at repo root; `architecture.md` §16 and `README.md` note the PowerShell equivalent. Team members on macOS/Linux (or with `make` installed) continue to use `make`; the `Makefile` itself is delivered in Sprint 1 alongside the first runnable code.

**Owner:** Aditya Srivastava

---

## D-032 · Sprint 1 Backlog Locked for Development

| Field | Value |
|-------|-------|
| **Date** | 22 Jul 2026 |
| **Category** | Process |
| **Status** | ✅ Accepted |

**Decision:** Approve and **lock** the Sprint 1 backlog (`docs/sprint_1_backlog.md`) — 11 user stories (US-1.1 … US-1.11) across five epics (Data Foundation, MBA Core, Explainability & Governance, API, UI) with their acceptance criteria and test cases. Sprint 1 development must implement exactly these stories.

**Rationale:**
- Freezing scope before coding prevents scope creep and gives a clear, testable Definition of Done.
- The backlog is fully traceable to `architecture.md`, `governance_charter.md` (POL-001–005), and `demo_script.md` Scenes 2–3.
- Locking establishes the review-gate discipline (D-026) at the story level, not just the doc level.

**Key confirmed scope points:**
- US-1.4 rationale is **template-generated, no LLM call** in Sprint 1 (principle #7, mock-first); a flag-gated seam (`generate_narrative()`) allows an LLM narrative to be added in Sprint 4 without changing callers.
- POL-003 / POL-004 return **"not-evaluated"** (never a false "pass") when brand/vendor config is absent.
- Only the **POS Transactions** and **Product Master** data domains are generated this sprint; the other four are deferred to later sprints.
- No FAISS vector store or NetworkX graph store in Sprint 1.

**Alternatives Considered:**
- *Begin coding without a locked backlog* — rejected: loses the acceptance-criteria contract and invites scope drift.
- *Lock only high-level stories without test cases* — rejected: test cases are the objective Definition of Done.

**Impact:** Any change to Sprint 1 scope after this point requires a new `D-XXX` entry before implementation. `CLAUDE.md` Section 10/11 already bind development to the active sprint backlog.

**Owner:** Aditya Srivastava

---

## D-033 · Rename Layer 4 Package `platform/` → `platform_services/`

| Field | Value |
|-------|-------|
| **Date** | 22 Jul 2026 |
| **Category** | Architecture · Technology |
| **Status** | ✅ Accepted |

**Decision:** Rename the Layer 4 (Local Platform Services) Python package from `platform/` to **`platform_services/`**. All references (imports, docs, tests) use the new name; the layer's conceptual name ("Local Platform Services") is unchanged.

**Rationale:**
- `platform` is a **Python standard-library module**. A top-level `platform/` package on the import path shadows it.
- The failure is not theoretical: `pandas` → `numpy` imports the stdlib `platform` at import time (`platform.machine()`); with our package shadowing it, numpy — and therefore nearly every dependency — fails to import. The app and test suite would not run.
- A `src/` layout does not fix this: the collision is on the import **name** `platform`, regardless of directory nesting.

**Alternatives Considered:**
- *Keep `platform/`* — rejected: breaks imports across the dependency tree (demonstrated during Sprint 1 setup).
- *`src/` layout keeping the name* — rejected: does not resolve the name collision.
- *`core/`* — rejected: loses the explicit "platform" wording the docs use for Layer 4.
- *`platform_svc/`* — considered; `platform_services` chosen for clarity.

**Impact:** `architecture.md` (§2, §3.1, §5, §6.3, §18) and `CLAUDE.md` (§5, §6, §8) updated to `platform_services/`. Tests mirror `services/` + `platform_services/`. The `sprint_1_backlog.md` US-1.2 paths updated accordingly.

**Owner:** Aditya Srivastava

---

# PART 6 — TENTATIVE / DEFERRED DECISIONS

These are consciously deferred to Phase 2+ and will be revisited as clarity emerges.

| ID | Item | Trigger for Reopening |
|----|------|-----------------------|
| **T-001** | Ollama offline LLM fallback | After first 2 prospect demos (data-sensitivity concerns) |
| **T-002** | Docker Compose packaging | After 2+ team members hit "works on my machine" issues |
| **T-003** | Postgres option via Docker | When a prospect asks about "real DB" during demo |
| **T-004** | Enterprise authentication (SSO/OIDC) | When moving to shared/remote hosting |
| **T-005** | React front-end | Only if a team member volunteers to build |
| **T-006** | MLflow server for model versioning | When >2 model versions to track |
| **T-007** | CI/CD deploy pipelines | After core app is stable and hosted |
| **T-008** | Neo4j graph database | Only if NetworkX proves insufficient for scale |
| **T-009** | Observability stack (Prometheus/Grafana) | For production deployment |
| **T-010** | Kafka / async messaging | For production scale |
| **T-011** | Cloud deployment (AWS/Azure/GCP) | When moving beyond demo phase |
| **T-012** | Enhancement #2 (CV + IoT) | Phase 2 roadmap |
| **T-013** | Enhancement #7 (Digital Twin + AR) | Phase 2 roadmap |

---

# PART 7 — RISKS & ASSUMPTIONS

## Key Assumptions

1. Synthetic data will be sufficiently realistic to represent prospect data patterns
2. Anthropic Claude API access will remain available and cost-controlled
3. Team members will have Python 3.11+ available on their laptops
4. Demo laptops will have at least 16 GB RAM
5. Prospects will value the "production mapping" story enough to bridge from demo to sales conversation

## Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude API rate limits during demo | Medium | High | Mock fallback + response caching |
| Demo data feels unrealistic to prospects | Medium | Medium | Use Nike-context distributions; iterate based on feedback |
| Non-technical builder blockers | Medium | High | Rely on Claude Code + documented decisions; escalate to dev community when stuck |
| Scope creep beyond 7 enhancements | High | High | Explicit non-goals + change control via this log |
| Team member setup failures | Medium | Medium | Test clone-to-demo on 2+ laptops before sharing widely |

---

# PART 8 — CHANGE LOG (DOCUMENT VERSIONS)

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| **v0.1** | Early Jul 2026 | Aditya S. | Initial concept notes captured |
| **v0.5** | 07 Jul 2026 | Aditya S. | Product Vision, Enhancement Deep-Dive, Data Contract decisions captured |
| **v1.0** | 07 Jul 2026 | Aditya S. | First finalized version — 30 decisions logged aligned with Phase 1 architecture lock-in |

---

# PART 9 — HOW TO ADD A NEW DECISION

When adding future decisions, copy this template:

```markdown
## D-XXX · [Short Decision Title]

| Field | Value |
|-------|-------|
| **Date** | DD MMM YYYY |
| **Category** | Product · Data · Architecture · Technology · Process · Governance |
| **Status** | Proposed · Accepted · Superseded · Deferred |

**Decision:** [One-sentence statement of what was decided]

**Rationale:**
- [Why this choice was made]

**Alternatives Considered:**
- *[Alternative]* — rejected: [reason]

**Impact:** [Downstream implications]

**Owner:** [Name]
```

**Numbering rule:** Increment `D-XXX` for accepted decisions and `T-XXX` for tentative/deferred items. Never reuse or renumber.

---

## 🔗 Related Documents

- **Product Vision One-Pager v2** — Locked product scope and enhancements
- **Enhancement Deep-Dive v1.0** — Detailed input/processing/output per enhancement
- **Data Product Contract v1.0** — 6 data domains mimicking leading systems
- **Phase 1 Solution Architecture (diagram)** — Visual reference for all architecture decisions

---

*Confidential — Cognizant Internal · Decision Log v1.0 · July 2026 · Maintained by Aditya Srivastava*
