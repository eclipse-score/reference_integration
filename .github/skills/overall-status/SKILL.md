---
name: overall-status
description: "How-to reference for the Feature and Process Status table in docs/s_core_v_1/roadmap/overall_status.rst. Explains the counting model, status criteria, RST formatting, path filters and progress-chart workflow used to derive completion status from eclipse-score GitHub repos (Baselibs, Communication, Logging, Persistency, Time, Config Management, Lifecycle, Security/Crypto, Some/IP). Use when updating, regenerating or reviewing the overall status / feature status tracker. The overall-status agent orchestrates the run; this skill holds the 'how'."
argument-hint: "optional: module name or 'all'"
---

# Feature and Process Status Tracker — the "how"

This skill is the **methodology** for refreshing the table in
`docs/s_core_v_1/roadmap/overall_status.rst` from live `eclipse-score` GitHub
repositories pinned via `known_good.json`.

The **[overall-status agent](../../agents/overall-status.agent.md)** is the
main actor: it is started to update or regenerate the table and executes the
procedure end-to-end. This skill supplies the detailed rules the agent reads
at each phase.

The content is split into a **Common** part (shared engine) and one file per
**Process Area** (PA-specific data), so each concern stays self-contained.

---

## When to use

- Update / refresh the overall status (feature & process status) table.
- Regenerate the table from scratch after a `known_good.json` ref bump.
- Add a new module row, or review the table for plausibility.
- Update the per-PA progress SVG charts.

## Structure — Common + Process Areas

| Scope | File | What it contains |
|---|---|---|
| **Common** | [references/common.md](./references/common.md) | Scope & modules, repos & pinned refs, counting model, RST formatting rules, the shared procedure (Steps 0–7), the progress-graphics workflow, and limitations |
| **PA1** | [references/pa1-change-management.md](./references/pa1-change-management.md) | `CR approved` — Feature Request issue lookup (labels, milestone scope, Project V2 status, manual overrides); the PA1-only modules Diagnostic Services & NM |
| **PA2** | [references/pa2-requirements.md](./references/pa2-requirements.md) | `Feature Req` · `Component Req` · `Req. Inspection` — directive types, split rendering, path filters |
| **PA3** | [references/pa3-architecture.md](./references/pa3-architecture.md) | `Feature Arch` · `Component Arch` · `Arch. Inspection` — directive types, path filters |
| **PA4** | [references/pa4-implementation.md](./references/pa4-implementation.md) | `SW Dev Plan` · `Code` (LOC) · `Detailed Design` · `Impl. Inspection` |
| **PA5** | [references/pa5-verification.md](./references/pa5-verification.md) | `Unit Tests` · `C0/C1 Cov` · `Comp. IT` · `Feat. IT` · `Static` · `Dynamic` · `Module Ver. Rpt`; coverage CI keys, static/dynamic CI table, platform verification report |

## Scope at a glance

Tracked modules (one row each, in order):
`Baselibs · Communication · Logging · Persistency · Time · Config Mgmt ·
Lifecycle · Security/Crypto · Diagnostic Services · NM · Some/IP`.
**Orchestrator** is never tracked.

| PA | Title | sphinx-needs tag | Columns |
|---|---|---|---|
| PA1 | Change Management | `change_management` | CR approved |
| PA2 | Requirements Engineering | `requirements_engineering` | Feature Req · Component Req · Req. Inspection |
| PA3 | Architecture Design | `architecture_design` | Feature Arch · Component Arch · Arch. Inspection |
| PA4 | Implementation | `implementation` | SW Dev Plan · Code · Detailed Design · Impl. Inspection |
| PA5 | Verification | `verification` | Unit Tests · C0/C1 Cov · Comp. IT · Feat. IT · Static · Dynamic · Module Ver. Rpt |

## Quickstart

1. Read [references/common.md](./references/common.md) and run **Step 0–1**
   (resolve pinned refs, fetch repo trees).
2. For each Process Area, read its file and compute the cells using the
   Common counting model + the PA's path filters / criteria.
3. Run the **sanity checks** (Common Step 5) before writing.
4. Write the RST (Common Step 6) — update every PA table, the per-table
   **Rollout status** row, and the **data collection date**.
5. Refresh the per-PA progress SVGs (Common C6).
