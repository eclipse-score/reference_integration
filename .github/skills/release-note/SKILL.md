---
name: release-note
description: "How-to reference for creating the S-CORE platform release note (docs/s_core_v_1/releases/release_note_score_vX_Y.rst). Defines the document format, the data sources (known_good.json, merged PRs and removed files of this repository, module GitHub releases), the generator script for the deterministic parts and the rules for the AI-written narrative sections. Use when preparing, regenerating or reviewing a platform release note. The release-note agent orchestrates the run; this skill holds the 'how'."
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
| Status banner directly below the title: **DRAFT** (`.. warning::`, title suffix "(DRAFT)", `:status: draft`) or **FINAL** (`.. note::` with link to the release tag, `:status: valid`) | `--final` | script |
| Header (`document` directive, Platform Name, Release Tag, Origin Release Tag, Release Date) | CLI args; Release Date = due date of the milestone `v<major>.<minor>` in [eclipse-score/score](https://github.com/eclipse-score/score/milestones) | script |
| Overview (fixed intro sentence) | release and origin tag | script |
| Architecture diagram (figure in the Overview, SVG in `docs/s_core_v_1/releases/_assets/architecture_vX_Y.svg`) | `known_good.json` (release and origin), `images/`, components from `needs.json` | script (`architecture_diagram.py`) |
| Disclaimer | fixed text | script |
| Changes to the Platform: New Features / Breaking Changes (platform-level only) | `collect_changes.py` (this repo's PRs, modules' own release notes, impact hints), `--changes` table | AI |
| Reference Integration scope: Version, Source / tag, Release notes, Platform Verification Report (bullets) | release tag | script |
| Integrated Software Modules (table incl. `score_platform` first; extra column Module verification report) | `known_good.json` group `target_sw` + `score_platform` | script |
| Associated Infrastructure Modules (table) | `known_good.json` group `tooling` (without `score_platform`) | script |
| Images (subchapter after the two module tables; table: Name, Tarball, How-to, Description) | release assets, README/runner docs at the tag | script |
| Known Issues, Upgrade Instructions (registry hint, hint for commit pins, link to `known_good.json` at the tag), Contact | fixed text | script |

The scope section describes this repository (reference_integration) and holds
links only; no change narrative. Changes of this repository and of the images
go into **Changes to the Platform**.

Every chapter heading carries an icon (emoji); the mapping is `ICONS` in the
script. When adding a chapter, add its icon there instead of typing it into the
heading (the script also lengthens the underline for the double-width emoji).
The title and the `~~~` item subsections have no icon.

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
contains the image directory name, else `---`. How-to is the first candidate that exists at the ref, else `---`.
When an image is added or renamed in `images/`, update `IMAGES`.

## Draft and final

A note has one of two states. The release note is part of the release and is
finalised before the tag is created, so the state is set explicitly:

- **Draft** (default) while the release is in progress: the note shows the
  current state of the release branch. Title suffix "(DRAFT)", a warning
  banner on top and `:status: draft`.
- **Final** with `--final`, only when the user says the note is final (content
  frozen for the release). No title suffix, a note banner with the link to the
  release tag and `:status: valid`.

To make a draft final, refresh it with `--final` as described in "Run from
scratch" and keep the reviewed narrative.

## Generator

```bash
# Skeleton (known_good.json is read from the release tag if it exists, else the checked-out release branch)
python3 scripts/release_note/generate_release_note.py --release vX.Y.0 --origin vX.W.0 \
    --output docs/s_core_v_1/releases/release_note_score_vX_Y.rst

# Module version changes origin -> release (input for the narrative)
python3 scripts/release_note/generate_release_note.py --release vX.Y.0 --origin vX.W.0 --changes
```

Behaviour worth knowing:

- Tags are resolved with `git ls-remote --tags` on every module repo. A
  `version` pin maps to `v<ver>` or `<ver>`; a `hash` pin maps to a tag only if
  one points exactly at that commit, otherwise the row shows `<sha7> (unreleased)`,
  links the commit and has no release-notes link.
- The Release Date is always the due date of the milestone `v<major>.<minor>`
  (for `vX.Y.0`: milestone `vX.Y`) in eclipse-score/score. Do not pass `--date`;
  it only exists as an override when the user asks for a different date. If
  the milestone or its due date is missing, the script warns and writes `TBD`;
  report this instead of guessing a date.
- Warnings (`no tag for version ...`) on stderr mean a broken link. Fix the
  `known_good.json` pin or report it, never silence it.
- Modules with `"enabled": false` are skipped.
- Unknown `known_good.json` groups abort the run; extend `SECTIONS` then.
- The two narrative sections (New Features, Breaking Changes) are emitted as
  `.. AI-FILL: <instruction>` comments.

## Architecture diagram

Every skeleton run renders the diagram from scratch
(`scripts/release_note/architecture_diagram.py`, called by the generator) to
`docs/s_core_v_1/releases/_assets/architecture_v<major>_<minor>.svg` and embeds
it with `.. figure::` in the Overview. The SVG is a generated file: never edit
it by hand and never keep an old one; regenerate it with the skeleton.

Content:

- Header: release, DRAFT/FINAL badge (`--final`), release date, origin and key
  figures (software modules, components, infrastructure modules, images).
- Left column over the full height: platform, infrastructure and tooling
  modules (`score_platform` + group `tooling`).
- Right: the integrated software modules as tiles side by side (no layering),
  each with version, the version in the origin release ("was ...") and its
  components as chips; below them the target images (same catalogue as the
  image table, dashed = experimental).
- Colour bar: green = released tag, orange = commit pin; NEW = not in the origin
  release.

Components come from the Sphinx-Needs of the `needs.json` of the **checked-out
branch**: the generator runs `bazel build //:needs_json_file` (Bazel caches it
and rebuilds only when the docs inputs changed; the first run takes a few
minutes) and reads `bazel-bin/needs.json`. These are the module docs at the
pins of the checkout, so components, versions and images describe the same
state. It takes every `comp` need whose source lies in
`modules/<module key>/`, plus the `includes` of the module's `mod` need (a `mod`
need outside the module docs, for example in `score_platform`, is matched by its
title). Modules without such needs show "no components documented"; report
them, do not add components by hand. If the Bazel build fails, the generator
stops; fix the build instead of falling back to another `needs.json`.
`--needs <file>` skips the build and is only for reproducing a diagram from a
kept `needs.json`.

The diagram is a pure function of its inputs: `known_good.json` at the release
ref and at the origin tag, `images/` at the release ref, the `needs.json` of the
checkout, the milestone date and the state (`--final`). There is no randomness,
no timestamp and no layout state; the same inputs give a byte-identical SVG. To
check, run the generator twice to a scratch output and `cmp` the SVG.
Run it on the checked-out release branch without `--known-good-ref`; with
another ref the components would still come from the checkout.
Colours follow the S-CORE docs theme (header `#2D1942`); change them only in
`architecture_diagram.py`.

## Run from scratch (any release, also for not yet tagged ones)

The procedure is identical for existing and new releases; only the inputs differ.
In chat, the prompt `/release-note` (`.github/prompts/release-note.prompt.md`)
asks for release, origin and state (`draft` or `final`) and starts the agent.

1. **Inputs.** `release` and `origin` tag and the output file
   `docs/s_core_v_1/releases/release_note_score_v<major>_<minor>.rst`. The
   release date is taken from the milestone (see above).
2. **Prepare.** Check out the release candidate branch of the release and
   update it (`git pull`, `git fetch --tags`). The note is created and
   committed only there; it reaches `main` when the release branch is merged
   back after the release. Never add a release note on `main` directly, it
   would conflict with that merge. Both scripts read the checked-out state by
   default; the release branch must be pushed, because the collector compares
   commits through the GitHub API. Set `GITHUB_TOKEN` for the GitHub API calls
   (anonymous access is rate limited); never print it.
3. **Skeleton.** Run the generator (see above); it also builds the
   `needs.json` of the checkout with Bazel and writes the architecture diagram
   (see "Architecture diagram"). Check the stderr warnings.
4. **Evidence.** Run `collect_changes.py` with the same `--release` and
   `--origin`, plus the `--changes` table. Runtime is a few minutes.
5. **Narrative.** Replace the two `AI-FILL` markers (New Features, Breaking
   Changes) with the rules below. Nothing else in the file is written by hand.
6. **Index.** Make sure the new note is part of the `toctree` in
   `docs/s_core_v_1/releases/releases.rst` on the release branch.
7. **Validate** (checklist below) and report.

An existing note is never overwritten unless the user asks for it; to compare,
write to another path. To refresh the tables of an existing draft (for example
after pin bumps, or to make it final with `--final`), generate to
another path and replace everything outside "Changes to the Platform"; keep the
reviewed narrative. The diagram SVG is always overwritten by the run, so it
matches the refreshed tables.

Re-running with the same inputs gives the same tables and chapter structure.
The narrative may be worded differently, but it has to name the same items as
long as the evidence did not change.

## Writing the narrative (AI-FILL)

"Changes to the Platform" has exactly two chapters: **New Features** and
**Breaking Changes**. It lists **platform-level** changes only. The release note
already links the release notes of every module, so module internals are not
repeated here.

What is platform-level:

1. Module set: newly integrated, removed or renamed modules and major version
   jumps (from the `--changes` table of `generate_release_note.py`).
2. Changes of this repository (reference_integration): new or changed images and
   platforms, Bazel/toolchain updates, build and integration mechanisms, new
   demos, documentation or process deliverables.
3. Cross-module changes: the same change in several modules (for example a
   dependency that all modules replace). Identical PR titles in several repos,
   or a module's release note, point to them.
4. Breaking changes of a module **with impact on integrators or other modules**,
   for example a removed flag that `known_good.json` still sets. Breaking changes
   without such impact stay in the module's own release note.

Evidence:

```bash
python3 scripts/release_note/collect_changes.py --release vX.Y.0 --origin vX.W.0 --output changes.md
```

The output has one section for the merged PRs and closed issues of this
repository, one for the files of this repository that were removed or renamed
(per directory, without `docs/` and `patches/`), and one section per changed
module with the **breaking** and **new-feature** parts of the module's own
GitHub release notes. For every
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
- **Breaking**:
  - this repository: a removed or renamed script, target, configuration file or
    mechanism, in particular one that an earlier release note announced. The
    "removed or renamed files" section points to them; read the PR that removed
    them.
  - a module: a removed or renamed module, target, flag or public API, or
    changed behaviour requiring action, as stated in the module's release note
    ("breaking" section). List it if this repository uses it (impact hint) or
    if it is a public API that applications use directly; say which of the two
    applies. Changes of internals stay in the module's release note.
- **New feature**: new module, platform, image, integration capability or
  deliverable; or a module feature that is visible across the platform.
- Anything else is omitted. When unsure, omit it and name it in the final report.
- PR labels like `breaking` or `feature` are not used consistently; decide from
  title, description and the module's release note.

Rules:

- Only state facts found in the evidence. No invented features, dates or versions.
  Read the PR description before describing a PR; the title alone is not enough
  (a PR may replace something instead of extending it).
- One `~~~` subsection per item with a short noun-phrase title, written for
  integrators; link to the PR, issue or the module's release note as RST links
  (`` `text <url>`__ ``). Name new scripts, targets or settings that
  integrators use.
- Order of the items: module set, integration and build, images and platforms,
  tests, documentation; breaking changes of this repository before those of
  the modules (one subsection per module, in table order).
- Breaking changes end with "Action required: ...".
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
- The Overview contains the `.. figure::` of the diagram and the SVG
  `docs/s_core_v_1/releases/_assets/architecture_v<major>_<minor>.svg` was
  written by this run (it is committed together with the note).
- The new note is part of the `toctree` in `releases.rst`.
- Every `~~~` item and every bullet names a PR, issue or release note link.
- Every new module of the `--changes` table and every removed mechanism of this
  repository is either in the note or named in the report.
- No stderr warnings of the generator; `(unreleased)` rows are named in the report.
- The scope links point to the release tag.
- Docs build: `bazel run --lockfile_mode=error //:docs_shim -- --github_user=eclipse-score --github_repo=reference_integration`
  (heavy; optional locally, CI runs it).
