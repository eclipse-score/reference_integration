---
name: pre-release
description: "How-to reference for the pre-release check of reference_integration: a branch and draft PR that pin every module of known_good.json (target_sw and tooling) to its latest Bazel registry release, regenerate the Bazel files and MODULE.bazel.lock, and list every module with its version before and now and the commits between the release and the module's HEAD (bold from 10 on) in one table with an OK/NOK column. Build and tests are verified by the PR's CI only. Use when testing whether the latest module releases work together, preparing a pre-release PR, or refreshing the module version table. The pre-release agent orchestrates the run; this skill holds the 'how'."
argument-hint: "optional base branch (default: main)"
---

# Pre-release check — rules

The [pre-release agent](../../agents/pre-release.agent.md) runs the procedure;
this skill holds the rules.

## 1. Files

| File | Role |
|---|---|
| `scripts/known_good/update_module_latest_release.py` | Latest registry release per module, release date, commits since release, module table; `--apply` writes the versions into `known_good.json` |
| `scripts/known_good/update_module_from_known_good.py` | Regenerates `bazel_common/score_modules_*.MODULE.bazel` and `bazel_common/docs_bundles.bzl` |
| `MODULE.bazel.lock` | Refreshed with `bazel mod deps --lockfile_mode=update` |
| `known_good.json` | The only file where versions are changed by the script |

Follow `.github/instructions/known-good-json.instructions.md` and
`.github/instructions/module-bazel-lock.instructions.md` for every
`known_good.json` change.

## 2. Version selection (done by the script)

- **All** modules of all groups, including those with `"pin_version": true`.
  The pre-release tests the latest releases; pinned modules are bumped too and
  listed as such in the PR (section 5).
- Registries in `.bazelrc` order: S-CORE registry first, then BCR. The first
  registry that knows the module decides.
- Latest version = semver maximum of `versions` minus `yanked_versions`.
  Pre-releases (`-rc1`, `-alpha`, …) count: `1.0.6-rc1` beats `1.0.5`.
- Release tag from the registry's `source.json` URL (`refs/tags/<tag>`),
  otherwise `v<version>`.
- `--apply` swaps `hash`/`version` for the new `version` in place and bumps
  `timestamp`; no other key in `known_good.json` changes (no model re-serialization).

## 3. Report table (done by the script)

Commit counts come from the GitHub compare API (`ahead_by`/`behind_by`).
Release date is the GitHub release's `published_at`, otherwise the tag's commit
date. A commit (pinned `hash` or branch head) is shown as the release whose tag
points exactly at it (highest tag if several, with the release date); an
untagged commit is shown as the short hash with its commit date.

The report has a single table with every module. The columns are fixed:

| Column | Content |
|---|---|
| `Before` | Release or commit pinned in `known_good.json` so far, (date) |
| `Now` | Latest registry release, (date), then the commits it gains (`+N`) or drops (`-N`, bold; `+N/-M` if diverged) compared to `Before` |
| `Head` | Head commit of the module's `branch` (default `main`), (date), then the commits since the `Now` release, bold from 10 on |
| `OK/NOK` | Empty |

Every commit count links to the GitHub commit list (compare view).
**OK/NOK stays empty**; it is set by hand in the PR later. The table is
changed only by the script: never edit rows or values by hand. Whenever the
table has to change, fix the script if needed, rerun it and replace the whole
table in the PR body with the new output.

## 4. Commands

Prerequisites: `GITHUB_TOKEN` or `GITHUB_PAT` set (never print it), clean
working tree, `git fetch origin`.

```bash
BRANCH=pre-release/$(date +%F)
git switch -c "$BRANCH" origin/main

python3 scripts/known_good/update_module_latest_release.py --apply --report /tmp/pre_release_report.md
python3 scripts/known_good/update_module_from_known_good.py
bazel mod deps --lockfile_mode=update
```

Exit code 2 of the script means at least one module had an error (see the
`Head` column); the other modules are still updated.

## 5. Commit and PR

- **No local build, tests or other checks, and no fixes.** Only the versions
  are replaced (plus the regenerated files and lockfile from section 4); the
  CI of the draft PR verifies build and tests. A red CI is a valid result.
- One commit with `known_good.json`, the generated `bazel_common/` files and
  `MODULE.bazel.lock`. Message in English.
- Draft PR against `main`, title
  `Pre-release check: latest module releases (<YYYY-MM-DD>)`.
- PR body (English), in this order:
  1. One sentence on the purpose (test of the latest module releases, build
     and tests verified by the PR's CI, not meant to be merged as is).
  2. The report from `/tmp/pre_release_report.md` unchanged
     (one table, *Module versions*).
  3. *Pinned modules bumped*: modules with `pin_version: true`, old -> new.
- Create the PR with `gh pr create --draft --base main --head "$BRANCH"
  --title "…" --body-file <file>`. Without `gh`, use
  `POST /repos/eclipse-score/reference_integration/pulls` with
  `"draft": true` and the token from the environment.
