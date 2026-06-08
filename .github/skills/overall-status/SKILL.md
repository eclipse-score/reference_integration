---
name: overall-status
description: "Update the Feature and Process Status table in docs/s_core_v_1/roadmap/overall_status.rst. Use when: checking module status, updating feature status tracker, refreshing work product status, deriving completion status from eclipse-score GitHub repos for Baselibs, Communication, Logging, Persistency, Time, Config Management, Lifecycle, Security/Crypto."
argument-hint: "optional: module name or 'all'"
---

# Feature and Process Status Tracker

Refreshes the table in `docs/s_core_v_1/roadmap/overall_status.rst` from
live `eclipse-score` GitHub repositories pinned via `known_good.json`.

---

## 1. Scope

Tracked modules (one table row each, in this order):

```
Baselibs · Communication · Logging · Persistency · Time · Config Mgmt
Lifecycle · Security/Crypto · Diagnostic Services · NM · Some/IP
```

Excluded: **Orchestrator** — never add a row for it.

> **PA1-only modules: Diagnostic Services and NM.** Both modules have a row in
> every PA table for layout consistency, but only the PA1 column carries real
> data: they are tracked via `feature_request` issues in `eclipse-score/score`
> (see §4.0 keyword map). They have **no own repository** and **no
> `known_good.json` key** yet, so §2 and the Step 4 path-filter table have no
> rows for them and their PA2–PA5 cells render as `❌ Open` (zero directives,
> zero files). They still contribute `0` to the per-PA progress charts
> (§6a.2) and are excluded from the coverage weighted mean (§7).

Five process areas, each with its own table:

| PA | Title | sphinx-needs tag | Columns |
|---|---|---|---|
| PA1 | Change Management | `change_management` | CR approved |
| PA2 | Requirements Engineering | `requirements_engineering` | Feature Req · Component Req · Req. Inspection |
| PA3 | Architecture Design | `architecture_design` | Feature Arch · Component Arch · Arch. Inspection |
| PA4 | Implementation | `implementation` | SW Dev Plan · Code · Detailed Design · Impl. Inspection |
| PA5 | Verification | `verification` | Unit Tests · C0/C1 Cov · Comp. IT · Feat. IT · Static · Dynamic · Module Ver. Rpt |

---

## 2. Repos and pinned refs

Each module has content in **`eclipse-score/score`** (feature-level) and in its
**own repo** (component-level). Always query both.

| Module | `known_good.json` key | Own repo | Score-side path |
|---|---|---|---|
| Baselibs | `score_baselibs` | `eclipse-score/baselibs` | `docs/{features,modules}/baselibs/**` |
| Communication | `score_communication` | `eclipse-score/communication` | `docs/{features,modules}/communication/**` |
| Logging | `score_logging` | `eclipse-score/logging` | `docs/features/analysis-infra/logging/**`, `docs/modules/logging/**` |
| Persistency | `score_persistency` | `eclipse-score/persistency` (`docs/persistency/kvs/**`) | `docs/features/persistency/**` |
| Time | — | `eclipse-score/inc_time` | `docs/features/time/**` |
| Config Mgmt | — | `eclipse-score/config_management` | `docs/features/configuration/**` |
| Lifecycle | `score_lifecycle_health` | `eclipse-score/lifecycle` (`docs/module/health_monitor/**`) | `docs/features/lifecycle/**` |
| Security/Crypto | — | `eclipse-score/inc_security_crypto` | `docs/features/security_crypto/**` |
| Some/IP | — | `eclipse-score/inc_someip_gateway` | `docs/features/communication/some_ip_gateway/**` |

> **No row for Diagnostic Services or NM** — see §1. They are PA1-only;
> PA2–PA5 cells render `❌ Open` until their own repos / `known_good.json`
> keys exist, at which point a row must be added here **and** in Step 4.

> `eclipse-score/score` itself is pinned under key **`score_platform`** in the
> **`tooling`** section of `known_good.json` (not `target_sw`). Use the helper
> `pinned_ref()` in §6 below.

> **TRLC files** (`.trlc`) are not parsed by this skill. `eclipse-score/communication`
> keeps real component requirements in
> `score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc`;
> render them in the cell as `0/0 comp_req [TRLC]` plus a link.

---

## 3. Counting model

For each deliverable column a set of allowed directive types is defined
(see §3.1). For every RST file under the deliverable's path filter, count
the `.. <type>::` directive blocks whose immediately-following indented
`:status:` field equals `valid` (= **valid**) and the total number of such
blocks regardless of status (= **total**). Sum both numbers across all files.

The cell renders as:

| Condition | Output |
|---|---|
| total = 0 | `❌ Open` |
| valid = total > 0 | `✅ Available (valid/total)` |
| 0 ≤ valid < total | `🔄 NN% (valid/total)`, `NN = floor(100 · valid / total)` |

> valid = 0 with total > 0 renders as `🔄 0% (0/total)`, **never** `❌ Open`.
> `❌ Open` means *no files / no directives found at all*.

### 3.1 Allowed directive types per deliverable

| Deliverable | Directive types in `A` |
|---|---|
| Feature Requirements | `feat_req` |
| Component Requirements | `comp_req`, `aou_req` |
| Feature Architecture | `feat`, `feat_arc`, `feat_arc_sta`, `feat_arc_dyn` |
| Component Architecture | `comp`, `comp_arc`, `comp_arc_sta`, `comp_arc_dyn`, `logic_arc_int`, `logic_arc_int_op`, `real_arc_int`, `real_arc_int_op` |
| Detailed Design | `dd`, `dd_sta`, `dd_dyn` |
| Req./Arch./Impl. Inspection | document-level `:status:` of each `chklst_*.rst` (one per file) |

Never counted as Req/Arch directives: `stkh_req`, `tool_req`, `document`,
`needtable`, `needpie`, `needextend`, `figure`, `uml`, `note`, `attention`,
`toctree`, `grid`. AoUs (`aou_req`) count for **Component** Req only, never for
Feature Req.

### 3.2 Component Requirements split format

Component Requirements counts both `comp_req` and `aou_req` but **renders them
split** so the reader sees what fraction is real component requirements vs.
Assumptions of Use:

```
✅ Available (84/84 comp_req + 32/32 AoU)
✅ Available (0/0 comp_req [TRLC] + 33/33 AoU)   ← Communication: comp_req live in .trlc
✅ Available (35/35 comp_req)                     ← no AoUs
🔄 0% (0/1 comp_req + 0/1 AoU)                    ← mixed, none valid
```

If both subtotals are zero → `❌ Open`.

### 3.3 Inspections

Each `chklst_*.rst` file contains a single `.. document::` directive whose
indented `:status:` field is treated as the document status. Each file
contributes `(1, 1)` if `:status: valid`, else `(0, 1)`. Files without any
`:status:` field contribute `(0, 0)`.

### 3.4 Lines of Code (PA4 Code column)

LOC counts every line in source files (`.cpp .h .c .rs .py`) outside `docs/`,
`third_party/`, and `bazel-*/`, then rounds to the nearest 100. Format:

> **Method.** The per-cell tracker uses the **same byte-÷-30 approximation**
> as the SVG charts (`sum(blob.size for path in tree if is_src(path)) / 30`,
> see §6a.2). The `is_src` filter in §6a.2 is authoritative for what counts
> as a source file (extensions and the `docs/`, `third_party/`, `bazel-*/`
> exclusions). Expect ±10 % vs. `cloc` (see §7).

```rst
   - ✅ Available (~12,500 LOC) `<repo-name> <https://github.com/eclipse-score/<repo-name>>`__
```

The link label MUST be the bare repository name (e.g. `baselibs`,
`communication`, `inc_time`), not the literal word `repo`.

---

## 4. Per-deliverable status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **PA1** CR approved | At least one matching `feature_request` issue **scoped to milestone v0.5 or v1.0** has Status `Accepted` (or `Done`) in Project V2 #4 "Feature Requests / Modification" (see §4.0); cell lists every matching FR with its individual project status and milestone tag | At least one in-scope FR in `In Progress`/`In Review`/`Ready for Review`/`Changes Requested`/`Draft`/`POC Needed` and none Accepted | No matching FR in scope, or all matching FRs `Rejected` |
| **PA2** Feature Req | `valid = total` per §3 | files exist, not all valid | no `feat_req` directives in `docs/features/<mod>/**` |
| **PA2** Component Req | `valid = total` per §3.2 | mixed | no `comp_req`/`aou_req` directives, and no TRLC stand-in |
| **PA2** Req. Inspection | every `chklst_req_inspection.rst` has `:status: valid` | mixed | no checklists |
| **PA3** Feature Arch | `valid = total` per §3 | mixed | no matching directives |
| **PA3** Component Arch | `valid = total` per §3 | mixed | no matching directives |
| **PA3** Arch. Inspection | every `chklst_arc_inspection.rst` valid | mixed | no checklists |
| **PA4** SW Dev Plan | `eclipse-score/score` has `docs/platform_management_plan/software_development.rst` (project-wide; same status in every row) | — | file absent |
| **PA4** Code | source files exist outside `docs/` | — | none found |
| **PA4** Detailed Design | `valid = total` per §3 over `dd*` directives | mixed | none |
| **PA4** Impl. Inspection | every `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` valid | mixed | no checklists |
| **PA5** Unit Tests | repo has `_test.cpp` / `_test.py` / `tests/` | — | none |
| **PA5** C0/C1 Coverage | C0 = C1 = 100 % | data exists (any %) | not in `reference_integration` CI |
| **PA5** Comp. Integration Tests | tests in module's own repo | — | none |
| **PA5** Static Analysis | zero-tolerance per-module CI workflow passes on `main` (clang-tidy / Clippy) | tools configured but no CI enforcement | no static-analysis config |
| **PA5** Dynamic Analysis | zero-tolerance sanitizer CI passes on `main` | — | no sanitizer CI |
| **PA5** Module Ver. Report | `verification/module_verification_report.rst` `:status: valid` and contains data | `:status: draft` | absent or template only |
| **PA5** Platform Ver. Report | _no column_ — the platform verification report exists **once** for the entire platform; do not render it as a per-module column. Add it as a **bold one-liner immediately after the PA5 table** (see §5.2). | | |

> **Static / Dynamic Analysis cells render the status only, no source-code
> link.** The PA5 link discipline of §5.2 does not apply to these two
> columns: there is no canonical per-module artefact to point at (CI
> workflows live in the org-wide `.github` repo, not per module).

### 4.0 PA1 — Feature Request issue lookup

PA1 "CR approved" tracks **Feature Request** issues in `eclipse-score/score`.
The label name is **`feature_request`** (lowercase, with underscore). Use
`state=all` (some FRs are still open) and combine the topical
`ft:<module>` label with a title-keyword pass; **always union both result
sets** (deduplicated by issue number) so that older FRs which pre-date the
`ft:*` label scheme are still attributed to a module — see the attribution
note below.

**Milestone scope.** Only Feature Requests targeted at the **v0.5** or
**v1.0** release milestones are counted. The GitHub milestone titles that
currently qualify are:

- `SCORE v0.5 Feature Complete`
- `S-CORE v0.5 Certifiable`
- `v1.0`

The match is performed by substring on the milestone title with whitespace
stripped (`"0.5" in title` or `"1.0" in title`, case-insensitive). FRs with
no milestone, or with any other milestone (`v0.6`…`v0.10`), are excluded
from PA1 — even if they carry a matching `ft:*` label. Each rendered FR is
tagged with its short milestone in square brackets (e.g. `[v1.0]`,
`[v0.5 Certifiable]`).

The issues fetch must therefore include the milestone field in the jq
projection.

For each issue, fetch its **`Status`** field from the org-level project
**"Feature Requests / Modification"** (Project V2, id
`PVT_kwDOCy9hX84Auo7w`, number `#4`). The PA1 cell renders **one entry per
Feature Request**, each annotated with its individual project status — not a
single aggregate "Available". The cell headline is the **best** status
across all FRs for that module (so a module with at least one Accepted FR
still shows ✅ in summaries).

```python
# 1. List feature requests via the issue label (incl. milestone).
#    `--paginate` must be a separate CLI flag — embedding it in the URL
#    string sends it as a query parameter and silently truncates results
#    at 100 issues.
def fetch_frs():
    out = subprocess.run(
        ["gh", "api", "--paginate",
         "repos/eclipse-score/score/issues?state=all"
         "&labels=feature_request&per_page=100",
         "--jq",
         '.[] | [(.number|tostring), .title,'
         ' ((.labels // []) | map(.name) | join(",")),'
         ' ((.milestone.title // ""))] | @tsv'],
        capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, f"gh api failed: {out.stderr}"
    return [tuple(line.split("\t")) for line in out.stdout.splitlines() if line]

def in_scope(milestone: str) -> bool:
    s = milestone.lower().replace(" ", "")
    return ("0.5" in s) or ("1.0" in s)

# 2. Pull Status per issue from Project V2 #4
PROJECT_FR_ID = "PVT_kwDOCy9hX84Auo7w"
def fetch_fr_project_status() -> dict[str, str]:
    q = ('query($endCursor:String){node(id:"' + PROJECT_FR_ID + '"){'
         '... on ProjectV2{items(first:100, after:$endCursor){'
         'pageInfo{hasNextPage endCursor} '
         'nodes{content{... on Issue{number repository{nameWithOwner}}} '
         'fieldValues(first:20){nodes{... on ProjectV2ItemFieldSingleSelectValue'
         '{name field{... on ProjectV2SingleSelectField{name}}}}}}}}}}')
    out = subprocess.run(
        ["gh","api","graphql","--paginate","-f", "query="+q,
         "--jq",
         '.data.node.items.nodes[] | '
         'select(.content.repository.nameWithOwner=="eclipse-score/score") | '
         '[(.content.number|tostring), '
         '((.fieldValues.nodes[]|select(.field.name=="Status")|.name) // "—")] | @tsv'],
        capture_output=True, text=True, timeout=120)
    return dict(line.split("\t",1) for line in out.stdout.splitlines() if "\t" in line)
```

Status-field options (from project schema) and the recommended emoji /
ranking the cell uses to pick the headline:

| Project Status      | Emoji | Rank |
|---------------------|:-----:|:----:|
| `Accepted` / `Done` | ✅    | 0    |
| `In Progress`       | 🔄    | 1    |
| `In Review`         | 🔄    | 1    |
| `Ready for Review`  | 🔄    | 1    |
| `Changes Requested` | 🔄    | 1    |
| `Draft`             | 📝    | 2    |
| `POC Needed`        | 🧪    | 3    |
| `Rejected`          | ❌    | 4    |
| _not in project_    | ❔    | 5    |

Cell layout (RST):

```rst
   - ✅ Accepted

     | `#914 <https://github.com/eclipse-score/score/issues/914>`__ — ✅ Accepted [v1.0] — Feature Request for SOME/IP Gateway
     | `#549 <https://github.com/eclipse-score/score/issues/549>`__ — ✅ Accepted [v0.5 Certifiable] — Feature request: common libraries for IPC and Logging
```

Each FR line is `\`#NNN <url>\`__ — <emoji> <Status> [<milestone>] — <issue title>`.
The issue title is taken verbatim from the GitHub `.title` field (already
fetched by `fetch_frs()`).

Module attribution mapping. **Always** combine the label-based hits and
the title-keyword hits (deduplicated by issue number) — do **not** treat
the keyword set as a fallback that only fires when the `ft:*` query is
empty. Older feature requests pre-date the `ft:*` label scheme and only
match by title keyword (e.g. `#69 "Feature Request for IPC"` for
Communication carries `feature_request` + `community:architecture` +
`planned-for:0.5` but no `ft:communication`); skipping the keyword pass
when `ft:*` already produced hits causes such issues to silently disappear
from PA1.

```python
FT_LABEL = {
    "Baselibs":         "ft:baselibs",
    "Communication":    "ft:communication",
    "Logging":          "ft:logging",
    "Persistency":      "ft:persistency",
    "Config Mgmt":      "ft:config_management",
    "Lifecycle":        "ft:health&lifecycle",
    "Security/Crypto":  "ft:security&crypto",
}
KW_FALLBACK = {
    "Baselibs":  ["baselib", "common librar", "abi compatible", "json parser"],
    "Communication": ["ipc", "streaming", "record and replay"],
    "Logging":   ["logging"],
    "Persistency": ["persistency", " kvs"],
    # Leading space is intentional: avoids matching "runtime", "realtime",
    # "datetime" etc. Do NOT "fix" by stripping it.
    "Time":      [" time"],
    "Some/IP":   ["some/ip", "someip", "some_ip"],
    "Diagnostic Services": ["diagnos"],
    "NM":        ["network management"],
}
```

Render up to ~6 hits per cell. If a module has zero matches, render
`❌ Open`. The older label `contribution request` exists too but tracks
formal contribution intent, not feature scope — **do not** use it for PA1.

> **Manual overrides — apply *after* the automated label∪keyword union
> has produced its hit set:**
>
> - **`#549` "common libraries for IPC and Logging"** is rendered **only
>   under Baselibs**, even though its title contains both "IPC" and
>   "Logging" (which would otherwise match Communication and Logging).
>   Drop `#549` from the Communication and Logging cells.
> - **`#757` "Feature request for qualified json-parser"** belongs to
>   **Baselibs** (label `ft:baselibs`). It has **no GitHub milestone**,
>   so the standard milestone filter (`"0.5"|"1.0" in title`) excludes
>   it; force-include it for Baselibs and render it without the `[…]`
>   milestone bracket.
> - **Communication scope is local IPC only.** Drop `#914` (SOME/IP
>   Gateway → Some/IP module) and `#917` (ABI compatible datatypes →
>   Baselibs) from the Communication cell, even though their title
>   keywords (`some/ip`, `abi compatible`) or labels could attribute
>   them. Communication renders only `#69 — Feature Request for IPC`.

### 4.1 PA5 — coverage CI keys

Coverage data is read from the latest successful run of workflow id
`234977097` (`Code Quality & Documentation`), job `test_and_docs`, in
`eclipse-score/reference_integration`.

| Tracker module | CPP key | Rust key |
|---|---|---|
| Baselibs | `score_baselibs_cpp` | `score_baselibs_rust_rust` |
| Communication | `score_communication_cpp` | — |
| Logging | `score_logging_cpp` | `score_logging_rust` |
| Persistency | `score_persistency_cpp` | `score_persistency_rust` |
| Lifecycle | `score_lifecycle_health_cpp` | `score_lifecycle_health_rust` |
| Time / Config Mgmt / Security/Crypto | not in CI | — |

```bash
RUN_ID=$(gh api "repos/eclipse-score/reference_integration/actions/workflows/234977097/runs?per_page=10" \
   --jq '[.workflow_runs[] | select(.conclusion=="success")][0].id')
JOB_ID=$(gh api "repos/eclipse-score/reference_integration/actions/runs/$RUN_ID/jobs" \
   --jq '.jobs[] | select(.name=="test_and_docs") | .id')
gh api "repos/eclipse-score/reference_integration/actions/jobs/$JOB_ID/logs" \
   | grep -A50 "COVERAGE ANALYSIS SUMMARY"
```

The log emits a single Python-dict dump after the
`=== QR: COVERAGE ANALYSIS SUMMARY ===` banner, e.g.

```text
{'score_baselibs_cpp': {'branches': '60.3%', 'exit_code': 0, 'functions': '85.4%', 'lines': '92.3%'},
 'score_logging_rust':  {'branches': 'NA',   'exit_code': 0, 'functions': '99.5%', 'lines': '74.4%'},
 ...}
```

Parse it with this regex (works for both cpp and rust keys; either field may be `'NA'`):

```python
COV_RE = re.compile(
    r"'(score_[a-z_]+)':\s*\{[^}]*'branches':\s*'([^']*)'"
    r"[^}]*'functions':\s*'([^']*)'"
    r"[^}]*'lines':\s*'([^']*)'")
```

### 4.2 PA5 — static / dynamic analysis CI table

> **Reader notes (rendered in the RST as `.. note::` blocks placed
> immediately after the PA5 `Rollout status` row and before
> the PA5 list-table — keep them in sync when regenerating):**
>
> 1. **C0/C1 Coverage source.** Coverage data comes from the
>    `reference_integration` CI (*Code Quality & Documentation* workflow,
>    `bazel coverage --config=ferrocene-coverage`). C0 = line coverage,
>    C1 = branch coverage. Rust coverage reports **line only**. Modules
>    not yet integrated into the `reference_integration` CI render
>    `❌ Open` (currently: Time, Config Mgmt, Security/Crypto, Some/IP —
>    update list each regen).
> 2. **Static / Dynamic semantics.** Static = per-module clang-tidy
>    (C++) / Clippy (Rust) workflows; Dynamic = sanitizer workflows
>    (`--config=asan_ubsan_lsan`, `--config=tsan`). All listed workflows
>    are **zero-tolerance** → a passing `main` ⇒ `✅ 0 findings`.
>    Central CodeQL runs in
>    `reference_integration/.github/workflows/codeql-multiple-repo-scan.yml`
>    (finding counts require the GitHub Security tab).

| Module | Static | Dynamic |
|---|---|---|
| Baselibs | ✅ `lint.yml` (clang-tidy) | ✅ `sanitizers_linux.yml` (ASan/UBSan/LSan) |
| Communication | 🔄 Configured (no CI) | ✅ ASan/UBSan/LSan + TSan |
| Logging | ❌ | ❌ |
| Persistency | ✅ `clippy.yml` | ❌ |
| Time | ❌ | ❌ |
| Config Mgmt | ✅ `static-analysis.yml` (clang-tidy) | ❌ |
| Lifecycle | ✅ `lint_clippy.yml` | ❌ |
| Security/Crypto | ❌ | ❌ |

Central CodeQL runs in `reference_integration/.github/workflows/codeql-multiple-repo-scan.yml`.

> **Link discipline:** The **Static** column renders the workflow YAML
> as a line-block link below the status emoji (so reviewers can click
> through to the actual configuration). The **Dynamic** column renders
> the **status only** (no link) — the dynamic-analysis CI is more
> heterogeneous (multiple sanitizer runs per repo, sometimes split across
> several workflow files) and listing one representative file would be
> misleading. Keep this asymmetry when regenerating.

---

## 5. RST formatting rules

### 5.0 Cross-reference labels (mandatory)

Each `Process Area N — …` heading **must** be preceded by an explicit
target label so that `pi1.rst`, `pi2.rst`, `pi3.rst` (and any future
release-gate page) can link back via `:ref:\`overall_status_paN\``:

```rst
.. _overall_status_pa2:

Process Area 2 — Requirements Engineering
-----------------------------------------
```

Required labels: `overall_status_pa1`, `overall_status_pa2`,
`overall_status_pa3`, `overall_status_pa4`, `overall_status_pa5`.
Omitting any of them produces Sphinx `WARNING: undefined label`
messages from the PI release-gate pages — a clean build is the
success criterion.

### 5.1 Cell layout

Status emoji + label on the **first line**; everything else (counts, links,
notes) goes on a **line-block** (`| `) after a blank line.

> **Pluralisation.** When emitting test counts, write `1 test` (singular)
> and `N tests` (plural). A naive `f"{n} tests"` will produce the wrong
> `1 tests` for Logging Feat. IT and any other 1-test cell:
>
> ```python
> def plur(n, s="test"):
>     return f"{n} {s}" if n == 1 else f"{n} {s}s"
> ```

```rst
   - ✅ Available (37/37)

     | `feature-level <https://.../docs/features/baselibs/docs/requirements/index.rst>`__
     | `abi-compatible-data-types <https://.../requirements.rst>`__
```

```rst
   - 🔄

     | **C0:** 92.3%
     | **C1:** 60.3% (cpp)
     | **Rust line:** 74.4%
```

> **PA5 test counts on a new line.** For the **Unit Tests**, **Comp. IT**
> and **Feat. IT** columns, the test count goes on its **own line-block
> line** below the status — never on the same line as `✅ Available`:
>
> ```rst
>      - ✅ Available
>
>             | 5376 tests
> ```
>
> Do **not** emit `✅ Available (5376 tests)` on a single line. The
> `(valid/total)` parenthetical form (§3, requirements/AoU columns) is
> unaffected.

> **Line-blocks inside table cells render flush-left.** Sphinx wraps an
> indented `| ...` continuation in a `<blockquote><div class="line-block">`
> which by default carries a left border + tinted background — visually
> noisy inside a status table. `docs/_assets/custom.css` neutralises this
> for `table … blockquote` and `table … .line-block` (zero margin/padding,
> `border: none`, `background: transparent`). Do **not** add per-cell
> raw-HTML wrappers to fight the styling — let the CSS rule do it.

When mentioning `:status: invalid` in prose, **always use double backticks**:
`` ``:status: invalid`` `` (single backticks are RST hyperlink syntax → parse warning).

### 5.2 Source links — mandatory

Every Req / Arch / Detailed-Design / Code / Inspection cell that is **not**
`❌ Open` **MUST** carry one or more source links directly below the count
line. Rules:

- One bullet per source RST file or per logical group (e.g. per module
  subfolder). **List every matching source** — Feature Req, Component Req,
  Feature Arch, Component Arch, Detailed Design, **and** Inspection cells
  use no link cap. Earlier revisions capped non-Inspection cells at ~4
  links; that rule is obsolete because the truncated cells (e.g. Baselibs
  with 10 components) hid components from the reader.
- **Link labels MUST be the component (or feature) name**, derived from
  the URL path. This applies to **all** cells with source links —
  Feature Req, Component Req, Feature Arch, Component Arch,
  Detailed Design, **and** Inspection cells. Do **not** use the bare
  filename (`index`, `requirements`, `aou_req`, `mw-fr_logging_req`,
  `chklst_req_inspection`, …) as the label.
- Algorithm to derive the label from a path:
  1. drop the filename;
  2. drop trailing segments `requirements` / `architecture` /
     `detailed_design` / `docs` / `component_requirements` /
     `feature_requirements`;
  3. use the last remaining path segment.

  Examples:

  | Path | Label |
  |---|---|
  | `docs/features/baselibs/docs/requirements/index.rst` | `baselibs` |
  | `docs/modules/baselibs/concurrency/docs/requirements/index.rst` | `concurrency` |
  | `docs/features/communication/ipc/docs/requirements/index.rst` | `ipc` |
  | `docs/persistency/kvs/requirements/index.rst` | `kvs` |
  | `docs/module/health_monitor/requirements/index.rst` | `health_monitor` |
  | `score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc` | `com` |
  | `docs/features/baselibs/docs/requirements/chklst_req_inspection.rst` | `baselibs` |
  | `docs/modules/baselibs/concurrency/docs/requirements/chklst_req_inspection.rst` | `concurrency` |

- Inspection cells (`Req. Inspection`, `Arch. Inspection`,
  `Impl. Inspection`) link the underlying `chklst_*_inspection.rst` files,
  not the parent index — readers want to click directly into the checklist
  whose `:status:` drives the cell.
- URLs **MUST** point to the pinned ref (40-char SHA from `known_good.json`),
  not `blob/main` — counts come from the pinned ref, and `main` may have been
  restructured. For repos not in `known_good.json` (`inc_time`,
  `config_management`, `inc_security_crypto`, `inc_someip_gateway`),
  `blob/main` is acceptable.
- For Communication `comp_req` link the `.trlc` file marked `[TRLC]`.
- **PA4 Code cell** links the **repository root** (e.g.
  `https://github.com/eclipse-score/baselibs`). The link label MUST be the
  repository name (last URL segment), **not** the literal word `repo` —
  e.g. `baselibs`, `communication`, `inc_time`, `config_management`,
  `inc_security_crypto`, `inc_someip_gateway`.
- **PA5 Static Analysis cell** is **status-only** — do NOT add links to
  CI workflow files or `quality/static_analysis` directories under the
  status. Same rule as Dynamic Analysis (§4.2).
- **PA5 Platform Verification Report** is a **single project-wide
  deliverable** — it does **not** get a per-module column. Render it as
  a prominent admonition immediately after the PA5 list-table (styled
  via `.platform-ver-report` in `docs/_assets/custom.css` — larger font,
  blue accent, so it can't be missed):

  ```rst
  .. admonition:: Platform Verification Report
     :class: important platform-ver-report

     `platform_ver_report
     <https://github.com/eclipse-score/score/blob/<pinned-sha>/
     docs/score_releases/verification/platform_ver_report.rst>`__
     — 🔄 **Draft** (single project-wide deliverable)
  ```

  Update the status emoji + label to match the report's current
  `:status:` field (✅ **Valid** / 🔄 **Draft**). Do **not** revert this
  to a plain `**bold paragraph**` — the admonition class is what makes
  it visually prominent.

### 5.3 Per-PA progress figures

Each Process Area embeds one SVG figure under `docs/_assets/`:

| PA  | File                              | `:width:`  |
|-----|-----------------------------------|------------|
| PA2 | `pa2_impl_progress.svg`           | `720px`    |
| PA3 | `pa3_arch_progress.svg`           | `720px`    |
| PA4 | `pa4_impl_progress.svg`           | `720px`    |
| PA5 | `pa5_verification_progress.svg`   | `1080px`   |

The PA5 verification figure is rendered at **1.5× the standard width**
(`1080px` instead of `720px`) because it carries four series across four
release columns and a 720px render makes the per-module test counts hard
to read. All other PAs keep the default 720px width.

```rst
.. figure:: /_assets/pa5_verification_progress.svg
   :alt: PA5 verification progress
   :width: 1080px

   Test counts and coverage across the 11 PA2 modules per release
   (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).
```

### 5.4 Pie chart row (Process Status)

Each PA section starts with a pie chart row. The section is introduced by a
**Process Status** rubric that uses the `status-heading` class for an
enlarged appearance (styles in `docs/_assets/custom.css`):

```rst
.. rubric:: Process Status
   :class: status-heading

.. list-table::
   :header-rows: 1
   :class: compact-overview-table

   * - Process req. status
     - ISO 26262 std_req status
     - Req. verification status
   * -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Valid, Draft, Invalid, Other
          :colors: LimeGreen, Gold, LightCoral, LightGray

          type == 'gd_req' and is_external == False and status == 'valid' and '<tag>' in tags
          type == 'gd_req' and is_external == False and status == 'draft' and '<tag>' in tags
          type == 'gd_req' and is_external == False and status == 'invalid' and '<tag>' in tags
          type == 'gd_req' and is_external == False and status not in ['valid', 'draft', 'invalid'] and '<tag>' in tags
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Ok, Recommendation, Open, Action, Deviation, N/A, Other
          :colors: LimeGreen, LightBlue, Gold, Orange, LightCoral, LightGray, Silver
          :filter-func: needs_filters.std_req_status_for_area(<tag>)
     -

       .. rst-class:: small-pie-cell

       .. needpie::
          :labels: Automated, Waiting for automation, Inspection list, Other
          :colors: LimeGreen, Gold, LightBlue, LightGray
          :filter-func: needs_filters.area_verification_status(<tag>)
```

Hard rules:
- `.. needpie::` does **not** support `:title:` (build error).
- Each cell needs `.. rst-class:: small-pie-cell` before its `.. needpie::`.
- Pie chart sizing is governed by `_assets/custom.css` (class
  `compact-overview-table`, fluid 33% per column, `!important` img override).
  Do not add explicit pixel sizes.

### 5.5 Rollout status row

Directly above the module tracker table, render a **single-line row** with
a label, percentage, an inline progress bar and a detail text. This
replaces the older `.. rubric:: Implementation status: ...` line. Use a
`raw:: html` block so the progress bar and the text sit on the same line:

```rst
.. raw:: html

   <div class="impl-status-row">
     <span class="impl-status-label">Rollout status:</span>
     <span class="impl-status-icon">🔄</span>
     <span class="impl-status-percent">NN%</span>
     <div class="impl-status-bar"><div class="impl-status-fill" style="width:NN%"></div></div>
     <span class="impl-status-detail">X/Y deliverables complete</span>
   </div>
```

- `X` = number of `✅ Available` cells in the table.
- `Y` = number of cells in the table excluding the leftmost stub column.
- `NN` = `floor(100 * X / Y)`, clamped to `[0, 100]`. Use the **same**
  value in both the `impl-status-percent` span and the
  `style="width:NN%"` of `impl-status-fill`.
- If `Y == 0`, render `NN = 0` (empty bar) and `0/0 deliverables complete`.
- Keep the wording **"Rollout status"** — not "Implementation status"
  (the term "implementation" is reserved for actual code).
- Styling lives in `docs/_assets/custom.css` (`.impl-status-row`,
  `.impl-status-bar`, `.impl-status-fill`). Do not inline additional
  styles beyond the `width:NN%` on the fill div.
- The `Process Status` rubric above the pie row uses the
  `:class: status-heading` option (see §5.4 above) so both headings have
  the same enlarged appearance.

---

## 6. Procedure

### Step 0 — Resolve pinned refs

```python
import json, base64, subprocess, re

def gh_raw(api_path, jq="."):
    r = subprocess.run(["gh", "api", api_path, "--jq", jq],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"gh api failed: {r.stderr}"
    return r.stdout.strip()

def gh_json_file(api_path):
    return json.loads(base64.b64decode(gh_raw(api_path, ".content")).decode())

known_good = gh_json_file(
    "repos/eclipse-score/reference_integration/contents/known_good.json")

def pinned_ref(module_key):
    """`score_platform` lives in `tooling`; everything else in `target_sw`."""
    all_mods = {**known_good["modules"]["target_sw"],
                **known_good["modules"]["tooling"]}
    entry = all_mods.get(module_key)
    return entry["hash"] if entry else "main"

REFS = {
    "score":               pinned_ref("score_platform"),
    "baselibs":            pinned_ref("score_baselibs"),
    "communication":       pinned_ref("score_communication"),
    "logging":             pinned_ref("score_logging"),
    "persistency":         pinned_ref("score_persistency"),
    "lifecycle":           pinned_ref("score_lifecycle_health"),
    "inc_time":            "main",
    "config_management":   "main",
    "inc_security_crypto": "main",
}
```

### Step 1 — Fetch repo trees

```python
def get_tree(repo, ref):
    out = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/trees/{ref}?recursive=1",
         "--jq", ".tree[].path"],
        capture_output=True, text=True)
    paths = [p for p in out.stdout.strip().split("\n") if p]
    assert paths, f"empty tree for {repo}@{ref}"
    return paths
```

### Step 2 — Count directives

```python
DIRECTIVE_TYPES = {
    "feat_req":  ("feat_req",),
    "comp_req":  ("comp_req", "aou_req"),
    "feat_arc":  ("feat", "feat_arc", "feat_arc_sta", "feat_arc_dyn"),
    "comp_arc":  ("comp", "comp_arc", "comp_arc_sta", "comp_arc_dyn",
                  "logic_arc_int", "logic_arc_int_op",
                  "real_arc_int", "real_arc_int_op"),
    "dd":        ("dd", "dd_sta", "dd_dyn"),
}

def fetch_file(repo, path, ref):
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return ""
    return base64.b64decode(r.stdout.strip()).decode(errors="replace")

def count_directives_with_status(content, allowed):
    """Return (valid, total) for `.. <type>::` blocks where type ∈ allowed,
    using the *indented* :status: field of each block. Document-level
    :status: at column 0 is ignored."""
    pat = re.compile(r'^\.\.\s+(' + '|'.join(allowed) + r')::', re.MULTILINE)
    valid = total = 0
    for m in pat.finditer(content):
        tail = content[m.end():]
        nxt = re.search(r'^\.\.\s+\w', tail, re.MULTILINE)
        block = tail[:nxt.start()] if nxt else tail
        st = re.search(r'^\s+:status:\s+(\w+)', block, re.MULTILINE)
        total += 1
        if st and st.group(1) == 'valid':
            valid += 1
    return valid, total

def count_checklist_status(content):
    """Status of the `.. document::` directive in a chklst_*.rst file.
    The :status: is indented inside the directive body, not at column 0."""
    m = re.search(r'^\.\.\s+document::', content, re.MULTILINE)
    if not m:
        return 0, 0
    tail = content[m.end():]
    nxt = re.search(r'^\.\.\s+\w', tail, re.MULTILINE)
    block = tail[:nxt.start()] if nxt else tail
    st = re.search(r'^\s+:status:\s+(\w+)', block, re.MULTILINE)
    if not st:
        return 0, 0
    return (1 if st.group(1) == 'valid' else 0), 1

def count_files(repo, paths, ref, path_filter, kind):
    """kind ∈ {'feat_req','comp_req','feat_arc','comp_arc','dd','chklst'}."""
    matched = [p for p in paths if path_filter(p)]
    tv = tt = 0
    for path in matched:
        content = fetch_file(repo, path, ref)
        if kind == 'chklst':
            v, t = count_checklist_status(content)
        else:
            v, t = count_directives_with_status(content, DIRECTIVE_TYPES[kind])
        tv += v; tt += t
    return tv, tt
```

### Step 3 — Render cells

```python
def cell(v, t):
    if t == 0: return "❌ Open"
    if v == t: return f"✅ Available ({v}/{t})"
    return f"🔄 {v*100//t}% ({v}/{t})"

def comp_req_cell(contents, *, trlc=False):
    cv = ct = av = at = 0
    for c in contents:
        v, t = count_directives_with_status(c, ('comp_req',)); cv+=v; ct+=t
        v, t = count_directives_with_status(c, ('aou_req',));  av+=v; at+=t
    if ct == 0 and at == 0: return "❌ Open"
    parts = []
    if ct or trlc: parts.append(f"{cv}/{ct} comp_req" + (" [TRLC]" if trlc else ""))
    if at:         parts.append(f"{av}/{at} AoU")
    body = " + ".join(parts)
    tot_v, tot_t = cv + av, ct + at
    if tot_v == tot_t: return f"✅ Available ({body})"
    return f"🔄 {tot_v*100//tot_t}% ({body})"
```

### Step 4 — Path filters (reference)

> **Component-level data may live in two repos at once.** Baselibs and
> Logging keep `comp_arc` directives both in `eclipse-score/score`
> (`modules/<area>/**`) **and** in their own repo (`docs/<area>/**`).
> Always query both filters and **sum** the `(valid, total)` tuples; never
> drop one source. The same is true for Persistency `kvs` (uses both
> `score/kvs/docs/<kind>` and the older `docs/persistency/kvs/<kind>`).
> Some/IP keeps `comp_req` partly in `docs/requirements/component/**` and
> partly in `docs/tc8_conformance/requirements.rst` — combine both.

| Module | Deliverable | Repo | Filter (`lambda p: ...`) |
|---|---|---|---|
| Baselibs | Feat. Req | score | `'features/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Comp. Req | score | `'modules/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Feat. Arch | score | `'features/baselibs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Comp. Arch | score | `'modules/baselibs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | *Inspections | score | `'baselibs' in p and 'chklst_<kind>' in p` |
| Communication | Feat. Req/Arch | score | `'features/communication' in p and '<requirements\|architecture>' in p and …` |
| Communication | Comp. Req/Arch | score | `'modules/communication' in p and …` |
| Logging | Feat. Req/Arch | score | `('features/logging' in p or 'features/analysis-infra/logging' in p) and …` |
| Logging | Comp. Req/Arch | score | `'modules/logging' in p and …` |
| Persistency | Feat. Req/Arch | score | `'features/persistency' in p and …` |
| Persistency | Comp. Req/Arch/DD | persistency | `'kvs' in p and …` |
| Lifecycle | Feat. Req/Arch | score | `'features/lifecycle' in p and …` *(must walk subfolders)* |
| Lifecycle | Comp. Req/Arch/DD | lifecycle | `'module' in p and …` |
| Time / Config Mgmt / Sec.Crypto | Feat. Req/Arch | score | `'features/<area>' in p and …` |

> **Lifecycle is the most complex module** — feature-level lives in
> `eclipse-score/score`, component-level (`docs/module/health_monitor/**`) in
> `eclipse-score/lifecycle`. Always query both and aggregate.

### Step 5 — Sanity checks (run **before** writing the RST)

#### 5a Structural — same modules, same columns

```python
def parse_rst_structure(rst_path):
    text = open(rst_path).read()
    parts = re.split(r'Process Area (\d+) —', text)[1:]
    out = {}
    for i in range(0, len(parts) - 1, 2):
        pa, body = f"PA{parts[i].strip()}", parts[i+1]
        hdr = re.search(r'\* - \*\*Module\*\*(.*?)(?=\n   \* -\s+\w)', body, re.DOTALL)
        cols = [c.strip() for c in re.findall(r'\*\*([^*]+)\*\*', hdr.group(0) if hdr else "") if c.strip() != 'Module']
        mods = [m.strip() for m in re.findall(r'\n   \* - ((?![\*\s])[\w][^\n]+)', body)]
        out[pa] = {'modules': mods, 'columns': cols}
    return out
```

Stop and investigate if:
- a module present before is missing now, or
- a column changed.

#### 5b Plausibility — diff each cell

| Old → New | Action |
|---|---|
| `✅` → `❌` or `🔄 NN%` → `❌` | 🛑 stop — almost certainly a filter bug |
| `✅` → `🔄` | ⚠️ investigate (regression) |
| `🔄 NN%` → `🔄 MM%`, MM<NN | ⚠️ investigate |
| `❌` → `🔄`/`✅` | ✅ confirm count is plausible |
| `🔄` → `✅` | ✅ confirm `valid == total` |
| LOC drop > 50 % | ⚠️ filter likely too strict |

### Step 6 — Write the RST

Update each PA's module table and the **Rollout status** `raw:: html`
block above it (see §5.5). Source links as in §5.2. Pie-chart row and the
`Process Status` rubric stay unchanged unless the sphinx-needs tag
changes.

### Step 7 — Adding a new module

1. Append to §1 module list and §2 repo table (with key + path filter).
2. Add a row to every PA table.
3. Re-run §6.

---

## 6a. Progress graphics (per-PA SVG charts above each table)

Above the module-tracker table of **PA2, PA3, PA4 and PA5** sits a `figure::`
that renders an inline SVG showing how the totals evolved across the four
most recent releases (`v0.5.0-beta → v0.6.0 → v0.7.0 → current main`).
Files live in `docs/_assets/`:

| PA | File | Bars |
|---|---|---|
| PA2 | `pa2_impl_progress.svg`        | Feature Req (`#1f77b4`), Component Req (`#ff7f0e`) |
| PA3 | `pa3_arch_progress.svg`        | Feature Arch (`#1f77b4`), Component Arch (`#ff7f0e`) |
| PA4 | `pa4_impl_progress.svg`        | Estimated LOC (`#1f77b4`) |
| PA5 | `pa5_verification_progress.svg`| 3 panels: Unit Tests, Integration Tests (Component `#ff7f0e` + Feature `#9467bd`), Coverage now (`#17becf`) |

Each figure embeds in RST as

```rst
.. figure:: /_assets/<file>.svg
   :alt: ...
   :width: 720px

   <caption sentence ending with "(v0.5.0-beta → v0.6.0 → v0.7.0 → current main)".>
```

### 6a.1 Release pinning

Resolve the four release SHAs once via the GitHub tag refs (annotated tags
must be dereferenced):

```python
def resolve_tag(repo, tag):
    d = json.loads(gh_raw(f"repos/{repo}/git/refs/tags/{tag}"))
    sha = d["object"]["sha"]
    if d["object"]["type"] == "tag":
        d2 = json.loads(gh_raw(f"repos/{repo}/git/tags/{sha}"))
        sha = d2["object"]["sha"]
    return sha
```

For each release tag of `eclipse-score/reference_integration`, fetch its
`known_good.json` and read the per-module hash. Schemas differ:

- v0.5 / v0.6: `modules.<key>.{hash,version}` flat
- v0.7+:       `modules.{target_sw,tooling}.<key>.hash`
- v0.7.0 itself only carries `version` for some entries → fall back to
  `resolve_tag(<owner/repo>, "v"+version)`.

`now` is the per-module SHA from `known_good.json` on the **`main` branch of
`eclipse-score/reference_integration`** (not the working tree). Fetch it via
`gh api repos/eclipse-score/reference_integration/contents/known_good.json` —
this keeps the charts reproducible regardless of local uncommitted changes
or temporary ref bumps in the workspace.

Module repos used for the charts:

```
score:             eclipse-score/score              (key: score_platform / "score")
baselibs:          eclipse-score/baselibs           (key: score_baselibs)
communication:     eclipse-score/communication      (key: score_communication)
logging:           eclipse-score/logging            (key: score_logging)
persistency:       eclipse-score/persistency        (key: score_persistency)
lifecycle:         eclipse-score/lifecycle          (key: score_lifecycle_health)
inc_time:          eclipse-score/inc_time           (only "now")
config_management: eclipse-score/config_management  (only "now")
inc_security_crypto: eclipse-score/inc_security_crypto (only "now")
inc_someip_gateway:  eclipse-score/inc_someip_gateway  (only "now")
```

### 6a.2 Metrics — what each chart sums

All four charts sum across the **11 PA2 modules** (Baselibs, Communication,
Logging, Persistency, Time, Config Mgmt, Lifecycle, Security/Crypto,
Diagnostic Services, NM, Some/IP). Modules whose data isn't in a release
contribute 0.

> **Communication vs. Some/IP — never double-count.**
> Some/IP and Communication are **separate** modules even though Some/IP
> lives at `docs/features/communication/some_ip_gateway/**` inside the score
> repo. Whenever a path filter for Communication includes
> `'features/communication' in p` (or its `modules/` counterpart), it
> **MUST also exclude** `some_ip_gateway`:
>
> ```python
> def is_comm(p):
>     return ('features/communication' in p
>             and 'some_ip_gateway' not in p)
> ```
>
> Some/IP gets its own filter that requires `some_ip_gateway` in the path
> plus its own repo `eclipse-score/inc_someip_gateway` for component-level
> data. The rule applies to **every** PA — PA2 (FR/CR), PA3 (FA/CA),
> PA4 (LOC, DD, code links) and PA5 (unit tests, integration tests, coverage).
> For PA4/PA5 the separation is usually automatic because Some/IP code lives
> in its own repo (`inc_someip_gateway`); but whenever a counter walks the
> Communication module repo (`eclipse-score/communication`) or the score
> repo's `features/communication/**` / `modules/communication/**` subtree,
> the `'some_ip_gateway' not in p` guard MUST be present.

| Chart | Metric | Source |
|---|---|---|
| PA2 — Feature Req | sum of `count_directives_with_status(..., DIRECTIVE_TYPES["feat_req"])` totals (denominator) | per-module `path_filter` from §4 |
| PA2 — Component Req | analogous, `comp_req` + `aou_req` | per-module `path_filter` |
| PA3 — Feature Arch | analogous, `DIRECTIVE_TYPES["feat_arc"]` | per-module under `architecture` |
| PA3 — Component Arch | analogous, `DIRECTIVE_TYPES["comp_arc"]` | per-module under `architecture` |
| PA4 — LOC | `sum(blob.size for path in tree if is_src(path)) / 30` (rounded) | each module's own repo at the release SHA |
| PA5 — Unit Tests (historical) | count of `TEST(`, `TEST_F(`, `TEST_P(`, `TYPED_TEST(`, `TYPED_TEST_P(` macros plus Rust `#[test]` and Python `^def test_` in files matching `is_test_path` | each module's own repo |
| PA5 — Comp. IT (historical) | same counters in files where path contains `integration` | each module's own repo |
| PA5 — Feat. IT (historical) | same counters in `feature_integration_tests/` and `platform_integration_tests/` | `eclipse-score/reference_integration` at the release tag |
| PA5 — Unit / Comp. IT / Feat. IT (**now** column) | **column sum** of the corresponding cells in the PA5 RST table (the `| N tests` line-block annotations) | parsed from `overall_status.rst` |
| PA5 — C0/C1 now | weighted mean of per-module C0 and C1 from the current PA5 RST table, weights = unit-test count per module | parsed from `overall_status.rst` |

> **PA5 test counts: table is the source of truth for "now".**
> The four releases use **two different sources** for the test-count bars:
> - `v0.5.0-beta`, `v0.6.0`, `v0.7.0` → macro-based regex over module repo
>   sources (Best-Effort, no curated table available for past tags).
> - `now` → **sum of the `| N tests` line-block annotations in the PA5 RST table**
>   (`Unit Tests`, `Comp. Integration Tests`, `Feature Integration Tests`
>   columns), because the curated table is what users see.
>
> The two methods diverge for several reasons that are NOT bugs:
> 1. Some/IP integration tests are named `stress_tests/` not `integration*`,
>    so the historical regex misses them; the table includes them.
> 2. Feature-Integration counts in the table are **per module** (i.e. how
>    many of the cross-module `reference_integration` tests exercise that
>    module), not the total `feature_integration_tests/` tree size — so
>    the table sum (≈7) is much smaller than the tree-walk total (≈59).
> 3. Some modules have CI test-run counts in the table that don't match
>    `TEST(...)` macro counts (parameterized tests count as one macro but
>    many runs).
>
> Practical rule: when updating the SVG, run both the §6a recipe **and**
> sum the `| N tests` line-block cells from the RST. Use the recipe values for the
> three release bars and the **table sum** for `now`. Note the divergence
> in the caption / commit message if it's >10 %.

> **Charts count TOTAL, not valid-only.**
> The progress bars must use the **total** count of directives (denominator
> from §3) — i.e. every `feat_req` / `comp_req` / `feat_arc` / `comp_arc`
> block irrespective of `:status:`. This is intentional and differs from
> the per-cell tracker logic in the tables, which renders `valid/total`.
> Rationale: the charts visualise *scope growth* across releases, not
> validation maturity. Drafts and invalids count.
>
> Practical consequence: use `count_directives_with_status(...)[1]` (returns total only),
> **never** the full return value of `count_directives_with_status(...)` for chart numbers. This is
> particularly important for Lifecycle, whose feature-level requirements
> were largely `:status: draft` or `:status: invalid` in v0.5/v0.6 — a
> valid-only counter would report 0 instead of ~92.

LOC source-file filter:

```python
SRC_EXT = (".cpp", ".cc", ".cxx", ".c", ".h", ".hpp", ".hh", ".rs", ".py")
def is_src(p):
    pl = p.lower()
    if not pl.endswith(SRC_EXT): return False
    if pl.startswith("docs/") or "/docs/" in pl: return False
    if pl.startswith("third_party/") or "/third_party/" in pl: return False
    if pl.startswith("bazel-"): return False
    return True

def is_test_path(p):
    pl = p.lower()
    if any(pl.startswith(x) or "/"+x in "/"+pl
           for x in ("docs/","third_party/","bazel-",".git/")):
        return False
    return any(t in pl for t in
               ("_test.","/test/","/tests/","_tests.","gtest","unit_test","unittest"))
```

### 6a.3 Generating / updating the SVGs

The SVGs are hand-written (no toolchain). Workflow:

1. Compute totals (one Python script per chart, using `gh api` with the
   on-disk cache `/tmp/status_cache/`). Write `/tmp/release_totals.json`,
   `/tmp/release_totals_pa3_pa4.json`, `/tmp/release_totals_pa5.json`.
2. Update the bar `y`/`height` values and the printed numbers inside the
   existing SVG. The chart frames stay fixed; only the bars and labels
   change.
3. Bar heights use linear scale anchored at the panel's plot area. For PA2
   `viewBox="0 0 720 320"` with plot area `x=70..690, y=50..260` (height
   210 px), max value 400 → `y = 260 − value · 0.525`,
   `height = 260 − y`. PA3 uses max 240 (`× 0.875`), PA4 uses max 900 000
   (`× 0.0002333`), PA5 panels: Unit `× 0.021`, Integration `× 2.1`,
   Coverage `× 2.1`.

When a metric goes out of the chart's current range, raise the y-axis max
and rescale **all four bars** of that panel; do not crop.

### 6a.4 Caption discipline

Caption template per chart:

> `<Metric description> across the 11 PA2 modules per release
> (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).`

Always write "across the 11 PA2 modules" (not "across all modules") — the
charts intentionally exclude orchestrator, baselibs_rust, score_platform,
docs_as_code, kyron and other repos that don't appear in the PA tables.

---

## 7. Limitations

- Test coverage of requirements (link analysis) is not detected — needs
  `needs.json`.
- Per-module CI workflows are zero-tolerance; "passing on `main` ⇒ 0 findings"
  is the only signal used for static / dynamic analysis.
- Central CodeQL finding counts require the GitHub Security tab.
- Feature-Integration-Test heuristic is path-based and weak — confirm
  manually.
- TRLC content is not parsed; cells reference the `.trlc` file via link only.
- PA4 LOC bars are an estimate (`tree blob bytes ÷ 30`) since `gh api`
  exposes blob sizes but not line counts; expect ±10 % vs `cloc`.
- PA5 historical coverage is not available — only the current snapshot.
- PA5 test-count bars use **two sources**: the three release bars come
  from a TEST-macro regex over module repos (Best-Effort), the `now` bar
  is the **column sum of the RST table cells**. Expect divergences of
  10–20 % between the methods (parameterized tests, naming conventions
  like Some/IP `stress_tests/`, per-module cross-feature attribution).
  Lifecycle has only C0; modules without coverage in CI (Time, Config Mgmt,
  Security/Crypto, Some/IP, NM, Diagnostic Services) are excluded from the
  weighted mean.
