# 🧾 Sprint 2A Backlog — #1 Contextual Affinity Modeling

> **Purpose:** The reviewable backlog for Sprint 2A. Defines the user stories, acceptance criteria, and test cases development must satisfy. Per `CLAUDE.md`, Sprint 2A code must implement exactly these stories once locked — no scope creep, no partial delivery.
>
> **Split note:** Original Sprint 2 (#1 + #6) was split into **Sprint 2A (#1 Contextual Affinity)** and **Sprint 2B (#6 Multi-Objective Optimization)** per `decision_log.md` D-038. This is the 2A half; 2B is `sprint_2b_backlog.md`.
>
> **Review gate:** Reviewed and approved by the owner **before** coding. Post-lock changes require a new `decision_log.md` entry.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Sprint Backlog (User Stories · Acceptance Criteria · Test Cases) |
| **Sprint** | Sprint 2A — Contextual Affinity Modeling (#1) |
| **Status** | 🔍 Draft for Owner Review |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 23 July 2026 |
| **Related Docs** | `architecture.md` §4.1 (contextual) · `Enhancement_DeepDive` §3.1 · `decision_log.md` D-025, D-036 (T-014), D-037, D-038 · `governance_charter.md` |

---

## 1. Sprint 2A Scope

Makes the Sprint 1 MBA core **context-aware** and adds **negative-association (cannibalization) detection**, plus the T-014 quality guard. Every recommendation still passes through governance (#9, principle #5).

**In scope:**
1. Synthesized **weather** signal (per store × day) behind a `WeatherProvider` seam (D-037).
2. Basket **context enrichment** — time-of-day band, day type, weather bucket, promo flag.
3. **Context-aware affinity mining** — recommendations change with the chosen context.
4. **Negative-association (cannibalization) detection** — pairs bought together less than chance.
5. **Minimum-supporting-baskets guard** (T-014).
6. API + UI wiring for context selection (the "weather changes the recommendations" demo moment).

**Explicitly OUT of scope for Sprint 2A** (do NOT build):
- ❌ Multi-objective scoring (margin/turn/shrink) — that's **Sprint 2B (#6)**.
- ❌ Sequence mining (PrefixSpan / SPADE) — deferred (owner-selected lean depth).
- ❌ Contextual-bandit / RL self-learning (LinUCB / Thompson) — deferred.
- ❌ Live weather API — Phase 2 (T-015); 2A uses a synthesized provider (D-037).
- ❌ #4/#5/#3/#8 (later sprints).

---

## 2. Personas

| Persona | Role in Sprint 2A |
|---------|-------------------|
| **Category Manager** | Selects context (time/weather/promo), reads context-aware recommendations and cannibalization flags |
| **Data Steward / Admin** | Confirms contextual and negative-association outputs are still governed and audited |

## 3. Definition of Ready / Done

**Ready:** persona + value + Given/When/Then acceptance criteria + ≥1 test case; no dependency on an out-of-scope item.
**Done:** acceptance criteria pass; unit + integration tests; `ruff` clean; type hints + docstrings; **every recommendation routes through `governance.govern()`**; CI green; journal entry filed.

---

# 4. User Stories

Story IDs `US-2A.x`; test IDs `TC-2A.x.y` (unit `U`, integration `I`).

### US-2A.1 — Weather via a provider seam (synthetic default + optional live Open-Meteo)

> **As a** Data Steward, **I want** weather behind a `WeatherProvider` interface with a local default and an opt-in live source, **so that** contextual affinity has a weather input that is offline-safe and demo-controllable, but can use real data when a network is available.

**Acceptance Criteria (revised per D-037):**
- **AC1** — `SyntheticWeatherProvider` (the **default**) returns a deterministic weather bucket (from a known set, e.g. sunny/rainy/cold/hot/mild) for a given store × date.
- **AC2** — `LiveWeatherProvider` (**opt-in** via config flag) fetches weather from the free, key-less **Open-Meteo** API and **falls back to the synthetic provider on any failure** (offline, proxy block, timeout, parse error) — the demo never breaks.
- **AC3** — The live provider trusts the corporate (Zscaler) root CA via the OS trust store (`truststore`); `verify=False` is never used.
- **AC4** — POS baskets can be enriched with the weather bucket for their store/date; deterministic under the synthetic default; `data_contract.md` updated for the new field.

**Test Cases:**
- **TC-2A.1.1 (U)** — Synthetic bucket is deterministic for a given (store, date) across two runs.
- **TC-2A.1.2 (U)** — Providers only return buckets from the known set.
- **TC-2A.1.3 (U)** — When the live call raises, `LiveWeatherProvider` falls back to a synthetic bucket (no exception propagates).

### US-2A.2 — Enrich baskets with context features

> **As a** Category Manager, **I want** baskets tagged with time-of-day, day type, weather, and promo, **so that** affinities can be computed per context.

**Acceptance Criteria:**
- **AC1** — A pure, typed function derives `hour_band`, `day_type` (weekday/weekend) from `transaction_datetime`, `promo_flag` from `promotion_id`, and `weather_bucket` from the `WeatherProvider`.
- **AC2** — Missing/invalid inputs degrade gracefully (no crash).

**Test Cases:**
- **TC-2A.2.1 (U)** — A known timestamp maps to the expected hour band and day type.
- **TC-2A.2.2 (U)** — A row with a `promotion_id` yields `promo_flag=True`; without, `False`.

### US-2A.3 — Context-aware recommendations

> **As a** Category Manager, **I want** recommendations to reflect a chosen context, **so that** advice differs by weekend vs weekday or rainy vs sunny.

**Acceptance Criteria:**
- **AC1** — `get_recommendations` accepts a `context` (e.g. `{time_of_day, day_type, weather, promo}`); baskets are sliced to that context before mining.
- **AC2** — `Recommendation.context` records the context used.
- **AC3** — Two different contexts on the same data can produce different rankings (demonstrable).
- **AC4** — No context supplied → Sprint 1 baseline behaviour (backward compatible).
- **AC5** — Contextual recommendations still pass through `govern()`.

**Test Cases:**
- **TC-2A.3.1 (U)** — A pair that co-occurs only on weekends ranks higher under `day_type=weekend` than `weekday`.
- **TC-2A.3.2 (U)** — `context` is populated on returned recommendations.
- **TC-2A.3.3 (I)** — Contextual results are all `GovernedRecommendation`.

### US-2A.4 — Negative-association (cannibalization) detection

> **As a** Category Manager, **I want** to see pairs bought together *less* than chance, **so that** I avoid placing cannibalizing products side by side.

**Acceptance Criteria:**
- **AC1** — The engine surfaces **negative associations** (lift below a configurable threshold < 1) as a distinct, clearly-labelled result set (not mixed into positive recommendations).
- **AC2** — Each carries lift/confidence/support and a plain-English "avoid co-placement" rationale via governance.
- **AC3** — Negative associations are governed and audited.

**Test Cases:**
- **TC-2A.4.1 (U)** — An anti-correlated pair (lift < 1) is returned as a negative association; an independent pair (lift ≈ 1) is not.
- **TC-2A.4.2 (U)** — The rationale reads as an avoid/cannibalization message.

### US-2A.5 — Minimum-supporting-baskets guard (T-014)

> **As a** Category Manager, **I want** recommendations backed by too few baskets excluded, **so that** context slicing never surfaces implausible one-basket "50×" lifts.

**Acceptance Criteria:**
- **AC1** — A configurable `min_supporting_baskets` threshold excludes rules below it.
- **AC2** — Applies to store-filtered and context-sliced mining (where basket counts shrink).
- **AC3** — Default documented; a threshold of 0/1 reproduces pre-guard behaviour.

**Test Cases:**
- **TC-2A.5.1 (U)** — A pair backed by 1 basket is excluded at `min_supporting_baskets=5`; a well-supported pair remains.
- **TC-2A.5.2 (U)** — Threshold 0/1 reproduces pre-guard behaviour.

### US-2A.6 — API: context parameters

> **As a** UI (via the API), **I want** to pass context, **so that** the screens can drive context-aware recommendations.

**Acceptance Criteria:**
- **AC1** — `POST /api/v1/recommendations` accepts optional context (time_of_day, day_type, weather, promo); backward compatible when omitted.
- **AC2** — The response echoes the context used.
- **AC3** — Negative associations are retrievable (new field or endpoint); auth + error envelope unchanged.

**Test Cases:**
- **TC-2A.6.1 (I)** — Request with context → 200 with echoed context.
- **TC-2A.6.2 (I)** — Request without new params behaves like Sprint 1.
- **TC-2A.6.3 (I)** — Negative associations are returned and governed.

### US-2A.7 — UI: context selectors

> **As a** Category Manager, **I want** context selectors, **so that** I can demo how weather/time changes placements.

**Acceptance Criteria:**
- **AC1** — Category Manager mode has selectors for time-of-day, day type, weather, and promo.
- **AC2** — Changing context/weather visibly changes results (the headline demo moment).
- **AC3** — Cannibalization pairs are surfaced separately.
- **AC4** — UI calls the API only (L1→L2), enforced by the existing import-boundary test.

**Test Cases:**
- **TC-2A.7.1 (U)** — A formatting helper renders the context on a result row.
- **TC-2A.7.2 (static)** — `ui/` still imports no services.

---

# 5. Demo-Ready Exit Criteria (Sprint 2A)

1. Toggle weather (Rainy → Sunny) and/or day type → recommendations visibly re-rank.
2. A cannibalization (avoid co-placement) pair is flagged.
3. Every recommendation still shows a rationale and appears in the audit log.
4. Thin-evidence rules no longer appear (T-014).
5. All tests green; `ruff` clean; CI passing.

---

*Confidential — Cognizant Internal · Sprint 2A Backlog · Draft for Review · July 2026 · Maintained by Aditya Srivastava*
