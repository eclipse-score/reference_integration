# Process Area 2 — Requirements Engineering

| Property | Value |
|---|---|
| sphinx-needs tag | `requirements_engineering` |
| Cross-reference label | `overall_status_pa2` |
| Columns | Feature Req · Component Req · Req. Inspection |
| Progress figure | `pa2_impl_progress.svg` (`720px`) |

This PA counts sphinx-needs directive blocks per
[common.md C3](./common.md#c3-counting-model). For shared conventions (cell
layout, source links, rollout-status row, pie chart row, progress figure
embedding) see [common.md C4](./common.md#c4-rst-formatting-rules).

---

## Status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **Feature Req** | `valid = total` per [C3](./common.md#c3-counting-model) | files exist, not all valid | no `feat_req` directives in `docs/features/<mod>/**` |
| **Component Req** | `valid = total` per [C3.2](./common.md#c32-component-requirements-split-rendering) | mixed | no `comp_req`/`aou_req` directives, and no TRLC stand-in |
| **Req. Inspection** | every `chklst_req_inspection.rst` has `:status: valid` | mixed | no checklists |

---

## Directive types & counting

| Column | `count_files` kind | Directive types |
|---|---|---|
| Feature Req | `feat_req` | `feat_req` |
| Component Req | `comp_req` | `comp_req`, `aou_req` (rendered split via `comp_req_cell`, see [C3.2](./common.md#c32-component-requirements-split-rendering)) |
| Req. Inspection | `chklst` | document `:status:` of each `chklst_req_inspection.rst` (see [C3.3](./common.md#c33-inspections)) |

- AoUs (`aou_req`) count for **Component** Req only, never for Feature Req.
- **Communication** keeps real component requirements in
  `score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc`
  (`.trlc`, not parsed) — render the Component Req cell as
  `0/0 comp_req [TRLC]` plus a link to the `.trlc` file (see
  [C4.2](./common.md#c42-source-links--mandatory)).

---

## Path filters

Cross-cutting rules (two-repo aggregation, Communication-vs-Some/IP
separation, Lifecycle complexity) are in
[common.md Step 4](./common.md#step-4--path-filters). The per-module filters
for the **Feature Req** and **Component Req** columns:

| Module | Deliverable | Repo | Filter (`lambda p: ...`) |
|---|---|---|---|
| Baselibs | Feat. Req | score | `'features/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Comp. Req | score | `'modules/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Req. Inspection | score | `'baselibs' in p and 'chklst_req_inspection' in p` |
| Communication | Feat. Req | score | `'features/communication' in p and 'requirements' in p and 'some_ip_gateway' not in p and …` |
| Communication | Comp. Req | score | `'modules/communication' in p and 'requirements' in p and 'some_ip_gateway' not in p and …` |
| Logging | Feat. Req | score | `('features/logging' in p or 'features/analysis-infra/logging' in p) and 'requirements' in p and …` |
| Logging | Comp. Req | score | `'modules/logging' in p and 'requirements' in p and …` |
| Persistency | Feat. Req | score | `'features/persistency' in p and 'requirements' in p and …` |
| Persistency | Comp. Req | persistency | `'kvs' in p and 'requirements' in p and …` |
| Lifecycle | Feat. Req | score | `'features/lifecycle' in p and 'requirements' in p and …` *(must walk subfolders)* |
| Lifecycle | Comp. Req | lifecycle | `'module' in p and 'requirements' in p and …` |
| Time / Config Mgmt / Sec.Crypto | Feat. Req | score | `'features/<area>' in p and 'requirements' in p and …` |

> Standard `path_filter` tail for directive counting:
> `… and p.endswith('.rst') and 'chklst' not in p`. Inspection filters use
> `'chklst_req_inspection' in p` instead.

> **Some/IP** keeps `comp_req` partly in `docs/requirements/component/**`
> and partly in `docs/tc8_conformance/requirements.rst` (own repo
> `eclipse-score/inc_someip_gateway`) — combine both.
