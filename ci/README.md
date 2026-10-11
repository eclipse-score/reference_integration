<!--
*******************************************************************************
Copyright (c) 2026 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at
https://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
*******************************************************************************
-->

# DR-008 two-stage test execution — running it locally

Every step of [`.github/workflows/dr8_test_execution.yml`](../.github/workflows/dr8_test_execution.yml)
reproduced on a workstation. The commands are the ones the workflow runs, so a local failure is
the same failure CI reports.

**Prerequisites:** `bazel` (or `bazelisk`), `git`, and `lcov` for Stage 2
(`sudo apt-get install -y lcov`, which provides `genhtml`). The scripts run as `bazel run`
targets, so their interpreter comes from Bazel's toolchain rather than the machine — a system
`python3` is needed only by the shell snippet below that picks a module out of the JSON.

## What the two stages are

| Stage | Bazel root | Question it answers |
|---|---|---|
| 1 — integration | `reference_integration` | Do the pinned modules integrate, and which versions does MVS actually select? |
| 2 — per module | the module under test | Does each module's own test suite pass against *those* versions? |

Stage 1's output is the `stage1-resolved-deps` artifact. Stage 2 consumes it, so Stage 1 must be
run first — there is no way to reproduce Stage 2 alone.

## Stage 1 — platform build and feature integration tests

```bash
bazel test --lockfile_mode=error --config=linux-x86_64 //feature_integration_tests/test_cases:fit
```

Then export the resolved dependency set that Stage 2 pins against:

```bash
mkdir -p artifacts/stage1-resolved-deps

# --verbose populates originalVersion. Without it every pin report verdict is "unknown" and
# no consumer version difference can be detected.
bazel mod graph --verbose --output=json --lockfile_mode=error > resolved_graph.json

bazel run //scripts/known_good:resolve_deps -- \
  --mod-graph resolved_graph.json \
  --export artifacts/stage1-resolved-deps/resolved_versions.json

cp MODULE.bazel.lock artifacts/stage1-resolved-deps/
```

`artifacts/stage1-resolved-deps/` then holds what CI uploads:

| File | Purpose |
|---|---|
| `resolved_versions.json` | The manifest: every dependency's resolved version or commit, plus the patches ref_int applies to it. |
| `graph.json` | The post-MVS graph, so Stage 2 can pin a module's whole transitive closure rather than only its direct deps. |
| `patches/` | The patch files themselves. Stage 2 re-hosts them inside the module checkout, so an injected dependency is built exactly as Stage 1 built it. |
| `resolved_pins_report.json` | Where each pin came from, which consumers asked for something else, and which overrides the manifest could not carry. Read this first when a Stage 2 module fails on a version. |
| `MODULE.bazel.lock` | Evidence of full resolution; not read by Stage 2. |

## Stage 2 — one module's unit tests and coverage

CI derives the module list from `known_good.json` rather than hardcoding it:

```bash
bazel run --ui_event_filters=-info,-stdout --noshow_progress \
  //scripts/known_good:list_modules -- --group target_sw
```

Pick one module and check it out at its `known_good` commit:

```bash
MODULE=score_logging
SLUG=$(bazel run --ui_event_filters=-info,-stdout --noshow_progress \
  //scripts/known_good:list_modules -- --group target_sw \
  | python3 -c "import json,sys;print(next(m['slug'] for m in json.load(sys.stdin) if m['name']=='$MODULE'))")
COMMIT=$(bazel run --ui_event_filters=-info,-stdout --noshow_progress \
  //scripts/known_good:list_modules -- --group target_sw \
  | python3 -c "import json,sys;print(next(m['commit'] for m in json.load(sys.stdin) if m['name']=='$MODULE'))")

rm -rf _module
git clone "https://github.com/${SLUG}.git" _module
git -C _module checkout "$COMMIT"
```

Run the module's tests against Stage 1's resolved set:

```bash
bazel run //scripts:quality_runners -- \
  --modules-to-test "$MODULE" \
  --module-dir _module \
  --resolved-deps artifacts/stage1-resolved-deps
```

In order, this applies the module's own `bazel_patches`, overwrites `_module/MODULE.bazel` with
ref_int's resolved overrides, re-hosts each pinned dependency's patches under
`_module/ref_int_patches/`, deletes the now-stale `_module/MODULE.bazel.lock`, pins
`.bazelversion` to ref_int's, then runs an analysis-only gate (`build --nobuild`) before the
tests and coverage.

**It also writes outside `_module/`**, into your ref_int checkout:
`docs/verification_report/{unit_test_summary.md,coverage_summary.md,failure_attribution.json}`
and `artifacts/coverage/`. The first two are tracked files, so a local run leaves them modified —
`git checkout -- docs/verification_report/` afterwards.

The module's own `.bazelrc` is not read (`--noworkspace_rc`), so
[`ci/stage2/module.bazelrc`](stage2/module.bazelrc) is the single source of common config.
Two exceptions, both listed at the top of `scripts/quality_runners.py`: `score_communication`
also gets `ci/stage2/score_communication.bazelrc`, and `score_config_management` keeps its own
`.bazelrc` (`MODULES_WITH_OWN_RC`) because ref_int cannot yet replace its libclang registration.

## Verify the module really built against ref_int's pins

```bash
bazel run //scripts/known_good:verify_stage2_resolution -- \
  --mod-graph _module/module_graph.json \
  --resolved artifacts/stage1-resolved-deps/resolved_versions.json \
  --module-bazel _module/MODULE.bazel \
  --module "$MODULE"
```

Fails when ref_int injected an override that did not take effect, or when a dependency ref_int
patches was pinned without its patches. Warns for anything ref_int never pinned — a
`dev_dependency`, or a dep behind an `archive_override` the manifest cannot express.

## Aggregate the report

The aggregator reads one `stage2-report-<module>/` directory per module, the layout CI gets from
downloading the per-module artifacts. Locally, stage the run you just did into that shape:

```bash
mkdir -p "_stage2_reports/stage2-report-${MODULE}"
cp docs/verification_report/* "_stage2_reports/stage2-report-${MODULE}/"

bazel run --ui_event_filters=-info,-stdout --noshow_progress \
  //scripts:aggregate_quality_report -- \
  --stage1-result success \
  --stage2-result success \
  --stage2-dir _stage2_reports/
```

## The Python unit tests behind all of this

```bash
bazel test //scripts:all_python_unit_tests
```

## When a Stage 2 module fails

Attribute the failure before debugging it — the harness records who owns it:

1. `resolved_pins_report.json` — did ref_int impose a version the module never asked for?
   `uncarried` lists overrides ref_int declares but cannot carry into Stage 2.
2. The `verify_stage2_resolution` output — an `::error::` there means ref_int's injection failed
   (a ref_int defect); a `::warning::` means the module resolved that dependency itself.
3. `quality_runners`' own warnings — a dependency pinned without its patches, or a module that
   resolves dependencies in ways ref_int's pins cannot reach (its own `*_override`, or an
   `http_archive`-style fetch outside bzlmod).
4. `docs/verification_report/failure_attribution.json` — written when the resolution gate fails,
   recording whether the cause was an integration conflict or a ref_int harness defect.
