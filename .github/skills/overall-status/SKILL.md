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

Five process areas, each with its own table:

| PA | Title | sphinx-needs tag | Columns |
|---|---|---|---|
| PA1 | Change Management | `change_management` | CR approved |
| PA2 | Requirements Engineering | `requirements_engineering` | Feature Req · Component Req · Req. Inspection |
| PA3 | Architecture Design | `architecture_design` | Feature Arch · Component Arch · Arch. Inspection |
| PA4 | Implementation | `implementation` | SW Dev Plan · Code · Detailed Design · Impl. Inspection |
| PA5 | Verification | `verification` | Unit Tests · C0/C1 Cov · Comp. IT · Feat. IT · Static · Dynamic · Module Ver. Rpt · Platform Ver. Rpt |

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

```rst
   - ✅ Available (~12,500 LOC) `repo <https://github.com/eclipse-score/<repo>>`__
```

---

## 4. Per-deliverable status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **PA1** CR approved | Closed GitHub issue tagged "Feature/Contribution Request" for the module exists in `eclipse-score/score` | — | No such issue |
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
| **PA5** Feature Integration Tests | `integration_test_scenarios` / `feature*test*` paths in repo | — | none |
| **PA5** Static Analysis | zero-tolerance per-module CI workflow passes on `main` (clang-tidy / Clippy) | tools configured but no CI enforcement | no static-analysis config |
| **PA5** Dynamic Analysis | zero-tolerance sanitizer CI passes on `main` | — | no sanitizer CI |
| **PA5** Module Ver. Report | `verification/module_verification_report.rst` `:status: valid` and contains data | `:status: draft` | absent or template only |
| **PA5** Platform Ver. Report | `eclipse-score/score: docs/score_releases/verification/platform_ver_report.rst` `:status: valid` (same status in every row) | `:status: draft` | absent or template only |

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

### 4.2 PA5 — static / dynamic analysis CI table

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

---

## 5. RST formatting rules

### 5.1 Cell layout

Status emoji + label on the **first line**; everything else (counts, links,
notes) goes on a **line-block** (`| `) after a blank line.

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

When mentioning `:status: invalid` in prose, **always use double backticks**:
`` ``:status: invalid`` `` (single backticks are RST hyperlink syntax → parse warning).

### 5.2 Source links — mandatory

Every Req / Arch / Detailed-Design / Code cell that is **not** `❌ Open`
**MUST** carry one or more source links directly below the count line. Rules:

- One bullet per source RST file or per logical group (e.g. per module
  subfolder).
- URLs **MUST** point to the pinned ref (40-char SHA from `known_good.json`),
  not `blob/main` — counts come from the pinned ref, and `main` may have been
  restructured. For repos not in `known_good.json` (`inc_time`,
  `config_management`, `inc_security_crypto`, `inc_someip_gateway`),
  `blob/main` is acceptable.
- For Communication `comp_req` link the `.trlc` file marked `[TRLC]`.

### 5.3 Pie chart row (Process Status)

Each PA section starts with a pie chart row.

```rst
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

### 5.4 Implementation status rubric

Directly above the module tracker table:

```rst
.. rubric:: Implementation status: 🔄 NN% (X/Y deliverables complete)
```

`X` = number of `✅ Available` cells in the table; `Y` = number of cells in
the table excluding the leftmost stub column. Both rubrics in a PA section
(`Process Status` and `Implementation status`) are inline text, not headings.

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
    parts = []
    if ct or trlc: parts.append(f"{cv}/{ct} comp_req" + (" [TRLC]" if trlc else ""))
    if at:         parts.append(f"{av}/{at} AoU")
    if not parts:  return "❌ Open"
    body = " + ".join(parts)
    tot_v, tot_t = cv + av, ct + at
    if tot_t == 0 or tot_v == tot_t: return f"✅ Available ({body})"
    return f"🔄 {tot_v*100//tot_t}% ({body})"
```

### Step 4 — Path filters (reference)

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

Update each PA's module table and the `.. rubric:: Implementation status:`
line. Source links as in §5.2. Pie-chart row stays unchanged unless the
sphinx-needs tag changes.

### Step 7 — Adding a new module

1. Append to §1 module list and §2 repo table (with key + path filter).
2. Add a row to every PA table.
3. Re-run §6.

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
