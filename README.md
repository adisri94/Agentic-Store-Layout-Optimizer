# Store Layout (Product Placement) Optimizer — Demo

An "Agentic Shelf Intelligence Platform" demo: a local-first analytics tool that recommends where to place products on a store shelf, using Market Basket Analysis (Apriori/FP-Growth) augmented with contextual AI, GenAI, and omnichannel signals — all running on a single laptop.

Built as a live, working demo for prospect retail clients. No cloud account, no Docker, no external database required to run it.

---

## What This Is

- **Input:** Synthetic POS transaction data (mimics Oracle Retail Xstore / SAP CAR schemas), product master, store master, e-commerce clickstream, loyalty data, and vendor trade promo data.
- **Processing:** Market Basket Analysis + 7 enhancements (contextual affinity, GenAI planogram design, omnichannel sync, segmentation, multi-objective optimization, vendor collaboration, explainability/governance).
- **Output:** Ranked, explainable, audited product-placement recommendations, viewable in a Streamlit app.

For the full technical reference, see [`docs/architecture.md`](docs/architecture.md). For why any given decision was made, see [`docs/decision_log.md`](docs/decision_log.md).

---

## Prerequisites

| Requirement | Version | Why |
|---|---|---|
| Python | 3.11+ | Core language for the whole stack |
| [`uv`](https://github.com/astral-sh/uv) | latest | Package manager (faster than pip/poetry) |
| RAM | 16 GB recommended | Demo data volumes run fully in memory |
| Anthropic API key | optional | GenAI features work without one — they fall back to realistic mock responses |

No Docker, no cloud account, no database server needed.

### Installing `uv`

The recommended one-liner (`irm https://astral.sh/uv/install.ps1 | iex`) may be blocked by corporate proxies that reject script downloads (e.g. Zscaler). If so, install `uv` from PyPI with the `pip` that ships with Python — this route pulls a normal wheel and is not blocked:

```powershell
python -m pip install --user uv
```

If `uv` isn't found afterward, add pip's user Scripts directory to your PATH (shown by `python -c "import site; print(site.USER_BASE)"`, then append `\PythonXYZ\Scripts`). The bundled `tasks.ps1` also falls back to `python -m uv` automatically if the `uv` command isn't on PATH.

---

## Setup (3 Commands)

```bash
make setup   # installs dependencies via uv
make seed    # generates synthetic retail data into data/samples/
make demo    # starts FastAPI (port 8000) + Streamlit (port 8501)
```

Then open **http://localhost:8501** in your browser.

### Optional: enable live GenAI

By default, the Generative AI Planogram Designer runs in mock mode (no API key needed — the app tells you when a response is mocked vs. live). To use live Claude responses:

1. Copy `.env.example` to `.env`
2. Add your key: `ANTHROPIC_API_KEY=sk-ant-...`
3. Re-run `make demo`

---

## What You Can Do in the Demo

| Mode | Persona | What it shows |
|---|---|---|
| **Category Manager** | Category Manager | Get placement recommendations, ask the GenAI agent to design a planogram in plain English, see lift/margin/turn trade-offs |
| **Vendor Portal** | CPG Vendor Partner | Upload a promo calendar, see co-placement suggestions and performance dashboards |
| **Admin / Governance** | Data Steward, Merchandising Head | View the audit log, inspect explainability narratives for any recommendation, review policy flags |

---

## Project Structure
ui/           Streamlit app — 3 modes above
api/          FastAPI — REST endpoints, auth, request/response schemas
services/     Business logic — affinity & optimization, GenAI & vendor, governance
platform/     Shared helpers — LLM client, data access, vector store, graph store
data/         Synthetic data generator + generated Parquet/SQLite/FAISS/audit files
tests/        pytest test suite
docs/         Architecture, decision log, data contract, demo script
Full breakdown in [`docs/architecture.md`](docs/architecture.md) §2.

---

## Common Commands

```bash
make setup   # install dependencies
make seed    # (re)generate synthetic data
make demo    # run the app (API + UI)
make test    # run pytest + ruff lint
make reset   # wipe SQLite DB, FAISS index, audit log (keeps synthetic data)
make clean   # full clean — also regenerates synthetic data from scratch
```

**On Windows without `make`?** Use the bundled PowerShell equivalent — same verbs, no extra install (see decision log D-031):

```powershell
./tasks.ps1 setup   # ./tasks.ps1 seed | demo | test | reset | clean
```

---

## Data & Privacy

All data in this demo is **synthetic** — generated with Python and Faker for a fictional global sports-apparel retailer. No real customer or transaction data is used. Any fields resembling PII (email, phone) are hashed by convention, matching how the schemas mimic real production systems.

---

## Project Status

This is a Phase 1 demo build, developed sprint by sprint (see [`docs/decision_log.md`](docs/decision_log.md) D-025 for the sequence). Some enhancements you may see referenced in supporting docs — computer vision/IoT shelf sensors, digital twin/AR — are intentionally out of scope for this build and are documented as a future roadmap, not missing functionality.

---

## Questions / Issues

This is an internal Cognizant demo project. For questions about scope, architecture, or roadmap, see the docs above or reach out to the project owner, Aditya Srivastava.

---

*Confidential — Cognizant Internal*
