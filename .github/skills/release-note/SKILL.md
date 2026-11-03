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
| Images (subchapter after the two module tables; table: Name, Download, How-to, Description) | `IMAGES` and `IMAGE_DOWNLOADS` in the script, release workflows and README/runner docs at the release ref | script |
| Known Issues (module release notes, incomplete safety packages), Upgrade Instructions (registry hint, hint for commit pins, link to `known_good.json` at the tag), Contact | fixed text | script |

The scope section describes this repository (reference_integration) and holds
links only; no change narrative. Changes of this repository and of the images
go into **Changes to the Platform**.

Every chapter heading carries an icon (emoji); the mapping is `ICONS` in the
script. When adding a chapter, add its icon there instead of typing it into the
heading (the script also lengthens the underline for the double-width emoji).
The title and the `~~~` item subsections have no icon.

Module tables have the columns **Name** (link to the repo at the pinned
tag/commit), **Version**, **Release notes** (one link per module release since
the origin release, oldest first, see "Release range"; a module unchanged since
the origin shows its current release). The Integrated Software Modules table has a fourth column **Module
verification report**: a `:doc:` link taken from
`docs/verification_report/modules/index.rst` (always the latest report in the
current docs tree), `---` where the module has none (e.g. the platform). Every
empty table cell is written as `---`.
Modules that publish their verification evidence as dependable elements (with
L.O.B.S.T.E.R. traceability reports) in their own versioned docs instead of an
S-CORE module verification report are listed in `MODULE_DOCS` (today
Communication). For them the cell lists one link per dependable element, found
in the `searchindex.js` of the module docs at the pinned tag (pages titled
"Dependable element: <name>"); `DEPENDABLE_ELEMENT_LABELS` sets the label and
order (e.g. `mw_com` -> LoLa (mw::com)). An unreleased pin or missing docs give
a warning and `---`.
Never write module versions or links by hand.

Image table: the image catalogue (`IMAGES` in the script) lists name,
`images/<dir>`, description and how-to candidates. An image is listed only if
`images/<dir>` exists at the release ref. How-to is the first candidate that
exists at the ref, else `---`.

Download: images that a workflow uploads to the GitHub release of this
repository are listed in `IMAGE_DOWNLOADS` (`images/<dir>` -> workflow, asset
file name), today only AutoSD (`build_and_test_autosd.yml` uploads
`eclipse-autosd-bootc-qemu-x86_64.qcow2.xz`, the AutoSD QEMU image with the
S-CORE showcases). The link is built from the release tag
(`.../releases/download/<release>/<asset>`), because the assets are uploaded
only when the release is published, after the note is final. The generator
checks that the workflow at the release ref still uploads the asset; if not, it
warns and writes `---`. All other images have `---`.

When an image is added or renamed in `images/`, update `IMAGES`; when a
workflow starts or stops uploading an image to the release, or renames the
asset, update `IMAGE_DOWNLOADS`. Images published by upstream projects (for
example the AutoSD Raspberry Pi 4 image of eclipse-autosd) are not S-CORE
images and are not listed.

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
  `version` pin maps to `v<ver>` or `<ver>` and is shown as that release. A
  `hash` pin is never shown as a release, even if a tag points at the same
  commit (the integration does not use the registry version): the row shows
  `<sha7> (unreleased)` and links the commit, and the diagram marks it as a
  commit pin. A tag on that commit only bounds the release range, so the
  *Release notes* column still lists the releases the commit contains. Report
  such modules and propose to pin them by `version`.
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
- Maturity badge (outlined, bottom right of each software module tile) and a
  legend line with the count per level, see "Module maturity (DR-003)".

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

### Module maturity (DR-003)

Every software module gets exactly one maturity classification of
[DR-003-Strat](https://github.com/eclipse-score/score/blob/main/docs/design_decisions/strategy/DR-003-strat.md)
(Release, Experimental, Preview). `assess_maturity()` in
`architecture_diagram.py` derives it on every run from the same `needs.json`
and the module docs, so a run from scratch always fills it in; never set it by
hand. DR-003 leaves the line between minor and major deviations open, so the
script applies this rule:

| Level | Rule |
|---|---|
| Preview | No verification report: neither a `mod_ver_report` need in `modules/<key>/` (S-CORE module verification report) nor dependable elements in the module's own docs (`MODULE_DOCS`, L.O.B.S.T.E.R. traceability reports). No quality statement possible. |
| Experimental | A verification report exists and makes the gaps transparent (untested or uninspected requirements, missing safety analyses or checklists). |
| Release | Report exists and every component requirement of the module is fully verified (`fully_verifies_back`) and inspected (`valid_inspected`; QM: `valid`). |

The locally built `needs.json` carries no test results, so the script cannot
assign Release. Before a final note, check the module verification reports of
the release branch CI docs build (`github-pages-<sha>` artifact of "Code Quality
& Documentation"): report modules that would meet Release, and the borderline
Experimental modules (report present but no FMEA/DFA, for example). Change the
rule in `assess_maturity()` only after agreement, never the result. The note
links DR-003 below the figure (fixed text of the generator).

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
6. **Index.** Add the new note as the **last** entry of the release-note
   `toctree` in `docs/s_core_v_1/releases/releases.rst` on the release branch.
   The toctree lists the notes explicitly in release order; a glob would sort
   `v0_10` before `v0_5`.
7. **Validate** (checklist below) and report.

An existing note is never overwritten unless the user asks for it; to compare,
write to another path. To refresh the tables of an existing draft (for example
after pin bumps, or to make it final with `--final`), generate to
another path and replace everything outside "Changes to the Platform"; keep the
reviewed narrative. The diagram SVG is always overwritten by the run, so it
matches the refreshed tables. Then run `collect_changes.py` again and add items
for evidence that is not covered yet (new PRs or direct commits on the release
branch); keep the reviewed items unless their evidence changed.

Everything outside "Changes to the Platform" is generated, including Images,
Known Issues and Upgrade Instructions. Lines added there by hand are lost on
the next refresh: carry them into the generator (`IMAGES`, `IMAGE_DOWNLOADS` or
the fixed text in `render`) in a separate commit and regenerate.

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

The evidence of this repository covers the commit range from the origin tag to
the checked-out release branch (not `main`). The output has one section for
the merged PRs and closed issues of this repository, one for the **commits
without PR** in that range (commits pushed directly to the release candidate
branch, with their changed files; commits that only touch
`docs/s_core_v_1/releases/` are skipped), one for the files of this repository
that were removed or renamed
(per directory, without `docs/` and `patches/`), and one section per changed
module with the **breaking** and **new-feature** parts of the module's own
GitHub release notes, for **every** module release since the origin release
("Release range" below), not only the pinned one. For every
breaking part the script lists "impact hints": places in this repository that
mention a flag, label or symbol named there. `--module <key>` restricts the run,
`--module-prs` adds the merged PRs of a module (slow, only for a deep dive),
`--include-infra` adds the infrastructure modules.

Release range: `releases_between()` in `generate_release_note.py` is shared by
the tables and the collector, so both always name the same releases. Candidates
are the published GitHub releases between the origin tag and the pinned tag; a
release counts if the pinned commit contains its tag and the origin commit does
not (GitHub compare), so releases on maintenance branches are skipped and a
release is still found when the origin was tagged on a side commit. Tags
without GitHub release have no release notes and are not listed.

Per release the collector prints the sections whose heading names breaking
changes, deprecations, removals, public API changes, migrations or features,
then "Candidate lines" (list items elsewhere in a hand-written text that mention
a removal, rename, deprecation, breaking change or feature), and then the
**release scope**: every PR of the release's generated "What's Changed" list,
marked `review` or `skip? (<reason>)`. Read all releases of the range; a
breaking change of an intermediate release is still breaking for an integrator
coming from the origin release.

Module releases are classified like the Baselibs release-notes skill
(eclipse-score/baselibs `.agents/skills/release-notes-skill/SKILL.md`) does it:

1. **Scope.** The "What's Changed" list is the scope of a module release. If a
   release has no such list ("scope cannot be determined"), use its curated
   sections and candidate lines only, and say so in the report; do not
   reconstruct the scope from `git log` or a comparison view.
2. **Read every PR to review.** Fetch title, body and author
   (`GET /repos/<owner>/<repo>/pulls/<n>` with `GITHUB_TOKEN`; `gh` is not
   required). When title and body do not support a precise statement, read the
   diff (`GET .../pulls/<n>` with `Accept: application/vnd.github.diff`, or
   `git show` in a local clone) before writing about it.
3. **Skip**: CI/workflow-only PRs, dependency bumps (bots such as
   `eclipse-score-bot`, `renovate`, `dependabot`), Bazel visibility-only
   changes, requirements/doc-only PRs, internal repo-sync or agent-tooling PRs,
   and anything that nets to zero across the range (a change reverted again).
   The `skip?` marks of the collector are title-based hints; confirm them.
4. **Notable**: breaking API or behaviour changes and deprecations, new public
   features or libraries, and anything that continues or completes a change an
   earlier release note announced (for example a deprecation in one release
   and the removal in a later one; the earlier platform release note's
   announcements count too). User-visible bug fixes are notable for the module,
   but this note has no bug-fix chapter; they stay in the module release notes.
5. **Platform filter.** Of the notable items, only those that pass the
   platform-level rules below go into the note.

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
- Commits without PR are classified like PRs; read the commit (`git show`)
  because the subject is often short. Pure pin bumps are already covered by the
  `--changes` table and the module sections.

Rules:

- Only state facts found in the evidence. No invented features, dates or versions.
  Read the PR description before describing a PR; the title alone is not enough
  (a PR may replace something instead of extending it).
- One `~~~` subsection per item with a short noun-phrase title, written for
  integrators; link to the PR, issue, commit (for commits without PR) or the
  module's release note as RST links
  (`` `text <url>`__ ``). Name new scripts, targets or settings that
  integrators use.
- Order of the items: module set, integration and build, images and platforms,
  tests, documentation; breaking changes of this repository before those of
  the modules (one subsection per module, in table order).
- Breaking changes end with "Action required: ...".
- Remove **Breaking Changes** only if there is none; never leave an `AI-FILL`
  marker behind (`grep -n AI-FILL <file>` must be empty).
- Report items you left out although they looked relevant, and modules without
  releases in the range.

Known limits of the evidence:

- Only some modules (for example Baselibs) structure their GitHub release notes
  with "Breaking changes" and "New features" sections; others only have
  GitHub's generated PR list, which is then the only module-level evidence. If
  the collector prints "No breaking/new-feature items and no PR list", there is
  no module-level evidence, and you must say so in the report instead of
  guessing.
- A release scope can be long (Persistency v0.4.0: 176 PRs). Reading every
  `review` PR is required; report how many PRs per module you read.
- GitHub generates "What's Changed" against the previous tag it finds; when the
  origin was tagged on a side commit (Persistency v0.3.5), the list can contain
  PRs that were already in the origin release. Drop a PR if the origin release
  note already lists it.
- Hash-pinned modules (`<sha7> (unreleased)`) have releases only up to their
  latest tag; changes after it are not covered by release notes.
- Impact hints search `known_good.json`, `.bazelrc`, `bazel_common`, `patches`,
  `images`, `showcases` and the integration tests; they do not understand code.

## Validation

- `grep -n "AI-FILL" <file>` is empty.
- The Overview contains the `.. figure::` of the diagram and the SVG
  `docs/s_core_v_1/releases/_assets/architecture_v<major>_<minor>.svg` was
  written by this run (it is committed together with the note).
- The diagram shows a maturity badge on every software module and the Overview
  links DR-003; the generator prints the `maturity (DR-003): ...` line.
- The new note is the last entry of the release-note `toctree` in `releases.rst`.
- The Download column links every image of `IMAGE_DOWNLOADS` (no generator
  warning about a missing asset upload).
- Every `~~~` item and every bullet names a PR, issue, commit or release note link.
- Every new module of the `--changes` table and every removed mechanism of this
  repository is either in the note or named in the report.
- No stderr warnings of the generator; `(unreleased)` rows are named in the report.
- The scope links point to the release tag.
- Docs build: `bazel run --lockfile_mode=error //:docs_shim -- --github_user=eclipse-score --github_repo=reference_integration`
  (heavy; optional locally, CI runs it).
