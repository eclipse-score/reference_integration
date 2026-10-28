# Common Reference — shared engine for all Process Areas

This file holds everything that is **not** specific to a single Process Area:
scope, repositories, the counting model, RST formatting rules, the shared
procedure, the progress-graphics workflow and the known limitations.

Per-PA details live in the sibling files:

| PA | File | Topic |
|----|------|-------|
| PA1 | [pa1-change-management.md](./pa1-change-management.md) | CR approved (Feature Request issues) |
| PA2 | [pa2-requirements.md](./pa2-requirements.md) | Feature/Component Req + Req. Inspection |
| PA3 | [pa3-architecture.md](./pa3-architecture.md) | Feature/Component Arch + Arch. Inspection |
| PA4 | [pa4-implementation.md](./pa4-implementation.md) | SW Dev Plan, Code/LOC, Detailed Design, Impl. Inspection |
| PA5 | [pa5-verification.md](./pa5-verification.md) | Tests, Coverage, Static/Dynamic, Module Ver. Report |

---

## C1. Scope & modules

Tracked modules (one table row each, in this order):

```
Baselibs · Communication · Logging · Persistency · Time · Config Mgmt
Lifecycle · Security/Crypto · Diagnostic Services · NM · Some/IP
```

Excluded: **Orchestrator** — never add a row for it.

Five process areas, each with its own table:

| PA | Title | sphinx-needs tag | Columns |
|---|---|---|---|
| PA1 | Change Management | `change_management` | CR approved |
| PA2 | Requirements Engineering | `requirements_engineering` | Feature Req · Component Req · Req. Inspection |
| PA3 | Architecture Design | `architecture_design` | Feature Arch · Component Arch · Arch. Inspection |
| PA4 | Implementation | `implementation` | SW Dev Plan · Code · Detailed Design · Impl. Inspection |
| PA5 | Verification | `verification` | Unit Tests · C0/C1 Cov · Comp. IT · Feat. IT · Static · Dynamic · Module Ver. Rpt |

> **PA1-only modules: Diagnostic Services and NM.** Both have a row in every
> PA table for layout consistency, but only the PA1 column carries real data.
> Full handling is documented in [pa1-change-management.md](./pa1-change-management.md);
> their PA2–PA5 cells render `❌ Open` and they contribute `0` to the per-PA
> progress charts (see [C6](#c6-progress-graphics-per-pa-svg-charts)) and are
> excluded from the coverage weighted mean (see [C7](#c7-limitations)).

---

## C2. Repos and pinned refs

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

> **No row for Diagnostic Services or NM** — see [C1](#c1-scope--modules). They
> are PA1-only; PA2–PA5 cells render `❌ Open` until their own repos /
> `known_good.json` keys exist, at which point a row must be added here **and**
> in the relevant PA path-filter table.

> `eclipse-score/score` itself is pinned under key **`score_platform`** in the
> **`tooling`** section of `known_good.json` (not `target_sw`). Use the helper
> `pinned_ref()` in [Step 0](#step-0--resolve-pinned-refs).

> **TRLC files** (`.trlc`) are not parsed by this skill. `eclipse-score/communication`
> keeps real component requirements in
> `score/mw/com/requirements/component_requirements/component_requirements_ipc.trlc`;
> render them in the cell as `0/0 comp_req [TRLC]` plus a link.

---

## C3. Counting model

For each deliverable column a set of allowed directive types is defined
(see [C3.1](#c31-allowed-directive-types-per-deliverable)). For every RST file
under the deliverable's path filter, count the `.. <type>::` directive blocks
whose immediately-following indented `:status:` field equals `valid`
(= **valid**) and the total number of such blocks regardless of status
(= **total**). Sum both numbers across all files.

The cell renders as:

| Condition | Output |
|---|---|
| total = 0 | `❌ Open` |
| valid = total > 0 | `✅ Available (valid/total)` |
| 0 ≤ valid < total | `🔄 NN% (valid/total)`, `NN = floor(100 · valid / total)` |

> valid = 0 with total > 0 renders as `🔄 0% (0/total)`, **never** `❌ Open`.
> `❌ Open` means *no files / no directives found at all*.

### C3.1 Allowed directive types per deliverable

| Deliverable | Directive types in `A` | PA |
|---|---|---|
| Feature Requirements | `feat_req` | PA2 |
| Component Requirements | `comp_req`, `aou_req` | PA2 |
| Feature Architecture | `feat`, `feat_arc`, `feat_arc_sta`, `feat_arc_dyn` | PA3 |
| Component Architecture | `comp`, `comp_arc`, `comp_arc_sta`, `comp_arc_dyn`, `logic_arc_int`, `logic_arc_int_op`, `real_arc_int`, `real_arc_int_op` | PA3 |
| Detailed Design | `dd`, `dd_sta`, `dd_dyn` | PA4 |
| Req./Arch./Impl. Inspection | document-level `:status:` of each `chklst_*.rst` (one per file) | PA2/3/4 |

Never counted as Req/Arch directives: `stkh_req`, `tool_req`, `document`,
`needtable`, `needpie`, `needextend`, `figure`, `uml`, `note`, `attention`,
`toctree`, `grid`. AoUs (`aou_req`) count for **Component** Req only, never for
Feature Req.

### C3.2 Component Requirements split rendering

Component Requirements counts both `comp_req` and `aou_req` but **renders them
split** so the reader sees what fraction is real component requirements vs.
Assumptions of Use (rendered by `comp_req_cell()`, see
[Step 3](#step-3--render-cells)):

```
✅ Available (84/84 comp_req + 32/32 AoU)
✅ Available (0/0 comp_req [TRLC] + 33/33 AoU)   ← Communication: comp_req live in .trlc
✅ Available (35/35 comp_req)                     ← no AoUs
🔄 0% (0/1 comp_req + 0/1 AoU)                    ← mixed, none valid
```

If both subtotals are zero → `❌ Open`.

### C3.3 Inspections

Each `chklst_*.rst` file contains a single `.. document::` directive whose
indented `:status:` field is treated as the document status. Each file
contributes `(1, 1)` if `:status: valid`, else `(0, 1)`. Files without any
`:status:` field contribute `(0, 0)`.

> **Lines of Code (PA4 Code column)** is a counting variant that uses byte
> size instead of directive blocks. It is documented with the PA4 deliverables
> in [pa4-implementation.md](./pa4-implementation.md), and shares the `is_src`
> filter defined in [C6.2](#c62-metrics--what-each-chart-sums).

---

## C4. RST formatting rules

### C4.0 Cross-reference labels (mandatory)

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

### C4.1 Cell layout

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
> `(valid/total)` parenthetical form ([C3](#c3-counting-model),
> requirements/AoU columns) is unaffected.

> **Line-blocks inside table cells render flush-left.** Sphinx wraps an
> indented `| ...` continuation in a `<blockquote><div class="line-block">`
> which by default carries a left border + tinted background — visually
> noisy inside a status table. `docs/_assets/custom.css` neutralises this
> for `table … blockquote` and `table … .line-block` (zero margin/padding,
> `border: none`, `background: transparent`). Do **not** add per-cell
> raw-HTML wrappers to fight the styling — let the CSS rule do it.

When mentioning `:status: invalid` in prose, **always use double backticks**:
`` ``:status: invalid`` `` (single backticks are RST hyperlink syntax → parse warning).

### C4.2 Source links — mandatory

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
  status. Same rule as Dynamic Analysis (see
  [pa5-verification.md](./pa5-verification.md)).
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

### C4.2.1 Per-link status markers — Inspection & Report cells (mandatory)

Inspection cells (`Req. Inspection`, `Arch. Inspection`, `Impl. Inspection`)
and the **Module Verification Report** cells routinely list many source
links (Baselibs alone has 10 checklists per inspection column). A reader
cannot tell which checklist is finished from the aggregate `3/10` count
alone. Therefore **every source link in these cells MUST be prefixed with a
status marker** derived from the *linked* file's document-level `:status:`
(the same `:status:` that drives the cell count — see
[C3.3](#c33-inspections)):

| Linked file `:status:` | Marker |
|---|---|
| `valid`                | ✅ |
| `draft`                | 🔄 |
| `invalid`              | ❌ |
| missing / no `:status:`| ⚠️ (investigate — usually a wrong path) |

Format — the marker sits **between** the line-block bar and the backtick:

```rst
   - 🔄 30% (3/10)

     | ✅ `baselibs <…/docs/requirements/chklst_req_inspection.rst>`__
     | ✅ `bitmanipulation <…/docs/requirements/chklst_req_inspection.rst>`__
     | 🔄 `concurrency <…/docs/requirements/chklst_req_inspection.rst>`__
```

Hard rules:
- Applies to **every** cell whose links point at `chklst_*_inspection.rst`
  files (`Req./Arch./Impl. Inspection`) **and** at
  `module_verification_report.rst` / `platform_ver_report.rst` files.
- The marker reflects the **document-level** `:status:` of the *linked*
  file (parse with `count_checklist_status`, see
  [Step 2](#step-2--count-directives)), **not** the aggregate cell status.
- Self-check: the number of ✅ markers in a cell **MUST equal** the `valid`
  numerator of that cell (e.g. `3/10` ⇒ exactly three ✅). A mismatch means
  a stale marker or a wrong link.
- Requirements / Architecture / Detailed-Design / Code cells (which link
  `index.rst` requirement/architecture files, **not** checklists) do **not**
  get per-link markers — only inspection and report links do.
- Markers are additive to the existing link rules ([C4.2](#c42-source-links--mandatory)):
  keep the component-name label, the pinned-ref URL and the no-cap listing.

Helper (renders one marked inspection/report link):

```python
INSP_MARK = {"valid": "✅", "draft": "🔄", "invalid": "❌"}

def insp_link(label, url, status):
    """status is the document :status: of the linked chklst_*/report file,
    from count_checklist_status()'s underlying :status: match."""
    return f"| {INSP_MARK.get(status, '⚠️')} `{label} <{url}>`__"
```

### C4.3 Per-PA progress figures

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

### C4.4 Pie chart row (Process Status)

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

### C4.5 Rollout status row

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
  `:class: status-heading` option (see [C4.4](#c44-pie-chart-row-process-status)
  above) so both headings have the same enlarged appearance.

---

## C5. Procedure (shared steps)

The per-PA cell criteria and path filters live in each PA file. The steps
below are the shared machinery used across all PAs.

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

### Step 4 — Path filters

The concrete per-module path filters live in each PA file (PA2/PA3/PA4).
The following cross-cutting rules apply to **all** of them:

> **Component-level data may live in two repos at once.** Baselibs and
> Logging keep `comp_arc` directives both in `eclipse-score/score`
> (`modules/<area>/**`) **and** in their own repo (`docs/<area>/**`).
> Always query both filters and **sum** the `(valid, total)` tuples; never
> drop one source. The same is true for Persistency `kvs` (uses both
> `score/kvs/docs/<kind>` and the older `docs/persistency/kvs/<kind>`).
> Some/IP keeps `comp_req` partly in `docs/requirements/component/**` and
> partly in `docs/tc8_conformance/requirements.rst` — combine both.

> **Lifecycle is the most complex module** — feature-level lives in
> `eclipse-score/score`, component-level (`docs/module/health_monitor/**`) in
> `eclipse-score/lifecycle`. Always query both and aggregate.

> **Communication vs. Some/IP — never double-count.** Some/IP and
> Communication are **separate** modules even though Some/IP lives at
> `docs/features/communication/some_ip_gateway/**` inside the score repo.
> Whenever a path filter for Communication includes `'features/communication'
> in p` (or its `modules/` counterpart), it **MUST also exclude**
> `some_ip_gateway`:
>
> ```python
> def is_comm(p):
>     return ('features/communication' in p
>             and 'some_ip_gateway' not in p)
> ```
>
> Some/IP gets its own filter that requires `some_ip_gateway` in the path
> plus its own repo `eclipse-score/inc_someip_gateway` for component-level
> data. The rule applies to **every** PA.

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
block above it (see [C4.5](#c45-rollout-status-row)). Source links as in
[C4.2](#c42-source-links--mandatory). Pie-chart row and the `Process Status`
rubric stay unchanged unless the sphinx-needs tag changes.

**Always update the data collection date** at the top of
`docs/s_core_v_1/roadmap/overall_status.rst` to the date the refresh was
performed (UTC, ISO format `YYYY-MM-DD`). The date lives in an
`important` admonition directly below the page title:

```rst
Overall Status
==============

.. important::

   **Data collected on: YYYY-MM-DD**
```

If the admonition is missing, add it. Never leave a stale date — every
regeneration must bump it, even if no module values changed.

### Step 7 — Adding a new module

1. Append to [C1](#c1-scope--modules) module list and
   [C2](#c2-repos-and-pinned-refs) repo table (with key + path filter).
2. Add a row to every PA table and the matching path filters in the PA files.
3. Re-run [Step 6](#step-6--write-the-rst).

---

## C6. Progress graphics (per-PA SVG charts above each table)

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

### C6.1 Release pinning

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

### C6.2 Metrics — what each chart sums

All four charts sum across the **11 PA2 modules** (Baselibs, Communication,
Logging, Persistency, Time, Config Mgmt, Lifecycle, Security/Crypto,
Diagnostic Services, NM, Some/IP). Modules whose data isn't in a release
contribute 0. The Communication-vs-Some/IP separation rule of
[Step 4](#step-4--path-filters) applies to **every** chart metric.

| Chart | Metric | Source |
|---|---|---|
| PA2 — Feature Req | sum of `count_directives_with_status(..., DIRECTIVE_TYPES["feat_req"])` totals (denominator) | per-module `path_filter` from PA2 |
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
> Practical rule: when updating the SVG, run both the C6 recipe **and**
> sum the `| N tests` line-block cells from the RST. Use the recipe values for the
> three release bars and the **table sum** for `now`. Note the divergence
> in the caption / commit message if it's >10 %.

> **Charts count TOTAL, not valid-only.**
> The progress bars must use the **total** count of directives (denominator
> from [C3](#c3-counting-model)) — i.e. every `feat_req` / `comp_req` /
> `feat_arc` / `comp_arc` block irrespective of `:status:`. This is
> intentional and differs from the per-cell tracker logic in the tables,
> which renders `valid/total`. Rationale: the charts visualise *scope growth*
> across releases, not validation maturity. Drafts and invalids count.
>
> Practical consequence: use `count_directives_with_status(...)[1]` (returns total only),
> **never** the full return value of `count_directives_with_status(...)` for chart numbers. This is
> particularly important for Lifecycle, whose feature-level requirements
> were largely `:status: draft` or `:status: invalid` in v0.5/v0.6 — a
> valid-only counter would report 0 instead of ~92.

LOC source-file filter (shared with the PA4 Code cell, see
[pa4-implementation.md](./pa4-implementation.md)):

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

### C6.3 Generating / updating the SVGs

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

### C6.4 Caption discipline

Caption template per chart:

> `<Metric description> across the 11 PA2 modules per release
> (v0.5.0-beta → v0.6.0 → v0.7.0 → current main).`

Always write "across the 11 PA2 modules" (not "across all modules") — the
charts intentionally exclude orchestrator, baselibs_rust, score_platform,
docs_as_code, kyron and other repos that don't appear in the PA tables.

---

## C7. Limitations

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
