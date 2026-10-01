---
description: "Use when adding a module, bumping a module's hash/version, or otherwise changing bazel_dep/git_override/single_version_override entries in MODULE.bazel or the generated bazel_common/*.MODULE.bazel files. Covers refreshing and committing MODULE.bazel.lock so the Bzlmod Lockfile Check CI job doesn't fail."
applyTo: "MODULE.bazel,MODULE.bazel.lock,bazel_common/*.MODULE.bazel,known_good.json"
---

# MODULE.bazel.lock refresh workflow

`MODULE.bazel.lock` is a **committed** file that pins the resolved Bazel module
graph. Any change that alters `bazel_dep` / `git_override` / `single_version_override`
entries — directly in `MODULE.bazel`, in a `bazel_common/*.MODULE.bazel` fragment, or
indirectly via a `known_good.json` edit followed by regeneration — changes the
resolved dependency set and makes the committed lockfile stale.

## Always refresh the lockfile after such a change

```bash
bazel mod deps --lockfile_mode=update
```

This re-resolves the module graph and writes the updated dependencies into
`MODULE.bazel.lock`. Run it **after** `python3 scripts/known_good/update_module_from_known_good.py`
if the change originated from `known_good.json` (see
[known-good-json.instructions.md](./known-good-json.instructions.md)) — the lockfile
update must see the already-regenerated `bazel_dep`/override entries.

Commit `MODULE.bazel.lock` together with the change that caused it to go stale.

## Why this matters / how CI catches a forgotten refresh

The **Bzlmod Lockfile Check** CI job (`bzlmod-lock.yml`, merge-queue gating) verifies
`MODULE.bazel.lock` is consistent with the module graph and fails the PR if it's out
of sync. It's easy to forget this step because the build often still works locally
with a stale lockfile (Bazel just re-resolves in memory) — the drift only surfaces
in CI or for other contributors doing a clean checkout.

## Quick check before committing

```bash
git status --short MODULE.bazel.lock
```

If a module version/hash/override change was made and this shows no diff, the
lockfile likely wasn't refreshed — re-run `bazel mod deps --lockfile_mode=update`.
