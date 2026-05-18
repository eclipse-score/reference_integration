---
name: overall-status
description: "Update the Feature and Process Status table in docs/s_core_v_1/roadmap/overall_status.rst. Use when: checking module status, updating feature status tracker, refreshing work product status, deriving completion status from eclipse-score GitHub repos for Baselibs, Communication, Logging, Orchestrator, Persistency, Time, Config Management, Lifecycle, Security/Crypto."
argument-hint: "optional: module name or 'all'"
---

# Feature and Process Status Tracker

Derives and updates the completion status table in
`docs/s_core_v_1/roadmap/overall_status.rst` by querying the live eclipse-score GitHub
repositories.

> **Navigation (updated 2026-05)**: `overall_status.rst` is linked from
> `docs/s_core_v_1/roadmap/roadmap.rst` under the **Status & Goals** toctree section.
> The file was moved from `docs/s_core_v_1/status/` to `docs/s_core_v_1/roadmap/`.
> The `status/` folder has been removed. The roadmap itself is split into sub-pages:
> `roadmap.rst`, `pi1.rst` – `pi4.rst`, `overall_status.rst`, all under `docs/s_core_v_1/roadmap/`.

## When to Use

- Refresh the tracker table with current data
- After a sprint/release to check progress
- When a module team reports a deliverable is done

## RST File Structure

`docs/s_core_v_1/roadmap/overall_status.rst` consists of a file header followed by 5
Process Area sections. Each section has this exact pattern:

```rst
Process Area N — <Name>
***********************

<Description paragraph.>
<Work products line (optional).>
See :ref:`<workflow_ref>`.

.. rubric:: Process Status

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

.. rubric:: Implementation status: 🔄 NN% (X/Y deliverables complete)

.. list-table::
   :header-rows: 1
   :stub-columns: 1
   :class: module-phase-tracker-table

   * - **Module**
     - **<Deliverable 1>**
     - **<Deliverable 2>**

   * - <Module name>
     - <status>
     ...
```

**Important rules:**
- `.. needpie::` does **NOT** support a `:title:` option — omit it entirely (causes build errors)
- The pie chart table uses CSS class `compact-overview-table`; each cell needs `.. rst-class:: small-pie-cell` before its `.. needpie::`
- **Pie chart sizing**: `custom.css` sets `compact-overview-table` to `width: 100%; table-layout: fixed` with each column at `width: 33%`. The generated `<img>` elements have their sphinx-needs fixed pixel sizes overridden via `width: 100% !important; max-width: 100% !important; height: auto !important` (selectors: `.small-pie-cell img`, `.compact-overview-table td img`, `img[id^="needpie-"]`). **Do NOT add explicit pixel sizes** — this causes horizontal scrolling.
- The module tracker table uses CSS class `module-phase-tracker-table`
- Both `.. rubric::` directives are plain inline text — NOT RST section headings
- The `.. rubric:: Implementation status:` line is computed (see Step 4 in Procedure) and placed directly before the module tracker table
- **Formatting rule for table cells** — applies to ALL process areas:
  - **First line**: status label only (emoji + keyword), e.g. `✅ 0 findings`, `✅ Available`, `🔄 Configured`, `🔄 **C0:** 92.3%`, `❌ Open`
  - **Further lines** (test counts, links, C1/Rust coverage, comments): each on its own RST **line-block** (`| `) entry after a blank line. Examples:
    ```rst
       - ✅ Available

         | (4,663 tests)
    ```
    ```rst
       - 🔄

         | **C0:** 92.3%
         | **C1:** 60.3% (cpp)
         | **Rust line:** 74.4%
    ```
    ```rst
       - ✅ 0 findings

         | `clang-tidy <https://...>`__
    ```
    ```rst
       - ✅ Available

         | (3 tests)
         | `reference_integration <https://...>`__ (cross-module)
    ```
    ```rst
       - 🔄 Configured

         | `clang-tidy <https://...>`__
         | `CodeQL/MISRA <https://...>`__
         | but no CI enforcement workflow yet
    ```
    ```rst
       - 🔄 0% (0/92)

         | `requirements <https://...>`__
         | (all 92 entries ``:status: invalid``)
    ```
  - This applies equally to: test counts in Unit/Integration Test cells, checklist links in Inspection cells, C1/Rust coverage in Coverage cells, CI workflow links in Static/Dynamic Analysis cells, cross-module repo links, and parenthetical notes after any link.
- When referencing `:status: invalid` inside RST text (e.g. lifecycle notes), always use **double backticks**: `` ``:status: invalid`` `` — single backticks are RST hyperlink syntax and will cause a parse warning.

| Process Area | sphinx-needs tag |
|---|---|
| PA 1 — Change Management | `change_management` |
| PA 2 — Requirements Engineering | `requirements_engineering` |
| PA 3 — Architecture Design | `architecture_design` |
| PA 4 — Implementation | `implementation` |
| PA 5 — Verification | `verification` |

The pie chart diagrams are computed live by sphinx-needs at build time — they **never need manual updates**. Only update the filter `<tag>` when adding a new Process Area.

## Modules and Repos

> **IMPORTANT**: Each module has its own dedicated repo in the `eclipse-score` GitHub org AND content in `eclipse-score/score`. **Always check BOTH** the module's own repo and `eclipse-score/score` when counting needs elements. Never rely on `eclipse-score/score` alone.

> **VERSION PINNING**: Always use the commit hash pinned in `known_good.json` (column `known_good.json key`) — **never use `main`** for source repos. This ensures data matches exactly the versions that `reference_integration` is currently testing against. For modules not listed in `known_good.json` (marked `—`), fall back to `main`.

| Module | `known_good.json` key | Own Repo (always check!) | Docs in `eclipse-score/score` |
|---|---|---|---|
| Baselibs | `score_baselibs` | `eclipse-score/baselibs` (no sphinx-needs RST so far) | `docs/modules/baselibs/**`, `docs/features/baselibs/docs` |
| Communication | `score_communication` | `eclipse-score/communication` (no sphinx-needs RST so far) | `docs/modules/communication/**`, `docs/features/communication/docs` |
| Logging | `score_logging` | `eclipse-score/logging` (no sphinx-needs RST so far) | `docs/modules/logging/**`, `docs/features/analysis-infra/logging/docs` |
| Orchestrator | `score_orchestrator` | `eclipse-score/orchestrator` | `docs/modules/orchestrator/**`, `docs/features/orchestration` |
| Persistency | `score_persistency` | `eclipse-score/persistency` — has `docs/persistency/kvs/` with comp_req/comp_arc ✅ | `docs/features/persistency` |
| Time | `—` (not in known_good) | `eclipse-score/inc_time` (no sphinx-needs RST so far) | `docs/features/time/docs` |
| Config Management | `—` (not in known_good) | `eclipse-score/config_management` (no sphinx-needs RST so far) | `docs/features/configuration` |
| Lifecycle | `score_lifecycle_health` | `eclipse-score/lifecycle` — has `docs/module/health_monitor/` (comp_arc_sta/dyn valid=15/16), `detailed_design/` (dd_sta/dyn valid=1/2), `tests/integration/` | `docs/modules/lifecycle/index.rst`, `docs/features/lifecycle/**` — Feature Arch in `docs/features/lifecycle/architecture/` (health_monitor.rst: 19v/2inv, launch_manager.rst: 10v, launch_manager_configuration.rst: 1v → 30/32 valid) |
| Security/Crypto | `—` (not in known_good) | `eclipse-score/inc_security_crypto` — `src/` has no implementation yet; `docs/index.rst` with stkh_req | `docs/features/security_crypto/**` |

> **`eclipse-score/score` pinned ref**: Look up key `score_platform` in the `tooling` section of `known_good.json`.

**How to search all repos for a module:**
```python
for repo in ["eclipse-score/score", "eclipse-score/<module_own_repo>"]:
    files = [p for p in get_tree(repo) if p.endswith(".rst") and "<relevant_path>" in p]
    for f in files:
        v, t = count_needs_in_file(repo, f)
```

## Status Format

- **``✅ Available (valid/total)``** — Artifact complete and approved: **100% of needs elements are `valid`** (valid == total). Always add the count in parentheses for requirements and architecture rows.
- **``🔄 NN% (valid/total)``** — In Progress: at least one element is `valid` but not all. Always show count.
- **``❌ Open``** — Not started, not found, or 0% valid
- For binary rows (Code, SW Development Plan, Unit Tests, CR approved): no count needed, just ``✅ Available`` or ``❌ Open``

**Percentage calculation per deliverable:**
- **Feature Req / Feature Arch**: count individual needs elements (e.g. `.. feat_req::`, `.. feat_arc::`) inside the doc with `:status: valid`; `valid / total`; 100% (valid == total) → ✅ Available
- **Comp. Req / Comp. Arch**: count individual needs elements across all component docs; `valid / total`; 100% (valid == total) → ✅ Available
- **Req. Inspection / Arch. Inspection**: `valid / total` across all checklists (feature + component combined); 100% (valid == total) → ✅ Available
- **Detailed Design + Code / Impl. Inspection**: `valid / total` across all `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` files
- **Binary deliverables** (CR approved, SW Dev Plan, Unit Tests, Integration Tests, Verification Report): no percentage

## Status Criteria (per Deliverable)

### Process Area 1 — CR approved
- **✅ Available**: A closed GitHub Issue with "Feature Request" or "Contribution Request" for the module exists in `eclipse-score/score`
- **❌ Open**: No such issue found

Known closed CRs: Baselibs (#549), Communication (#69), Logging (#68), Orchestrator (#273), Persistency (#95), Time (#910), Config Management (#754, #1764), Lifecycle (#909), Security/Crypto (#905)

### Process Area 2 — Feature Requirements
- **✅ Available**: 100% of individual needs elements (e.g. `.. feat_req::`) inside the requirements doc have `:status: valid`
- **🔄 NN%**: elements exist but not all are `valid`; show `valid / total` percentage. **This includes `🔄 0% (0/N)` when N elements exist but ALL are `:status: invalid` — do NOT use `❌ Open` in this case.**
- **❌ Open**: no requirements file found, OR zero needs elements found

### Process Area 2 — Component Requirements
- **✅ Available**: 100% of all individual needs elements across all component requirements `.rst` files have `:status: valid`
- **🔄 NN%**: elements exist but not all are `valid`; show `valid / total` percentage.
- **❌ Open**: no component requirement files found, OR all found files contain zero `.. comp_req::` directives

### Process Area 2 — Req. Inspection
- **✅ Available**: 100% of all `chklst_req_inspection.rst` files (feature + component level) have `:status: valid`
- **🔄 In Progress**: checklists exist but not all are `valid`
- **❌ Open**: no checklists found

### PA3 RST structure

```rst
Process Area 3 — Architecture Design
*************************************

Feature and component architecture must be designed and inspected.
Work products: ``wp__feature_arch``, ``wp__component_arch``, ``wp__sw_arch_verification``.
See :ref:`arch_workflow`.
```

Columns: **Feature Architecture**, **Component Architecture**, **Arch. Inspection**

### PA4 RST structure

```rst
Process Area 4 — Implementation
********************************

Source code and detailed design must be implemented and inspected.
Work products: ``wp__sw_development_plan``, ``wp__sw_implementation``, ``wp__sw_implementation_inspection``.
See :ref:`workflow_implementation`.
```

Columns: **SW Development Plan**, **Code**, **Detailed Design**, **Impl. Inspection**

### PA5 RST structure

PA5 has two `.. note::` blocks **before** the `.. rubric:: Implementation status:` line:

```rst
Process Area 5 — Verification
*****************************

All tests must be implemented and a module verification report must be approved.
Work products: ``wp__verification_sw_unit_test``, ``wp__verification_comp_int_test``, ``wp__verification_feat_int_test``, ``wp__verification_module_ver_report``.
See :ref:`verification_workflows`.
```

```rst
.. note::

   **C0/C1 Coverage** data is sourced from the `reference_integration <...>`__
   CI (``Code Quality & Documentation`` workflow, ``bazel coverage --config=ferrocene-coverage``).
   C0 = line coverage, C1 = branch coverage. Rust coverage reports line coverage only.
   Modules not yet integrated into the reference_integration CI (Time, Config Mgmt) or with
   disabled coverage extraction (Orchestrator) show ❌ Open.

.. note::

   **Static Code Analysis** is tracked per module via dedicated CI workflows ...

   **Dynamic Code Analysis** is tracked via sanitizer CI workflows ...
```

Columns: **Unit Tests**, **C0/C1 Coverage**, **Comp. Integration Tests**, **Feature Integration Tests**, **Static Code Analysis**, **Dynamic Code Analysis**, **Module Verification Report**, **Platform Verification Report**

**Cross-module integration test format** (when tests live in `reference_integration`, not the module's own repo):
```rst
   - ✅ Available

     | (3 tests)
     | `reference_integration <https://github.com/eclipse-score/reference_integration>`__ (cross-module)
```

**Unit Tests and Integration Tests with known count:**
```rst
   - ✅ Available

     | (N tests)
```
- **✅ Available**: 100% of individual needs elements (e.g. `.. feat_arc::`) inside the architecture doc have `:status: valid`
- **🔄 NN%**: elements exist but not all are `valid`
- **❌ Open**: no architecture file found, OR zero `.. feat_arc::` directives found

### Process Area 3 — Component Architecture
- **✅ Available**: 100% of all individual needs elements across all component architecture files have `:status: valid`
- **🔄 NN%**: elements exist but not all are `valid`
- **❌ Open**: no component architecture docs containing directives found

### Process Area 3 — Arch. Inspection
- **✅ Available**: 100% of all architecture checklists have `:status: valid`
- **🔄 In Progress**: checklists exist but not all are `valid`
- **❌ Open**: no architecture checklists found

### Process Area 4 — SW Development Plan
- **✅ Available**: `eclipse-score/score` contains `docs/platform_management_plan/software_development.rst` (project-wide)
- **❌ Open**: file absent

### Process Area 4 — Code
- **✅ Available**: source files (`.cpp`, `.h`, `.py`, `.rs` etc.) exist in the module's own repo outside of `docs/`
- **❌ Open**: no source files found

**Always include the LOC count** in the cell using the format `✅ Available (~X,XXX LOC) \`repo <url>\`__`.

**How to count LOC:**
Count all lines (including blank/comment lines) across all source files (`.cpp`, `.h`, `.c`, `.rs`, `.py`) in the module's own repo. Round to the nearest 100.

```python
def count_loc(repo, tree, ref="main"):
    src_files = [p for p in tree if
                 any(p.endswith(ext) for ext in ('.cpp', '.h', '.c', '.rs', '.py'))
                 and not p.startswith('docs/')]
    total = 0
    for f in src_files:
        content = fetch_file(repo, f, ref)
        total += len(content.split('\n'))
    # round to nearest 100
    rounded = round(total / 100) * 100
    print(f"  LOC: {total} → ~{rounded:,}")
    return rounded
```

**RST format:**
```rst
   - ✅ Available (~12,500 LOC) `inc_someip_gateway <https://github.com/eclipse-score/inc_someip_gateway>`__
```

### Process Area 4 — Detailed Design
- **✅ Available**: 100% of formal design doc needs elements in `detailed_design/` folders have `:status: valid`
- **🔄 NN%**: design docs exist and at least one element is `valid` but not all
- **❌ Open**: no RST files with actual design directives found

### Process Area 4 — Impl. Inspection
- **✅ Available**: 100% of `chklst_impl_inspection.rst` / `chklst_dd_inspection.rst` files have `:status: valid`
- **🔄 In Progress**: checklists exist but not all are `valid`
- **❌ Open**: no impl inspection checklists found

### Process Area 5 — Unit Tests
- **✅ Available**: Source repo contains `_test.cpp`, `_test.py`, or `/test(s)/` directories (excluding docs/)
- **❌ Open**: no test files found

### Process Area 5 — C0/C1 Coverage

Coverage data is sourced from the `reference_integration` CI (`Code Quality & Documentation` workflow, job `test_and_docs`).
It runs `bazel coverage --config=ferrocene-coverage` per module and extracts C0 (line) and C1 (branch) coverage via `genhtml`/`lcov` for C++ and `cargo llvm-cov` for Rust.

**Status criteria:**
- **✅ Available**: C0 ≥ 100% AND C1 ≥ 100%
- **🔄 C0: XX% / C1: YY%**: Coverage data exists (regardless of %)
- **❌ Open**: Module not in reference_integration CI, or coverage extraction disabled

**How to fetch the latest values:**
```bash
# Find the latest successful run of the "Code Quality & Documentation" workflow (ID 234977097):
gh api "repos/eclipse-score/reference_integration/actions/workflows/234977097/runs?per_page=10" \
  --jq '.workflow_runs[] | select(.conclusion=="success") | {id: .id, created_at: .created_at}' | head -1

# Get the job ID for test_and_docs from that run:
RUN_ID=<run_id>
JOB_ID=$(gh api "repos/eclipse-score/reference_integration/actions/runs/$RUN_ID/jobs" \
  --jq '.jobs[] | select(.name=="test_and_docs") | .id')

# Extract the coverage summary from the job log:
gh api "repos/eclipse-score/reference_integration/actions/jobs/$JOB_ID/logs" \
  | grep -E "COVERAGE ANALYSIS SUMMARY|'score_.*_cpp'|'score_.*_rust'|lines|functions|branches" \
  | grep -A50 "COVERAGE ANALYSIS SUMMARY"
```

**Module → CI key mapping:**
| Tracker Module | CI key (CPP) | CI key (Rust) |
|---|---|---|
| Baselibs | `score_baselibs_cpp` | `score_baselibs_rust_rust` |
| Communication | `score_communication_cpp` | — (disabled) |
| Logging | `score_logging_cpp` | `score_logging_rust` |
| Orchestrator | — (disabled) | — (disabled) |
| Persistency | `score_persistency_cpp` | `score_persistency_rust` |
| Time | not in CI | — |
| Config Mgmt | not in CI | — |
| Lifecycle | `score_lifecycle_health_cpp` | `score_lifecycle_health_rust` |
| Security/Crypto | not in CI | — |

**Format in table (status emoji alone on first line, all coverage metrics as `| ` line-blocks below):**
- CPP + Rust:
  ```rst
     - 🔄

       | **C0:** 92.3%
       | **C1:** 60.3% (cpp)
       | **Rust line:** 74.4%
  ```
- CPP only:
  ```rst
     - 🔄

       | **C0:** 87.9%
       | **C1:** 58.8% (cpp)
  ```
- Not available: `❌ Open`

### Process Area 5 — Comp. Integration Tests

Look for component-level integration test targets inside the module’s own repository (i.e. tests that are **not** cross-module tests in `reference_integration`).

**How to find them:**
```bash
# Count test targets or test files with "integration" in their path or name
gh api repos/eclipse-score/<repo>/git/trees/main?recursive=1 \
  --jq '[.tree[] | select(.path | test("integrat"; "i")) | select(.type=="blob")] | length'
```

Alternatively, look for test target names containing `_it_`, `_integration_`, `component_test`, or similar naming patterns.

**Status criteria:**
- **`✅ Available (N tests)`**: Component integration tests exist in the module repo.
- **`❌ Open`**: No component integration tests found.

**RST format:**
```rst
   - ✅ Available (9 tests)
```

### Process Area 5 — Feature Integration Tests
- **🔄 In Progress**: `integration_test_scenarios` or `feature*test*` paths found in source repo
- **❌ Open**: none found

### Process Area 5 — Static Code Analysis

Static analysis CI exists at two levels:
1. **Per-module CI workflow** — zero-tolerance enforcement on `main` (clang-tidy for C++, Clippy for Rust). A passing CI implies 0 open findings.
2. **Central CodeQL** — runs in `eclipse-score/reference_integration` via `codeql-multiple-repo-scan.yml`.

**Status criteria:**
- **`✅ 0 findings`**: A zero-tolerance CI workflow enforcing clang-tidy or Clippy exists in the module's own repo AND it passes on `main`. Format:
  ```rst
     - ✅ 0 findings

       | `clang-tidy <https://...lint.yml>`__
  ```
- **`🔄 Configured`**: Static analysis tools are configured in the repo but no CI workflow enforces them on every PR/push. Format:
  ```rst
     - 🔄 Configured

       | `clang-tidy <https://...bazelrc>`__
       | `CodeQL/MISRA <https://...>`__
       | but no CI enforcement workflow yet
  ```
- **`❌ Open`**: No static analysis configuration found at all in the module's own repo.

**Per-module static analysis status** (as of 2026-05):
| Module | Status | CI / Config link |
|---|---|---|
| Baselibs | `✅ 0 findings` | [clang-tidy lint.yml](https://github.com/eclipse-score/baselibs/blob/main/.github/workflows/lint.yml) |
| Communication | `🔄 Configured` | [static_analysis.bazelrc](https://github.com/eclipse-score/communication/blob/main/quality/static_analysis/static_analysis.bazelrc) + [CodeQL/MISRA](https://github.com/eclipse-score/communication/tree/main/quality/static_analysis) — no CI enforcement yet |
| Logging | `❌ Open` | — |
| Orchestrator | `✅ 0 findings` | [Clippy clippy.yml](https://github.com/eclipse-score/orchestrator/blob/main/.github/workflows/clippy.yml) |
| Persistency | `✅ 0 findings` | [Clippy clippy.yml](https://github.com/eclipse-score/persistency/blob/main/.github/workflows/clippy.yml) |
| Time | `❌ Open` | — |
| Config Mgmt | `✅ 0 findings` | [clang-tidy static-analysis.yml](https://github.com/eclipse-score/config_management/blob/main/.github/workflows/static-analysis.yml) |
| Lifecycle | `✅ 0 findings` | [Clippy lint_clippy.yml](https://github.com/eclipse-score/lifecycle/blob/main/.github/workflows/lint_clippy.yml) |
| Security/Crypto | `❌ Open` | — |

**Central CodeQL** (all modules):
[codeql-multiple-repo-scan.yml](https://github.com/eclipse-score/reference_integration/blob/main/.github/workflows/codeql-multiple-repo-scan.yml) in `reference_integration`. Finding counts require the GitHub Security tab.

### Process Area 5 — Dynamic Code Analysis

Dynamic analysis is performed via sanitizer CI workflows (ASan/UBSan/LSan for C++, TSan for threading). All zero-tolerance workflows imply 0 sanitizer findings on a passing `main` branch.

**Status criteria:**
- **`✅ 0 findings`**: A zero-tolerance sanitizer CI workflow exists in the module's own repo AND it passes on `main`. Format:
  ```rst
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://...sanitizers_linux.yml>`__
  ```
  For multiple sanitizer workflows:
  ```rst
     - ✅ 0 findings

       | `ASan/UBSan/LSan <https://...>`__
       | `TSan <https://...>`__
  ```
- **`❌ Open`**: No sanitizer CI workflow found in the module's own repo.

**Per-module dynamic code analysis status** (as of 2026-05):
| Module | Status | CI link(s) |
|---|---|---|
| Baselibs | `✅ 0 findings` | [sanitizers_linux.yml](https://github.com/eclipse-score/baselibs/blob/main/.github/workflows/sanitizers_linux.yml) — ASan+UBSan+LSan |
| Communication | `✅ 0 findings` | [ASan/UBSan/LSan](https://github.com/eclipse-score/communication/blob/main/.github/workflows/address_undefined_behavior_leak_sanitizer.yml), [TSan](https://github.com/eclipse-score/communication/blob/main/.github/workflows/thread_sanitizer.yml) |
| Logging | `❌ Open` | — |
| Orchestrator | `❌ Open` | — |
| Persistency | `❌ Open` | — |
| Time | `❌ Open` | — |
| Config Mgmt | `❌ Open` | — |
| Lifecycle | `❌ Open` | — |
| Security/Crypto | `❌ Open` | — |

### Process Area 5 — Module Verification Report
- **✅ Available**: `verification/module_verification_report.rst` exists AND `:status: valid` AND contains actual verification data
- **🔄 In Progress**: file exists with `:status: draft`
- **❌ Open**: file does not exist, OR file is a template placeholder only

### Process Area 5 — Platform Verification Report
The Platform Verification Report (`wp__verification_platform_ver_report`) is a single cross-module document in `eclipse-score/score` at `docs/score_releases/verification/platform_ver_report.rst`. It tracks **feature requirement test coverage** (via `FullyVerifies`/`PartiallyVerifies` links in Feature Integration Tests on `feat_req__...` IDs) and platform-level test results.

- **✅ Available**: `docs/score_releases/verification/platform_ver_report.rst` has `:status: valid` AND contains actual verification data
- **🔄 In Progress**: file exists with `:status: draft`
- **❌ Open**: file does not exist, OR is a template placeholder only

> ⚠️ This column is **not per-module** — it is the same document for all modules. Show the same status in every row.

## Procedure

### Prerequisites
- `gh` CLI must be authenticated (`gh auth status`)
- Python 3.8+

---

### Step 0 — Read `known_good.json` (MANDATORY FIRST STEP)

**Never skip this.** All repo queries must use the pinned hash, not `main`.

```python
import json, base64, subprocess, re

def gh_raw(api_path, jq="."):
    r = subprocess.run(["gh", "api", api_path, "--jq", jq],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"gh api failed: {r.stderr}"
    return r.stdout.strip()

def gh_json_file(api_path):
    content_b64 = gh_raw(api_path, ".content")
    return json.loads(base64.b64decode(content_b64).decode())

known_good = gh_json_file(
    "repos/eclipse-score/reference_integration/contents/known_good.json"
)

def pinned_ref(module_key):
    """Return pinned git hash from known_good.json, or 'main' if not tracked.
    IMPORTANT: score_platform lives in 'tooling', all others in 'target_sw'."""
    all_mods = {
        **known_good["modules"]["target_sw"],
        **known_good["modules"]["tooling"],   # score_platform is here!
    }
    entry = all_mods.get(module_key)
    return entry["hash"] if entry else "main"

REFS = {
    "score":               pinned_ref("score_platform"),    # in 'tooling' section!
    "baselibs":            pinned_ref("score_baselibs"),
    "communication":       pinned_ref("score_communication"),
    "logging":             pinned_ref("score_logging"),
    "orchestrator":        pinned_ref("score_orchestrator"),
    "persistency":         pinned_ref("score_persistency"),
    "lifecycle":           pinned_ref("score_lifecycle_health"),
    "inc_time":            "main",   # not in known_good
    "config_management":   "main",   # not in known_good
    "inc_security_crypto": "main",   # not in known_good
}
# Verify: print all refs and confirm hashes are 40-char SHA1, not "main" for tracked modules
for k, v in REFS.items():
    print(f"  {k}: {v}")
```

> ⚠️ **Common mistake**: `score_platform` (= `eclipse-score/score`) is in the `tooling` section of `known_good.json`, not `target_sw`. The `pinned_ref()` function above merges both — use it exactly as shown.

---

### Step 1 — Fetch repo trees (recursive, with pinned ref)

```python
def get_tree(repo, ref):
    """Returns list of all file paths in repo at given ref."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/trees/{ref}?recursive=1",
         "--jq", ".tree[].path"],
        capture_output=True, text=True)
    if result.returncode != 0:
        print(f"WARNING: could not fetch tree for {repo}@{ref}: {result.stderr}")
        return []
    paths = [p for p in result.stdout.strip().split("\n") if p]
    print(f"  {repo}@{ref[:8]}: {len(paths)} files")
    return paths

# Fetch once, reuse for all PA computations:
tree_score    = get_tree("eclipse-score/score",         REFS["score"])
tree_baselibs = get_tree("eclipse-score/baselibs",      REFS["baselibs"])
tree_comm     = get_tree("eclipse-score/communication", REFS["communication"])
tree_log      = get_tree("eclipse-score/logging",       REFS["logging"])
tree_orch     = get_tree("eclipse-score/orchestrator",  REFS["orchestrator"])
tree_pers     = get_tree("eclipse-score/persistency",   REFS["persistency"])
tree_life     = get_tree("eclipse-score/lifecycle",     REFS["lifecycle"])
tree_time     = get_tree("eclipse-score/inc_time",      REFS["inc_time"])
tree_cfg      = get_tree("eclipse-score/config_management", REFS["config_management"])
tree_sec      = get_tree("eclipse-score/inc_security_crypto", REFS["inc_security_crypto"])
```

> ⚠️ **Common mistake**: If `get_tree()` returns an empty list due to a network error or wrong ref, all subsequent counts for that module will be 0 and appear as `❌ Open`. **Always print the file count and verify it is > 0 before proceeding.**

---

### Step 2 — Count needs elements per file

```python
def fetch_file(repo, path, ref):
    """Fetch raw file content from GitHub. Returns empty string on error."""
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}", "--jq", ".content"],
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return ""
    return base64.b64decode(r.stdout.strip()).decode(errors="replace")

def count_needs_status(content):
    """Count :status: fields that are INDENTED (i.e. inside a needs directive).
    
    CRITICAL: Only match lines with leading whitespace before ':status:'.
    A top-level ':status: valid' at column 0 is a document-level field, NOT
    an individual needs element — do NOT count it.
    """
    # Matches lines like "   :status: valid" (indented) but NOT ":status: valid" (col 0)
    statuses = re.findall(r'^\s+:status:\s+(\w+)', content, re.MULTILINE)
    valid = sum(1 for s in statuses if s == 'valid')
    return valid, len(statuses)

def count_files(repo, paths, ref, path_filter):
    """Aggregate valid/total across all files matching path_filter.
    
    CRITICAL: path_filter must match ALL relevant files in ALL subfolders.
    Use broad filters (e.g. 'architecture') and check the count printed below.
    A result of total=0 means NO files were found — investigate before reporting ❌ Open.
    """
    matched = [p for p in paths if path_filter(p)]
    print(f"    {repo}: {len(matched)} files match filter")  # ALWAYS verify this
    total_valid, total_all = 0, 0
    for path in matched:
        content = fetch_file(repo, path, ref)
        v, t = count_needs_status(content)
        if t > 0:
            print(f"      {path}: {v}v / {t}t")
        total_valid += v
        total_all   += t
    return total_valid, total_all
```

> ⚠️ **Common mistake (caused Lifecycle PA3 bug)**: Using a filter that only matches top-level index files misses content in subfolders like `docs/features/lifecycle/architecture/health_monitor.rst`. Always use `in path` substring filters, never exact filename matches. **Print the matched file list and verify it is complete.**

---

### Step 3 — Derive cell status from counts

```python
def cell_status(valid, total, label=""):
    """Convert valid/total counts to RST cell status string.
    
    Rules:
      total == 0            → ❌ Open  (no files found at all — verify tree was non-empty!)
      valid == total > 0    → ✅ Available (valid/total)
      0 < valid < total     → 🔄 NN% (valid/total)
      valid == 0, total > 0 → 🔄 0% (0/total)  ← NOT ❌ Open! Files exist but all invalid.
    """
    if total == 0:
        return "❌ Open"
    pct = valid * 100 // total
    if valid == total:
        return f"✅ Available ({valid}/{total})"
    return f"🔄 {pct}% ({valid}/{total})"
```

> ⚠️ **Common mistake**: Reporting `❌ Open` when `total > 0` but `valid == 0`. This is wrong — use `🔄 0% (0/N)` to indicate files exist but all are invalid/draft (e.g. Lifecycle requirements).

---

### Step 4 — Per-module path filters (reference table)

Use these exact filters when calling `count_files()`. Verify printed file counts before trusting results.

| Module | Deliverable | Repo | Path filter |
|---|---|---|---|
| Baselibs | Feat. Req | score | `lambda p: 'features/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Comp. Req | score | `lambda p: 'modules/baselibs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Req. Inspection | score | `lambda p: 'baselibs' in p and 'chklst_req_inspection' in p` |
| Baselibs | Feat. Arch | score | `lambda p: 'features/baselibs' in p and 'architecture' in p and p.endswith('.rst')` |
| Baselibs | Comp. Arch | score | `lambda p: 'modules/baselibs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Baselibs | Arch. Inspection | score | `lambda p: 'baselibs' in p and 'chklst_arc_inspection' in p` |
| Baselibs | Impl. Inspection | score | `lambda p: 'baselibs' in p and 'chklst_impl_inspection' in p` |
| Orchestrator | Feat. Req | score | `lambda p: 'features/orchestration' in p and 'requirements' in p and p.endswith('.rst')` |
| Orchestrator | Comp. Req | score | `lambda p: 'modules/orchestrator' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Orchestrator | Comp. Arch | score | `lambda p: 'modules/orchestrator' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Persistency | Feat. Req | score | `lambda p: 'features/persistency' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Persistency | Feat. Arch | score | `lambda p: 'features/persistency' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| Persistency | Comp. Req | pers | `lambda p: 'kvs' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` |
| Persistency | Comp. Arch | pers | `lambda p: 'kvs' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |
| **Lifecycle** | **Feat. Req** | **score** | `lambda p: 'features/lifecycle' in p and 'requirements' in p and p.endswith('.rst') and 'chklst' not in p` — **includes subfolders!** |
| **Lifecycle** | **Feat. Arch** | **score** | `lambda p: 'features/lifecycle' in p and 'architecture' in p and p.endswith('.rst')` — **matches health_monitor.rst, launch_manager.rst, launch_manager_configuration.rst** |
| **Lifecycle** | **Comp. Arch** | **lifecycle** | `lambda p: 'module' in p and 'architecture' in p and p.endswith('.rst') and 'chklst' not in p` |

> ⚠️ **Lifecycle is the most complex module** — content is split across `eclipse-score/score` (feature-level: `docs/features/lifecycle/**`) AND `eclipse-score/lifecycle` (component-level: `docs/module/health_monitor/**`). Always query both repos and aggregate.

---

### Step 5 — Sanity checks before writing the RST

Before updating the file, verify these invariants:

1. **No module with non-empty tree has all-zero counts across all PAs** — that indicates a filter bug, not genuine absence of content.
2. **total=0 for a known deliverable** — investigate. Run `get_tree()` result manually and search for relevant paths.
3. **PA summary arithmetic**: `complete/total` must equal the number of `✅ Available` cells in the table. Count manually.
4. **`🔄 0%` vs `❌ Open`**: grep all cells — any `🔄 0%` means files exist but are all invalid. Any `❌ Open` means zero files found. These are fundamentally different states.
5. **Cross-check against previous version**: If a cell flips from `🔄 NN%` to `❌ Open` compared to the prior RST, investigate before accepting — it almost certainly means a filter missed files, not that content disappeared.

#### 5a — Structural completeness check (same set of information)

**Before comparing values, verify that the new data has the same structure as the existing RST.**
This catches missing modules, missing columns, or accidentally dropped rows — and must run first.

```python
def parse_rst_structure(rst_path):
    """
    Parses overall_status.rst and returns the set of modules and deliverable
    columns present in each PA table.

    Returns:
      {
        'PA1': {'modules': ['Baselibs', ...], 'columns': ['CR approved']},
        'PA2': {'modules': [...], 'columns': ['Feature Requirements', ...]},
        ...
      }
    """
    with open(rst_path) as f:
        text = f.read()

    pa_sections = re.split(r'Process Area (\d+) —', text)[1:]  # alternating: pa_num, pa_body
    result = {}
    for i in range(0, len(pa_sections) - 1, 2):
        pa = f"PA{pa_sections[i].strip()}"
        body = pa_sections[i + 1]

        # Extract header row (columns)
        header_match = re.search(r'\* - \*\*Module\*\*(.*?)(?=\n   \* -\s+\w)', body, re.DOTALL)
        cols = re.findall(r'\*\*([^*]+)\*\*', header_match.group(0)) if header_match else []
        cols = [c.strip() for c in cols if c.strip() != 'Module']

        # Extract module names (stub column = first cell of each data row)
        modules = re.findall(r'\n   \* - ((?![\*\s])[\w][^\n]+)', body)
        modules = [m.strip() for m in modules]

        result[pa] = {'modules': modules, 'columns': cols}
    return result

def structural_check(old_structure, new_structure):
    """
    Compares structure dicts from parse_rst_structure.
    Prints errors for any missing modules or columns.
    Returns True if identical, False otherwise.
    """
    ok = True
    for pa in old_structure:
        if pa not in new_structure:
            print(f"  🛑 MISSING PA: {pa} not found in new data")
            ok = False
            continue

        old_mods = set(old_structure[pa]['modules'])
        new_mods = set(new_structure[pa]['modules'])
        missing_mods = old_mods - new_mods
        extra_mods = new_mods - old_mods
        if missing_mods:
            print(f"  🛑 {pa}: MISSING MODULES: {sorted(missing_mods)}")
            ok = False
        if extra_mods:
            print(f"  ℹ️  {pa}: NEW MODULES: {sorted(extra_mods)}  (verify intentional)")

        old_cols = old_structure[pa]['columns']
        new_cols = new_structure[pa]['columns']
        if old_cols != new_cols:
            print(f"  🛑 {pa}: COLUMN MISMATCH")
            print(f"       old: {old_cols}")
            print(f"       new: {new_cols}")
            ok = False

    return ok
```

**Run this before any value comparison:**
```python
old = parse_rst_structure("docs/s_core_v_1/roadmap/overall_status.rst")
# ... compute new_structure from your freshly calculated data ...
assert structural_check(old, new_structure), "Structure mismatch — do not write RST until resolved"
```

**Rules:**

| Situation | Action |
|---|---|
| Module present in old, missing in new | 🛑 **STOP** — row was dropped accidentally |
| Column present in old, missing in new | 🛑 **STOP** — deliverable column was dropped |
| New module not in old | ℹ️ Intentional addition — verify it was requested |
| Module count in new < old | 🛑 **STOP** — data loss |
| All PA sections present | ✅ |

#### 5b — Compare new values against existing RST (plausibility diff)

**Only run this after 5a passes.** Diff computed values against the existing RST cell-by-cell:

```python
def plausibility_check(old_val, new_val, module, deliverable):
    """
    Flags suspicious regressions. Print a WARNING for human review.
    """
    def rank(val):
        if '✅' in val: return 2
        if '🔄' in val: return 1
        return 0  # ❌ Open

    old_rank = rank(old_val)
    new_rank = rank(new_val)

    if new_rank < old_rank:
        print(f"  ⚠️  REGRESSION [{module} / {deliverable}]: {old_val!r} → {new_val!r}")
        print(f"      → Check filter paths, repo tree, and pinned ref.")
    elif old_rank == 0 and new_rank == 2:
        print(f"  ℹ️  LARGE JUMP [{module} / {deliverable}]: {old_val!r} → {new_val!r}")
        print(f"      → Confirm count is correct before accepting.")
    else:
        print(f"  ✓  [{module} / {deliverable}]: {old_val!r} → {new_val!r}")
```

**Rules for human review:**

| Old value | New value | Action |
|---|---|---|
| `✅ Available` | `❌ Open` | 🛑 **STOP** — almost certainly a filter bug. Do not write. |
| `✅ Available` | `🔄 NN%` | ⚠️ Regression — investigate before accepting. |
| `🔄 NN%` | `❌ Open` | 🛑 **STOP** — files existed before, filter is now missing them. |
| `🔄 NN%` → `🔄 MM%` | MM < NN | ⚠️ Percentage dropped — check if content was deleted or filter changed. |
| `❌ Open` | `🔄 NN%` or `✅` | ✅ Progress — verify count is plausible. |
| `🔄 NN%` | `✅ Available` | ✅ Completion — confirm valid == total. |
| Any | Same | ✅ No change — OK. |

**LOC plausibility** (PA4 Code column): if the new LOC count is less than 50% of the previous value, flag it — most likely a filter excluded files it shouldn't have.

---

### Step 6 — Update the RST file

Write the computed values to `docs/s_core_v_1/roadmap/overall_status.rst` following the formatting rules in the RST File Structure section above. Update the `.. rubric:: Implementation status:` line for each PA.

---

### Step 7 — Adding a new module

Add a row to the Modules and Repos table above (with known_good.json key and path filters), then add a row to each tracker table.

## Interpretation Notes

### Artifacts vs. Checklists — Key Rule
- **Artifacts** (Feature Requirements, Component Requirements, Feature Architecture, Component Architecture, Detailed Design, Code): derive status by **directly inspecting the repos**.
- **Inspection rows** (Req. Inspection, Arch. Inspection, Impl. Inspection): report what is found in `chklst_*.rst` files.

### Additional Notes
- **Requirements/Architecture rows**: count individual needs elements (`:status:` fields inside `.. feat_req::`, `.. feat_arc::`, `.. comp_req::`, etc.) — NOT the document-level `:status:` field.
- The SW Development Plan check is project-wide (not per-module).
- **Template vs. real report**: A file with `:status: valid` can still be an empty template. Look for actual content beyond section headings.
- **Aggregation pitfall**: When a module has architecture/requirements content spread across multiple files in a subfolder (e.g. `docs/features/lifecycle/architecture/*.rst`), make sure to fetch and aggregate ALL files in that folder — not just the top-level index. Missing any file leads to falsely reporting `❌ Open` instead of the correct percentage.

## Limitations

- Cannot detect whether requirements have 100% test coverage (needs needs.json analysis)
- **Static analysis findings**: Per-module CI enforcement workflows are zero-tolerance — a passing `main` branch implies 0 findings.
- Central CodeQL finding counts require GitHub Security tab access.
- Feature integration tests heuristic is weak — manual verification recommended

## Docs Structure (reference_integration)

```
docs/
  index.rst                          ← top-level: Modules, PMT, S-Core v1.0, Integration Status
  conf.py                            ← Sphinx config (pydata theme, sidebar-toggle.js, custom.css)
  _assets/
    custom.css                       ← compact-overview-table (fluid 33%-per-column pie charts, !important img override), module-phase-tracker-table, wide-content-page, collapsible right sidebar
    sidebar-toggle.js                ← right sidebar collapse/expand toggle (persisted in localStorage)
  _templates/
    sidebar-root-nav.html            ← left nav with startdepth=0 (shows full toctree on all pages)
  s_core_v_1/
    index.rst                        ← S-Core v1.0 section: Status, Releases, Verification, Roadmap
    status/
      status.rst                     ← Status section index (toctree)
      overall_status.rst             ← Feature and Process Status tracker (THIS FILE — updated by this skill)
    releases/
      releases.rst
      score_07.rst
    verification/
      verification.rst
      unit_test_summary.md
      coverage_summary.md
    roadmap.rst
  integration_process/
    integration_process.rst          ← Integration Process section (currently empty placeholder)
  sw_components.rst
  process_tools.rst
  needs_filters.py                   ← sphinx-needs filter functions for pie charts
```

**`conf.py` key settings:**
- `html_sidebars = {"**": ["sidebar-root-nav"]}` — full left nav on every page
- `html_js_files = ["sidebar-toggle.js"]` — collapsible right TOC sidebar
- `html_theme_options.secondary_sidebar_items` — suppresses right TOC on `s_core_v_1/roadmap/overall_status` and `feature_and_process_status` pages

## Complete RST Snapshot

Full content of `docs/s_core_v_1/roadmap/overall_status.rst` as of last update (2026-05).
Use this to recreate the file from scratch if needed.

See the file directly at `docs/s_core_v_1/roadmap/overall_status.rst` in `eclipse-score/reference_integration`.
