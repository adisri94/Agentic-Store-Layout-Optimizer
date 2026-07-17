# Product Vision One-Pager v2.1
## Store Layout (Product Placement) Optimizer Tool

| Owner | Version | Date | Status |
|---|---|---|---|
| Aditya Srivastava, Senior Consultant, Cognizant | v2.1 (Draft) | 17 July 2026 | For Review |

---

## Version Tracking

| Version | Date | Change Owner | Change Summary |
|---|---|---|---|
| **2.0** | July 2026 | Aditya Srivastava | Current baseline version of the Product Vision One-Pager. |
| **2.1** | 17 July 2026 | Aditya Srivastava | - Updated 9 High-Level Architecture Principles to replace microservices with modular monolith approach: 3 logical services in one FastAPI process, referencing D-011 from decision_log.md.<br>- Updated 9 to defer MLflow/Feast and clarify local model artifact handling, referencing architecture.md 12.2 and T-006.<br>- Updated 3 Target Users & Personas to annotate Store Operations Manager as consumer of output only, not primary UI persona, referencing D-004.<br>- Updated 10 Build Sequence to rename Phase 1–Phase 5 as Sprint 1–Sprint 5 to avoid conflicting phase terminology across documents, referencing D-025. |

---

## 1. Vision Statement

Build an Agentic Shelf Intelligence Platform that transforms static planogram decisions into continuously learning, context-aware placement recommendations. The platform combines classical Market Basket Analysis with contextual ML, Generative AI, and omnichannel signals to help retailers maximize sell-through, store traffic, and shopper experience — deployable on any leading cloud.

---

## 2. Problem Statement

Retailers face intensifying margin pressure and want to maximize revenue per square foot. Legacy planogram tools rely on static Market Basket Analysis that ignores shopper missions, time/context effects, negative associations, and omnichannel behavior. Category managers spend weeks producing planograms that go stale within days, and vendor collaboration is fragmented. A modern, explainable, AI-augmented placement platform is needed.

---

## 3. Target Users & Personas

| Persona | Role & Need |
|---|---|
| **Category Manager** | Primary user — designs planograms, evaluates lift and margin trade-offs. |
| **Store Operations Manager** | Consumer of output only, not primary UI persona (D-004). |
| **CPG Vendor Partner** | Uploads promo calendars; collaborates on co-placement opportunities. |
| **Data Steward** | Owns data quality, lineage, and governance for the data product. |
| **Merchandising Head** | Consumes KPI dashboards; makes strategic assortment decisions. |

---

## 4. Core Capability (Foundational)

The analytical backbone is a Market Basket Analysis engine using Apriori and FP-Growth on POS transaction data. Every enhancement below either augments or contextualizes this engine.

| Aspect | Description |
|---|---|
| **Input** | POS transaction data in standard schema (transaction ID, SKU, timestamp, store, quantity, price). |
| **Processing** | Apriori / FP-Growth association rule mining → lift, confidence, support scoring. |
| **Output** | Ranked placement recommendations (adjacency / endcap / aisle) with lift, confidence, and support metrics. |
| **Role** | Analytical backbone — every enhancement either augments or contextualizes this engine. |

---

## 5. In-Scope Enhancements (Finalized for v1)

| # | Enhancement | What It Does | Key Features | Business Value | Data / Tech Dependencies |
|---|---|---|---|---|---|
| **1** | **Contextual Affinity Modeling** | Moves beyond static MBA to capture shopper journeys and self-learn from live sales response. | Sequence mining (PrefixSpan); contextual bandits / RL; negative-association detection. | Higher recommendation precision; adaptive to seasonality, weather, and promo state. | POS + time/context features; RL framework; feature store. |
| **3** | **Generative AI Planogram Designer** | LLM-based agent that auto-generates planogram suggestions with natural-language explanations. | NL chat interface for category managers; agent uses MBA + category rules + brand mandates. | Drastically reduces time-to-planogram; democratizes access for non-technical users. | LLM gateway (Bedrock / Azure OpenAI / Vertex); prompt registry; vector DB. |
| **4** | **Omnichannel Affinity Sync** | Unifies e-commerce clickstream affinities with in-store basket affinities into a single graph. | Cross-channel affinity graph; loyalty-based identity resolution; channel-lift comparisons. | Consistent shopper experience across channels; unlocks digital-to-physical cross-merchandising. | Clickstream feed; loyalty ID; graph DB or pgvector. |
| **5** | **Shopper Segment & Mission-Based Placement** | Generates micro-planograms per shopper mission and store cluster. | Mission classification (fill-in / stock-up / occasion); store cluster overlay; segment personas. | Personalized layouts per store cluster; improves conversion and basket size. | Loyalty data; demographic clusters; segmentation models. |
| **6** | **Multi-Objective Optimization** | Optimizes placements against multiple business goals, not just lift. | Weighted scoring of lift + margin + inventory turn + shrink risk; optional sustainability factor. | Balances revenue with operational and ESG objectives; reduces stockouts and shrink. | Product master; inventory data; margin data; optimization solver. |
| **8** | **Vendor Collaboration Module** | Portal enabling CPG vendors to share promo calendars and view co-placement opportunities. | Vendor onboarding workflow; secure upload of trade promo data; collaboration dashboard. | Monetizable SaaS + data marketplace angle; deeper brand partnerships. | Vendor data schema; identity & access management; secure portal. |
| **9** | **Explainability & Governance** | Ensures every recommendation is transparent, auditable, and bias-checked. | Lift / confidence / support metrics + plain-English 'why' narrative; bias & guardrail checks. | Drives category manager adoption; enables regulatory and internal audit compliance. | Explainability service; policy engine; prompt governance for GenAI outputs. |

---

## 6. Out-of-Scope (Explicit Non-Goals for v1)

The following enhancements are consciously deferred to a v2 roadmap. They are high-complexity, high-value additions that require dedicated hardware/vendor partnerships and will be addressed once the v1 platform is stabilized:

- **#2 Computer Vision + IoT Integration** — shelf cameras, in-store sensors, dwell-time analytics. Deferred to v2.
- **#7 Digital Twin + AR Execution** — 3D simulation of store layouts and AR-guided resets. Deferred to v2.

These are deliberate deferrals, not omissions — they remain on the strategic roadmap.

---

## 7. Key KPIs & Success Metrics

- Sales lift % attributed to recommended placements
- Margin uplift % across optimized categories
- Inventory turn improvement
- % of SKUs with explainable recommendations (target: 100%)
- Category manager adoption rate (weekly active users)
- Vendor engagement — number of vendors onboarded to collaboration module
- Model quality — precision@k for placement recommendations
- Time-to-planogram reduction (baseline vs. AI-assisted)

---

## 8. Data Product Contract (Summary)

The platform is designed on Data-as-a-Product principles. Six data domains form the input contract, each with a clear consuming capability.

| Data Domain | Source System To Be Replicated (Examples) | Key Fields | Consuming Capability |
|---|---|---|---|
| **POS Transactions** | Oracle Retail Xstore, NCR, SAP CAR | txn_id, sku, timestamp, store_id, qty, price, promo_flag | Core MBA (foundational); #1 Contextual Affinity; #6 Optimization |
| **Product Master** | SAP MDG / Informatica MDM | sku, category, subcategory, brand, cost, margin, dimensions | Core MBA; #6 Multi-Objective Optimization |
| **Store Master** | Retail ERP / MDM | store_id, format, cluster, geo, sq_ft, planogram_zones | #5 Segment/Mission-Based Placement; core planogram output |
| **E-commerce Clickstream** | Adobe Analytics, GA4, Segment | session_id, user_id, product_view, add_to_cart, purchase | #4 Omnichannel Affinity Sync |
| **Loyalty & Segmentation** | Salesforce Loyalty, Braze, custom CDP | loyalty_id, segment, mission_score, demographics | #4 Omnichannel; #5 Segment/Mission-Based Placement |
| **Vendor Trade Promo** | Vendor portal uploads (JSON / IDOC) | vendor_id, sku, promo_period, discount, co_display_ask | #8 Vendor Collaboration Module; #6 Optimization |

---

## 9. High-Level Architecture Principles

- UI / backend separation with clean API contracts
- API-first design using REST (and WebSocket for chat)
- Modular monolith — 3 logical services in one FastAPI process (D-011)
- Modularity and maintainability — independently deployable services
- Security-compliant by design (RBAC, secrets management, encryption in transit and at rest)
- Cloud-deployable on any leading platform (AWS / Azure / GCP)
- Production-grade coding standards, code reviews, and unit/integration testing
- Well-documented — code, API specs (OpenAPI), architecture, and decision records
- Model artifacts as local files; MLflow/Feast deferred (T-006, 12.2)
- LLM governance — prompt registry, evaluation harness, and output guardrails

---

## 10. Build Sequence (Phased Roadmap Summary)

| Sprint | Focus | Primary Deliverables |
|---|---|---|
| **Foundation (2–3 wks)** | Discovery, Data Strategy, Architecture | Vision one-pager, Data Product Contract, Architecture Blueprint, Repo + CI/CD, Governance Charter, Project Journal |
| **Sprint 1** | Core MBA + #9 Explainability guardrails | Apriori/FP-Growth engine; lift/confidence/support outputs; explainability service; bias checks |
| **Sprint 2** | #1 Contextual Affinity + #6 Multi-Objective Optimizer | Sequence mining; RL scaffolding; weighted optimizer for lift/margin/inventory/shrink |
| **Sprint 3** | #4 Omnichannel Affinity + #5 Segmentation | Unified affinity graph; identity resolution; mission classifier; store clustering |
| **Sprint 4** | #3 GenAI Planogram Agent | LLM gateway; prompt registry; NL chat UI; agent tools for MBA + optimizer |
| **Sprint 5** | #8 Vendor Collaboration Module | Vendor portal; trade promo ingestion; collaboration dashboard; RBAC |
| **Hardening + Demo** | Cloud Deployment & Showcase | Perf/security hardening; cloud demo environment; client-ready showcase artifacts |
