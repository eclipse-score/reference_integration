# DR-008 Stage 2 — mission, and the decisions ref_int made deliberately

Read this before changing anything in `ci/stage2/`. It exists because this area has already
been implemented the wrong way once, and the misalignment came from paraphrasing the goal
instead of writing it down.

## The mission (acceptance criteria for Stage 2)

1. CI runs Stage 1 → Stage 2 matrix over the `target_sw` modules → aggregate report.
2. Each Stage-2 job reports a **non-zero test count**. A job that configures but runs no
   tests is a failure, not a pass.
3. Each module's regenerated `MODULE.bazel.lock` agrees with `resolved_versions.json` for
   every dependency present in both.
4. Every failure is classified: **0 tests executed ⇒ ref_int harness defect**;
   **>0 tests with failures ⇒ integration finding owned by the module team**.
5. No module is built with semantics different from its own CI **unless ref_int decided so
   deliberately and recorded it in the table below**.

Explicitly *not* the mission: "ref_int owns every flag a module builds with." That was an
over-reading of the review guidance and it cost a Critical regression (see below).

## What the review guidance actually said

The maintainer asked which `.bazelrc` Stage 2 uses, was told "the downstream one", and did
not object. What they objected to was the *next* answer:

> "config names are coming from ref_int's `known_good.json`, but the actual flag definitions
> are downstream" — **"that needs to be changed / so we have a control over the flags that
> are passed to modules / please check with config and toolchain from ref_int / if there is
> still an issue check toolchain difference"**

So the defect was a **dangling reference**: ref_int named a config (`--config=per-x86_64-linux`)
whose meaning lived in the module. The fix is for ref_int to **define** the configs it names.
It is *not* to discard the module's `.bazelrc`.

## Mechanism: layer, never `--noworkspace_rc`

Stage 2 passes `--bazelrc=<ref_int>/ci/stage2/module.bazelrc` and **keeps** the module's own
`.bazelrc`. Bazel reads rc files in order, and that order is what gives ref_int control:

| Flag kind | Two rc files disagree | Outcome |
|---|---|---|
| single-valued (`--platforms`, `--test_tag_filters`, `--instrumentation_filter`) | module first, ref_int last | **ref_int wins** |
| accumulating (`--extra_toolchains`, `--copt`, `--per_file_copt`, `--aspects`) | both apply | both kept |

`--noworkspace_rc` was tried and **reverted**. It discarded module settings unrelated to the
configs ref_int names — `score_communication`'s generic-trace-library **stub** selection, its
sandbox settings and its own libclang/cc toolchains; `score_kyron`'s Rust coverage
instrumentation; `score_baselibs`/`score_orchestrator`'s clippy aspects. Net effect was worse
than the bug it fixed: all 8 modules configured, 3 silently mis-configured. Loud failures
traded for quiet wrongness.

Consequence of layering to keep in mind: ref_int **cannot un-register** a toolchain the module
registers, because `--extra_toolchains` accumulates. Version skew therefore has to be fixed at
the source (see `score_toolchains_rust` below), not papered over in the rc.

## Why per-module opt-in configs still exist (and when they go away)

`known_good.json`'s `bazel_config` carries **additive opt-ins only**. `stage2-linux-x86_64` is
emitted unconditionally by `quality_runners.py`, so a module with an empty or mistyped
`bazel_config` can never run with no platform/toolchain again.

| Config | Who selects it | Why it is not in the base | Removable when |
|---|---|---|---|
| `stage2-gcc` | all except `score_communication` | communication's `gcc.toolchain()` call passes `use_base_constraints_only = True`, so its generated target is `:x86_64-linux`, not `:x86_64-linux-gcc_12.2.0`. It registers its own cc toolchain unconditionally, so it needs nothing from ref_int here. | ref_int injects the toolchain *declarations* into the module (design option β) |
| `stage2-rust` | all except `score_time` | `score_time` declares no `score_toolchains_rust`, so `@score_toolchains_rust//...` is not a resolvable apparent repo name in its graph | the Phase-1 transitive-pinning fix lands (PR #278): injecting a `bazel_dep` stub for every module in the resolved set makes the repo present everywhere, and this folds into the base |

Both are named after a **capability**, not a module. That distinction matters: the file may
branch, but the branch condition must be derivable from the module's own sources — never
duplicated by hand for a module name.

Deleted and not to be reintroduced: `stage2-libclang-communication`. It was a `//`-relative
label in a ref_int-owned file that only resolved because the module happened to be the Bazel
root. Under layering `score_communication` registers its own libclang toolchain
unconditionally (`.bazelrc`: `common --extra_toolchains=//bazel/toolchains:score_communication_libclang_toolchain`),
so ref_int does not need to name it at all.

## Decisions ref_int made deliberately (criterion 5)

Anything here is a place where Stage 2 differs from the module's own CI **on purpose**.
Anything *not* here that differs is a bug.

| Decision | Effect | Rationale |
|---|---|---|
| `--test_tag_filters=-manual,-miri,-no-coverage` | miri and `no-coverage`-tagged tests do not run in Stage 2 | ref_int registers no miri toolchain; `*_tsan_test` under `bazel coverage` reports false races on non-atomic `__gcov*` counters |
| `--copt/--linkopt=-fprofile-update=atomic` | gcov counters updated atomically | makes any remaining multithreaded coverage test race-free |
| `--repo_env=ANDROID_HOME=` | `android_sdk_repository` gets an empty stub | GitHub runners leave `ANDROID_HOME` set after the SDK is removed; only `score_baselibs` guards against this itself |
| Rust coverage extraction is skipped in module context | no `*_rust` coverage rows for Rust-only modules | the `rust_coverage_*` targets are generated in ref_int's `rust_coverage/BUILD` and do not exist inside a module checkout. **Tracked gap, reported explicitly in the aggregate report — not silently absent.** |
| `score_communication` keeps its own coverage report generator | its `coverage.bazelrc` (imported unconditionally by its `.bazelrc`) emits a pre-built llvm-cov HTML zip, so genhtml is skipped and it contributes no lcov numbers | its llvm-cov pipeline is the path its own CI exercises; forcing uniform gcov is a larger, separately-testable change |

## Known limitations

**Transitive dependencies are not pinned.** `overwrite()` injects an override only for deps the
module declares itself, so everything reached transitively resolves via the module's own MVS.
Measured on `score_time`: of ref_int's 155 resolved modules, 127 agree, **3 were built at a
different version** (`boringssl` 0.20241024.0 vs resolved 0.20251124.0, `zlib` 1.3.1.bcr.5 vs
1.3.1.bcr.8, `score_rules_imagefs` 0.0.3 vs 0.0.1) and 7 are absent from its graph entirely. So
the DR-008 claim currently holds for the directly-declared slice, not the whole resolved set.

`verify_stage2_resolution.py` splits these deliberately: a dep ref_int **did** inject an
override for that still mismatches is an injection failure and **fails** the job; a transitive
one **warns**. Tracked against Phase 1 (PR #278) — the fix is to inject a `bazel_dep` stub plus
override for every module in the resolved set. Once that lands, run the verifier with
`--strict` and fold `stage2-rust` into the base config.



Stage 2 runs `bazel coverage` with `--build_tests_only`, so **non-test targets are never
analyzed**. A resolved set in which a module's own binary cannot build will not be caught. Live
example: `score_time`'s `TimeDaemon`/`TimeSlave` depend on
`@score_lifecycle_health//src/lifecycle_client_lib`, which does not exist at the lifecycle
commit ref_int resolves — Stage 2 is green regardless. This is a scope limit, not a pass.
