# Process Area 4 — Implementation

| Property | Value |
|---|---|
| sphinx-needs tag | `implementation` |
| Cross-reference label | `overall_status_pa4` |
| Columns | SW Dev Plan · Code · Detailed Design · Impl. Inspection |
| Progress figure | `pa4_impl_progress.svg` (`720px`) |

This PA mixes a project-wide file check (SW Dev Plan), a byte-based LOC
estimate (Code), directive counting (Detailed Design) and checklist status
(Impl. Inspection). For shared conventions see
[common.md C4](./common.md#c4-rst-formatting-rules).

---

## Status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **SW Dev Plan** | `eclipse-score/score` has `docs/platform_management_plan/software_development.rst` (project-wide; same status in every row) | — | file absent |
| **Code** | source files exist outside `docs/` | — | none found |
| **Detailed Design** | `valid = total` per [C3](./common.md#c3-counting-model) over `dd*` directives | mixed | none |
| **Impl. Inspection** | every `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` valid | mixed | no checklists |

---

## Directive types & counting

| Column | `count_files` kind | Directive types / method |
|---|---|---|
| SW Dev Plan | — | presence check of `docs/platform_management_plan/software_development.rst` in `eclipse-score/score`; project-wide → identical status in every row |
| Code | — | LOC estimate (see below) |
| Detailed Design | `dd` | `dd`, `dd_sta`, `dd_dyn` |
| Impl. Inspection | `chklst` | document `:status:` of each `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` (see [C3.3](./common.md#c33-inspections)) |

- **Per-link status markers (Impl. Inspection):** prefix every
  `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` link with
  ✅/🔄/❌ by its document `:status:` (count of ✅ must equal the `valid`
  numerator) — see
  [common.md C4.2.1](./common.md#c421-per-link-status-markers--inspection--report-cells-mandatory).

### Lines of Code (Code column)

LOC counts every line in source files (`.cpp .h .c .rs .py`) outside `docs/`,
`third_party/`, and `bazel-*/`, then rounds to the nearest 100.

> **Method.** The per-cell tracker uses the **same byte-÷-30 approximation**
> as the SVG charts (`sum(blob.size for path in tree if is_src(path)) / 30`,
> see [common.md C6.2](./common.md#c62-metrics--what-each-chart-sums)). The
> `is_src` filter in C6.2 is authoritative for what counts as a source file
> (extensions and the `docs/`, `third_party/`, `bazel-*/` exclusions). Expect
> ±10 % vs. `cloc` (see [common.md C7](./common.md#c7-limitations)).

```rst
   - ✅ Available (~12,500 LOC) `<repo-name> <https://github.com/eclipse-score/<repo-name>>`__
```

The link label MUST be the bare repository name (e.g. `baselibs`,
`communication`, `inc_time`), not the literal word `repo`. The **Code cell**
links the **repository root** (see
[common.md C4.2](./common.md#c42-source-links--mandatory)).

---

## Path filters

Cross-cutting rules are in
[common.md Step 4](./common.md#step-4--path-filters). The per-module filters
for the **Detailed Design** column (`Code` uses the repo root + `is_src`; SW
Dev Plan is a single project-wide file):

| Module | Deliverable | Repo | Filter (`lambda p: ...`) |
|---|---|---|---|
| Baselibs | Detailed Design | score | `'modules/baselibs' in p and 'detailed_design' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Impl. Inspection | score | `'baselibs' in p and ('chklst_impl_inspection' in p or 'chklst_dd_inspection' in p)` |
| Communication | Detailed Design | score | `'modules/communication' in p and 'detailed_design' in p and 'some_ip_gateway' not in p and …` |
| Logging | Detailed Design | score / logging | `'modules/logging' in p and 'detailed_design' in p and …` (query both repos, sum) |
| Persistency | Detailed Design | persistency | `'kvs' in p and 'detailed_design' in p and …` |
| Lifecycle | Detailed Design | lifecycle | `'module' in p and 'detailed_design' in p and …` |
| Time / Config Mgmt / Sec.Crypto | Detailed Design | score | `'features/<area>' in p and 'detailed_design' in p and …` |

> Standard `path_filter` tail for directive counting:
> `… and p.endswith('.rst') and 'chklst' not in p`. Inspection filters match
> `'chklst_impl_inspection' in p or 'chklst_dd_inspection' in p`.
