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
- If the pinned `hash`/`version` is newer than the latest release (the release
  is an ancestor of it, compare `ahead_by == 0`, `behind_by > 0`), the pin is
  kept unchanged and shown as *kept* in the table.
- `--use-head MODULE …` pins the given modules to the head commit of their
  `branch` (as `hash`) instead of the latest release, e.g. when a needed fix is
  only on `main`; shown as *branch head* in the table.

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
| `Now` | Latest registry release, (date), then the commits it gains (`+N`) or drops (`-N`, bold; `+N/-M` if diverged) compared to `Before`; if `Before` is newer than the release: `Before` *kept*, `+N` since the latest release |
| `Head` | Head commit of the module's `branch` (default `main`), (date), then the commits since `Now`, bold from 10 on |
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
  CI of the draft PR verifies build and tests. A red CI is a valid result;
  fixes follow only on request (section 6).
- One commit with `known_good.json`, the generated `bazel_common/` files and
  `MODULE.bazel.lock`. Message in English.
- Draft PR against `main`, title
  `Pre-release check: latest module releases (<YYYY-MM-DD>)`.
- PR body (English), in this order (reference: PR #508). Sections 4-7 are
  added or updated whenever the branch changes after the first push (section
  6); omit a section only if it would be empty, except *Incompatible Changes*.
  1. One paragraph on the purpose: pins every module of `known_good.json` to
     its latest Bazel registry release (keeping a pinned commit if it is newer
     than that release; name the modules on a branch head) to test whether the
     latest module releases work together; build and tests are verified by
     this PR's CI only, it is not meant to be merged as is.
  2. The report from `/tmp/pre_release_report.md` unchanged
     (one table, *Module versions*).
  3. `### Pinned modules bumped`: modules with `pin_version: true` as
     ``- `module`: old -> new``; one sentence naming the pinned modules that
     already are at their latest release.
  4. `### Modules set to their branch head`: which modules use `--use-head`
     and why (e.g. fixes that make local patches obsolete are not released).
  5. `### Incompatible Changes`: one bullet per change in a module that breaks
     reference_integration (build, tests, docs), format:
     ``- **`module` version: what changed.** Details (link the upstream PR),
     what was adapted here (patch, files) and the upstream follow-up.``
     Keep the heading with no bullets if there are none.
  6. `### Patches checked against the new versions`: one sentence on how the
     patches were checked, then a table `| Module | Patch | Result |` with the
     module version, the patch file and one of *Removed: <why>*, *Still
     needed, rebased (<what changed>)*, *Still needed: <why>*, *New: <why>;
     remove once <condition>*; last row `| all others | | Still apply
     cleanly |`.
  7. `### Cherry-picked` (only if PRs were cherry-picked): ``- #<n>: `<sha>`
     <title>`` plus how conflicts were resolved or why a pick was skipped.
- Create the PR with `gh pr create --draft --base main --head "$BRANCH"
  --title "…" --body-file <file>`. Without `gh`, use
  `POST /repos/eclipse-score/reference_integration/pulls` with
  `"draft": true` and the token from the environment. Update the body later
  with `PATCH /repos/eclipse-score/reference_integration/pulls/<n>`. Use
  unique `/tmp` file names per run (old helper scripts may still exist there).

## 6. Follow-up after CI (only when the user asks)

The first push contains only the version changes (section 5). Fixes are made
only on request, on the same branch, **one commit per patch or change**, and
are listed in the PR body (sections 5.5-5.7).

- **Check a patch before rebasing it.** Clone the module at its new ref under
  `/tmp`, apply the patches in `bazel_patches` order with `git apply`
  (forward), and check failing ones with `git apply --check --reverse`
  (already upstream -> remove). A patch that still applies can still be
  obsolete: re-check its reason against the new ref (e.g. a page that is now
  committed upstream, a dependency that is no longer used). For un-dev
  patches, grep which of the dev-only repos are still referenced by the
  packages reference_integration uses (`code_root_path`, test targets, root
  `BUILD` for `docs_bundle`) and drop hunks for unused ones.
- **Rebase** by re-doing the change on the new ref in the clone and taking
  `git diff` (keep the patch's header text; keep CRLF line endings of CRLF
  files). Remove a dropped patch from `bazel_patches` and delete the file.
- **Verify** with `bazel mod deps --lockfile_mode=update` and
  `bazel query --keep_going` on the used packages (`@module//...`); for docs
  changes `bazel run //:docs` (the `docs-check` job). Patches of
  `git_override` modules do not change `MODULE.bazel.lock`.
- **Docs of mounted modules:** absolute `:doc:` links (`/path`) resolve
  against the reference_integration docs root, not the module's mount point
  (`modules/functional_modules/<module>`); patch them to relative links.
  Sphinx settings of a module's `conf.py` (e.g. `required_in_id`) do not apply
  when mounted; mirror them in `docs/conf.py`. Renamed need IDs (e.g.
  `feat__logging` -> `feat__log_and_trace`) need patches in every module that
  links them.
- **Cherry-picks** from other PRs: `git cherry-pick -x`; skip empty "Initial
  plan" commits; resolve conflicts in generated files by regenerating, and
  skip a pick whose change is already on the branch.
- Stage only the files of the current commit (`git add <paths>`); a staged
  `git rm` from an earlier step otherwise ends up in the wrong commit.
- CI logs: `GET /repos/{repo}/commits/{sha}/check-runs`, then
  `GET /repos/{repo}/actions/jobs/{id}/logs` and follow the redirect
  **without** the auth header. Compare with the same jobs on `main` to tell
  new failures from existing ones.
