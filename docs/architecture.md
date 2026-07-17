# 🏗️ Architecture Reference — Store Layout (Product Placement) Optimizer

> **Purpose of this document:** This is the **authoritative architecture reference** for the Store Layout Optimizer demo tool. It is written to be consumed by **Claude Code** (or any LLM-assisted coding tool) as a stable context anchor. Reference this file from `CLAUDE.md` at the repo root.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product** | Store Layout (Product Placement) Optimizer Tool |
| **Doc Type** | Architecture Reference (LLM-facing) |
| **Version** | 1.0 |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 07 July 2026 |
| **Related Docs** | `decision_log.md` · `data_contract.md` · `demo_script.md` · `production_mapping.md` |

---

## 🧭 How Claude Code Should Use This Document

**When implementing anything:**
1. Read this file **first** to understand where code belongs
2. Follow the **naming conventions**, **directory structure**, and **contracts** exactly as specified
3. If a decision is unclear, check `decision_log.md`
4. Never introduce dependencies not listed in Section 12
5. Never break the layer boundaries described in Section 3
6. Every recommendation-producing function must route through the **Governance Service** before returning to the caller (Section 6)

**Rules of engagement:**
- ✅ Prefer boring, well-documented libraries over exotic ones
- ✅ Keep functions small, pure, and typed with Pydantic where possible
- ✅ Write docstrings on every module and public function
- ✅ Add a unit test for every new business function
- ❌ Do not introduce microservices, message queues, or containers in Phase 1
- ❌ Do not add cloud SDKs (boto3, azure-sdk, gcloud) in Phase 1
- ❌ Do not commit real customer data or API keys

---

# 1. System Overview

## 1.1 One-Line Description

A **local-first, Python-native demo tool** that ingests synthetic retail data mimicking industry systems, runs Market Basket Analysis augmented with contextual AI, GenAI, and omnichannel signals, and outputs governed product-placement recommendations through a Streamlit UI.

## 1.2 Deployment Model

- **Runtime:** Single Python process on a laptop
- **UI:** Streamlit on port **8501**
- **API:** FastAPI on port **8000**
- **Storage:** Local files only (SQLite, Parquet, FAISS index, JSONL logs)
- **External calls:** Anthropic Claude API only (optional; mock fallback if no key)

## 1.3 Design Principles

| # | Principle | Implication |
|---|-----------|-------------|
| 1 | **Local-first, zero cloud** | No boto3, azure-sdk, gcloud, Terraform in Phase 1 |
| 2 | **Python everywhere** | No JS, no separate frontend build |
| 3 | **File-based storage** | SQLite + Parquet + FAISS + JSONL — no DB servers |
| 4 | **Modular monolith** | 3 logical services in 1 FastAPI process; module boundaries are strict |
| 5 | **Governance-in-path** | Every recommendation intercepted by Governance before return |
| 6 | **Data-as-a-Product** | Data domains have contracts (see `data_contract.md`) |
| 7 | **Mock-first LLM** | GenAI features must degrade gracefully without API key |
| 8 | **AI-friendly conventions** | Well-typed, well-documented, mainstream libs — friendly for LLM-assisted coding |

---

# 2. Repository Structure (Canonical)

**Claude Code: use this structure exactly. Do not rename directories.**

```
store-layout-optimizer/
├── CLAUDE.md                    # LLM-facing project brief — references this file
├── README.md                    # Human-facing setup guide
├── Makefile                     # setup | seed | demo | test | reset
├── pyproject.toml               # uv-managed dependencies
├── .env.example                 # Config template
├── .gitignore
├── .python-version              # 3.11
│
├── ui/                          # Streamlit app (Layer 1)
│   ├── __init__.py
│   ├── streamlit_app.py         # Main entrypoint (streamlit run)
│   └── modes/
│       ├── __init__.py
│       ├── category_manager.py  # Recommendations, What-If, NL Chat, Planogram
│       ├── vendor_portal.py     # Promo upload, co-placement, dashboard
│       └── admin_governance.py  # Audit log, explainability, overrides
│
├── api/                         # FastAPI (Layer 2)
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + startup/shutdown hooks
│   ├── auth.py                  # API key + vendor scope check
│   ├── schemas.py               # Pydantic request/response models
│   └── routes/
│       ├── __init__.py
│       ├── recommendations.py   # POST /api/v1/recommendations
│       ├── planogram.py         # POST /api/v1/planogram/generate
│       ├── vendor.py            # POST /api/v1/vendor/promo
│       ├── audit.py             # GET  /api/v1/audit/log
│       └── health.py            # GET  /health
│
├── services/                    # Business logic (Layer 3)
│   ├── __init__.py
│   │
│   ├── affinity_optimization/   # Service 1 — MBA + #1 + #4 + #5 + #6
│   │   ├── __init__.py
│   │   ├── mba_core/            # Baseline Apriori / FP-Growth
│   │   ├── contextual/          # #1 PrefixSpan, bandits, negative associations
│   │   ├── omnichannel/         # #4 Unified affinity graph
│   │   ├── segmentation/        # #5 RFM, k-means, XGBoost mission classifier
│   │   └── optimizer/           # #6 LP/MIP/weighted scoring
│   │
│   ├── genai_vendor/            # Service 2 — #3 + #8
│   │   ├── __init__.py
│   │   ├── planogram_agent/     # #3 LLM agent with tool calls
│   │   └── vendor_portal/       # #8 Promo intake, co-placement
│   │
│   └── governance/              # Service 3 — #9
│       ├── __init__.py
│       ├── explainability.py    # SHAP + NL narrative generation
│       ├── policy_engine.py     # Bias checks, guardrails
│       └── audit_writer.py      # JSONL append-only writer
│
├── platform/                    # Shared platform services (Layer 4)
│   ├── __init__.py
│   ├── llm_client.py            # Anthropic Claude adapter (with mock fallback)
│   ├── data_access.py           # SQLite + DuckDB + Parquet helpers
│   ├── vector_store.py          # FAISS wrapper
│   ├── graph_store.py           # NetworkX affinity graph loader
│   └── config.py                # Env var loading, feature flags
│
├── data/                        # Data layer (Layer 5)
│   ├── seed.py                  # Synthetic data generator (Faker-based)
│   ├── samples/                 # Pre-generated Parquet files (Git LFS)
│   │   ├── pos_transactions.parquet
│   │   ├── product_master.parquet
│   │   ├── store_master.parquet
│   │   ├── clickstream.parquet
│   │   ├── loyalty.parquet
│   │   └── vendor_promo.parquet
│   ├── app.db                   # SQLite operational DB (gitignored)
│   ├── audit.jsonl              # Governance audit log (gitignored)
│   └── faiss_index/             # Vector index files (gitignored)
│
├── tests/                       # pytest test suite
│   ├── __init__.py
│   ├── unit/                    # Mirrors services/ + platform/ structure
│   └── integration/             # End-to-end flow tests
│
├── docs/                        # All markdown docs
│   ├── architecture.md          # THIS FILE
│   ├── data_contract.md         # Full data product contract
│   ├── decision_log.md          # Project journal
│   ├── demo_script.md           # Prospect walkthrough
│   └── production_mapping.md    # Local → cloud mapping
│
├── logs/                        # App logs (gitignored)
│
└── .github/workflows/
    └── ci.yml                   # Lint + test (no deploy)
```

---

# 3. Layered Architecture

The system is organized into **6 active layers** (Phase 1) plus a **deferred cloud layer** (Phase 2). Layers communicate **top-down only**; no layer skipping.

## 3.1 Layer Map

| Layer | Name | Directory | Purpose |
|-------|------|-----------|---------|
| **L1** | Presentation UI | `ui/` | Streamlit app, 3 modes |
| **L2** | API Layer | `api/` | FastAPI, auth, request contracts |
| **L3** | Consolidated Services | `services/` | Business logic — 3 services |
| **L4** | Local Platform Services | `platform/` | LLM client, data access, vector, graph |
| **L5** | Data Layer | `data/` | SQLite, Parquet, FAISS, JSONL |
| **L6** | Local Runtime & Tooling | root files | Python, uv, Makefile, GitHub |
| **L7** | *(Deferred)* Cloud & Enterprise | — | See `production_mapping.md` |

## 3.2 Allowed Cross-Layer Calls

**Rule:** A layer may only call the layer directly below it (or same-layer utilities).

| From → To | Allowed? |
|-----------|----------|
| L1 (UI) → L2 (API) | ✅ via HTTP |
| L2 (API) → L3 (Services) | ✅ direct Python call |
| L3 (Services) → L4 (Platform) | ✅ direct Python call |
| L4 (Platform) → L5 (Data) | ✅ direct Python call |
| L1 → L3 | ❌ never |
| L2 → L4 | ❌ never |
| L3 → L5 | ❌ never (must go via L4) |
| L3 → L3 (service-to-service) | ⚠️ only through defined interfaces (Section 4.5) |

---

# 4. Service Architecture (Layer 3 Deep-Dive)

Three logical services live in **one FastAPI process** as separate Python packages. This is a **modular monolith** — designed so any service can later be extracted into its own microservice by wrapping its package with FastAPI and updating the caller.

## 4.1 Service 1 — Affinity & Optimization Service

**Path:** `services/affinity_optimization/`
**Enhancements covered:** MBA Core + #1 + #4 + #5 + #6
**Owns:** All analytical / ML recommendation logic

| Sub-module | Enhancement | Responsibility | Key Libraries |
|-----------|-------------|----------------|---------------|
| `mba_core/` | Baseline | Apriori / FP-Growth on POS baskets | `mlxtend` |
| `contextual/` | #1 | Sequence mining (PrefixSpan), contextual bandits (LinUCB), negative associations | `mlxtend`, custom RL |
| `omnichannel/` | #4 | Unified affinity graph (in-store + online) | `networkx` |
| `segmentation/` | #5 | RFM + k-means clustering + XGBoost mission classifier | `scikit-learn`, `xgboost` |
| `optimizer/` | #6 | Weighted multi-objective ranking (lift + margin + turn − shrink) | `pulp` (optional), `numpy` |

**Public interface** (what other services can call):

```python
# services/affinity_optimization/__init__.py

def get_recommendations(
    store_id: str,
    category: str | None = None,
    context: dict | None = None,   # {"time_of_day": ..., "weather": ...}
    segment: str | None = None,
    top_k: int = 20,
) -> list[Recommendation]:
    """Returns top-k placement recommendations for a given context."""

def rebuild_affinity_graph() -> None:
    """Rebuild the NetworkX affinity graph from latest Parquet data."""

def get_segment_for_basket(basket: list[str]) -> str:
    """Return the mission segment label for a basket."""
```

## 4.2 Service 2 — GenAI & Vendor Service

**Path:** `services/genai_vendor/`
**Enhancements covered:** #3 + #8
**Owns:** LLM-orchestrated planogram generation + vendor collaboration

| Sub-module | Enhancement | Responsibility |
|-----------|-------------|----------------|
| `planogram_agent/` | #3 | LLM agent that uses tool-calling to invoke affinity + optimizer, generates planograms with NL rationale |
| `vendor_portal/` | #8 | Vendor promo intake, co-placement suggestion generation |

**Public interface:**

```python
# services/genai_vendor/__init__.py

def generate_planogram(
    nl_query: str,
    category: str,
    store_id: str,
) -> PlanogramDraft:
    """LLM-driven planogram generation from a natural language brief."""

def process_vendor_promo(
    vendor_id: str,
    promo: VendorPromoSubmission,
) -> list[CoPlacementSuggestion]:
    """Ingest vendor promo, return co-placement suggestions."""
```

## 4.3 Service 3 — Governance Service

**Path:** `services/governance/`
**Enhancement covered:** #9
**Owns:** Explainability, policy checks, audit logging

**Public interface:**

```python
# services/governance/__init__.py

def govern(
    recommendation: Recommendation,
    context: dict,
) -> GovernedRecommendation:
    """
    Intercept a recommendation, attach NL rationale, run policy checks,
    write audit entry. Returns the recommendation wrapped with governance metadata.
    """

def get_audit_log(
    limit: int = 100,
    filters: dict | None = None,
) -> list[AuditEntry]:
    """Return recent audit entries (for Admin UI)."""
```

## 4.4 Governance-in-the-Path Rule (Critical)

**Every function in Services 1 and 2 that produces a user-facing recommendation MUST pass its output through `governance.govern()` before returning.**

```python
# ✅ CORRECT pattern
from services.governance import govern

def get_recommendations(...):
    raw_recs = _compute_raw_recommendations(...)
    return [govern(r, context) for r in raw_recs]

# ❌ WRONG — bypasses governance
def get_recommendations(...):
    return _compute_raw_recommendations(...)
```

Governance calls are cheap (in-process); there is no excuse for skipping them.

## 4.5 Inter-Service Calls

Services **may** call each other, but **only through their `__init__.py` public interfaces** (never reach into sub-modules).

```python
# ✅ CORRECT
from services.affinity_optimization import get_recommendations

# ❌ WRONG — reaches into internal module
from services.affinity_optimization.contextual.bandits import LinUCBModel
```

---

# 5. Platform Layer (Layer 4)

Shared utilities used by all services. Located in `platform/`.

## 5.1 LLM Client (`platform/llm_client.py`)

**Purpose:** Single point of contact with the Anthropic Claude API.

**Contract:**

```python
class LLMClient:
    def __init__(self, api_key: str | None = None):
        """If api_key is None or env var missing, uses MockLLMClient."""
    
    def complete(
        self,
        prompt: str,
        system: str | None = None,
        tools: list[dict] | None = None,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Synchronous completion. Handles tool calls, retries, logging."""
    
    def is_mocked(self) -> bool:
        """Returns True if using the mock fallback."""
```

**Behavior:**
- If `ANTHROPIC_API_KEY` is missing or empty → returns realistic mock responses
- Every call is logged with prompt version, token counts, latency
- PII redaction: emails/phones stripped from prompts before send

**Model:** `claude-sonnet-4.5` (default; overridable via `.env`)

## 5.2 Data Access (`platform/data_access.py`)

**Purpose:** Central helpers for SQLite operational reads/writes and DuckDB analytical queries.

**Contract:**

```python
def get_sqlite_conn() -> sqlite3.Connection:
    """Returns a SQLite connection (data/app.db). Auto-creates schema on first call."""

def duckdb_query(sql: str, parameters: dict | None = None) -> pd.DataFrame:
    """Execute SQL over Parquet files. Files are auto-discovered from data/samples/."""

def load_parquet(domain: str) -> pd.DataFrame:
    """Load a full data domain into a DataFrame. Cached."""
```

**Convention:** Never use raw `open()` on Parquet files or raw `sqlite3.connect()` in service code. Always go through `data_access.py`.

## 5.3 Vector Store (`platform/vector_store.py`)

**Purpose:** FAISS wrapper for product embeddings + RAG.

**Contract:**

```python
class VectorStore:
    def build_index(self, embeddings: np.ndarray, ids: list[str]) -> None:
        """Build FAISS index from embeddings, persist to data/faiss_index/."""
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> list[tuple[str, float]]:
        """Returns [(id, score), ...] for top-k nearest neighbors."""
    
    def load(self) -> None:
        """Load persisted index into memory (called on service startup)."""
```

## 5.4 Graph Store (`platform/graph_store.py`)

**Purpose:** Load and serve the NetworkX affinity graph.

**Contract:**

```python
class AffinityGraph:
    def load_from_parquet(self) -> None:
        """Build in-memory NetworkX graph from Parquet edges/nodes."""
    
    def neighbors(self, sku_id: str, min_lift: float = 1.0) -> list[dict]:
        """Return affinities for a given SKU."""
    
    def cross_channel_lift(self, sku_a: str, sku_b: str) -> float:
        """Return the cross-channel lift score for a pair."""
```

## 5.5 Config (`platform/config.py`)

**Purpose:** Central place for environment variables and feature flags.

**Contract:**

```python
class Settings(BaseSettings):
    anthropic_api_key: str = ""
    api_key: str = "demo-key"           # For FastAPI auth
    llm_model: str = "claude-sonnet-4.5"
    data_dir: Path = Path("data")
    log_level: str = "INFO"
    enable_governance: bool = True      # Feature flag
    mock_llm: bool = False              # Force mock mode

    class Config:
        env_file = ".env"

settings = Settings()
```

**Rule:** No `os.environ.get()` calls anywhere in the codebase except inside `config.py`.

---

# 6. Data Layer (Layer 5)

## 6.1 Storage Overview

| Store | Format | Location | Contents |
|-------|--------|----------|----------|
| **Operational DB** | SQLite | `data/app.db` | Vendor uploads, user preferences, planogram drafts, service state |
| **Analytical Data** | Parquet | `data/samples/*.parquet` | 6 domain data files (see 6.2) |
| **Vector Index** | FAISS files | `data/faiss_index/` | Product embeddings |
| **Audit Log** | JSONL | `data/audit.jsonl` | Governance decisions, immutable-by-convention |

## 6.2 Data Domains (mimicked schemas)

| Domain | File | Mimicked System | Volume |
|--------|------|-----------------|--------|
| POS Transactions | `pos_transactions.parquet` | Oracle Xstore / SAP CAR | ~500K |
| Product Master | `product_master.parquet` | SAP MDG-M / Stibo STEP | ~10K SKUs |
| Store Master | `store_master.parquet` | SAP Retail / Oracle Retail | ~50 stores |
| E-commerce Clickstream | `clickstream.parquet` | Adobe Analytics / GA4 | ~2M events |
| Loyalty & Segmentation | `loyalty.parquet` | Salesforce Mktg Cloud / Adobe AEP | ~100K profiles |
| Vendor Trade Promo | `vendor_promo.parquet` | SAP TPM / Blue Yonder TPO | ~200 promos |

**Full schemas:** see `data_contract.md`.

## 6.3 Rules for Data Access

- ❌ Do not read Parquet files directly from services — go through `platform.data_access`
- ❌ Do not write to `audit.jsonl` from anywhere except `services/governance/audit_writer.py`
- ✅ SQLite writes must go through parameterized queries (SQL injection protection)
- ✅ Every synthetic data generation is deterministic when seeded (use `random.seed(42)`)

---

# 7. API Contracts (Layer 2)

## 7.1 Base URL

`http://localhost:8000/api/v1`

## 7.2 Authentication

- **Header:** `X-API-Key: <value>` (matches `settings.api_key`)
- **Vendor endpoints additionally require:** `X-Vendor-Id: <vendor_id>` (validated against vendor master)

## 7.3 Endpoints

| Method | Path | Purpose | Consumer |
|--------|------|---------|----------|
| `GET` | `/health` | Liveness probe | All |
| `POST` | `/api/v1/recommendations` | Get placement recommendations | Category Mgr Mode |
| `POST` | `/api/v1/planogram/generate` | LLM-driven planogram | Category Mgr Mode |
| `POST` | `/api/v1/vendor/promo` | Submit vendor promo | Vendor Portal Mode |
| `GET` | `/api/v1/vendor/{vendor_id}/suggestions` | Co-placement suggestions | Vendor Portal Mode |
| `GET` | `/api/v1/audit/log` | Recent audit entries | Admin Mode |
| `GET` | `/api/v1/audit/{recommendation_id}` | Audit trail for one recommendation | Admin Mode |
| `POST` | `/api/v1/recommendations/{id}/override` | User override with reason | Category Mgr Mode |

## 7.4 Contract Conventions

- All request/response bodies are **Pydantic models** defined in `api/schemas.py`
- All timestamps are **ISO 8601 UTC**
- All monetary values are **decimal**, currency code included
- All error responses follow: `{"error": {"code": "...", "message": "..."}}`

---

# 8. Two Canonical Request Flows

## 8.1 Flow A — Category Manager Requests Recommendations

```
User (Streamlit UI)
   │
   │  1. User clicks "Get Recommendations" for beverage category
   ▼
[L1] ui/modes/category_manager.py
   │
   │  2. HTTP POST /api/v1/recommendations
   │     Headers: X-API-Key
   │     Body: {store_id, category, context, segment, top_k}
   ▼
[L2] api/routes/recommendations.py
   │
   │  3. auth.verify_api_key()
   │  4. Validate Pydantic schema
   ▼
[L3] services.affinity_optimization.get_recommendations(...)
   │
   │  5. mba_core → baseline affinities
   │  6. contextual → contextual re-ranking
   │  7. segmentation → apply segment overlay
   │  8. optimizer → multi-objective re-rank
   │  9. Each recommendation → governance.govern()
   │       ├── explainability.generate_narrative()
   │       ├── policy_engine.check()
   │       └── audit_writer.write()
   ▼
[L4] platform helpers used along the way:
   │   - data_access (DuckDB over Parquet)
   │   - graph_store (affinity lookups)
   │   - llm_client (NL narratives, if enabled)
   │
   ▼
[L2] Response serialized via Pydantic
   ▼
[L1] Streamlit renders recommendations + rationale panels
```

## 8.2 Flow B — NL Planogram Generation (GenAI Agent)

```
User: "Optimize the running footwear aisle for margin"
   │
   ▼
[L1] Streamlit chat input → POST /api/v1/planogram/generate
   ▼
[L2] api/routes/planogram.py → services.genai_vendor.generate_planogram(...)
   ▼
[L3] planogram_agent:
   │
   │  1. LLM parses intent + constraints
   │  2. LLM tool call: get_recommendations(category="running_footwear", ...)
   │       → services.affinity_optimization
   │  3. LLM tool call: get_shelf_constraints(store_id=...)
   │  4. LLM generates draft planogram JSON + rationale per placement
   │  5. governance.govern() wraps each placement
   ▼
[L2] Response: PlanogramDraft + rationale
   ▼
[L1] Streamlit renders planogram visualization + NL rationale
```

---

# 9. Data Contracts (Cross-Layer)

Core Pydantic models used across layers. Defined in `api/schemas.py` and re-exported where needed.

```python
class Recommendation(BaseModel):
    recommendation_id: str
    sku_a: str
    sku_b: str
    placement_type: Literal["adjacency", "endcap", "aisle_entry", "checkout"]
    lift: float
    confidence: float
    support: float
    context: dict = {}

class GovernedRecommendation(Recommendation):
    rationale: str                       # NL narrative from #9
    policy_warnings: list[str] = []      # Any guardrail flags
    fairness_score: float | None = None
    audit_id: str

class PlanogramDraft(BaseModel):
    planogram_id: str
    category: str
    store_id: str
    placements: list[GovernedRecommendation]
    generation_notes: str
    llm_model_used: str

class VendorPromoSubmission(BaseModel):
    promo_id: str
    vendor_id: str
    promo_name: str
    start_date: date
    end_date: date
    participating_skus: list[str]
    promo_type: Literal["TPR", "BOGO", "Bundle", "Display", "Endcap"]
    discount_value: Decimal
    funding_type: Literal["vendor", "retailer", "co-op"]

class CoPlacementSuggestion(BaseModel):
    suggestion_id: str
    sku: str
    partner_sku: str
    expected_lift: float
    rationale: str

class AuditEntry(BaseModel):
    audit_id: str
    timestamp: datetime
    recommendation_id: str
    user_id: str | None
    policy_result: dict
    evidence: dict
```

---

# 10. Governance Deep-Dive (Enhancement #9)

## 10.1 What Governance Does on Every Recommendation

1. **Extract evidence** — lift, confidence, support, contributing basket count
2. **Generate NL narrative** — via LLM (or template fallback if mocked)
3. **Run policy checks:**
   - Margin over-concentration check
   - Brand mandate compliance
   - Fairness across SKU tiers (don't over-recommend premium)
   - Vendor equity (don't systematically favor one vendor)
4. **Compute fairness metrics** — SKU diversity index, vendor share
5. **Write audit entry** to `data/audit.jsonl`
6. **Return `GovernedRecommendation`** wrapping the original

## 10.2 Audit Log Format (JSONL)

Every line is one JSON object with the `AuditEntry` schema. **Append-only.** Do not truncate or edit.

```json
{"audit_id": "aud_abc123", "timestamp": "2026-07-07T14:30:00Z", "recommendation_id": "rec_xyz", "policy_result": {"passed": true, "warnings": []}, "evidence": {"lift": 1.42, "confidence": 0.31, "support": 0.08}}
```

## 10.3 Policy Rules (Phase 1)

| Rule ID | Description | Severity |
|---------|-------------|----------|
| POL-001 | High-margin SKUs must not exceed 40% of any endcap | Medium |
| POL-002 | Every recommendation must have confidence ≥ 0.1 | High |
| POL-003 | Brand mandate SKUs (config-driven) must appear in top-3 for their category | High |
| POL-004 | No single vendor's SKUs may exceed 30% of co-placement suggestions | Medium |
| POL-005 | Recommendations for regulated categories (alcohol, tobacco) require explicit flag | Critical |

Rules live in `services/governance/policy_engine.py` as small pure functions returning `PolicyResult`.

---

# 11. LLM Usage Guardrails (Enhancement #3)

## 11.1 Where LLM Calls Are Allowed

- `services/genai_vendor/planogram_agent/` — primary LLM-driven flow
- `services/governance/explainability.py` — NL narrative generation
- **Nowhere else.** Do not sprinkle LLM calls across the codebase.

## 11.2 Prompt Management

- Prompts live in `services/genai_vendor/planogram_agent/prompts/*.txt`
- Each prompt file has a **version comment header**: `# prompt_version: v1.2`
- Every LLM call logs the prompt version used

## 11.3 Tool Calling

The planogram agent uses Claude's tool-calling. Available tools:

```python
TOOLS = [
    {
        "name": "get_recommendations",
        "description": "Get top-k placement recommendations for a category/store/context",
        "input_schema": {...}
    },
    {
        "name": "get_shelf_constraints",
        "description": "Get shelf capacity and adjacency constraints",
        "input_schema": {...}
    },
    {
        "name": "get_category_rules",
        "description": "Get brand mandates and category rules",
        "input_schema": {...}
    },
]
```

## 11.4 Mock Fallback

If `settings.mock_llm=True` or `anthropic_api_key` is missing:
- `LLMClient.complete()` returns pre-canned responses shaped like real Claude outputs
- Mock responses live in `platform/llm_mocks.py`
- Log every mock use so demo audiences can be told when it's mock vs. live

---

# 12. Dependencies (Locked)

**Claude Code: do not add dependencies outside this list without a decision log entry.**

## 12.1 Core Runtime

```toml
[project]
requires-python = ">=3.11"

dependencies = [
    # Web
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "streamlit>=1.40",
    "pydantic>=2.9",
    "pydantic-settings>=2.6",
    "python-multipart>=0.0.12",
    "requests>=2.32",

    # Data
    "pandas>=2.2",
    "numpy>=1.26",
    "pyarrow>=17.0",
    "duckdb>=1.1",

    # ML
    "scikit-learn>=1.5",
    "xgboost>=2.1",
    "mlxtend>=0.23",
    "networkx>=3.4",
    "faiss-cpu>=1.9",

    # LLM
    "anthropic>=0.39",

    # Utilities
    "python-dotenv>=1.0",
    "faker>=30.0",
    "structlog>=24.4",
    "typer>=0.13",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-cov>=6.0",
    "ruff>=0.7",
    "mypy>=1.13",
]
```

## 12.2 Explicitly Forbidden in Phase 1

- ❌ `docker`, `docker-compose`
- ❌ `boto3`, `azure-*`, `google-cloud-*` (any cloud SDK)
- ❌ `kafka-python`, `confluent-kafka`, `celery`, `rabbitmq`
- ❌ `neo4j`, `psycopg2`, `sqlalchemy` (Postgres/ORM)
- ❌ `mlflow`, `feast`, `dvc` (heavy MLOps)
- ❌ `react`, `vue`, `next`, any JS framework
- ❌ `langchain`, `llamaindex` (keep LLM layer thin; use `anthropic` SDK directly)

*If any of these become necessary, they must be discussed and logged in `decision_log.md` before adoption.*

---

# 13. Configuration & Environment

## 13.1 `.env.example`

```bash
# LLM (optional — leave blank for mock mode)
ANTHROPIC_API_KEY=

# API auth (any string; used for X-API-Key header)
API_KEY=demo-key

# LLM model
LLM_MODEL=claude-sonnet-4.5

# Data
DATA_DIR=data

# Logging
LOG_LEVEL=INFO

# Feature flags
ENABLE_GOVERNANCE=true
MOCK_LLM=false
```

## 13.2 Startup Behavior

On FastAPI startup (`api/main.py`):
1. Load `Settings`
2. Verify data files exist in `data/samples/` (raise if seed not run)
3. Load `AffinityGraph` into memory
4. Load `VectorStore` from disk
5. Initialize `LLMClient` (with mock fallback if no key)
6. Register routes
7. Log architecture version and mode (live vs. mocked)

---

# 14. Testing Strategy

## 14.1 Test Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── affinity_optimization/
│   │   ├── genai_vendor/
│   │   └── governance/
│   └── platform/
└── integration/
    ├── test_flow_recommendations.py
    ├── test_flow_planogram.py
    └── test_flow_vendor_promo.py
```

## 14.2 Testing Rules

- ✅ Every service public function has ≥1 unit test
- ✅ Integration tests use synthetic data + mocked LLM
- ✅ Every policy rule in `policy_engine.py` has a test
- ✅ Every audit write has a test verifying the log line format
- ❌ No test may hit the real Anthropic API (use mock mode)

## 14.3 CI (`.github/workflows/ci.yml`)

Runs on every PR:
1. `uv sync`
2. `ruff check .`
3. `pytest tests/ -v`

No deploy step. No release automation in Phase 1.

---

# 15. Naming & Coding Conventions

**Claude Code: follow these strictly.**

## 15.1 Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `contextual_affinity.py` |
| Classes | `PascalCase` | `AffinityGraph` |
| Functions | `snake_case` | `get_recommendations()` |
| Constants | `UPPER_SNAKE` | `DEFAULT_TOP_K` |
| Pydantic models | `PascalCase`, singular noun | `Recommendation`, not `Recommendations` |
| Private helpers | leading underscore | `_compute_lift()` |

## 15.2 Docstrings

Every module and public function has a Google-style docstring:

```python
def get_recommendations(store_id: str, top_k: int = 20) -> list[Recommendation]:
    """Compute placement recommendations for a store.

    Args:
        store_id: The store master identifier.
        top_k: Number of recommendations to return.

    Returns:
        Governed recommendations sorted by composite score descending.

    Raises:
        StoreNotFoundError: If store_id does not exist in store master.
    """
```

## 15.3 Type Hints

- **Required** on all public function signatures
- Use `from __future__ import annotations` at top of modules
- Prefer `list[X]` over `List[X]` (Python 3.11+)

## 15.4 Logging

- Use `structlog` (configured in `platform/config.py`)
- Never use `print()` in service or platform code
- Log level convention:
  - `DEBUG` — deep tracing (LLM prompts, SQL queries)
  - `INFO` — normal flow (request received, recommendation returned)
  - `WARNING` — policy violations, fallbacks used
  - `ERROR` — unhandled failures

---

# 16. Makefile Commands (Contract)

```makefile
setup:   ## Install dependencies via uv
seed:    ## Generate synthetic data into data/samples/
demo:    ## Start FastAPI (8000) + Streamlit (8501)
test:    ## Run pytest + ruff
reset:   ## Wipe SQLite DB, FAISS index, audit log (keep Parquet)
clean:   ## Full clean including Parquet (forces regeneration)
```

**Contract:** these command names must not change. Team members will memorize them.

---

# 17. Known Non-Goals (Do Not Build in Phase 1)

Referenced from `decision_log.md`:

- Enhancement #2 (Computer Vision + IoT)
- Enhancement #7 (Digital Twin + AR)
- Docker / Docker Compose
- Kubernetes
- Cloud deployment
- Kafka / streaming ingestion
- MLflow server / Feast
- Neo4j
- React front-end
- Enterprise SSO
- Prometheus / Grafana
- Ollama offline LLM (deferred; can be added in Phase 2 as an `LLMClient` variant)

---

# 18. Extension Points (When You Need to Add Something)

**Adding a new enhancement in the future?** Follow this pattern:

1. Add a new sub-package under the appropriate service (`services/<service>/<new_enhancement>/`)
2. Expose only what's needed via the service's `__init__.py`
3. If it produces recommendations, ensure they pass through `governance.govern()`
4. Add its data needs to `data_contract.md`
5. Add a decision log entry (`D-XXX`)
6. Update this file (`architecture.md`) if the layer boundaries change

**Adding a new API endpoint?**

1. Add a new file under `api/routes/`
2. Define request/response schemas in `api/schemas.py`
3. Register the route in `api/main.py`
4. Add auth check via `Depends(verify_api_key)`
5. Add integration test

**Adding a new data domain?**

1. Update `data/seed.py` to generate synthetic data for it
2. Add schema to `data_contract.md`
3. Add loader helper in `platform/data_access.py`
4. Never bypass `platform/data_access.py` for reads

---

# 19. Quick Reference Card for Claude Code

**When Claude Code is asked to build a feature, it should:**

1. **Confirm the layer** the feature belongs to (Section 3)
2. **Locate the correct directory** (Section 2)
3. **Match the naming convention** (Section 15)
4. **Use only allowed dependencies** (Section 12)
5. **Call `governance.govern()`** if producing recommendations (Section 4.4)
6. **Access data only via `platform/data_access.py`** (Section 5.2)
7. **Add a unit test** in `tests/unit/` (Section 14)
8. **Add a docstring** (Section 15.2)
9. **Update `decision_log.md`** if introducing a material choice
10. **Never introduce** items from the forbidden list (Section 12.2)

---

## 🔗 Related Documents

| Doc | Purpose |
|-----|---------|
| `CLAUDE.md` | LLM project brief — should reference this file first |
| `decision_log.md` | Why decisions were made |
| `data_contract.md` | Full field-level schemas per data domain |
| `demo_script.md` | How to demo the tool to prospects |
| `production_mapping.md` | How each local component maps to cloud in Phase 2 |
| `README.md` | Human setup guide (3 commands) |

---

*Confidential — Cognizant Internal · Architecture Reference v1.0 · July 2026 · Maintained by Aditya Srivastava*
