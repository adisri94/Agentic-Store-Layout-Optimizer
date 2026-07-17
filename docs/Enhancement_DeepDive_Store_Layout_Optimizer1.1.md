# Enhancement Deep-Dive

## Store Layout (Product Placement) Optimizer Tool

_Detailed Working, Data Inputs, Processing Logic, and Outputs for the 7 In-Scope Enhancements_

| Field | Value |
|---|---|
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Version** | 1.1 |
| **Date** | July 2026 |
| **Status** | Approved v1.1 |
| **Companion To** | Product Vision One-Pager v2 |

## Version Tracking

| Version | Date | Area Updated | Change Summary |
|---|---|---|---|
| 1.0 | July 2026 | Draft |  |
| 1.1 | July 2026 | Technology stack alignment | Updated Enhancement #3 to use Anthropic Claude API as the single LLM provider and direct tool-calling via the anthropic SDK. |
| 1.1 | July 2026 | Enhancement #4 | Replaced Neo4j/Amazon Neptune with in-memory NetworkX per D-020; marked Neo4j as Phase 2 only. Replaced Kafka/Airflow/Spark ETL with batch load from Parquet files and deferred Kafka per T-010. |
| 1.1 | July 2026 | Enhancement #1 | Removed the Feast feature-store reference because it is explicitly excluded as a heavyweight MLOps tool in architecture.md §12.2. |
| 1.1 | July 2026 | Enhancement #8 | Replaced OAuth 2.0/SSO with API-Key auth and vendor-scope header check per D-029; deferred SSO per T-004. Replaced embedded analytics tools with Streamlit-native dashboard rendering per D-014. |
| 1.1 | July 2026 | Enhancement #6 | Kept PuLP as the Phase 1 optimization library and marked OR-Tools/genetic algorithms as Phase 2 candidates only, aligning with architecture.md §12.1. |
| 1.1 | July 2026 | Enhancement #9 | Replaced Drools/Open Policy Agent rule-engine wording with small pure Python policy functions to maintain Python-only alignment per D-013. Marked MLOps drift monitoring as Aspirational/Phase 2 because no drift tool exists in the Phase 1 dependency list. |

## 1. Introduction

This document is a companion to the Product Vision One-Pager v2 for the Store Layout (Product Placement) Optimizer Tool. It provides an engineering- and data-team-ready breakdown of how each of the seven in-scope enhancements works: the input data required, the processing logic and algorithms involved, and the outputs produced. The goal is to establish a shared understanding across product, data, ML, and platform teams before Sprint planning, and to serve as the technical anchor for the Project Journal.

## 2. Foundational Context — The MBA Core

At the heart of the tool is the Market Basket Analysis (MBA) engine, which applies Apriori and FP-Growth association rule mining to POS transactions. It produces baseline placement recommendations (adjacency, endcap, aisle) scored with lift, confidence, and support. Every enhancement described below either augments this core (by adding context, personalization, or governance) or exposes it to new consumers (category managers via GenAI, vendors via collaboration portal). Understanding this core is essential before reading the enhancement details.

## 3.1 Enhancement #1 — Contextual Affinity Modeling

### Overview & Objective

Contextual Affinity Modeling extends the static MBA core by making affinities aware of context — time of day, day of week, weather, promo state, store cluster, and shopper journey. It also learns from live sales response using reinforcement learning and captures negative associations (cannibalization) that traditional Apriori misses. This turns placement intelligence from a periodic batch exercise into a continuously improving decision system.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| POS transactions (with timestamps, store, basket) | POS / Data Lake | Parquet / CSV | Core basket signal for affinity mining |
| Shopper session / journey logs | Loyalty / CRM | JSON events | Sequence mining and journey reconstruction |
| Contextual features (time, day, weather) | Weather API, calendar | JSON / feature store | Enrich baskets with situational context |
| Promotion calendar | Promo Mgmt System | CSV / API | Detect promo-driven affinities |
| SKU master (category, brand, price) | PIM / MDM | Relational table | Attribute-based rule refinement |
| Inventory snapshots | ERP / WMS | Daily snapshot table | Filter recommendations by stock feasibility |
| Historical placement changes | Planogram history | Log / CSV | Feedback signal for RL training |

### Processing Logic

- Ingest and clean POS transactions; standardize basket-item schema and remove voids/returns.
- Enrich each basket with contextual features (hour band, day type, weather bucket, promo flag).
- Run baseline MBA using Apriori and FP-Growth to establish global affinity rules with lift, confidence, and support.
- Apply sequence-mining algorithms (PrefixSpan, SPADE) on shopper journeys to detect ordered purchase patterns.
- Train a contextual bandit or offline RL policy (LinUCB / Thompson Sampling) using historical placement→sales as rewards.
- Compute a cannibalization matrix by identifying SKU pairs whose co-placement historically depressed each other's sales.
- Score and rank contextual affinity rules per (segment × context × store cluster) combination.
- Publish rules to the affinity store, versioned and tagged with confidence intervals and context metadata.

### Techniques / Algorithms Used

- Apriori and FP-Growth for association rules
- PrefixSpan and SPADE for sequential pattern mining
- Contextual bandits (LinUCB, Thompson Sampling)
- Offline reinforcement learning for placement policy
- Negative association mining for cannibalization detection
- Feature engineering with time-series and contextual variables

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Contextual affinity rules with tags | JSON / affinity store | GenAI Planogram Agent (#3), Optimizer (#6) | Used to generate placement candidates |
| Sequence patterns | JSON list | Segmentation service (#5) | Inform mission-based planograms |
| Cannibalization matrix | Sparse matrix / DB table | Optimizer (#6), Governance (#9) | Penalize adverse co-placements |
| RL placement policy | Serialized model + config | Optimizer, Execution layer | Recommend next best placement action |
| Contextual recommendation scores | REST API response | UI, Vendor portal (#8) | Rank displayed suggestions |

### Illustrative Example

_Example — Sports Apparel: The engine learns that running shoes and moisture-wicking socks show a 42% lift on weekday mornings but only 12% on weekends. On rainy days, running-gear affinities shift toward indoor training gear, so the contextual recommendation for a rainy Tuesday morning promotes an indoor training endcap instead of the outdoor running display._

## 3.2 Enhancement #3 — Generative AI Planogram Designer

### Overview & Objective

This enhancement introduces an LLM-based agent that consumes affinity rules, category constraints, brand mandates, and shelf/fixture data to auto-generate planograms complete with natural-language rationales. Category managers interact via a chat-style NL interface (e.g., 'Optimize the beverage aisle for margin'), and the agent produces draft planograms that can be reviewed, adjusted, and exported to downstream execution systems.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| MBA / contextual affinity rules | Enhancement #1 output | JSON / API | Core placement signal |
| Category rules & adjacency constraints | Category Mgmt system | YAML / rules DB | Enforce merchandising policy |
| Shelf & fixture master | Store planning system | Relational table | Physical constraints (bays, shelves, facings) |
| SKU dimensions and pack sizes | PIM / MDM | Relational table | Facing capacity and fit calculations |
| Brand mandates and contracts | Vendor / Legal | Documents indexed for RAG | Compliance with contractual placements |
| Historical planogram versions | Space planning archive | Planogram files | Baseline and version control |
| Category manager NL query | Chat UI | Text prompt | Trigger and scope agent reasoning |

### Processing Logic

- Category manager submits a natural-language query via the chat interface.
- LLM agent parses intent, extracts entities (aisle, category, KPI), and identifies constraints to respect.
- Agent invokes tools: affinity API (#1), category rules API, shelf constraint API, product master API.
- A constraint-satisfaction solver (e.g., OR-Tools) generates feasible candidate planograms.
- LLM composes a draft planogram with a rationale for each placement decision, grounded in retrieved evidence.
- The explainability service (#9) annotates each recommendation with lift, confidence, and support.
- Human-in-the-loop review — category manager accepts, edits, or requests alternatives; feedback is captured.
- Approved planogram is exported to execution systems (JDA / Nielsen Spaceman / custom) in the standard format.

### Techniques / Algorithms Used

- Anthropic Claude API (single provider, per D-018)
- Direct tool-calling via the anthropic SDK
- Retrieval-Augmented Generation (RAG) over category rules and mandates
- Tool-calling / function-calling for deterministic API access
- Constraint solvers (Google OR-Tools) for feasibility
- Prompt versioning and prompt registry
- Human-in-the-loop feedback capture for continual improvement

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Draft planogram | JSON / planogram file | Category Manager, Store Ops | Review and approve |
| NL rationale per placement | Text block | Category Manager | Build trust and enable override |
| Alternative scenarios | Ranked JSON list | Category Manager | Compare trade-offs |
| Confidence-tagged recommendations | JSON | Governance service (#9) | Audit and policy check |
| Exportable planogram file | JDA / Spaceman format | Space planning system | Execute in store |

### Illustrative Example

_Example — Men's Training Apparel: The Category Manager types, 'Redesign the men's training aisle to maximize cross-sell with footwear.' The agent produces a planogram placing training tees adjacent to running shoes with the rationale, 'A 34% lift is observed across 12 comparable stores; this supports the morning-workout shopper mission and honors the brand-blocking rule for the premium sub-brand.'_

## 3.3 Enhancement #4 — Omnichannel Affinity Sync

### Overview & Objective

This enhancement merges e-commerce clickstream and in-store basket data into a single, segment-aware affinity graph. It surfaces cross-channel patterns — such as 'browsed online, bought in-store' — and translates digital engagement into physical placement recommendations, closing the loop between the online and offline shelf.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| E-commerce clickstream | Web / App analytics | Event stream (JSON) | Digital affinity signal |
| Add-to-cart / purchase events | E-commerce platform | Event stream / DB | Intent and conversion signal |
| Loyalty ID mapping | Loyalty / CDP | Identity graph table | Unify shoppers across channels |
| In-store POS baskets | POS / Data Lake | Parquet / CSV | Physical basket signal |
| Product master with digital-physical SKU map | PIM / MDM | Relational table | Reconcile SKUs across channels |
| Customer profile data | CDP | Relational table | Segment enrichment |
| Wishlist / save-for-later | E-commerce | DB table | Latent-intent signal |

### Processing Logic

- Ingest clickstream and POS data into a unified data lake with consistent event schemas.
- Perform identity resolution using loyalty ID and hashed email/phone to link online and offline shoppers.
- Build channel-specific affinity graphs (browse-based, purchase-based, in-store basket-based).
- Merge into a unified affinity graph with weighted edges reflecting channel strength and recency.
- Compute cross-channel lift metrics — for example, online-browse → in-store-purchase probability.
- Segment the affinity graph by shopper cluster and store cluster to preserve personalization signal.
- Publish the graph and derived rules to the affinity store, tagged by source channel for governance.

### Techniques / Algorithms Used

- NetworkX (in-memory, per D-020). Neo4j is a Phase 2 trigger only
- Identity resolution and probabilistic matching
- Graph embeddings (node2vec, GraphSAGE)
- Collaborative filtering across channels
- Cross-channel attribution modeling
- Batch load from Parquet files (Kafka deferred, T-010)
- PII handling and consent-aware pipelines

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Unified affinity graph per segment | Graph DB | Contextual Affinity (#1), Segmentation (#5) | Feed contextual and mission models |
| Cross-channel lift scores | Table / API | Optimizer (#6) | Weight placement recommendations |
| Online-viewed / in-store-bought pairs | JSON list | Category Manager | Identify digital-to-physical opportunities |
| Digital-to-physical placement recommendations | JSON / API | GenAI Agent (#3) | Seed planogram design |
| Cross-channel journey insights | Dashboard | Marketing, Category leaders | Strategic decision-making |

### Illustrative Example

_Example — Trail Running: Data shows customers who browse trail running shoes online often buy hydration packs in-store on weekends near hiking-trail catchments. The recommendation is to move hydration packs adjacent to the trail-running footwear display in those stores, with a projected 19% incremental lift._

## 3.4 Enhancement #5 — Shopper Segment & Mission-Based Placement

### Overview & Objective

This enhancement replaces one-size-fits-all planograms with micro-planograms tailored to shopper missions (fill-in, stock-up, occasion, quick trip) and store clusters (urban express vs suburban family, etc.). It personalizes the physical shelf the same way e-commerce personalizes the digital shelf.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| Loyalty transactions with customer ID | Loyalty / POS | Relational / Parquet | Enable RFM and cohort analysis |
| Basket size and composition | POS | Table | Infer mission from basket shape |
| Visit frequency and recency | Loyalty | Table | Segment shoppers behaviourally |
| Demographic data | CDP / third-party | Table | Attribute-based segmentation |
| Store master with cluster attributes | Store MDM | Table | Cluster stores by format and geography |
| Time-of-day / day-of-week patterns | POS derived | Aggregated table | Detect mission timing |
| Mission-labeled historical baskets | Analyst labels + rules | Training dataset | Train mission classifier |

### Processing Logic

- Analyze basket composition (size, categories, price bands) to infer probable shopper mission.
- Compute RFM and behavioural features per loyalty customer.
- Cluster shoppers using k-means or hierarchical clustering on the combined feature set.
- Cluster stores using demographic, geographic, and format attributes.
- Train a mission-classification model (Random Forest or XGBoost) on the labeled basket dataset.
- Compute affinity rules for each (shopper segment × store cluster × mission) combination.
- Generate micro-planogram variants per cluster and A/B test them in matched store pairs.
- Feed refined segment-aware rules to the GenAI Agent (#3) and the Optimizer (#6).

### Techniques / Algorithms Used

- K-means and hierarchical clustering
- RFM (Recency, Frequency, Monetary) analysis
- XGBoost / Random Forest for mission classification
- Cohort analysis and lifecycle segmentation
- A/B testing frameworks and matched-store experimentation
- Feature engineering on basket structure
- Consent-aware personalization

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Shopper segment definitions | Segment catalog | Marketing, Category Mgmt | Align personalization strategy |
| Mission labels per basket | Enriched POS table | Contextual Affinity (#1) | Contextualize affinity mining |
| Store cluster assignments | Store master field | GenAI Agent (#3) | Cluster-specific planograms |
| Mission-specific affinity rules | Rules DB | Optimizer (#6) | Rank placements per mission |
| Micro-planograms per segment × cluster | Planogram set | Store Ops | Execute cluster-specific layouts |
| Segment coverage metrics | Dashboard | Governance (#9) | Fairness / coverage checks |

### Illustrative Example

_Example — Store Formats: For a suburban family-format store, the 'weekend stock-up' mission planogram places bulk athletic wear near kids' training gear; in an urban express-format store, the 'quick trip' planogram places single-item essentials and grab-and-go accessories near checkout._

## 3.5 Enhancement #6 — Multi-Objective Optimization

### Overview & Objective

This enhancement moves the tool from single-objective (sales lift) to a multi-objective decision engine, optimizing for a weighted combination of lift, margin, inventory turn, shrink risk, and optionally sustainability. It ensures placement decisions reflect the retailer's full operational and strategic priorities.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| Product master with margin and cost | PIM / Finance | Relational table | Compute margin impact |
| Inventory turnover data | ERP / WMS | Aggregated table | Score turn contribution |
| Shrink and theft history | Loss Prevention | Table | Penalize high-shrink placements |
| Shelf-space cost proxy | Store planning | Table | Space-productivity scoring |
| Carbon footprint / logistics data (optional) | Sustainability system | Table | Sustainability weighting |
| Affinity outputs from Enhancement #1 | Affinity store | API / JSON | Candidate placements |
| Operational constraints (bay, hazmat, etc.) | Store Ops | Rules DB | Feasibility filter |
| Strategic weights | Category Mgmt config | Config file | Tune objective function |

### Processing Logic

- Ingest candidate placements produced by the affinity engine (#1).
- Enrich each candidate with margin, turn, shrink, and (optional) sustainability data.
- Define the multi-objective function using configurable weights (e.g., 0.4 lift + 0.3 margin + 0.2 turn − 0.1 shrink).
- Run a space-elasticity model to estimate sales response to facing and shelf-share changes.
- Solve the resulting constrained optimization problem via linear/mixed-integer programming or genetic algorithms.
- Rank candidate placements by composite score and compute Pareto-optimal alternatives.
- Apply guardrails, such as caps on high-margin SKU concentration and mandatory value-tier coverage.
- Publish ranked recommendations with a trade-off report for governance and category manager review.

### Techniques / Algorithms Used

- Linear Programming with PuLP
- Mixed-Integer Programming for discrete facing counts
- OR-Tools and genetic algorithms are Phase 2 candidates only
- Pareto frontier analysis for trade-off surfacing
- Space-elasticity modeling
- Weighted scoring with configurable objectives
- Guardrail rule engine

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Composite-scored recommendations | Ranked list (JSON) | GenAI Agent (#3), UI | Feed planogram design |
| Pareto-optimal alternatives | JSON set | Category Manager | Compare trade-offs |
| Trade-off analysis (lift vs margin) | Chart / table | Category leadership | Strategic sign-off |
| Weight-sensitivity report | Report | Analytics team | Tune objective weights |
| Executive summary with KPI impact | PDF / dashboard | Merchandising Head | Executive review |

### Illustrative Example

_Example — Snack vs Accessory: An MBA-only recommendation to place a high-lift, low-margin snack next to premium coffee is re-ranked lower after multi-objective scoring because it displaces a higher-margin premium accessory. The category manager sees both options with clear trade-offs and can pick based on business priority._

## 3.6 Enhancement #8 — Vendor Collaboration Module

### Overview & Objective

The Vendor Collaboration Module is a secure vendor-facing portal where CPG and brand partners upload trade promo calendars, view co-placement suggestions, and collaborate on joint category plans. It creates a structured monetization and partnership channel and closes the loop with post-execution performance sharing.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| Vendor trade promo calendar | Vendor upload | CSV / API | Align placements to promo windows |
| Vendor product catalog | Vendor upload / PIM | Table | Match vendor SKUs to retailer master |
| Vendor brand mandates | Contracts / Legal | Documents | Enforce contractual placements |
| Retailer affinity outputs | Enhancement #1 | API | Generate co-placement suggestions |
| Retailer category plans | Category Mgmt | Rules DB | Constrain vendor suggestions |
| Vendor identity and role data | IAM / Vendor Mgmt | Directory | RBAC and access control |
| Historical vendor performance | Sales analytics | Dashboard data | Show ROI post-execution |

### Processing Logic

- Vendor authenticates via secure SSO or OAuth 2.0 with role-based access.
- Vendor uploads promo calendar via the UI or a dedicated API endpoint.
- System validates schema, matches vendor SKUs against the retailer product master, and flags mismatches.
- Backend calls the affinity engine (#1) with a promo overlay to detect placement opportunities.
- The portal displays ranked co-placement suggestions with lift projections and constraints.
- Vendor and retailer collaborate on a shared placement plan with in-tool commenting and versioning.
- Approved plans flow to the planogram execution pipeline, gated by governance (#9) checks.
- Post-execution, the portal shows a performance dashboard with actual vs projected KPIs.

### Techniques / Algorithms Used

- API-Key auth with vendor-scope header check (D-029). SSO deferred (T-004).
- Role-Based Access Control (RBAC) and fine-grained permissions
- Secure API gateway with rate limiting and audit
- Schema validation and data quality checks
- Integration with affinity and optimizer services
- Dashboard rendered natively in Streamlit
- Immutable audit logging for collaboration events

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Vendor co-placement suggestion dashboard | Web UI | CPG Vendor | Review and act |
| Joint planogram plan draft | JSON / planogram | Category Manager | Approve or edit |
| Promo-performance report | Dashboard / PDF | Vendor + Retailer | Post-execution review |
| Vendor engagement metrics | KPI dashboard | Category Leadership | Manage vendor program |
| Compliance audit log | Immutable log | Governance (#9), Legal | Audit and dispute resolution |

### Illustrative Example

_Example — Summer Running Campaign: A footwear brand uploads a summer running campaign calendar. The tool recommends placing the campaign SKUs adjacent to running accessories, projecting a 22% lift during campaign weeks. The retailer approves; both sides see performance in near-real time on the shared dashboard._

## 3.7 Enhancement #9 — Explainability & Governance

### Overview & Objective

Explainability & Governance is a cross-cutting service that wraps every recommendation from the other enhancements. It attaches a plain-English rationale, evidence (lift, confidence, support), fairness checks, and policy compliance status to each output. This is essential for adoption, trust, audit, and responsible AI.

### Input Data

| Data Element | Source System | Format / Type | Purpose / Use |
|---|---|---|---|
| Recommendations and scores | Enhancements #1, #3, #4, #5, #6, #8 | API payloads | Objects to explain and govern |
| Policy rules (mandates, regulatory) | Governance config | Rule files (YAML) | Compliance checks |
| Fairness / bias thresholds | Responsible AI config | Config file | Detect skew or over-concentration |
| User feedback and override logs | UI | Event stream | Continual learning and audit |
| Model metadata | Model registry | MLflow metadata | Traceability and lineage |
| Audit log requirements | Compliance / Legal | Policy doc | Retention and format standards |

### Processing Logic

- Intercept every recommendation before it is delivered to a UI, API consumer, or execution system.
- Extract supporting evidence — lift, confidence, support, and contributing baskets or sequences.
- Run the rule-based policy engine to check violations (e.g., margin over-concentration, brand mandate breach).
- Generate a plain-English narrative using an LLM-based explanation service tightly grounded on the evidence bundle.
- Compute fairness metrics (SKU diversity, vendor equity, segment coverage).
- Log the recommendation, evidence, and policy result in an immutable audit store.
- Surface explanation and any warnings in the UI, ensuring the user can inspect and override.
- Capture overrides and downstream outcomes to feed continual learning and drift monitoring.

### Techniques / Algorithms Used

- SHAP / LIME for local model explanations
- Small pure Python policy functions
- LLM-based narrative generation grounded on evidence (RAG)
- Fairness metrics (demographic parity, equal opportunity, coverage)
- Immutable audit logging (append-only stores)
- MLOps monitoring for drift and performance degradation — Aspirational/Phase 2; no drift tool in Phase 1 dependency list
- Human-in-the-loop feedback capture

### Output

| Output Element | Format | Consumer | Downstream Action |
|---|---|---|---|
| Explanation narrative | Text block | Category Manager, Vendor | Understand and trust recommendation |
| Evidence bundle (lift / confidence / support) | JSON | UI / API consumers | Inspect rationale |
| Policy compliance flag | Enum + reason | Governance dashboard | Block or warn |
| Fairness scorecard | Dashboard | Responsible AI board | Portfolio-level oversight |
| Audit trail entry | Immutable log record | Compliance / Legal | Audit and dispute defense |
| Override analytics | Dashboard / dataset | Data Science team | Model improvement |

### Illustrative Example

_Example — Eye-Level Placement Warning: A recommendation to feature premium SKUs at eye-level is flagged with a warning: 'This may under-expose value SKUs to price-sensitive shoppers (segment coverage drop 8%).' The category manager sees the trade-off and can either accept, adjust, or override with reasoning captured for audit._

## 4. Cross-Enhancement Data Flow

The seven enhancements are not siloed — they form an integrated pipeline where outputs from one become inputs to another. The table below summarizes the primary directional data flows. This shared understanding is critical for API contract design, service ownership, and Sprint sequencing.

| Producer Enhancement | Consumer Enhancement(s) | What Is Passed |
|---|---|---|
| #1 Contextual Affinity | #3, #6, #9 | Contextual affinity rules, cannibalization matrix, RL policy |
| #4 Omnichannel Sync | #1, #5 | Unified affinity graph and cross-channel signals |
| #5 Segmentation & Mission | #3, #6 | Segment/mission-tagged rules and micro-planogram variants |
| #6 Multi-Objective Optimizer | #3, #9 | Composite-scored and Pareto-optimal placements |
| #8 Vendor Collaboration | #1, #6 (consumes) | Promo calendars and joint plans (consumes affinity/optimizer) |
| #9 Explainability & Governance | Wraps all of the above | Explanations, policy flags, and audit entries |

## 5. Consolidated Summary Table

| # | Enhancement | Primary Input | Primary Output | Primary Consumer |
|---|---|---|---|---|
| 1 | Contextual Affinity Modeling | POS + context + journeys | Contextual affinity rules & RL policy | GenAI Agent, Optimizer |
| 3 | Generative AI Planogram Designer | Affinity rules + constraints + NL query | Draft planogram with rationale | Category Manager |
| 4 | Omnichannel Affinity Sync | Clickstream + POS + identity | Unified affinity graph | Contextual Affinity, Segmentation |
| 5 | Segment & Mission-Based Placement | Loyalty + basket + store master | Micro-planograms per segment × cluster | GenAI Agent, Optimizer, Store Ops |
| 6 | Multi-Objective Optimization | Affinity + margin + turn + shrink | Composite-scored placements | GenAI Agent, Category Leadership |
| 8 | Vendor Collaboration Module | Vendor promo + affinity outputs | Co-placement suggestions & dashboards | CPG Vendors, Category Mgrs |
| 9 | Explainability & Governance | All recommendations + policies | Explanations, flags, audit trail | All users and auditors |

_Confidential — Cognizant Internal | Enhancement Deep-Dive v1.0 | July 2026_
