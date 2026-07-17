# Data Product Contract
# Store Layout (Product Placement) Optimizer Tool — Demo

_Data-as-a-Product Definition mimicking leading industry system schemas_

| Field | Value |
|---|---|
| Owner | Aditya Srivastava, Senior Consultant, Cognizant |
| Version | 1.1 |
| Date | July 2026 |
| Status | Draft for Review |
| Related Docs | Product Vision One-Pager v2, Enhancement Deep-Dive v1.0 |

---

## Version Tracking

| Version | Date | Change Type | Change Summary | Updated By |
|---|---|---|---|---|
| 1.0 | July 2026 | Baseline | Current baseline version of the Data Product Contract. | Aditya Srivastava |
| 1.1 | July 2026 | Contract Alignment Update | Updated Phase 1 demo data strategy to use data/samples/ Parquet files queried via DuckDB with FAISS vectors, excluding cloud/Postgres; clarified API contract intent that raw data-domain endpoints are internal-only access patterns and the public API surface is defined in architecture.md §7.3. | Aditya Srivastava |

**Note:** This contract defines the data required, mimicked source system schemas, transformation rules, quality gates, and consuming capabilities for the Demo build. Because this is a demo, we replicate structures from leading tools so the demo mirrors real-client data landscapes.

---

## 1. Introduction

This document operationalizes the Data-as-a-Product principle from the Product Vision One-Pager v2. It defines every data domain, the leading industry tool whose schema is mimicked, the fields, transformations, data quality gates, security posture, and which enhancement (#1, #3, #4, #5, #6, #8, #9) consumes each field. Because this build is a live demo tool intended to be shown to prospect clients, schemas intentionally mirror those of leading production systems so that the data landscape feels authentic and comparable to a real client environment.

---

## 2. Data Product Principles

- Every data domain has an identified owner, published schema, and named consumer.
- Schemas mimic leading industry systems (SAP, Oracle Retail, Adobe, Salesforce, Blue Yonder, Stibo) for demo realism.
- All data has documented quality gates, SLAs, and freshness expectations.
- Demo data is stored in **data/samples/** as Parquet, queried via DuckDB, with FAISS for vectors — no cloud/Postgres in Phase 1 (D-010, D-016, D-019).
- Strict master-transactional separation; master data governed independently.
- Every data element is traceable to a KPI, feature, or capability it enables.
- Privacy and PII compliance built-in — PII is hashed or masked; consent flags honored.
- Ready-for-consumption via versioned APIs and published contracts (semantic + syntactic).

---

## 3. Data Domain Overview

The demo tool is built on six data domains that together support the core MBA engine and all seven in-scope enhancements.

| # | Data Domain | Mimicked Leading System | Refresh Cadence | Volume (Demo) | Primary Consumer(s) |
|---|---|---|---|---|---|
| 1 | POS Transactions | Oracle Retail Xstore / NCR / SAP CAR | Near real-time (5–15 min) | ~500K transactions | Core MBA, #1, #6 |
| 2 | Product Master | SAP MDG-M / Stibo STEP / Oracle Product Hub | Daily | ~10K SKUs | Core, #3, #6 |
| 3 | Store Master | SAP Retail / Oracle Retail Merchandising | Weekly | ~50 stores | Core, #5, #8 |
| 4 | E-commerce Clickstream | Adobe Analytics / GA4 / SF Commerce Cloud | Hourly | ~2M events | #4 |
| 5 | Loyalty & Segmentation | SF Marketing Cloud / Adobe Experience Platform / SAP CDC | Daily | ~100K profiles | #4, #5 |
| 6 | Vendor Trade Promo | SAP TPM / Blue Yonder TPO | Weekly | ~200 promo events | #8 |

---

## 5. Domain Deep-Dives

The following sub-sections detail each of the six data domains — from schema to quality rules to consumers.

---

## Domain 1: POS Transactions

### 5.1.1 Overview

POS Transactions form the transactional backbone of the tool. Every basket, line item, price, discount, and payment event flows through this domain. It powers the core Market Basket Analysis and every enhancement that reasons over co-purchase behavior. This domain is sourced from the store operations business function.

### 5.1.2 Mimicked Source System

- **Leading Tool:** Oracle Retail Xstore Point-of-Service / NCR / SAP Customer Activity Repository (CAR)
- **Business Function Owner:** Store Operations / Retail Systems
- **Rationale:** Oracle Retail Xstore and SAP CAR are the reference systems for enterprise retail POS today; their schemas approximate the ARTS ODM (Association for Retail Technology Standards) retail data model, which we mimic for demo realism.

### 5.1.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| transaction_id | STRING | TXN-2026-000123 | Y | Unique transaction identifier | Oracle Xstore trans log |
| transaction_datetime | TIMESTAMP | 2026-07-05T14:32:11Z | Y | Timestamp of transaction close | SAP CAR sales audit |
| store_id | STRING | STR-0025 | Y | Store where txn occurred | Oracle Retail org hierarchy |
| register_id | STRING | REG-03 | Y | Register/POS lane ID | Xstore register master |
| cashier_id | STRING | EMP-4471 | Y | Cashier employee ID | Xstore employee link |
| customer_id | STRING | CUST-889001 | N | Loyalty customer (if identified) | SAP CDC customer master |
| loyalty_card_number | STRING | LOY-7788-2201 | N | Loyalty card number scanned | Xstore loyalty capture |
| basket_id | STRING | BSK-2026-000123 | Y | Basket ID (=txn for single-basket) | ARTS ODM Basket entity |
| line_item_seq | INT | 1 | Y | Line item sequence in basket | Xstore line item |
| sku_id | STRING | SKU-100234 | Y | SKU sold | SAP MM material |
| sku_description | STRING | Men's Running Tee — Black — M | Y | SKU short description | SAP MDG-M |
| quantity | DECIMAL(10,2) | 1.00 | Y | Quantity sold | Xstore line qty |
| unit_price | DECIMAL(10,2) | 39.99 | Y | Unit selling price | Xstore line price |
| discount_amount | DECIMAL(10,2) | 5.00 | N | Line-level discount | Xstore promo engine |
| promotion_id | STRING | PROMO-SUM26-01 | N | Applied promotion ID | SAP TPM link |
| tax_amount | DECIMAL(10,2) | 2.80 | Y | Tax on line | Xstore tax engine |
| payment_method | STRING | CARD | Y | Tender type | Xstore tender |
| currency_code | STRING | USD | Y | ISO 4217 currency | ARTS ODM |
| tender_total | DECIMAL(12,2) | 44.79 | Y | Basket-level tender total | SAP CAR |
| source_system | STRING | XSTORE_v22 | Y | Originating source system | Ingestion metadata |

### 5.1.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON (near real-time) | Kafka topic 'pos.transactions' | Every 5–15 min micro-batch | S3 raw / ADLS bronze |
| CSV (end-of-day) | SFTP batch | Nightly (backup path) | S3 raw / ADLS bronze |
| IDOC WPUBON | SAP PO/PI | Every 15 min | SAP CAR staging |

### 5.1.5 Transformations & Enrichment

- Deduplicate on (transaction_id, line_item_seq).
- Normalize timestamp to UTC and add local_datetime with store timezone.
- Enrich with product master (category hierarchy, brand, margin).
- Enrich with store master (cluster, format, region).
- Compute basket-level aggregates (basket_size, unique_sku_count, basket_value).
- Hash customer_id and loyalty_card_number for PII compliance.

### 5.1.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-POS-01 | transaction_id must be unique | Critical | Reject record + alert |
| DQ-POS-02 | transaction_datetime not null and within retention window | Critical | Reject |
| DQ-POS-03 | sku_id must exist in Product Master | High | Quarantine to review queue |
| DQ-POS-04 | store_id must exist in Store Master | High | Quarantine |
| DQ-POS-05 | quantity > 0 and unit_price >= 0 | Medium | Flag for review |
| DQ-POS-06 | tender_total = sum(lines) ± 0.01 | Medium | Reconciliation exception |

### 5.1.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| Core MBA | basket_id, sku_id, quantity | Association rules (lift, confidence, support) |
| #1 Contextual Affinity | transaction_datetime, promotion_id, store_id | Context-aware affinity, sequence mining |
| #6 Multi-Objective Optimizer | unit_price, discount_amount (via margin) | Margin-weighted lift score |
| #9 Explainability | basket_id, sku_id | Evidence backing every recommendation |

### 5.1.8 Ownership & SLA

- **Data Owner:** Retail Systems Lead (Store Ops)
- **Steward:** POS Data Steward
- **SLA** — Freshness: 15 min | Completeness: 99.5% | Availability: 99.9%
- **Retention:** 3 years hot, 7 years cold

---

## Domain 2: Product Master

### 5.2.1 Overview

Product Master is the golden record for every SKU sold. It underpins category-based reasoning, margin-based optimization, and brand/vendor constraints. Source from the Merchandising / PICC business function.

### 5.2.2 Mimicked Source System

- **Leading Tool:** SAP MDG-M (Master Data Governance – Material) / Stibo STEP / Oracle Product Hub
- **Business Function Owner:** Merchandising / Product Innovation & Consumer Creation (PICC)
- **Rationale:** SAP MDG-M is the de-facto master data governance system for large retailers running SAP; Stibo STEP is the leading PIM for multi-channel product data. Their combined schema provides the richest realistic reference for demo.

### 5.2.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| sku_id | STRING | SKU-100234 | Y | Internal SKU key | SAP MM MATNR |
| gtin_upc | STRING | 0194953012345 | Y | Global Trade Item Number | GS1 standard via Stibo STEP |
| product_name | STRING | Men's Running Tee | Y | Marketing product name | Stibo STEP |
| brand | STRING | AeroFit | Y | Brand name | SAP MDG-M attribute |
| category_l1 | STRING | Apparel | Y | Category level 1 | Merch hierarchy |
| category_l2 | STRING | Men's | Y | Category level 2 | Merch hierarchy |
| category_l3 | STRING | Running Tops | Y | Category level 3 | Merch hierarchy |
| department | STRING | Sportswear | Y | Department | SAP Retail Article Hierarchy |
| color | STRING | Black | N | Color attribute | Stibo STEP |
| size | STRING | M | N | Size attribute | Stibo STEP variant model |
| gender | STRING | Men | N | Gender segment | PIM attribute |
| pack_size | DECIMAL(6,2) | 1.00 | Y | Selling pack size | SAP MM |
| unit_of_measure | STRING | EA | Y | UoM (ISO) | SAP MM MEINS |
| unit_cost | DECIMAL(10,2) | 14.50 | Y | Landed cost per unit | SAP FI/CO valuation |
| unit_price_msrp | DECIMAL(10,2) | 39.99 | Y | MSRP | SAP SD condition |
| margin_pct | DECIMAL(5,2) | 63.74 | Y | Gross margin % | Derived |
| supplier_id | STRING | VEND-2201 | Y | Primary supplier | SAP MM vendor link |
| country_of_origin | STRING | VN | N | ISO country | GTIN/customs data |
| dimensions_lwh | STRING | 30x25x2 cm | N | Product dimensions | Stibo STEP |
| weight | DECIMAL(6,3) | 0.180 | N | Weight in kg | Stibo STEP |
| sustainability_score | DECIMAL(3,1) | 7.5 | N | 0–10 ESG score | Retailer-computed |
| lifecycle_status | STRING | Active | Y | Active / EOL / NPI | SAP MDG-M lifecycle |
| created_date | DATE | 2025-11-01 | Y | Master creation date | SAP MM |
| last_updated | DATE | 2026-06-30 | Y | Last change date | SAP MDG-M |
| source_system | STRING | SAP_MDGM_v3 | Y | Source system | Ingestion metadata |

### 5.2.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON | REST API pull nightly | Daily 02:00 UTC | S3 raw / ADLS bronze |
| IDOC MATMAS | SAP PO/PI | On-change publish | SAP interface staging |
| CSV | SFTP (Stibo STEP export) | Daily | Landing zone |

### 5.2.5 Transformations & Enrichment

- Deduplicate on sku_id keeping latest last_updated.
- Standardize category hierarchy to internal 3-level taxonomy.
- Compute margin_pct = (unit_price_msrp - unit_cost) / unit_price_msrp.
- Enrich brand with brand family and vendor mapping.
- Flag SKUs with missing dimensions for shelf-space modeling exceptions.
- Publish only lifecycle_status IN (Active, NPI) to consumable layer.

### 5.2.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-PM-01 | sku_id + gtin_upc uniqueness | Critical | Reject + alert MDM steward |
| DQ-PM-02 | Mandatory fields present (see schema) | Critical | Reject |
| DQ-PM-03 | unit_cost <= unit_price_msrp | High | Flag for merch review |
| DQ-PM-04 | category_l1/l2/l3 aligned to taxonomy | High | Quarantine |
| DQ-PM-05 | Margin within category bounds (5–90%) | Medium | Flag |
| DQ-PM-06 | Lifecycle_status transitions valid | Low | Warn only |

### 5.2.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| Core | sku_id, category_l1/l2/l3 | Rule mining scope |
| #3 GenAI Planogram | category, brand, dimensions | Category rules + fixture fit |
| #6 Multi-Objective | margin_pct, unit_cost, sustainability_score | Multi-objective score |
| #9 Explainability | brand, category | Bias & fairness checks (vendor equity) |

### 5.2.8 Ownership & SLA

- **Data Owner:** Head of Merchandising / PICC
- **Steward:** Product Master Steward
- **SLA** — Freshness: 24h | Completeness: 99% | Availability: 99.9%
- **Retention:** Indefinite (governed)

---

## Domain 3: Store Master

### 5.3.1 Overview

Store Master describes every physical selling location — its format, size, cluster, and demographic context. It is the anchor for store-cluster-based micro-planograms and vendor-targeted co-placement plans. Sourced from Retail Operations.

### 5.3.2 Mimicked Source System

- **Leading Tool:** SAP Retail (SAP for Retail) / Oracle Retail Merchandising (RMS)
- **Business Function Owner:** Retail Operations / Store Operations
- **Rationale:** SAP Retail and Oracle RMS are the leading enterprise store master systems; their organizational hierarchies and location attributes are widely adopted and provide a realistic reference schema.

### 5.3.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| store_id | STRING | STR-0025 | Y | Unique store identifier | SAP T001W / Oracle RMS LOC |
| store_name | STRING | Downtown Flagship | Y | Store display name | SAP T001W |
| store_format | STRING | Flagship | Y | Flagship/Express/Outlet | Oracle RMS location trait |
| store_cluster | STRING | Metro-Premium | Y | Analytical cluster | Retail analytics |
| banner | STRING | AeroFit | Y | Retail banner | SAP retail banner |
| address_line | STRING | 123 Market St | Y | Street address | SAP address |
| city | STRING | San Francisco | Y | City | SAP address |
| state | STRING | CA | Y | State / region code | ISO 3166-2 |
| postal_code | STRING | 94103 | Y | Postal code | SAP address |
| country_code | STRING | US | Y | ISO country code | ISO 3166-1 |
| latitude | DECIMAL(9,6) | 37.774929 | Y | Latitude | Geocoded |
| longitude | DECIMAL(9,6) | -122.419418 | Y | Longitude | Geocoded |
| region | STRING | West | Y | Reporting region | Oracle RMS hierarchy |
| total_sqft | INT | 18000 | Y | Total footprint | Facilities |
| selling_sqft | INT | 12500 | Y | Selling area | Facilities |
| open_date | DATE | 2019-04-12 | Y | Store open date | SAP store |
| fixture_count | INT | 220 | Y | # fixtures for planogram | Facilities / VM |
| planogram_version | STRING | PGM-2026-Q3 | Y | Active planogram version | Space planning |
| operating_hours | STRING | Mon-Sun 09-21 | Y | Standard hours | SAP retail |
| climate_zone | STRING | Temperate-Coastal | N | Climate context | Enrichment |
| demographic_cluster | STRING | Urban-High-Income | Y | Demographic overlay | Analytics |
| source_system | STRING | SAP_RETAIL_v6 | Y | Source | Ingestion metadata |

### 5.3.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON | REST API pull weekly | Weekly Sundays | S3 raw / ADLS bronze |
| IDOC WBBDLD | SAP PO/PI | On change | Interface staging |
| CSV | SFTP | Weekly | Landing zone |

### 5.3.5 Transformations & Enrichment

- Deduplicate on store_id keeping most recent record.
- Geocode address if latitude/longitude missing.
- Assign store_cluster via clustering job (k-means on format+demographic+sales).
- Enrich demographic_cluster from external market data.
- Compute selling_sqft ratio and shelf-space capacity per fixture.
- Publish to consumable layer with cluster tags.

### 5.3.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-STR-01 | store_id unique | Critical | Reject + alert |
| DQ-STR-02 | Mandatory address fields present | Critical | Reject |
| DQ-STR-03 | Latitude/longitude within valid ranges | High | Flag for geocoding |
| DQ-STR-04 | selling_sqft <= total_sqft | High | Flag |
| DQ-STR-05 | planogram_version references valid version | Medium | Warn |
| DQ-STR-06 | Cluster assignments cover 100% of stores | Medium | Trigger reclustering |

### 5.3.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| Core | store_id, store_cluster | Store-scoped rule mining |
| #5 Segment & Mission | store_cluster, demographic_cluster | Micro-planogram per cluster |
| #8 Vendor Collaboration | store_cluster, banner | Vendor-targeted co-placement |
| #9 Explainability | store_cluster | Segment coverage fairness checks |

### 5.3.8 Ownership & SLA

- **Data Owner:** Head of Store Operations
- **Steward:** Store Master Steward
- **SLA** — Freshness: 7 days | Completeness: 99.5% | Availability: 99.9%
- **Retention:** Indefinite

---

## Domain 4: E-commerce Clickstream

### 5.4.1 Overview

Clickstream captures every meaningful digital shopper interaction — page views, PDP visits, add-to-cart, purchases, wishlists. It is the fuel for the omnichannel affinity graph (#4), providing browse-based affinity signals that complement in-store baskets. Sourced from the Digital business function.

### 5.4.2 Mimicked Source System

- **Leading Tool:** Adobe Analytics (Data Feed) / Google Analytics 4 (BigQuery export) / Salesforce Commerce Cloud
- **Business Function Owner:** Digital / E-commerce
- **Rationale:** Adobe Analytics and GA4 dominate enterprise digital analytics; their data-feed schemas are the industry reference for clickstream. Salesforce Commerce Cloud (Demandware) is widely used in specialty retail.

### 5.4.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| event_id | STRING | EVT-9982-0001 | Y | Unique event ID | Adobe Analytics eVar |
| event_timestamp | TIMESTAMP | 2026-07-05T14:22:00Z | Y | Server-side event time | GA4 event_timestamp |
| session_id | STRING | SES-778-441 | Y | Session identifier | Adobe / GA4 session |
| user_id | STRING | USR-889001 | N | Site user (if signed-in) | Commerce Cloud |
| loyalty_id | STRING | LOY-7788-2201 | N | Linked loyalty ID | Identity resolution |
| device_type | STRING | Mobile | Y | Device class | GA4 device.category |
| browser | STRING | Chrome | Y | Browser name | GA4 device.web_info |
| page_url | STRING | /men/running/tees | Y | Page URL path | Adobe pagename |
| page_type | STRING | PLP | Y | PDP/PLP/Home/Cart/Checkout | Commerce Cloud |
| event_type | STRING | view | Y | view/click/add_to_cart/purchase/wishlist | GA4 event_name |
| product_id | STRING | SKU-100234 | N | Product interacted with | GA4 items.item_id |
| product_category | STRING | Men's Running Tops | N | Category hit | Adobe custom |
| quantity | INT | 1 | N | Qty (for cart/purchase) | GA4 items.quantity |
| search_term | STRING | running tee | N | Site search term | Adobe search eVar |
| referrer | STRING | google.com | N | Traffic referrer | GA4 traffic_source |
| utm_source | STRING | email | N | Marketing source | GA4 UTM |
| utm_campaign | STRING | summer26 | N | Marketing campaign | GA4 UTM |
| geo_country | STRING | US | Y | Geo country | GA4 geo.country |
| geo_city | STRING | San Francisco | N | Geo city | GA4 geo.city |
| source_system | STRING | GA4_BQ_EXPORT | Y | Source | Ingestion metadata |

### 5.4.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON (BigQuery export) | GA4 → BQ → landing pull | Hourly | GCS / S3 landing |
| Adobe Data Feed (TSV) | SFTP | Hourly | S3 landing |
| Kafka topic 'digital.events' | Streaming | Real-time | Bronze layer |

### 5.4.5 Transformations & Enrichment

- Normalize event_type to a controlled vocabulary.
- Perform identity resolution: user_id → loyalty_id via CDP.
- Sessionize events (30-min inactivity) and derive session-level metrics.
- Map product_id (site SKU) to product master sku_id via cross-reference.
- Aggregate to product-affinity edges (co-view, co-cart, co-purchase).
- Anonymize IP and honor consent flags before publishing.

### 5.4.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-CS-01 | event_id unique per source per day | Critical | Reject |
| DQ-CS-02 | event_timestamp within tolerance (±2h) | High | Quarantine |
| DQ-CS-03 | Consent flags respected | Critical | Drop event |
| DQ-CS-04 | product_id resolves to Product Master | High | Flag unmapped |
| DQ-CS-05 | Bot traffic filtered (IAB spiders/bots list) | Medium | Exclude |
| DQ-CS-06 | Session length < 6h | Low | Split session |

### 5.4.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| #4 Omnichannel Affinity | event_type, product_id, session_id, loyalty_id | Cross-channel affinity graph |
| #4 Omnichannel Affinity | search_term | Search-to-shelf intent signal |
| #5 Segment & Mission | loyalty_id, event_type patterns | Digital-behavior segment features |
| #9 Explainability | event_id | Traceability for omnichannel recs |

### 5.4.8 Ownership & SLA

- **Data Owner:** Head of Digital / E-commerce
- **Steward:** Digital Analytics Steward
- **SLA** — Freshness: 1h | Completeness: 98% | Availability: 99.5%
- **Retention:** 25 months (aligned to GA4 default) hot, 5 yrs cold

---

## Domain 5: Loyalty & Customer Segmentation

### 5.5.1 Overview

Loyalty & Segmentation stores the unified customer profile — tier, RFM, mission, LTV, channel preference, and consent flags. It is the foundation for mission-based placement (#5) and omnichannel identity resolution (#4). Sourced from Customer Success / CRM.

### 5.5.2 Mimicked Source System

- **Leading Tool:** Salesforce Marketing Cloud (Customer 360) / Adobe Experience Platform (XDM) / SAP Customer Data Cloud (CDC)
- **Business Function Owner:** Customer Success / CRM / Non-Frontline CSE
- **Rationale:** SFMC and Adobe Experience Platform (with XDM Individual Profile schema) are the leading CDPs; SAP CDC provides consent and identity. Together they represent the most realistic reference for a retail loyalty & profile data product.

### 5.5.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| customer_id | STRING | CUST-889001 | Y | Golden customer ID | CDP master |
| loyalty_id | STRING | LOY-7788-2201 | Y | Loyalty program ID | SFMC loyalty extension |
| hashed_email | STRING | sha256:ab12… | Y | Hashed email (SHA-256) | SAP CDC identity |
| hashed_phone | STRING | sha256:cd34… | N | Hashed phone | SAP CDC identity |
| enrollment_date | DATE | 2023-03-14 | Y | Loyalty enrollment | SFMC |
| tier | STRING | Gold | Y | Silver/Gold/Platinum | SFMC loyalty |
| lifetime_value | DECIMAL(12,2) | 2450.75 | Y | Predicted or observed LTV | Analytics |
| recency_score | INT | 4 | Y | RFM R (1-5) | Analytics |
| frequency_score | INT | 5 | Y | RFM F (1-5) | Analytics |
| monetary_score | INT | 4 | Y | RFM M (1-5) | Analytics |
| rfm_segment | STRING | Champions | Y | Named RFM cluster | Analytics |
| primary_mission | STRING | Stock-Up | Y | Dominant shopper mission | Mission classifier |
| preferred_channel | STRING | Omni | Y | store / web / app / omni | CDP behavior |
| preferred_store_id | STRING | STR-0025 | N | Most-visited store | POS-derived |
| demographic_cluster | STRING | Urban-Family | Y | Demographic segment | Enrichment |
| age_band | STRING | 30-39 | N | Age band (privacy-safe) | CDP |
| consent_marketing | BOOLEAN | true | Y | Marketing consent | SAP CDC consent |
| consent_analytics | BOOLEAN | true | Y | Analytics consent | SAP CDC consent |
| last_visit_date | DATE | 2026-07-02 | Y | Last transaction/visit | POS/CDP |
| source_system | STRING | SFMC_C360_v4 | Y | Source | Ingestion metadata |

### 5.5.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON | REST API pull daily | Daily 03:00 UTC | S3 raw / ADLS bronze |
| Adobe XDM (Parquet) | AEP Data Lake export | Daily | ADLS bronze |
| CSV (SAP CDC consent) | SFTP | Daily | Landing zone |

### 5.5.5 Transformations & Enrichment

- Identity stitch across SFMC, AEP, SAP CDC using deterministic + probabilistic matching.
- Compute or refresh RFM scores from POS transactions.
- Run mission-classification model (XGBoost) to assign primary_mission.
- Compute LTV via predictive model (BG/NBD + Gamma-Gamma).
- Enforce consent: drop marketing profile if consent_marketing=false.
- Publish to consumable layer with only hashed PII.

### 5.5.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-LOY-01 | customer_id unique | Critical | Reject / merge candidate |
| DQ-LOY-02 | Consent flags present | Critical | Reject profile |
| DQ-LOY-03 | No plaintext PII in outbound layer | Critical | Block publish |
| DQ-LOY-04 | RFM scores in [1,5] | High | Recompute |
| DQ-LOY-05 | Mission label from allowed set | Medium | Reclassify |
| DQ-LOY-06 | LTV within plausible range | Low | Flag anomaly |

### 5.5.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| #4 Omnichannel Affinity | loyalty_id, hashed_email | Identity resolution across channels |
| #5 Segment & Mission | rfm_segment, primary_mission, demographic_cluster | Mission-based micro-planograms |
| #5/#6 Weighted lift | lifetime_value | LTV-weighted lift scoring |
| #9 Explainability | consent flags, tier | Fairness & consent-aware recommendations |

### 5.5.8 Ownership & SLA

- **Data Owner:** Head of Customer / CRM
- **Steward:** Loyalty Data Steward
- **SLA** — Freshness: 24h | Completeness: 98% | Availability: 99.5%
- **Retention:** Per privacy policy (typically 24 months after last activity)

---

## Domain 6: Vendor Trade Promo

### 5.6.1 Overview

Vendor Trade Promo captures the joint promotional calendar between the retailer and its CPG/brand vendors — including promo type, SKUs involved, funding, and targeted store clusters. It powers the Vendor Collaboration Module (#8). Sourced from Vendor Management / Trade Marketing.

### 5.6.2 Mimicked Source System

- **Leading Tool:** SAP Trade Promotion Management (TPM) / Blue Yonder Trade Promotion Optimization (TPO)
- **Business Function Owner:** Vendor Management / Trade Marketing
- **Rationale:** SAP TPM and Blue Yonder TPO are the reference systems for CPG-retailer trade promo planning; their schemas cover funding, SKUs, timing, and store targeting comprehensively.

### 5.6.3 Schema Definition (Mimicked)

| Field Name | Data Type | Sample Value | Mandatory | Description | Mimicked From |
|---|---|---|---|---|---|
| promo_id | STRING | PROMO-SUM26-01 | Y | Unique promo ID | SAP TPM promo header |
| vendor_id | STRING | VEND-2201 | Y | Vendor / supplier ID | SAP vendor master |
| vendor_name | STRING | AeroFit Brands Inc. | Y | Vendor name | SAP vendor master |
| promo_name | STRING | Summer Running 2026 | Y | Marketing promo name | TPM |
| promo_type | STRING | Endcap | Y | TPR/BOGO/Bundle/Display/Endcap | TPM promo type |
| start_date | DATE | 2026-07-15 | Y | Promo start | TPM validity |
| end_date | DATE | 2026-08-15 | Y | Promo end | TPM validity |
| promo_status | STRING | Approved | Y | Planned/Approved/Live/Closed | TPM workflow |
| participating_sku_id | STRING | SKU-100234 | Y | SKU in promo | TPM sku list |
| discount_type | STRING | % | Y | % or absolute | TPM |
| discount_value | DECIMAL(6,2) | 20.00 | Y | Discount amount | TPM |
| funding_type | STRING | Co-op | Y | vendor/retailer/co-op | TPM funding |
| funding_amount | DECIMAL(12,2) | 15000.00 | Y | Committed funding | TPM |
| targeted_store_cluster | STRING | Metro-Premium | Y | Target cluster | TPM store target |
| targeted_segment | STRING | Champions | N | Target customer segment | TPM extension |
| expected_lift_pct | DECIMAL(5,2) | 22.00 | Y | Vendor-forecast lift | TPO forecast |
| placement_type | STRING | Endcap | Y | aisle/endcap/entry/checkout | TPM placement |
| approval_status | STRING | Approved | Y | Workflow status | TPM |
| source_system | STRING | SAP_TPM_v5 | Y | Source | Ingestion metadata |

### 5.6.4 Data Source & Ingestion

| Source Format | Ingestion Mechanism | Frequency | Landing Zone |
|---|---|---|---|
| JSON | Vendor Portal REST API (upload) | On submission | Landing (vendor scope) |
| IDOC PROMO05 | SAP PO/PI | Weekly batch | SAP interface staging |
| CSV | SFTP (vendor upload) | Weekly | Landing zone |

### 5.6.5 Transformations & Enrichment

- Validate SKUs against Product Master; reject unknown SKUs.
- Map vendor_id to internal vendor master.
- Validate date ranges (start<end, within planning horizon).
- Enrich with expected in-store affinity partner SKUs (from #1).
- Compute vendor-scoped visibility (row-level security per vendor).
- Publish to consumable layer with vendor scope tags.

### 5.6.6 Data Quality Rules

| Rule ID | Rule Description | Severity | Action on Failure |
|---|---|---|---|
| DQ-VP-01 | promo_id unique | Critical | Reject |
| DQ-VP-02 | All participating SKUs exist | Critical | Reject promo |
| DQ-VP-03 | funding_amount > 0 | High | Flag |
| DQ-VP-04 | targeted_store_cluster valid | High | Reject |
| DQ-VP-05 | Vendor scope isolation enforced | Critical | Block cross-vendor read |
| DQ-VP-06 | expected_lift_pct within [0,100] | Medium | Flag |

### 5.6.7 Consuming Capabilities

| Consumer (Enhancement #) | Fields Used | KPI / Feature Driven |
|---|---|---|
| #8 Vendor Collaboration | All | Vendor portal dashboards & co-placement |
| #1 Contextual Affinity | promo_id (join to POS) | Promo-state context feature |
| #6 Multi-Objective | funding_amount, expected_lift_pct | Promo-aware optimization |
| #9 Explainability | vendor_id, promo_id | Vendor equity fairness checks |

### 5.6.8 Ownership & SLA

- **Data Owner:** Head of Vendor Management / Trade Marketing
- **Steward:** Vendor Data Steward
- **SLA** — Freshness: 7 days | Completeness: 99% | Availability: 99.5%
- **Retention:** 5 years

---

## 6. Data-to-KPI Traceability Matrix

This matrix makes every data element accountable to a KPI, capability, and consumer — supporting the Data-as-a-Product principle.

| Data Domain | Key Field(s) | Feature / Capability Enabled | KPI Impacted | Consumer Enhancement |
|---|---|---|---|---|
| POS Transactions | basket_id, sku_id | Association rule mining | Sales lift %, precision@k | Core, #1 |
| POS Transactions | transaction_datetime, promotion_id | Contextual affinity | Contextual lift, time-of-day pattern | #1 |
| Product Master | margin_pct, unit_cost | Multi-objective scoring | Margin uplift % | #6 |
| Product Master | category_l1/l2/l3 | Category rules & adjacency | Category adherence, planogram quality | #3 |
| Store Master | store_cluster, demographic_cluster | Cluster-based micro-planogram | Segment coverage % | #5 |
| Clickstream | event_type, product_id | Online-offline affinity graph | Cross-channel lift | #4 |
| Clickstream | search_term | Intent signal for placement | Search-to-shelf conversion | #4 |
| Loyalty | rfm_segment, primary_mission | Mission-based planogram | Basket size uplift | #5 |
| Loyalty | lifetime_value | Segment weighting | LTV-weighted lift | #5, #6 |
| Vendor Promo | expected_lift_pct, promo_type | Vendor co-placement suggestion | Vendor engagement, promo ROI | #8 |
| Vendor Promo | funding_amount | Promo-aware optimization | Trade funding efficiency | #6, #8 |
| All | Any recommendation output | Explainability narrative | Adoption, trust, override rate | #9 |

---

## 7. Demo Data Strategy

Because this is a demo tool intended to be showcased to prospect clients, the data must feel authentic while remaining fully synthetic and privacy-safe. We assume a Global sports apparel retailer context to align with the primary demo storyline.

Data will be generated using Python (Faker + custom distributions) with realistic seasonality, mission-mix, category hierarchies, and vendor mixes. Generated data lands in **data/samples/** as Parquet, is queried via DuckDB, uses FAISS for vectors, and excludes cloud/Postgres in Phase 1 (D-010, D-016, D-019).

Data seeding pipeline: generator scripts → landing zone → ingestion API → bronze → silver → gold consumable layer → API/serving layer.

| Domain | Synthetic Records | Realism Techniques | Refresh in Demo |
|---|---|---|---|
| POS Transactions | ~500,000 line items | Basket composition sampled from real MBA patterns; seasonality & daypart curves | Continuous (streamed via Kafka simulator) |
| Product Master | ~10,000 SKUs | Realistic category tree (Apparel/Footwear/Accessories); brand/vendor mix; margin distributions | Daily snapshot |
| Store Master | 50 stores | Multiple formats & clusters; realistic geocoding across US/EU regions | Weekly snapshot |
| Clickstream | ~2,000,000 events | Session models per persona; PDP→cart→purchase funnels; UTM mix | Hourly stream |
| Loyalty & Segmentation | ~100,000 profiles | RFM distribution; mission labels; consent flags; hashed PII | Daily refresh |
| Vendor Trade Promo | ~200 promos | Seasonal calendar (Summer Running, Back-to-School, Holiday); co-op funding mix | Weekly refresh |

---

## 8. API Contracts (Summary)

All data is exposed to consuming services via versioned REST APIs; every consumer authenticates via OAuth 2.0. Vendor-scoped endpoints add a vendor scope claim for row-level isolation.

| API Endpoint | Method | Payload Format | Consumer | Auth |
|---|---|---|---|---|
| /api/v1/pos/transactions | GET | JSON | Core MBA engine, #1, #6 | OAuth 2.0 |
| /api/v1/product/master | GET | JSON | All | OAuth 2.0 |
| /api/v1/store/master | GET | JSON | Core, #5, #8 | OAuth 2.0 |
| /api/v1/clickstream/events | GET | JSON | #4 | OAuth 2.0 |
| /api/v1/loyalty/profile | GET | JSON | #4, #5 | OAuth 2.0 + PII scope |
| /api/v1/vendor/promo | GET / POST | JSON | #8 | OAuth 2.0 + vendor scope |
| /api/v1/recommendations | GET | JSON | UI, #9 | OAuth 2.0 |
| /api/v1/explanations | GET | JSON | UI | OAuth 2.0 |

---

## 9. Security, Privacy & Compliance

- **PII masking:** email and phone are SHA-256 hashed; no plaintext PII crosses domain boundaries.
- **GDPR / CCPA readiness:** consent flags honored, right-to-erasure via customer_id purge.
- **RBAC & ABAC:** role-based access + vendor-scoped attribute isolation for #8.
- **Secrets management:** cloud secret manager (AWS Secrets Manager / Azure Key Vault).
- **Audit logs:** immutable append-only log for every data access and recommendation delivery.
- **Encryption:** AES-256 at rest, TLS 1.3 in transit.
- **Vendor scope isolation:** vendors can only read their own promo & performance data.
- **Consent-aware consumption:** services must inspect consent flags before using loyalty data.

---

## 10. Ownership & Governance

| Role | Responsibility |
|---|---|
| Data Product Owner (Aditya Srivastava) | Overall contract, roadmap, cross-domain alignment |
| Domain Data Stewards | Schema integrity, quality gates, SLA per domain |
| Data Engineering Lead | Pipelines, APIs, ingestion, transformations |
| ML / Analytics Lead | Consumer readiness for enhancements #1, #3, #4, #5, #6 |
| Security & Privacy Officer | PII, consent, encryption, audit |
| Vendor Liaison | Vendor onboarding, portal support, scope validation for #8 |

---

## 11. Versioning & Change Log

| Version | Date | Author | Change Summary |
|---|---|---|---|
| v0.1 | Jun 2026 | Aditya Srivastava | Initial draft — domain identification & scope |
| v1.0 | Jul 2026 | Aditya Srivastava | First finalized version aligning with Product Vision v2 and Enhancement Deep-Dive v1.0 |

---

_Confidential — Cognizant Internal | Data Product Contract v1.0 | July 2026_
