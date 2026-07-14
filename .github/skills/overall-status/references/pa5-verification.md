# Process Area 5 — Verification

| Property | Value |
|---|---|
| sphinx-needs tag | `verification` |
| Cross-reference label | `overall_status_pa5` |
| Columns | Unit Tests · C0/C1 Cov · Comp. IT · Feat. IT · Static · Dynamic · Module Ver. Rpt |
| Progress figure | `pa5_verification_progress.svg` (`1080px` — 1.5× standard width) |

This PA combines test discovery, CI coverage data, static/dynamic analysis CI
status and the module verification report. For shared conventions see
[common.md C4](./common.md#c4-rst-formatting-rules).

---

## Status criteria

| Deliverable | `✅ Available` | `🔄 …` | `❌ Open` |
|---|---|---|---|
| **Unit Tests** | repo has `_test.cpp` / `_test.py` / `tests/` | — | none |
| **C0/C1 Coverage** | C0 = C1 = 100 % | data exists (any %) | not in `reference_integration` CI |
| **Comp. Integration Tests** | tests in module's own repo | — | none |
| **Static Analysis** | zero-tolerance per-module CI workflow passes on `main` (clang-tidy / Clippy) | tools configured but no CI enforcement | no static-analysis config |
| **Dynamic Analysis** | zero-tolerance sanitizer CI passes on `main` | — | no sanitizer CI |
| **Module Ver. Report** | `verification/module_verification_report.rst` `:status: valid` and contains data | `:status: draft` | absent or template only |
| **Platform Ver. Report** | _no column_ — the platform verification report exists **once** for the entire platform; do not render it as a per-module column. Add it as a **bold one-liner immediately after the PA5 table** (see [Platform Verification Report](#platform-verification-report)). | | |

- **Per-link status marker (Module Ver. Report):** prefix the
  `module_verification_report.rst` link with ✅/🔄/❌ by its document
  `:status:` — see
  [common.md C4.2.1](./common.md#c421-per-link-status-markers--inspection--report-cells-mandatory).

> **Static / Dynamic Analysis cells render the status only, no source-code
> link.** The PA5 link discipline of
> [common.md C4.2](./common.md#c42-source-links--mandatory) does not apply to
> these two columns: there is no canonical per-module artefact to point at (CI
> workflows live in the org-wide `.github` repo, not per module).

---

## Test-count rendering

For the **Unit Tests**, **Comp. IT** and **Feat. IT** columns, the test count
goes on its **own line-block line** below the status — never on the same line
as `✅ Available` (see
[common.md C4.1](./common.md#c41-cell-layout)). Use `plur()` for correct
singular/plural (`1 test` vs `N tests`).

---

## Test-counting pitfalls (read before touching Unit / Comp. IT numbers)

Test discovery is the **most error-prone** part of PA5. Verified failure
modes (each has produced a wrong number in the past — Logging was `340`
unit / `❌` comp when the truth is `650` / `8`):

1. **Count all components of a module, not just one subtree.** Two-component
   modules keep tests in several roots — e.g. Logging has **both**
   `score/datarouter/**` (~324 cases) **and** `score/mw/log/**` (~326).
   Missing one silently halves the count. Always walk the *whole* repo tree.
2. **Rust inline unit tests live in `src/`, not in `tests/`.** Counting only
   files under a `test/`-style path (the old `is_test_path`) **misses every
   `#[cfg(test)] mod tests { #[test] … }`** in `src/*.rs`. Lifecycle has
   **235** such inline tests, all in `src/`. Count `#[test]` /
   `#[tokio::test]` in **all** `.rs` files (outside `docs/`, `third_party/`,
   `bazel-*`).
3. **Unit vs. Component/Integration is per-repo convention, not one rule.**
   There is no single reliable heuristic; classify with the module's own
   convention:

   | Module | Component/Integration tests live in | Count |
   |---|---|---|
   | Logging | `score/test/component/**` (Bazel `tags=["integration"]`, ITF `py_*_itf_test`) | 8 |
   | Persistency | `tests/test_cases/tests/test_cit_*.py` (**CIT** = Component Integration Test) | 44 |
   | Baselibs | `score/os/utils/test/mqueueintegration_test.cpp` | 13 |
   | Communication | `score/mw/com/test/**/integration_test/*.py` | 63 |
   | Time | `score/**/tests/integration_tests/**` | 4 |
   | Security/Crypto | `tests/integration_tests/integration_test.py` | 11 |
   | Some/IP | `tests/integration_test/**` + `quality/integration_testing/**` | 21 |

   A **Rust `tests/` directory is a *crate integration* test**, but a
   C++ component's `tests/` subfolder (e.g. `futurecpp/tests/`) is that
   component's **unit** tests — do **not** blanket-classify `tests/` as
   integration.
4. **Two different "test count" metrics exist — do not mix them.**
   - *Test-case declarations* — count of `TEST*(` / `#[test]` / `def test_`
     macros (Logging 650, Baselibs ~5.7k).
   - *Executed test cases* — the same expanded over `TYPED_TEST` types and
     parametrised instances (Baselibs `25833`). Bazel CI reports *test
     **targets*** (`Executed N tests` ≈ 297), a **third** number.

   The current table predominantly uses the **executed-case** metric. When a
   single cell is corrected, match the metric already used in that column;
   do **not** silently switch the whole column to a different metric.

> **When in doubt, verify a suspicious cell manually** against the repo at
> the pinned ref (fetch the test files, count) before overwriting — a
> `✅ Available` test cell dropping to `❌ Open` is almost always a discovery
> bug, not a real regression (see the plausibility gate in
> [common.md Step 5b](./common.md#5b-plausibility--diff-each-cell)).

---

## Coverage CI keys

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

C0 = line coverage, C1 = branch coverage. Rust coverage reports **line only**.
Modules not yet integrated into the `reference_integration` CI render `❌ Open`
(currently: Time, Config Mgmt, Security/Crypto, Some/IP — update list each
regen).

---

## Static / dynamic analysis CI table

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

## Platform Verification Report

The platform verification report is a **single project-wide deliverable** — it
does **not** get a per-module column. Render it as a prominent admonition
immediately after the PA5 list-table (styled via `.platform-ver-report` in
`docs/_assets/custom.css`):

```rst
.. admonition:: Platform Verification Report
   :class: important platform-ver-report

   `platform_ver_report
   <https://github.com/eclipse-score/score/blob/<pinned-sha>/
   docs/score_releases/verification/platform_ver_report.rst>`__
   — 🔄 **Draft** (single project-wide deliverable)
```

Update the status emoji + label to match the report's current `:status:` field
(✅ **Valid** / 🔄 **Draft**). Do **not** revert this to a plain
`**bold paragraph**` — the admonition class is what makes it visually
prominent. See [common.md C4.2](./common.md#c42-source-links--mandatory).
