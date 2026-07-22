# ✅ Sprint 1 — Review & Test Checklist (Plain Language)

> **What this is:** A simple, non-technical checklist you can walk through to confirm Sprint 1 works before you sign it off. No coding knowledge needed — just run a couple of commands and click through the app. Mark each row **Pass** or **Fail**.
>
> **Sprint 1 in one line:** the tool reads shopping-basket data, finds products often bought together, and shows each suggestion with a plain-English reason and a permanent record — nothing reaches the screen without being checked and logged.

---

## Before you start (one-time setup)

Open a terminal in the project folder and run these:

| Step | Command | What it does |
|---|---|---|
| 1 | `python -m uv sync` | Installs everything the app needs |
| 2 | `./tasks.ps1 seed --sample` *(fast)* or `./tasks.ps1 seed` *(full)* | Creates the pretend shop data |
| 3 | `./tasks.ps1 demo` | Starts the app (leave this running) |

Then open **http://localhost:8501** in your browser. You should see a sidebar with two modes: **Category Manager** and **Admin / Governance**.

> If the sidebar says "API: unreachable", the app didn't start fully — re-run step 3.

---

## Part A — Automated checks (one command)

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| A1 | All automated tests pass | Run `./tasks.ps1 test` | Ends with "45 passed" and "All checks passed!" | ☐ |

That single command runs every built-in test (data, recommendations, governance, API) and the code-quality check. If it's all green, the engine and rules are behaving as designed.

---

## Part B — Walk through the app yourself

### Category Manager mode

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B1 | You can ask for recommendations | Pick a Store ID (e.g. `STR-0001`), leave category blank, click **Get Recommendations** | A table of product pairs appears | ☐ |
| B2 | Each suggestion shows the three numbers | Look at the table columns | Every row shows **Lift**, **Confidence**, and **Support** | ☐ |
| B3 | Each suggestion has a plain-English reason | Open a "Why this recommendation?" panel | You see a sentence like *"Recommended because customers who buy X are 2.1x more likely to also buy Y, based on N transactions."* | ☐ |
| B4 | Policy checks are visible | Look inside a "Why…" panel | It shows either "No policy warnings" or a listed warning | ☐ |
| B5 | Category filter works | Type a category (e.g. `Footwear`) and click Get Recommendations again | Results are limited to that category | ☐ |

### Admin / Governance mode

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B6 | The audit log is visible | Switch to **Admin / Governance** mode | A table of audit entries appears | ☐ |
| B7 | Every suggestion was recorded | Compare the count | There is at least one audit entry for each recommendation you generated | ☐ |
| B8 | Each record has evidence | Look at the audit columns | Each row shows a timestamp, the recommendation, a "Passed" flag, and the numbers behind it | ☐ |

### Trust & safety (the differentiator)

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B9 | Nothing skips the checks | Every recommendation in B1 had a reason (B3) and appears in the log (B7) | Confirmed — no suggestion appears without a reason and a record | ☐ |
| B10 | Access needs a key | (Optional, technical) Call the API without the key | The request is refused | ☐ |

---

## What is **not** in Sprint 1 (so don't expect it yet)

These are planned for later sprints — their absence is by design, not a defect:

- Adjusting for time of day, weather, or promotions (Sprint 2)
- Balancing profit / stock / shrink, not just "bought together" (Sprint 2)
- Online + in-store combined data, shopper segments (Sprint 3)
- Typing a request in plain English to design a shelf (Sprint 4)
- The vendor portal (Sprint 5)
- AI-written reasons — Sprint 1 uses a fixed, reliable sentence template (no AI key needed)

---

## Known limitation to be aware of during review

- **Thin-evidence suggestions in a single small store:** when you filter to one store that has very few baskets, some suggestions can be backed by just one or two transactions, which makes the "lift" number look extremely high (e.g. "50x"). This is mathematically correct but not convincing for a demo. A small follow-up (requiring a minimum number of supporting baskets) can be added — flag this if you'd like it addressed before or during Sprint 2. Using the **full** data set (`./tasks.ps1 seed`) rather than `--sample` largely avoids it.

---

## Sign-off

| Field | Value |
|---|---|
| Reviewed by | ________________________ |
| Date | ________________________ |
| Result | ☐ All checks pass — approve Sprint 1 closure   ☐ Issues found (list below) |

Notes / issues:

_______________________________________________________________

---

*Confidential — Cognizant Internal · Sprint 1 Review Checklist · Maintained by Aditya Srivastava*
