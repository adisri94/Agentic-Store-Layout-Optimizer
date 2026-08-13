# ✅ Sprint 2A — Review & Test Checklist (Plain Language)

> **What this is:** A simple, non-technical checklist to confirm Sprint 2A works before you sign it off. Run a couple of commands and click through the app. Mark each row **Pass** or **Fail**.
>
> **Sprint 2A in one line:** the tool now makes its recommendations **context-aware** — they change with the time of day, day of week, weather, and promotions — and it flags **cannibalization** pairs (products that sell *worse* together), while still explaining and logging every recommendation.

---

## Before you start (one-time setup)

| Step | Command | What it does |
|---|---|---|
| 1 | `python -m uv sync` | Installs dependencies |
| 2 | `./tasks.ps1 seed` | Generates the pretend shop data (use the **full** set, not `--sample`, so context slices have enough data) |
| 3 | `./tasks.ps1 demo` | Starts the app (leave running) |

Then open **http://localhost:8501**. Sidebar should say "API: connected".

---

## Part A — Automated checks (one command)

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| A1 | All automated tests pass | `./tasks.ps1 test` | Ends with "75 passed" and "All checks passed!" | ☐ |

---

## Part B — Walk through the app

### Context-aware recommendations (the headline)

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B1 | Context controls exist | In Category Manager mode, look under the Store/Category row | Selectors for **Time of day, Day type, Weather, Promo** appear | ☐ |
| B2 | Weather changes the result | Set Weather = **sunny**, Get recommendations; then Weather = **rainy**, Get recommendations again | The list and/or ranking **changes** between the two, and a banner shows the applied context | ☐ |
| B3 | Day type changes the result | Compare Day type = **weekday** vs **weekend** | Results differ (or the ranking order changes) | ☐ |
| B4 | It's still explained + logged | Open a "Why this recommendation?" panel; then check Admin/Governance mode | Each still has a plain-English reason and a matching audit entry | ☐ |

### Cannibalization (avoid co-placing)

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B5 | Cannibalization pairs show | Click **"Show cannibalization pairs (avoid co-placing)"** | A list of pairs appears (or a clear "none found" message) | ☐ |
| B6 | The reason says "avoid" | Open one of those pairs | The reason reads like *"Avoid co-placing X and Y: bought together less often than chance…"* | ☐ |

### Trust & data quality

| # | What to check | How | Expected result | Pass/Fail |
|---|---|---|---|---|
| B7 | No flimsy "50×" suggestions | Try a single store with a narrow context (e.g. one store + rainy) | You still get results, but none are backed by just 1 transaction (the guard keeps a floor) | ☐ |
| B8 | Weather source is safe offline | (Optional) Disconnect the network and Get recommendations | Still works — weather falls back to the built-in synthetic source; the demo never breaks | ☐ |

---

## What is **not** in Sprint 2A (so don't expect it yet)

- Margin / inventory-turn / shrink optimization and lift-vs-margin trade-offs — that's **Sprint 2B (#6)**.
- Sequence mining (ordered journeys) and self-learning (RL bandits) — deferred.
- A *live* weather API is optional and off by default; Sprint 2A uses a controllable synthetic weather source (see decision D-037). Turning on live Open-Meteo is a config flag and still falls back safely.

---

## How the weather works (for your awareness)

By default the tool uses a **synthetic** weather signal you can control on stage (toggle Rainy/Sunny). A **live Open-Meteo** source can be switched on via config (`ENABLE_LIVE_WEATHER=true`); it needs the corporate certificate to be trusted and automatically falls back to synthetic if the network/proxy blocks it (decisions D-037 / D-040).

---

## Sign-off

| Field | Value |
|---|---|
| Reviewed by | ________________________ |
| Date | ________________________ |
| Result | ☐ All checks pass — approve Sprint 2A closure   ☐ Issues found (below) |

Notes / issues:

_______________________________________________________________

---

*Confidential — Cognizant Internal · Sprint 2A Review Checklist · Maintained by Aditya Srivastava*
