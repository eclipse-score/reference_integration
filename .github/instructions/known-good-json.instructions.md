---
description: "Use when adding a module to known_good.json, bumping a module's hash/version, changing a module's docs/bazel_patches/metadata, or touching the known_good workflow. Covers the mandatory regeneration step and CI checks that catch forgetting it."
applyTo: "known_good.json,scripts/known_good/**"
---

# known_good.json workflow

`known_good.json` is the single source of truth for which modules — and at
which commit/version — are part of the integration. `bazel_common/score_modules_*.MODULE.bazel`,
`rust_coverage/BUILD` and `bazel_common/docs_bundles.bzl` are all **generated**
from it — never edit those generated files by hand.

## After every edit to known_good.json, always run:

```bash
python3 scripts/known_good/update_module_from_known_good.py
```

This regenerates, in one go:

- `bazel_common/score_modules_target_sw.MODULE.bazel` / `score_modules_tooling.MODULE.bazel`
  (`bazel_dep` + `git_override`/`single_version_override` + `patches = [...]` per module)
- `rust_coverage/BUILD` (a `rust_coverage_report` target for every module with `"rust"` in `langs`)
- `bazel_common/docs_bundles.bzl` (the `DOCS_BUNDLES` mounts consumed by the `docs()` macro)

Then commit the regenerated files **together with** the `known_good.json` change.
`git diff` must show changes in all affected generated files — if you changed a
module's `docs` flag or hash and a file that should reflect it doesn't change,
something is wrong (see the known bug note below).

## Then refresh the Bazel lockfile

Any change to a `bazel_dep` / `git_override` / `single_version_override` (new module,
bumped hash/version) changes the resolved module graph, which requires updating
`MODULE.bazel.lock` — see
[module-bazel-lock.instructions.md](./module-bazel-lock.instructions.md) for that step.
Do this **after** regenerating the `known_good.json`-derived files above, since the
lockfile update re-resolves against the newly generated `bazel_dep`/override entries.

## Bumping an existing module (hash or version)

- Manual edit: change `hash` (git-pinned modules) or `version` (registry modules) in
  the module's entry, then run the regenerate command above.
- Automated bump to latest HEAD of the tracked branch:
  `python3 scripts/known_good/update_module_latest.py` (skips modules with
  `"pin_version": true`).
- To override a repo's commit programmatically before regenerating, use
  `scripts/known_good/override_known_good_repo.py` first.
- `hash` and `version` are mutually exclusive per module entry.

## Checking whether a module's local patch is still needed after a bump

1. `patch --dry-run` against a fresh shallow clone at the new hash — "Reversed (or
   previously applied) patch detected" means the patch is definitely obsolete, but a
   clean apply does **not** prove it's still functionally required.
2. Ground truth: find every `@<module>//...` label reference_integration actually
   touches (grep the repo, plus `code_root_path`/docs bundle usage in
   `known_good.json`), then `bazel query`/`bazel build` those exact targets with the
   patch removed. If clean, the patch is obsolete — remove it from `bazel_patches` in
   `known_good.json`, delete the `.patch` file, and re-run the regenerate command.

## CI checks that catch a forgotten regeneration

- **Known Good Matches Bazel** (`known_good_correct.yml`) — re-runs
  `update_module_from_known_good.py` and fails if the generated Bazel fragments
  differ from what was committed.
- **Bzlmod Lockfile Check** (`bzlmod-lock.yml`) — fails if `MODULE.bazel.lock` is out
  of sync with the module graph (see the lockfile instructions).

## Known pitfalls

- `update_module_from_known_good.py`'s `main()` previously forgot to actually write
  `docs_bundles.bzl` even though the generator function existed (fixed 2026-09-17,
  but always verify with `git diff bazel_common/docs_bundles.bzl` after toggling a
  module's `"docs"` flag).
- A module can live in a different generated `*.MODULE.bazel` file depending on its
  group (`target_sw` vs `tooling`) — when verifying a regen, grep across all
  `bazel_common/*.MODULE.bazel` files, not just the one that "sounds right".
