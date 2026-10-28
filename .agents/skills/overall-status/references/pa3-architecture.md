# Process Area 3 — Architecture Design

| Property | Value |
|---|---|
| sphinx-needs tag | `architecture_design` |
| Cross-reference label | `overall_status_pa3` |
| Columns | Feature Arch · Component Arch · Arch. Inspection |
| Progress figure | `pa3_arch_progress.svg` (`720px`) |

This PA counts sphinx-needs directive blocks per
[common.md C3](./common.md#c3-counting-model). For shared conventions (cell
layout, source links, rollout-status row, pie chart row, progress figure
embedding) see [common.md C4](./common.md#c4-rst-formatting-rules).

---

## Status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **Feature Arch** | `valid = total` per [C3](./common.md#c3-counting-model) | mixed | no matching directives |
| **Component Arch** | `valid = total` per [C3](./common.md#c3-counting-model) | mixed | no matching directives |
| **Arch. Inspection** | every `chklst_arc_inspection.rst` valid | mixed | no checklists |

---

## Directive types & counting

| Column | `count_files` kind | Directive types |
|---|---|---|
| Feature Arch | `feat_arc` | `feat`, `feat_arc`, `feat_arc_sta`, `feat_arc_dyn` |
| Component Arch | `comp_arc` | `comp`, `comp_arc`, `comp_arc_sta`, `comp_arc_dyn`, `logic_arc_int`, `logic_arc_int_op`, `real_arc_int`, `real_arc_int_op` |
| Arch. Inspection | `chklst` | document `:status:` of each `chklst_arc_inspection.rst` (see [C3.3](./common.md#c33-inspections)) |

Never counted as Arch directives: `stkh_req`, `tool_req`, `document`,
`needtable`, `needpie`, `needextend`, `figure`, `uml`, `note`, `attention`,
`toctree`, `grid`.

- **Per-link status markers (Arch. Inspection):** prefix every
  `chklst_arc_inspection.rst` link with ✅/🔄/❌ by its document `:status:`
  (count of ✅ must equal the `valid` numerator) — see
  [common.md C4.2.1](./common.md#c421-per-link-status-markers--inspection--report-cells-mandatory).

---

## Path filters

Cross-cutting rules (two-repo aggregation, Communication-vs-Some/IP
separation, Lifecycle complexity) are in
[common.md Step 4](./common.md#step-4--path-filters). The per-module filters
for the **Feature Arch** and **Component Arch** columns:

| Module | Deliverable | Repo | Filter (`lambda p: ...`) |
|---|---|---|---|
| Baselibs | Feat. Arch | score | `'features/baselibs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Comp. Arch | score | `'modules/baselibs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Arch. Inspection | score | `'baselibs' in p and 'chklst_arc_inspection' in p` |
| Communication | Feat. Arch | score | `'features/communication' in p and 'architecture' in p and 'some_ip_gateway' not in p and …` |
| Communication | Comp. Arch | score | `'modules/communication' in p and 'architecture' in p and 'some_ip_gateway' not in p and …` |
| Logging | Feat. Arch | score | `('features/logging' in p or 'features/analysis-infra/logging' in p) and 'architecture' in p and …` |
| Logging | Comp. Arch | score | `'modules/logging' in p and 'architecture' in p and …` |
| Persistency | Feat. Arch | score | `'features/persistency' in p and 'architecture' in p and …` |
| Persistency | Comp. Arch | persistency | `'kvs' in p and 'architecture' in p and …` |
| Lifecycle | Feat. Arch | score | `'features/lifecycle' in p and 'architecture' in p and …` *(must walk subfolders)* |
| Lifecycle | Comp. Arch | lifecycle | `'module' in p and 'architecture' in p and …` |
| Time / Config Mgmt / Sec.Crypto | Feat. Arch | score | `'features/<area>' in p and 'architecture' in p and …` |

> Standard `path_filter` tail for directive counting:
> `… and p.endswith('.rst') and 'chklst' not in p`. Inspection filters use
> `'chklst_arc_inspection' in p` instead.

> **Component-level architecture may live in two repos at once.** Baselibs and
> Logging keep `comp_arc` directives both in `eclipse-score/score`
> (`modules/<area>/**`) **and** in their own repo (`docs/<area>/**`) — query
> both filters and **sum** the `(valid, total)` tuples. The same is true for
> Persistency `kvs`.
