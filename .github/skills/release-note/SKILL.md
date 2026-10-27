---
name: release-note
description: "How-to reference for creating the S-CORE platform release note (docs/s_core_v_1/releases/release_note_score_vX_Y.rst). Defines the document format, the data sources (known_good.json, git log, module GitHub releases), the generator script for the deterministic parts and the rules for the AI-written narrative sections. Use when preparing, regenerating or reviewing a platform release note. The release-note agent orchestrates the run; this skill holds the 'how'."
argument-hint: "release tag, e.g. v0.10.0 (and optionally origin tag)"
---

# Platform Release Note — the "how"

Format basis: the official template `wp__platform_sw_release_note`
(`process_description/process/folder_templates/platform/docs/release/release_note.rst`),
adapted as described below. The **[release-note agent](../../agents/release-note.agent.md)**
runs the procedure; this skill holds the rules.

## Document format

| Section | Source | Written by |
|---|---|---|
| Header (`document` directive, Platform Name, Release Tag, Origin Release Tag, Release Date) | CLI args, tag date | script |
| Overview (fixed intro sentence only, no summary of the changes) | release and origin tag | script |
| Disclaimer | fixed text | script |
| Changes to the Platform: New Features / Breaking Changes (platform-level only) | `collect_changes.py` (this repo's PRs, modules' own release notes, impact hints), `--changes` table | AI |
| Reference Integration scope: Version, Source / tag, Release notes, Platform Verification Report (bullets) | release tag | script |
| Integrated Software Modules (table incl. `score_platform` first; extra column Module verification report) | `known_good.json` group `target_sw` + `score_platform` | script |
| Associated Infrastructure Modules (table) | `known_good.json` group `tooling` (without `score_platform`) | script |
| Images (subchapter after the two module tables; table: Name, Tarball, How-to, Description) | release assets, README/runner docs at the tag | script |
| Known Issues, Upgrade Instructions, Contact | fixed text, link to `known_good.json` at the tag | script |

The scope section describes this repository (reference_integration) and holds
links only; no change narrative. Changes of this repository and of the images
go into **Changes to the Platform**.

Every chapter heading carries an icon (emoji) so that readers recognise the
topic at a glance. The mapping is `ICONS` in the script. The script also makes
the heading underline longer, because emoji are double-width and docutils would
warn about a too short underline (warnings are errors in the docs build). Use
the same mechanism when adding a chapter; do not add icons to the `~~~` item
subsections or to the title.

Module tables have the columns **Name** (link to the repo at the pinned
tag/commit), **Version**, **Release notes** (link to the GitHub release of that
tag). The Integrated Software Modules table has a fourth column **Module
verification report**: a `:doc:` link taken from
`docs/verification_report/modules/index.rst` (always the latest report in the
current docs tree), `---` where the module has none (e.g. the platform). Every
empty table cell is written as `---`.
Never write module versions or links by hand.

Image table: the image catalogue (`IMAGES` in the script) lists name,
`images/<dir>`, description and how-to candidates. An image is listed only if
`images/<dir>` exists at the release ref. Tarball is a release asset whose name
contains the image directory name, else `---` (currently no image tarballs are
published). How-to is the first candidate that exists at the ref, else `---`.
When an image is added or renamed in `images/`, update `IMAGES`.

## Generator

```bash
# Skeleton (known_good.json is read from the release tag if it exists, else the working tree)
python3 scripts/release_note/generate_release_note.py --release v0.10.0 --origin v0.9.0 \
    --date 2026-11-02 --output docs/s_core_v_1/releases/release_note_score_v0_10.rst

# Module version changes origin -> release (input for the narrative)
python3 scripts/release_note/generate_release_note.py --release v0.10.0 --origin v0.9.0 --changes
```

Behaviour worth knowing:

- Tags are resolved with `git ls-remote --tags` on every module repo. A
  `version` pin maps to `v<ver>` or `<ver>`; a `hash` pin maps to a tag only if
  one points exactly at that commit, otherwise the row shows `<sha7> (unreleased)`,
  links the commit and has no release-notes link.
- Warnings (`no tag for version ...`) on stderr mean a broken link. Fix the
  `known_good.json` pin or report it, never silence it.
- Modules with `"enabled": false` are skipped.
- Unknown `known_good.json` groups abort the run; extend `SECTIONS` then.
- Narrative sections are emitted as `.. AI-FILL: <instruction>` comments
  (only New Features and Breaking Changes; Overview has no AI text).

## Run from scratch (any release, also for not yet tagged ones)

The procedure is identical for existing and new releases; only the inputs differ.

1. **Inputs.** `release` and `origin` tag (for example `v0.10.0` / `v0.9.0`),
   output file `docs/s_core_v_1/releases/release_note_score_v<major>_<minor>.rst`.
   Planned release date if the release tag does not exist yet.
2. **Prepare.** `git fetch origin main --tags`. The local `main` may be behind;
   for an upcoming release read `known_good.json` from `origin/main` with
   `--known-good-ref origin/main` (the working tree stays untouched). Export
   `GITHUB_PAT` for the GitHub API calls of `collect_changes.py` (anonymous
   access is rate limited); never print it.
3. **Skeleton.** Run the generator (see above). Check the stderr warnings.
4. **Evidence.** Run `collect_changes.py` with the same `--release`, `--origin`
   and `--known-good-ref`, plus the `--changes` table. Runtime is a few minutes.
5. **Narrative.** Replace the two `AI-FILL` markers (New Features, Breaking
   Changes) with the rules below. Nothing else in the file is written by hand.
6. **Index.** `docs/s_core_v_1/releases/releases.rst` lists the notes in an
   explicit order (a glob would sort `v0_10` before `v0_5`); append the new file
   at the end of that `toctree`.
7. **Validate** (checklist below) and report.

An existing note is never overwritten unless the user asks for it; to compare,
write to another path (for example under `/tmp`).

Re-running with the same inputs gives the same tables and chapter structure.
The narrative may be worded differently, but it has to name the same items if
the evidence did not change; when in doubt, keep the items and cite the same
PRs.

## Writing the narrative (AI-FILL)

"Changes to the Platform" has exactly two chapters: **New Features** and
**Breaking Changes**. It lists **platform-level** changes only. The release note
already links the release notes of every module, so module internals are not
repeated here.

What is platform-level:

1. Module set: newly integrated, removed or renamed modules and major version
   jumps (from the `--changes` table of `generate_release_note.py`).
2. Changes of this repository (reference_integration): new or changed images and
   platforms, Bazel/toolchain updates, build and integration mechanisms (for
   example the resolved-dependency override), new demos, documentation or
   process deliverables.
3. Cross-module changes: the same change in several modules (for example all of
   them moving from `baselibs_rust` to `baselibs`). Identical PR titles in
   several repos, or a module's release note, point to them.
4. Breaking changes of a module **with impact on integrators or other modules**,
   for example a removed flag that `known_good.json` still sets. Breaking changes
   without such impact stay in the module's own release note.

Evidence:

```bash
python3 scripts/release_note/collect_changes.py --release v0.10.0 --origin v0.9.0 --output /tmp/changes.md
```

The output has one section for the merged PRs and closed issues of this
repository and one section per changed module with the **breaking** and
**new-feature** parts of the module's own GitHub release notes. For every
breaking part the script lists "impact hints": places in this repository that
mention a flag, label or symbol named there. `--module <key>` restricts the run,
`--module-prs` adds the merged PRs of a module (slow, only for a deep dive),
`--include-infra` adds the infrastructure modules.

Classification:

- Impact hints are leads, not verdicts. A hint is only meaningful if the hit really
  uses what the module removed or changed (for example a flag set in
  `known_good.json` or `.bazelrc` that the release note says was removed). A hit
  that merely shares a name (a different configuration with a similar name) is a
  false alarm; ignore it.
- **Breaking**: removed or renamed module, target, flag or API that integrators or
  other modules use, changed behaviour requiring action. An impact hint in this
  repository is strong evidence. Without any hint, treat it as module-internal
  and omit it.
- **New feature**: new module, platform, image, integration capability or
  deliverable; or a module feature that is visible across the platform.
- Anything else is omitted. When unsure, omit it and name it in the final report.
- Labels like `breaking` or `feature` are rare in the repositories and not
  reliable; decide from title, description and the module's release note. If
  `release-note:*` labels or a `release-note` block exist in a PR, they take
  precedence.

Rules:

- Only state facts found in the evidence. No invented features, dates or versions.
- One `~~~` subsection per item, written for integrators; link to the PR, issue or
  the module's release note as RST links (`` `text <url>`__ ``).
- Breaking changes state what integrators have to do.
- Remove **Breaking Changes** only if there is none; never leave an `AI-FILL`
  marker behind (`grep -n AI-FILL <file>` must be empty).
- Report items you left out although they looked relevant, and modules without
  GitHub releases in the range.

Known limits of the evidence:

- Only some modules (for example Baselibs) structure their GitHub release notes
  with "Breaking changes" and "New features" sections. For the others the
  collector prints "No breaking/new-feature sections found"; there is then no
  module-level evidence, and you must say so in the report instead of guessing.
- Hash-pinned modules (`<sha7> (unreleased)`) have releases only up to their
  latest tag; changes after it are not covered by release notes.
- Impact hints search `known_good.json`, `.bazelrc`, `bazel_common`, `patches`,
  `images`, `showcases` and the integration tests; they do not understand code.

## Validation

- `grep -n "AI-FILL" <file>` is empty.
- `releases.rst` lists the new note last.
- Every `~~~` item and every bullet names a PR, issue or release note link.
- Every table row links to an existing tag (no stderr warnings).
- Platform scope version equals the `score_platform` row source.
- Docs build: `bazel run --lockfile_mode=error //:docs_shim -- --github_user=eclipse-score --github_repo=reference_integration`
  (heavy; optional locally, CI runs it).
