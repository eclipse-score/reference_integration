---
name: overall-status
description: "How-to reference for the per-release progress charts on docs/s_core_v_1/roadmap/overall_status.rst. Explains the two scripts (collect_metrics.py, generate_progress_charts.py), the counting model, the forecast column and the module/colour mapping. Use when refreshing the overall status page after a release, a known_good.json ref bump, or when adding a module. The overall-status agent orchestrates the run; this skill holds the 'how'."
argument-hint: "optional: release name, e.g. v1.0"
---

# Overall Status progress charts — the "how"

`docs/s_core_v_1/roadmap/overall_status.rst` is a **thin page**: an intro, five
`figure::` directives and links to the verification reports. It carries no
per-module tables — those were replaced by the **Platform Verification Report**
and the per-module **Module Verification Reports**
(`docs/verification_report/`), which are generated from the needs data of the
documentation build and are the authoritative source for the *current* state.

The only thing this page owns is the **multi-release trend**. Refreshing it is
two commands.

## Files

| File | Role |
|---|---|
| `scripts/overall_status/collect_metrics.py` | counts every release from the module sources, writes the data file |
| `docs/s_core_v_1/roadmap/overall_status_data.json` | generated data; safe to hand-tune, but a re-collect overwrites it |
| `scripts/overall_status/generate_progress_charts.py` | renders the five SVGs; never hand-edit the SVGs |
| `docs/_assets/pa{2,3,4,5}_*.svg` | generated output |
| `docs/s_core_v_1/roadmap/overall_status.rst` | only the *data collection date* changes on a refresh |

## Procedure

```bash
export GITHUB_PAT=...                                   # for tag / pin lookups
python3 scripts/overall_status/collect_metrics.py       # ~5 min, clones to /tmp
python3 scripts/overall_status/generate_progress_charts.py
```

Then bump the date in the `.. important::` admonition of `overall_status.rst`
to the `data_collected` value, and verify with
`python3 scripts/overall_status/generate_progress_charts.py --check`.

The first run clones ~11 bare repositories (~1.8 GB) into
`/tmp/overall_status_repos`; later runs only fetch. Use `--cache` to relocate.

## How the columns are built

One column per `reference_integration` release tag, oldest first, plus a
trailing forecast column:

- **Release columns** — the tag's `known_good.json` gives each module's pin.
  Entries carrying only a `version` are resolved to `v<version>` in the module's
  own repository. Modules that were never pinned (Security/Crypto, Some/IP) fall
  back to the commit on `main` as of the release date.
- **Forecast column** (`v0.10 (forecast)`) — the **working tree's**
  `known_good.json`, i.e. today's state, labelled as the projection for the next
  release. Rename it in `collect_metrics.py` when the target release changes.

Every bar is stacked by module. `MODULE_COLORS` is the single source of truth
for the colour of a module and is shared by every chart, so a module keeps its
colour throughout the page; it also fixes the legend order. Within a bar the
slots are sorted by size, largest at the bottom. Modules contributing `0` are
dropped from the stack and the legend.

## Counting model

Per module, metrics are summed over **its own repository** plus the matching
feature paths in `eclipse-score/score` (`SCORE_PATHS` fragments, which cover
both the old `modules/<mod>` and the current `features/<area>` layout).
Communication excludes `some_ip_gateway`, which is its own module.

| Metric | Counted as |
|---|---|
| `req` | `.. feat_req::` / `.. comp_req::` / `.. aou_req::` in `.rst`, plus `CompReq` / `FeatReq` / `AoU` / `ExternalCompReq` / `AssumedSystemReq` objects in `.trlc` |
| `arc` | `.. feat*::` / `.. comp*::` / `.. logic_arc_int*::` / `.. real_arc_int*::` in `.rst` |
| `loc` | newlines in `.cpp .cc .cxx .c .h .hpp .hh .rs .py`, excluding `docs/`, `third_party/`, `bazel-*` |
| `unit_tests` | test definitions (`TEST(` / `TEST_F(` / `TEST_P(` / `TYPED_TEST(` / `TYPED_TEST_P(` / Rust `#[test]` / Python `def test_`) outside an `INT_TEST_DIRS` directory |
| `int_tests` | the same patterns **inside** a directory named `component`, `integration`, `integration_test(s)`, `integration_testing`, `itf`, `feature_integration_tests` or `platform_integration_tests` |

The integration count also includes `reference_integration`'s own feature tests.
Those are read from this checkout (not from a clone) at the release tag, and the
module is taken from the path segment below `feature_integration_tests/` or
`platform_integration_tests/` via `RI_ALIASES`. Only the test count is taken
from there — never the lines of code, which belong to the modules.

Counts are **totals**, irrespective of `:status:` — the charts visualise scope
growth, not validation maturity. `chklst_*.rst` files are excluded.

## Rules

- Keep the cross-reference labels `overall_status_pa2` … `overall_status_pa5` —
  `pi1.rst`, `pi2.rst` and `pi3.rst` link to them.
- Never hand-edit an SVG; regenerate it.
- Re-collect **all** columns rather than appending one by hand. The value of the
  series is that every column used the same counter.
- Adding a module means one entry in `MODULES` (repo, `known_good` keys, score
  path fragments), one in `MODULE_COLORS` and one in `RI_ALIASES`.
- These numbers are source-derived and will **not** match CI dashboards. Test
  counts are test definitions, not parameterised CI runs; expect the CI unit
  test total to be several times larger. Say so if a reader compares them.
