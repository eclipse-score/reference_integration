# Stage 2 — Constraint Sheet

Living document. Amend it when a constraint turns out to be wrong, and record why in the
changelog at the end. Every Stage-2 fix is checked against this sheet **before** it is written.

This exists because the same defect was found and fixed three times — `.bazelrc`, dev-dependency
versions, `.bazelversion` — each time by a module breaking rather than by a rule. The sheet's job
is to make the fourth one decidable in advance, and to say when this work is finished.

---

## The sheet

**Problem**
ref_int must build each module as its own Bazel root while imposing the dependency versions
Stage 1 resolved, but bzlmod's override / `dev_dependency` / extension semantics are all
root-relative — so the module's build configuration is absent from the graph Stage 1 resolves,
and which inputs ref_int may therefore impose has never been written down.

**Consumers**
- *Stage-2 job* — needs a checkout whose module graph resolves and whose tests execute.
- *Module team* — a failure must be reproducible in their own repo, or it is not actionable and
  they will not act on it.
- *ref_int integrator* — needs the module exercised against the integrated version set; a
  Stage 2 that validates nothing ref_int resolved produces no integration signal.
- *Module's own CI* — must keep working; ref_int may not require changes to released sources.
- *The next maintainer adding module #9* — must be able to decide, from this sheet alone and
  without a CI failure, whether a given input is ref_int's to set.
- *DR-008 evidence trail* — every failure must be attributable to exactly one owner.

**Invariants**
1. ref_int **replaces** an input's value only if its Stage-1 resolved set contains the complete
   closure of the replacement. *Violated by:* an injected override with a closure member absent
   from `resolved_versions.json`.
2. For any input outside that set ref_int may **add** or **defer**, never replace.
   *Violated by:* a Stage-2 step that overwrites a module-owned file or field wholesale.
3. A module is never built with a Bazel release older than the one it pins.
   *Violated by:* written `.bazelversion` < the module's own.
4. Every input ref_int reads or writes has a row in the Input Inventory before it is acted on.
   *Violated by:* a Stage-2 step touching an input with no row.
5. Injection is ephemeral — confined to the CI checkout, never committed to module sources.
   *Violated by:* a diff in a `repos/` checkout surviving the job.
6. Every failure reaches the report with the owner Stage 2 computed, never one the report
   re-derives. *Violated by:* the Step Summary naming a different owner than the job log.
7. Every element of the mechanism has a caller that requires it today. *Violated by:* a function,
   flag or parsing branch whose only caller is its own test, or handling an input nothing emits.

**Optimizing**
Integration conflicts surfaced per Stage-2 run.
**Tie-break:** when surfacing a conflict requires diverging from the module's own build
semantics, fidelity to the module wins — a failure the module team cannot reproduce is not a
finding, it is noise. *This tie-break is asserted, not ratified — see Escalation E1.*

**Non-goals**
- Making ref_int able to build a module its own CI cannot build.
- Imposing ref_int's quality/documentation tooling versions on modules.
- Converging the matrix onto a single Bazel release (separate decision — see E1).
- Fixing upstream registry inconsistencies.
- Reproducing every module-CI behaviour — only what determines resolution and build semantics.
- Extending Stage 2 beyond linux-x86_64.

**Costs**
- Stage 2 runs a heterogeneous Bazel matrix (8.4.2 / 8.5.1 / 8.6.0): more downloads, more output
  bases, and a module defect that only appears on ref_int's Bazel will not be caught.
- ref_int cannot un-register a toolchain a module registers; version skew must be fixed at the
  source, never papered over in the rc.
- `archive_override` / `local_path_override` cannot be represented in the manifest, so a module
  relying on one keeps its own — unvalidated by ref_int.
- The dev-dependency carve-out means quality tooling versions are unvalidated **by design**.
- `--build_tests_only` means non-test targets are never analysed; a resolved set in which a
  module's binary cannot build passes Stage 2.

---

## Why the invariants take that shape — the measurement

Counted across all 8 `target_sw` modules' `MODULE.bazel` at their `known_good` pins:

| | count |
|---|---|
| `use_extension` calls | 35 |
| …`dev_dependency = True` | **35 (100%)** |
| `register_toolchains` / `register_execution_platforms` | 2 |
| …`dev_dependency = True` | **2 (100%)** |
| `*_override` directives declared by modules | 30 |
| …targeting a module absent from ref_int's 155-entry resolved set | **11** |
| modules declaring a dep at `0.0.0`/no-version (resolvable only via a root override) | **5 of 8** |
| modules whose `.bazelrc` sets `--registry` | **8 of 8** (2 each) |

`dev_dependency` edges and extension usages are active only while the declaring module is root,
and ref_int is root in Stage 1. So **100% of every module's build configuration is invisible to
the graph Stage 1 resolves** — not merely different from it.

That is what makes "inject Stage 1's answer into Stage 2" a *partial* function. Its domain is
the region where the answer is root-independent: the public, non-overridden dependency closure.
Invariants 1 and 2 are that domain restriction written down. They are derived from bzlmod's
semantics, not chosen.

---

## Input Inventory — the definition of done

Every input that determines a Stage-2 build. **Done = every row classified and green.** A new
input with no row is a violation of Invariant 4, not a discovery.

| # | Input | Visible to Stage 1? | Class | Implementation | Status |
|---|---|---|---|---|---|
| 0 | Which targets the gate analyses | ref_int's | own | `stage2_target_args`, shared with the test run | ✅ |
| 1 | Public `bazel_dep` versions | yes | own | injected override | ✅ |
| 2 | Transitive public closure | yes | own | closure from Stage-1 graph | ✅ |
| 3 | `dev_dependency` versions | no (Stage 1) / yes (gate) | **own, iff closure owned** | pinned **with `closure(dep)` from Stage 1**; captured in `module_graph.json` | ✅ |
| 4 | `use_extension` usages (35/35 dev) | no (Stage 1) / yes (gate) | defer — but **recorded** | untouched; captured in `module_graph.json` | ✅ |
| 5 | `register_toolchains` (2/2 dev) | no | add-only | rc adds `--extra_toolchains` | ⚠️ accepted limit |
| 6 | Module's own `*_override` directives | root-only | own **iff** target is in the owned set | stripped + replaced for injected names, in **both** layouts | ✅ |
| 7 | `.bazelversion` | root-only | add-only (floor) | `max(ref_int, module)` | ✅ |
| 8 | Workspace `.bazelrc` | root-only | add-only (layer) | `--bazelrc`, read last | ✅ |
| 9 | `--registry` list | root-only | defer | ref_int sets none | ✅ |
| 10 | `MODULE.bazel.lock` | derived | replace (regenerate) | deleted, rewritten by the resolution gate; test run on `--lockfile_mode=update` with `selection_digest` asserting no version moved (see below) | ✅ |
| 11 | `.bazelignore` (2 of 8) | root-only | defer | untouched | ✅ |
| 12 | Build/test flags and configs | ref_int's | own, add-only | `ci/stage2/module.bazelrc` | ✅ |
| 13 | Environment / `--repo_env` | ref_int's | add-only | `ANDROID_HOME=` stub | ✅ |
| 14 | Test target selection | ref_int's | own | `known_good.json` metadata | ✅ |
| 15 | Patches referenced by overrides | root-relative | defer | `bazel_patches` stripped on injection | ✅ |
| 16 | Module source tree | module's | never touch | — | ✅ |

### Row 3 — dev dependencies are now pinned, with their closure

This row previously read *defer*: dev-declared deps were excluded from the pin scope wholesale.
The stated reason was a measured failure — pinning `score_lifecycle_health`'s dev-only
`score_tooling` to ref_int's commit aborted the build with
`module lobster@0.0.0 not found in registries`, because `lobster`/`trlc` are non-registry modules
only a root can override.

That reading was too broad. The failure is not "dev deps are unsound to pin"; it is Invariant 1
being violated — replacing an input without owning its closure. Injecting `closure(score_tooling)`
alongside it resolves cleanly, and the module then analyses and tests **identically** (246/0/2/248,
its exact baseline). Re-measured end to end on a real build, not through the resolution gate,
which was itself defective at the time the carve-out was decided.

The carve-out's cost was real: `score_platform`, `score_itf`, `score_process` and
`score_docs_as_code` are all in ref_int's resolved set and were all being validated against
versions ref_int never integrated. Scope is now every declared dependency plus the closure of
each, which is Invariant 1 discharged at the point of injection rather than avoided.

Where the closure cannot be supplied — `overwrite()` called without a graph — dev deps drop back
out of scope, so "pinned without its closure" is unrepresentable rather than merely discouraged.

### Row 6 — closed by row 3's fix

`_strip_existing_overrides()` deletes a module's own override for every name ref_int injects.
Stripping is *forced* — Bazel rejects two overrides for one module — so this is legitimate under
Invariant 1 **only while ref_int owns the replacement's full closure**.

Measured: 11 of the 30 module-declared overrides target modules ref_int has no entry for. Under
the old carve-out all 11 were dev-declared and therefore excluded, so the invariant held *by
coincidence of an unrelated rule*. That coincidence is gone now that dev deps are in scope — and
it has been replaced by the thing it was standing in for: a dependency is injected only when it
has an entry in the resolved set, and its closure is pulled in with it. A closure member with no
entry is reported and left alone (Invariant 2's *defer*), and the module's own override for it
survives untouched because ref_int never injects that name.

*Still worth adding:* an explicit assertion at strip time, so the guarantee is checked rather than
inferred from the scope rule. Cheaper now that it can only fail on a genuine gap.

**Amended 2026-08-11 — the strip had a layout hole.** It matched only the exploded layout (closing
`)` on its own line), so a single-line override survived, ref_int's became the *second* one, and
Bazel aborts with `multiple overrides for dep <x> found`. Both layouts are now matched by separate
patterns; one pattern covering both would swallow a neighbouring override instead. Latent, not
live — all three modules that declare overrides today write them exploded.

### Rows 5 and 6b — accepted limitations, not pending work

- **Toolchain registration (5).** ref_int cannot un-register what a module registers; only
  additive `--extra_toolchains` is available. Skew must be fixed at the module.
- **Unrepresentable overrides (6b).** `archive_override` / `local_path_override` cannot be
  expressed in the manifest and are dropped with a warning. Those deps are ref_int-unvalidated.

Both are consequences of bzlmod semantics, not of this implementation. Recording them as
accepted is what stops them being rediscovered as bugs.

---

## Escalation E1 — unresolved, and blocking a final answer

Two requirements point in opposite directions, and every root-context input sits on the fault
line between them:

- **Fidelity** — a module must not be built with semantics different from its own CI, or its
  failures are not actionable by the team that owns them.
- **Integration signal** — Stage 2 exists to surface conflicts between modules *at one
  integrated configuration*; the more of the module's own configuration is preserved, the less
  Stage 2 differs from simply re-running each module's CI.

The sheet currently asserts **fidelity wins**. That is a defensible reading of the Stage-2
acceptance criteria, but it was never ratified, and it decides real questions:

| If fidelity wins | If integration signal wins |
|---|---|
| `.bazelversion` floor (current) | ref_int pins one Bazel; raise ref_int to ≥ the newest module |
| heterogeneous 8.4.2/8.5.1/8.6.0 matrix | one release across the matrix |
| dev-dep carve-out permanent | dev deps in scope, with ref_int owning their closure |

**Decision requested:** which of the two wins when they conflict?

**What would settle it empirically:** run the full Stage-2 matrix under a single Bazel ≥ 8.6.0
and count modules that fail on configuration alone. If that number is zero, the two requirements
do not actually conflict today and the tie-break can stay theoretical. If it is non-zero, the
cost of "integration signal wins" is now a measured number rather than an argument.

That experiment has not been run. It is cheap, and it is the check that decides E1.

---

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-08-11 | Sheet tracked in git. Invariants 6 (the owner Stage 2 computes is the owner the report prints) and 7 (every element has a caller today) added. Row 6 closes — the strip now matches both override layouts. Row 10 corrected: the test run is on `--lockfile_mode=update` with `selection_digest`, not `--lockfile_mode=error`. | Audit of both PRs ([`docs/dr8_pr_inspection.md`](../../docs/dr8_pr_inspection.md)). The sheet was never committed, so fixes were never checked against it: the three-bucket attribution landed in `quality_runners.py` only while the report re-derived ownership from `total == 0`; nine code paths had no producer or consumer; the override strip missed the single-line layout; and `known_good_tests` was never invoked by any workflow. Row 10's staleness is the same failure — the sheet asserted a guarantee the code had already replaced. |
| 2026-08-10 | Row 3 moves from *defer* to **own iff closure owned**: dev-declared deps are pinned together with `closure(dep)`. Row 6 closes. New row 0: the gate analyses the test run's target set, never more. Third attribution bucket added — *integration conflict*. | The gate (`bazel mod deps`) evaluated every module extension in the graph and failed `score_lifecycle_health` on a latent `grpc`/`grpc-java` inconsistency no build reaches — identically with and without ref_int's injection. Every conclusion drawn while that gate was the instrument had to be re-measured. Re-measured against real builds: the injection was always correct (248 tests, exact baseline), and the dev-dep carve-out was an over-correction for an Invariant 1 violation. Fourth symptom-driven fix predicted by this sheet's own preamble — this time the sheet's rule, not a module breaking, is what identified the real scope. |
| 2026-08-09 | Rows 3–4 move from *deferred and invisible* to *deferred but recorded*: the resolution gate captures the module-rooted graph (`module_graph.json`) and it is published. Measured on `score_baselibs`: 97 modules including `score_docs_as_code`, `score_process`, `score_tooling`, `score_bazel_cpp_toolchains`, `toolchains_llvm` — every one of which is absent from Stage 1's artifact by construction. **Pin scope is unchanged**; visibility is not authority. | "Complete closure including dev dependencies" is unobtainable from a ref_int-rooted resolve (no `bazel mod` flag exposes a non-root module's dev edges), but Stage 2 was already computing the module-rooted graph and discarding it. Same move as storing Stage 1's `graph.json`, sourced from the only root that can produce it. |
| 2026-08-09 | Sheet created. Invariants 1–2 derived from the 100%-dev-scoped measurement; inventory populated from all 8 modules at their pins. | Three consecutive symptom-driven fixes to module-owned inputs, with no rule stating which inputs ref_int owns. Supersedes design decision D1 ("ref_int owns every input that determines how a module is built"), which the 100% measurement shows was never implementable and which was retracted without replacement. |
