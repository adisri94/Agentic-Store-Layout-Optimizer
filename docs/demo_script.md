# 🎬 Demo Script — Store Layout (Product Placement) Optimizer

> **Purpose of this document:** A presenter's walkthrough — what to click, what to say, and what business outcome to land — for showing the tool to a prospect client. This is different from `architecture.md` or `decision_log.md`, which are written for the *builder*. This one is written for the *person standing in front of a client*.
>
> **Living document rule:** A new "Scene" section gets added at the end of every sprint, once that sprint's feature is working end-to-end. If you can't confidently write a demo scene for a feature, that's a signal the feature isn't demo-ready yet.

---

## 📌 Document Metadata

| Field | Value |
|-------|-------|
| **Product Name** | Store Layout (Product Placement) Optimizer Tool |
| **Document Type** | Demo Script (Living Document) |
| **Current Scope** | Sprint 1 only — Core MBA + #9 Explainability & Governance |
| **Owner** | Aditya Srivastava, Senior Consultant, Cognizant |
| **Last Updated** | 20 July 2026 |
| **Related Docs** | `decision_log.md` · `architecture.md` · Product Vision One-Pager v2.1 |

---

## ⚠️ Scope Honesty Check (Read Before Every Demo)

Sprint 1 delivers exactly two things. **Do not demo or imply anything beyond this list** — later sprints add contextual AI (#1), GenAI planograms (#3), omnichannel (#4), segmentation (#5), optimization (#6), and vendor collaboration (#8). Promising those now sets a false expectation with the client.

| ✅ What Sprint 1 Actually Does | ❌ What It Does NOT Do Yet |
|---|---|
| Finds product pairs frequently bought together, from historical POS data | Does not adjust for time-of-day, weather, or promos (that's Sprint 2, Enhancement #1) |
| Scores each pairing with **lift, confidence, support** (defined below) | Does not generate planograms via natural-language chat (that's Sprint 4, Enhancement #3) |
| Attaches a plain-English reason to every recommendation | Does not personalize by shopper segment or mission (that's Sprint 3, Enhancement #5) |
| Writes a permanent, tamper-proof log of every recommendation shown | Does not optimize for margin/inventory/shrink trade-offs (that's Sprint 2, Enhancement #6) |

---

## 🧠 Plain-English Glossary (For the Presenter, Not the Client)

You don't need to explain these terms to the client using jargon — but you should understand them so you can translate on the fly.

| Term | What It Actually Means |
|------|------------------------|
| **Apriori / FP-Growth** | Two different "recipe" algorithms that both do the same job: scan thousands of shopping baskets and find which items keep showing up together. Think of it like a librarian noticing that people who borrow cookbooks often also borrow diet books — done automatically, at massive scale. |
| **Lift** | "How much more likely are these two items bought together, versus by random chance?" Lift of 1.0 = no special connection. Lift of 2.0 = twice as likely as chance. This is the headline number for the client. |
| **Confidence** | "Of the people who bought item A, what % also bought item B?" A supporting number — shows how *reliable* the pattern is. |
| **Support** | "Out of all transactions, what % contained this exact pair?" A frequency check — makes sure we're not building a recommendation on 3 lucky transactions out of 500,000. |
| **Governance wrapper** | Every recommendation is stopped and checked before the user ever sees it — like a manager reviewing a report before it goes to a client, every single time, automatically. |
| **Audit log** | A permanent, append-only diary entry for every recommendation ever shown — who saw it, when, and why it was suggested. Can never be edited after the fact, only added to. |

---

## 🎯 Demo Objective for This Sprint

Prove two things to the prospect:

1. **The analytical core works and is grounded in real transaction patterns** — not a black box, not a guess.
2. **Nothing reaches a category manager's screen without a transparent, auditable reason** — this is the trust and compliance story that differentiates this tool from a plain MBA engine bought off the shelf.

---

## 🎬 Scene 1 — Setting the Business Context (2 min)

**What's on screen:** Streamlit home / Category Manager landing view.

**Say:**
> "Right now, category managers at most retailers build planograms — that's the map of what product goes where on the shelf — using static reports that get refreshed maybe once a quarter. By the time the report lands, shopper behavior has already moved on. What I'm going to show you is a tool that looks at your own point-of-sale data — literally every basket rung up at the register — and tells you, in plain language, what should go next to what, and *why*."

**Business point landed:** This isn't a generic industry benchmark tool — it learns from *their* store's actual transactions.

---

## 🎬 Scene 2 — Running the Core MBA Engine (4 min)

**What to click:** Select a category (e.g., "Men's Running Footwear") → click "Get Recommendations."

**Say:**
> "Behind the scenes, the tool just scanned our synthetic sports-apparel retailer's transaction history — about half a million basket line items — looking for products that repeatedly show up together. This is the same category of technique retailers have used for years, just applied automatically and continuously instead of manually and occasionally."

**Point at the result:** e.g., *Running Shoes → Moisture-Wicking Socks*

**Say:**
> "The tool tells us these two items have a **lift of 2.1** — meaning shoppers are twice as likely to buy both together than random chance would suggest. It backs that up with a **confidence score** — of everyone who bought the shoes, what percentage also bought the socks — and a **support score**, which confirms this isn't a fluke from a handful of transactions; it's a pattern across thousands of baskets."

**Business point landed:** The recommendation is a *data-grounded* suggestion with three independent statistical checks behind it, not a single fragile number.

---

## 🎬 Scene 3 — The Explainability & Governance Layer (4 min)

**What to click:** Open the "Why this recommendation?" panel next to the suggestion. Then switch to Admin/Governance mode and show the audit log entry for the same recommendation.

**Say:**
> "Here's what really sets this apart from a basic analytics report: every single recommendation is intercepted — automatically — by a governance layer before a category manager ever sees it. That layer does three things: it writes a plain-English explanation of *why* this was recommended, it runs policy checks — for example, making sure we're not over-recommending one vendor's products or over-concentrating high-margin items in a way that looks unfair — and it writes a permanent record to an audit log that can never be silently edited or deleted."

**Show the audit log entry on screen — point to the timestamp, the evidence (lift/confidence/support), and the policy result.**

**Say:**
> "If a regulator, an internal auditor, or even just a skeptical category manager asks 'why did the system suggest this,' the answer isn't 'trust the algorithm' — it's a permanent, inspectable record, generated automatically, every time."

**Business point landed:** This is the trust and compliance differentiator — most placement tools give you a number; this one gives you a defensible, auditable decision trail.

---

## 🎬 Scene 4 — Closing the Loop (2 min)

**Say:**
> "What you've just seen — the core recommendation engine plus the governance wrapper around every single suggestion — is our first working increment. We're building this in stages: next, the system starts factoring in time of day, weather, and promotions; after that, generative AI lets a category manager just type a request in plain English and get a full planogram back. But even at this early stage, the foundation you're looking at is real, working code connected to real transaction-shaped data — not a mockup."

**Business point landed:** Sets expectation this is an evolving platform being built incrementally, and what's shown today is genuinely functional, not a slide deck pretending to be a product.

---

## 🛟 Fallback Plan (If Something Breaks Mid-Demo)

| Risk | Fallback |
|------|----------|
| App crashes or hangs | Have a screen-recording of Scenes 2–3 ready to play (`/demo_assets/sprint1_recording.mp4` — to be recorded once Sprint 1 build is stable) |
| No internet / API issue | Sprint 1 has no external LLM dependency yet, so this shouldn't occur — but confirm before every demo |
| Client asks about a later-sprint feature (e.g., "can it do this by weather?") | Be honest: "That's actually next sprint — here's the roadmap" — and show the Build Sequence table from the Product Vision One-Pager |

---

## 📝 Post-Demo Checklist (Presenter To-Do)

- [ ] Log any client questions that weren't answered — feed into `decision_log.md` if they surface a new requirement
- [ ] Note any moment the client looked confused or disengaged — useful for refining this script next sprint
- [ ] Confirm whether the client asked about data privacy/compliance — if so, flag Governance (#9) more prominently next time

---

## 🔗 Related Documents

| Doc | Use for |
|-----|---------|
| `architecture.md` | Technical detail behind what's being demoed |
| `decision_log.md` | Why Sprint 1 was scoped exactly this way (see D-025 build sequence) |
| Product Vision One-Pager v2.1 | The full roadmap to reference when client asks "what's next" |

---

*Confidential — Cognizant Internal · Demo Script v1.0 (Sprint 1 scope) · July 2026 · Maintained by Aditya Srivastava*
