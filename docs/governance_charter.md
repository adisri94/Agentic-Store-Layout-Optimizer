# 🛡️ Governance Charter — Store Layout (Product Placement) Optimizer

> **Purpose of this document:** This is the **business-facing rulebook** that every recommendation produced by this tool must satisfy before it reaches a category manager, vendor, or any other user. It is the plain-language policy that Enhancement #9 (Explainability & Governance) enforces automatically, in code, on every single recommendation. If `architecture.md` and `decision_log.md` describe *how* the system is built, this charter describes *what it must never violate, no matter how it's built*.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Governance Charter |
| **Version** | 1.0 |
| **Status** | Draft for Review |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 20 July 2026 |
| **Related Documents** | `architecture.md` §10 (Governance Deep-Dive) · `decision_log.md` D-012, D-029 · Enhancement Deep-Dive §3.7 |

---

## 1. Purpose & Scope

This charter exists to guarantee one promise to every user of this tool, technical or non-technical: **no product-placement recommendation is ever shown to a person without first being checked, explained, and permanently recorded.**

**In scope:** Every recommendation produced by Enhancements #1 (Contextual Affinity), #3 (GenAI Planogram Designer), #4 (Omnichannel Affinity Sync), #5 (Segment & Mission-Based Placement), #6 (Multi-Objective Optimization), and #8 (Vendor Collaboration Module).

**Out of scope:** Internal system logs unrelated to a user-facing recommendation (e.g., API health checks) are not subject to this charter.

**Plain-English analogy:** Think of this the way a newsroom has an editorial policy — a reporter (an enhancement) can draft a story (a recommendation), but nothing gets published until an editor (the Governance Service) checks it against a fixed set of standards.

---

## 2. Roles & Accountability

| Role | Responsibility Under This Charter |
|------|-----------------------------------|
| **Category Manager** | Primary consumer of recommendations; can accept, edit, or override — with reason captured |
| **CPG Vendor Partner** | Consumer of co-placement suggestions; protected by vendor-equity rules (Section 3) |
| **Data Steward / Admin** | Owns audit log integrity, policy configuration, and data quality gates feeding recommendations |
| **Merchandising Head** | Reviews fairness scorecards and KPI dashboards; escalation point for systemic concerns |
| **Governance Service (system)** | Automated enforcement — intercepts every recommendation, runs checks, writes the audit record |

**Rule of accountability:** A human role can *override* a recommendation. No human role, and no code path, is permitted to *bypass* the governance check itself. Override ≠ bypass — see Section 7.

---

## 3. Policy Rules (The Guardrails)

These are the specific, testable rules every recommendation must pass. Written here in plain business language; the technical implementation (small Python functions) lives in `services/governance/policy_engine.py` and is indexed in `architecture.md` §10.3.

| Rule ID | Plain-English Rule | Why It Matters |
|---------|--------------------|-----------------|
| **POL-001** | A high-margin product cannot make up more than 40% of any single endcap display | Prevents the tool from silently pushing profit over customer experience |
| **POL-002** | Every recommendation must clear a minimum reliability bar (confidence ≥ 0.1) | Stops the tool from acting on a fluke — the "3 lucky transactions" problem |
| **POL-003** | Contractually mandated brand placements must appear in the top 3 for their category | Keeps the tool honest to existing vendor contracts and legal commitments |
| **POL-004** | No single vendor's products may exceed 30% of co-placement suggestions | Protects fairness across CPG partners — no silent favoritism |
| **POL-005** | Recommendations touching regulated categories (alcohol, tobacco) must be explicitly flagged | Ensures regulatory and compliance visibility on sensitive categories |

**Illustrative example:** If the engine finds that "energy drinks near the checkout" has a great lift score, but the checkout endcap is already at 38% high-margin items, POL-001 blocks pushing it past 40% — the system re-ranks the alternative instead of just taking the top statistical result blindly.

---

## 4. Explainability Standard

Every recommendation, regardless of which enhancement produced it, must be accompanied by:

1. **The evidence bundle** — lift, confidence, and support scores (see `demo_script.md` glossary for plain-English definitions of these three terms)
2. **A plain-English rationale** — a sentence a category manager can read without any data science background, e.g., *"Recommended because customers who buy running shoes are twice as likely to also buy moisture-wicking socks, based on 3,200 comparable transactions."*
3. **Any policy warnings** — if a rule in Section 3 was close to being triggered, this is surfaced, not hidden

**Rule of thumb:** If a recommendation cannot be explained in one plain sentence, it does not go out. This is the "no black box" commitment referenced in the Enhancement Deep-Dive.

---

## 5. Fairness & Bias Commitments

The system commits to monitoring and reporting on:

- **SKU diversity index** — are we recommending a healthy range of products, not just a favored few?
- **Vendor equity** — is any one vendor being over- or under-represented in suggestions? (ties to POL-004)
- **Segment coverage** — are all shopper segments and store clusters receiving fair-quality recommendations, not just the highest-value ones?

**Plain-English analogy:** This is similar to a loyalty program auditing whether it's accidentally only rewarding its biggest spenders and ignoring everyone else — the fairness scorecard is the mechanism that catches that kind of silent skew before it becomes a business or reputational problem.

---

## 6. Audit & Recordkeeping

Every recommendation shown to any user results in a **permanent, append-only audit entry** — meaning it can be added to, but never edited or deleted after the fact.

**What gets recorded, every time:**
- Timestamp of when the recommendation was shown
- The recommendation itself and its evidence bundle
- The result of every policy check (pass/fail/warning)
- Who saw it and, if applicable, what they did with it (accepted / edited / overridden)

**Plain-English analogy:** Think of this like a flight data recorder ("black box") on an aircraft — nobody expects to need it day-to-day, but if a question is ever raised about *why* a decision happened, there is an unambiguous, tamper-proof record to point to.

**Retention:** Aligned to the Phase 1 demo posture in `decision_log.md` D-021 — stored in `data/audit.jsonl`, an append-only file, with production-grade retention policy to be defined when the tool moves beyond demo scope.

---

## 7. Override & Escalation Process

Category managers and other authorized roles **may override** a recommendation. This charter's requirement is not that recommendations must always be followed — it's that every override is captured with equal rigor:

1. The human's override decision is logged with the same audit discipline as the original recommendation
2. A reason must be captured — free text is acceptable, but it cannot be skipped
3. Override patterns are reviewed by the Merchandising Head periodically to detect systemic issues with the recommendation engine (e.g., if the same rule is overridden 80% of the time, that's a signal the rule itself needs revisiting)

**What overriding is not:** Overriding a single recommendation is not the same as bypassing the governance check for that recommendation. The check still runs, is still logged, and is still explainable — a human simply chose a different path afterward.

---

## 8. Regulatory & Compliance Alignment

- **Consent handling:** Loyalty and segmentation data is only used in recommendations where `consent_marketing` / `consent_analytics` flags are honored (per Data Product Contract §5.5.5 and §9)
- **PII protection:** No plaintext personal data ever enters a recommendation or its audit trail — only hashed identifiers, per D-029
- **Regulated categories:** Alcohol, tobacco, and similarly regulated product recommendations are explicitly flagged (POL-005) for additional review
- **Vendor scope isolation:** A vendor can only ever see their own promotional data and suggestions — never a competitor's (D-029, DQ-VP-05)

This section exists so that, if a real prospect's legal or compliance team asks "how does this tool handle data privacy and regulatory categories," there is a single section of a single document that answers the question directly.

---

## 9. Review Cadence

This charter is a **living document**, not a one-time sign-off:

- **Reviewed at the start of every sprint** that introduces or modifies a recommendation-producing enhancement (per the Sprint sequence in `decision_log.md` D-025)
- **Amended via the same discipline as `decision_log.md`** — any change to a policy rule (Section 3) or fairness commitment (Section 5) must be logged as a new decision (`D-XXX`) before it takes effect
- **Not amended silently** — a change to this charter is itself a governance-relevant event and must be traceable

---

## 🔗 Related Documents

| Doc | Use for |
|-----|---------|
| `architecture.md` §10 | Technical deep-dive on how Governance is implemented in code |
| `decision_log.md` D-012, D-029 | Why governance-in-path and the security posture were designed this way |
| Enhancement Deep-Dive §3.7 | Detailed input/processing/output for Enhancement #9 |
| `demo_script.md` Scene 3 | How this charter is demonstrated live to a prospect client |
| Data Product Contract §9 | Data-level security, privacy, and compliance detail |

---

*Confidential — Cognizant Internal · Governance Charter v1.0 · July 2026 · Maintained by Aditya Srivastava*
