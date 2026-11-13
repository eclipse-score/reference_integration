---
name: release-note
description: "How-to reference for creating the S-CORE platform release note (docs/s_core_v_1/releases/release_note_score_vX_Y.rst). Defines the document format, the data sources (known_good.json, merged PRs and removed files of reference_integration, module GitHub releases), the generator script for the deterministic parts and the rules for the AI-written narrative sections. Use when preparing, regenerating or reviewing a platform release note. The release-note agent orchestrates the run; this skill holds the 'how'."
argument-hint: "release tag, e.g. v0.10.0 (and optionally origin tag)"
---

# Platform Release Note — rules

The [release-note agent](../../agents/release-note.agent.md) runs the procedure;
this skill holds the rules. Template basis: `wp__platform_sw_release_note`
(`process_description/process/folder_templates/platform/docs/release/release_note.rst`).

## 1. Basics

### 1.1 Files

| File | Role |
|---|---|
| `scripts/release_note/generate_release_note.py` | Generator: skeleton, tables, `--changes` table |
| `scripts/release_note/architecture_diagram.py` | Diagram SVG and DR-003 maturity (called by the generator) |
| `scripts/release_note/collect_changes.py` | Evidence for the narrative |
| `docs/s_core_v_1/releases/release_note_score_v<major>_<minor>.rst` | The note |
| `docs/s_core_v_1/releases/_assets/architecture_v<major>_<minor>.svg` | The diagram (generated) |
| `docs/s_core_v_1/releases/releases.rst` | Release-note `toctree` (explicit list, release order) |

### 1.2 Who writes what

- **Script:** everything except the two narrative chapters.
- **AI:** only *New Features* and *Breaking Changes* (the two `.. AI-FILL:` markers).
- **Never** edit generated parts or write module versions or links by hand.
  If generated content must change, change the generator (`IMAGES`,
  `IMAGE_DOWNLOADS`, `ICONS`, fixed text in `render`) in a separate commit and
  regenerate.

## 2. Document structure

Numbers in parentheses refer to sections of this skill.

| Section | Content | Source |
|---|---|---|
| Status banner (below the title) | DRAFT or FINAL (3) | `--final` |
| Header | `document` directive, platform name, release tag, origin tag, release date | CLI args, milestone (4.2) |
| Overview | fixed intro sentence, architecture diagram (5), DR-003 sentence | release and origin tag |
| Disclaimer | fixed text | script |
| Changes to the Platform | *New Features*, *Breaking Changes* (platform-level only, 8) | **AI** |
| Reference Integration scope | version, source/tag, release notes, Platform Verification Report (links only) | release tag |
| Integrated Software Modules | table, `score_platform` first (2.2) | `known_good.json` group `target_sw` + `score_platform` |
| Associated Infrastructure Modules | table (2.2) | `known_good.json` group `tooling` |
| Images | table (2.3) | `IMAGES`, `IMAGE_DOWNLOADS`, release ref |
| Known Issues, Upgrade Instructions, Contact | fixed text | script |

### 2.1 Headings

- Every chapter heading has an icon from `ICONS`; add a new chapter's icon
  there (the script lengthens the underline for the double-width emoji).
- The title and the `~~~` item subsections have no icon.
- The scope section holds links only. Changes of reference_integration and of the
  images go into *Changes to the Platform*.

### 2.2 Module tables

| Column | Content |
|---|---|
| Name | Link to the repository at the pinned tag or commit |
| Version | `v<x.y.z>`; hash pin: `<sha7> (unreleased)` (4.2) |
| Release notes | One link per module release in the release range (7.3), oldest first; module unchanged since the origin: its current release |
| Module verification report (Integrated Software Modules only) | `:doc:` link from `docs/verification_report/modules/index.rst`; for modules in `MODULE_DOCS`: one link per dependable element |

- Empty cell: `---`.
- `MODULE_DOCS` modules publish their evidence as dependable elements
  (L.O.B.S.T.E.R. reports) in their own versioned docs. Links come from the
  `searchindex.js` of those docs at the pinned tag (pages titled "Dependable
  element: <name>"); `DEPENDABLE_ELEMENT_LABELS` sets label and order.
- Unreleased pin or missing module docs: warning and `---`.

### 2.3 Images table

| Column | Rule |
|---|---|
| Name, Description | From `IMAGES`; an image is listed only if `images/<dir>` exists at the release ref |
| How-to | First how-to candidate that exists at the release ref, else `---` |
| Download | Only images in `IMAGE_DOWNLOADS`: `.../releases/download/<release>/<asset>`, else `---` |

- The download link points to the release tag because the assets are uploaded
  when the release is published. The generator checks that the workflow at
  the release ref still uploads the asset; if not: warning and `---`.
- Image added or renamed in `images/` → update `IMAGES`.
- Workflow starts or stops uploading an image, or renames the asset → update
  `IMAGE_DOWNLOADS`.
- Images of upstream projects are not S-CORE images; do not list them.

## 3. Draft and final

The note is finalised before the tag exists, so the state is set explicitly.

| | Draft (default) | Final (`--final`) |
|---|---|---|
| When | Release in progress | Only when the user says the note is final |
| Title | Suffix "(DRAFT)" | No suffix |
| Banner | `.. warning::` | `.. note::` with link to the release tag |
| `:status:` | `draft` | `valid` |
| Diagram | DRAFT badge, "planned <date>" | FINAL badge, "released <date>" |

- Draft → final: generate the note from scratch with `--final` (6).

## 4. Generator

### 4.1 Commands

```bash
# Skeleton (tables, diagram, AI-FILL markers)
python3 scripts/release_note/generate_release_note.py --release vX.Y.0 --origin vX.W.0 \
    --output docs/s_core_v_1/releases/release_note_score_vX_Y.rst

# Module version changes origin -> release (input for the narrative)
python3 scripts/release_note/generate_release_note.py --release vX.Y.0 --origin vX.W.0 --changes
```

### 4.2 Rules

| Topic | Rule |
|---|---|
| `known_good.json` source | Release tag if it exists, else the checked-out release branch (working tree). Do not pass `--known-good-ref`. |
| `version` pin | Resolved with `git ls-remote --tags` to `v<ver>` or `<ver>`; shown as that release. |
| `hash` pin | Always `<sha7> (unreleased)` with a commit link, also if a tag points at the commit; the diagram marks it as commit pin. A tag on the commit only bounds the release range (7.3). Report the module and propose a `version` pin. |
| Release date | Due date of the milestone `v<major>.<minor>` in [eclipse-score/score](https://github.com/eclipse-score/score/milestones). Do not pass `--date` unless the user asks. Missing milestone or due date: `TBD` and a warning; report it, never guess. |
| stderr warnings | Mean a broken link (e.g. `no tag for version ...`). Fix the pin or report it; never silence it. |
| `"enabled": false` | Module is skipped. |
| Unknown `known_good.json` group | Run aborts; extend `SECTIONS`. |
| Narrative | Emitted as `.. AI-FILL: <instruction>` comments. |

## 5. Architecture diagram

### 5.1 Rules

- Every skeleton run renders it (`architecture_diagram.py`) and embeds it with
  `.. figure::` in the Overview.
- Generated file: never edit it by hand, never keep an old one.
- Run on the checked-out release branch without `--known-good-ref`; with
  another ref the components would still come from the checkout.
- Colours follow the S-CORE docs theme (header `#2D1942`); change them only in
  `architecture_diagram.py`.
- Display size: the figure gets `:width:` `DIAGRAM_WIDTH` (75 % of the content
  width), so the whole diagram fits on screen; a click opens it in full size.
  Change the size only in `DIAGRAM_WIDTH`, keep it a percentage (scales with
  the page) and never set `:height:` (distorts the diagram on narrow screens).

### 5.2 Content

| Area | Content |
|---|---|
| Header | Release, DRAFT/FINAL badge, release date, origin, key figures (software modules, components, infrastructure modules, images) |
| Left column | `score_platform` and group `tooling` |
| Right | Software modules as tiles side by side: version, origin version ("was ..."), components as chips, maturity badge (5.5); below: target images (dashed = experimental) |
| Colour bar | Green = released tag, orange = commit pin; NEW = not in the origin release |
| Legend | Count of modules per maturity level |
| Footer | Commit of the checkout (changes with every commit) |

### 5.3 Components

- Source: `needs.json` of the checkout. The generator runs
  `bazel build //:needs_json_file` and reads `bazel-bin/needs.json` (cached;
  the first run takes minutes).
- Taken: every `comp` need in `modules/<module key>/`, plus the `includes` of
  the module's `mod` need (a `mod` need outside the module docs is matched by
  its title).
- No components found: tile shows "no components documented"; report it, do
  not add components by hand.
- Bazel build fails: the generator stops. Fix the build; do not use another
  `needs.json`.
- `--needs <file>` skips the build; only for reproducing a diagram from a kept
  `needs.json`.

### 5.4 Determinism

- Inputs: `known_good.json` at the release ref and at the origin tag, `images/`
  at the release ref, `needs.json` of the checkout, milestone date, state.
- Same inputs give a byte-identical SVG (no randomness, no timestamp). Check:
  generate twice to a scratch path and `cmp`.

### 5.5 Module maturity (DR-003)

Every software module gets exactly one level of
[DR-003-Strat](https://github.com/eclipse-score/score/blob/main/docs/design_decisions/strategy/DR-003-strat.md).
`assess_maturity()` derives it on every run from `needs.json` and the module
docs.

| Level | Rule |
|---|---|
| Preview | No verification report: neither a `mod_ver_report` need in `modules/<key>/` nor dependable elements (`MODULE_DOCS`). |
| Experimental | A verification report exists and shows gaps (untested or uninspected requirements, missing safety analyses or checklists). |
| Release | Report exists and every component requirement is fully verified (`fully_verifies_back`) and inspected (`valid_inspected`; QM: `valid`). |

- Never set a level by hand. Change the rule in `assess_maturity()` only after
  agreement, never the result.
- The local `needs.json` has no test results, so Release cannot be assigned
  locally. Before a final note, check the module verification reports of the
  CI docs build of the release branch (`github-pages-<sha>` artifact of "Code
  Quality & Documentation") and report modules that would meet Release and
  borderline Experimental modules (e.g. report without FMEA/DFA).
- The note links DR-003 below the figure (fixed text of the generator).

## 6. Always from scratch

Every run creates the whole note anew, also when it already exists (pin bumps,
new commits on the release branch, draft → final).

1. Write the skeleton directly to the note path; it replaces the existing note.
   The SVG is replaced as well.
2. Run `collect_changes.py` (7) and write both narrative chapters anew from the
   evidence (8). Do not copy items from the previous version of the note.
3. Lines added by hand anywhere in the note are lost: generated content goes
   into the generator (1.2), narrative content must follow from the evidence.
4. Before replacing, compare with the previous version (`git diff`) and name
   items that disappeared or changed in the report.

## 7. Evidence (`collect_changes.py`)

### 7.1 Command and options

```bash
python3 scripts/release_note/collect_changes.py --release vX.Y.0 --origin vX.W.0 --output changes.md
```

| Option | Effect |
|---|---|
| `--module <key>` | Restrict the module sections (repeatable) |
| `--include-infra` | Also cover the infrastructure modules |
| `--module-prs` | Also list all merged PRs of a module (slow, deep dive only) |

Prerequisites: release branch pushed (the collector compares commits through
the GitHub API), `GITHUB_TOKEN` set and never printed.

### 7.2 Output sections

| Section | Content |
|---|---|
| reference_integration | Merged PRs and closed issues, origin tag → checked-out release branch (not `main`) |
| Commits without PR | Direct commits on the release branch with changed files; commits that only touch `docs/s_core_v_1/releases/` are skipped |
| Removed or renamed files | Per directory, without `docs/` and `patches/` |
| Per changed module, per release in the range | 1. headed sections (breaking, deprecations, removals, public API, migrations, features); 2. *Candidate lines* (matching list items elsewhere in the text); 3. *Release scope*: every PR of "What's Changed", marked `review` or `skip? (<reason>)`; impact hints for breaking parts |

### 7.3 Release range

- `releases_between()` (generator) is shared by the tables and the collector;
  both always name the same releases.
- Candidates: published GitHub releases between the origin tag and the pinned
  tag.
- A release counts if the pinned commit contains its tag and the origin commit
  does not (GitHub compare). Releases on maintenance branches are skipped; a
  release is still found when the origin was tagged on a side commit.
- Tags without a GitHub release are not listed.
- Read **all** releases in the range: a breaking change of an intermediate
  release is still breaking for an integrator coming from the origin.

## 8. Narrative (AI-FILL)

*Changes to the Platform* has exactly two chapters, *New Features* and
*Breaking Changes*, with **platform-level** changes only. Module internals stay
in the module release notes, which the tables link.

### 8.1 What is platform-level

1. **Module set:** new, removed or renamed modules; major version jumps
   (`--changes` table).
2. **reference_integration:** images and platforms, Bazel/toolchain updates, build
   and integration mechanisms, demos, documentation or process deliverables.
3. **Cross-module changes:** the same change in several modules (identical PR
   titles in several repos, or a module's release note, point to them).
4. **Module breaking changes with impact on integrators or other modules**
   (e.g. a removed flag that `known_good.json` still sets).

### 8.2 Classify each release separately

Classify every module release in **its own pass**: one module, one release,
nothing else in view. Do not mix PRs or release texts of other modules or
releases into a pass; this keeps the context small and the decisions
independent. The evidence of reference_integration (PRs, commits without PR,
removed files) is one more pass. Same method as the Baselibs release-notes
skill (eclipse-score/baselibs `.agents/skills/release-notes-skill/SKILL.md`).

Steps of one pass:

| Step | Rule |
|---|---|
| 1. Scope | The "What's Changed" list is the scope. Without it ("scope cannot be determined"): use only the headed sections and candidate lines and say so in the report; do not reconstruct the scope from `git log` or a compare view. |
| 2. Read | Read every `review` PR: title, body, author (`GET /repos/<owner>/<repo>/pulls/<n>`). If that is not precise enough, read the diff (`Accept: application/vnd.github.diff` or `git show`). Commits without PR: read them with `git show`. |
| 3. Skip | CI/workflow-only, dependency bumps (`eclipse-score-bot`, `renovate`, `dependabot`), Bazel visibility-only, requirements/doc-only, repo-sync or agent-tooling PRs, pure pin bumps (covered by the tables). Confirm the collector's `skip?` marks; they are title-based. |
| 4. Notable | Breaking API or behaviour changes, deprecations, new public features or libraries, removed or renamed mechanisms of reference_integration. Bug fixes are not notable for this note. |
| 5. Record | For each notable item one line: module, release, link (PR, commit or release note), proposed class (breaking or feature), impact-hint verdict (8.3). Every single statement of the headed sections "Breaking", "Upgrade instructions", "Removed" and "Deprecated" is its own candidate line; do not combine them. |

Result of each pass: a candidate list. No platform filter and no wording yet.

### 8.3 Merge and decide

Put the candidate lists of all passes together, then decide per item:

1. **Merge** related candidates into one item:
   - the same change in several modules → one cross-module item (8.1);
   - a deprecation in one release and the removal in a later one, or a
     follow-up of an announcement in the previous platform release note →
     one item;
   - a change reverted in a later release of the range → drop both.
2. **Filter**: keep only platform-level items (8.1); add the module set
   changes from the `--changes` table.
3. **Classify** with the table below.
4. **Account for every candidate**: each candidate line ends either in the
   note or in the omitted list of the report, with the reason. Merging (1)
   keeps the content of all merged candidates; no candidate is dropped
   silently.

| Class | Criteria |
|---|---|
| Breaking — reference_integration | Removed or renamed script, target, configuration file or mechanism (see "Removed or renamed files"; read the PR that removed it), especially if an earlier note announced it. |
| Breaking — module | Removed or renamed module, target, flag or public API, or changed behaviour that requires action. List it only if reference_integration uses it (impact hint) **or** applications use it directly; say which applies. |
| New feature | New module, platform, image, integration capability or deliverable; or a module feature visible across the platform. |
| Omit | Everything else. When unsure: omit and name it in the report. |

- **Impact hints** are leads, not verdicts: valid only if the hit really uses
  what was removed or changed; a hit that merely shares a name is a false
  alarm.
- **PR labels** (`breaking`, `feature`) are not used consistently; decide from
  title, description and the module release note.

### 8.4 Writing rules

- State only facts from the evidence; no invented features, dates or versions.
  Read the PR description, not only the title.
- One `~~~` subsection per item: short noun-phrase title, written for
  integrators, with RST links (`` `text <url>`__ ``) to the PR, issue, commit
  or module release note. Name new scripts, targets and settings.
- Order: module set → integration and build → images and platforms → tests →
  documentation. Breaking changes: reference_integration first, then one subsection
  per module in table order.
- Every breaking change ends with "Action required: ...".
- Name the repository: write ``reference_integration``, never "this
  repository" (the note is read outside the repository, too).
- How reference_integration itself handles a change (patch, workaround, flag
  it still sets, excluded tests) goes into a ``.. note::`` block in the item,
  starting with "Important for integrators:". Use it only when this is
  relevant for integrators; the change itself stays in the item text.
- Remove *Breaking Changes* only if there is none. No `AI-FILL` marker may
  remain.
- Same inputs → same items: the wording may differ, the items may not.

### 8.5 Known limits of the evidence

| Limit | Consequence |
|---|---|
| Many modules have no "Breaking"/"New features" sections, only "What's Changed" | The PR list is the only module evidence. "No breaking/new-feature items and no PR list" means no evidence: say so in the report, do not guess. |
| Long release scopes | Reading every `review` PR is still required; report how many PRs per module you read. |
| Origin tagged on a side commit | "What's Changed" may contain PRs already in the origin; drop PRs the origin release note already lists. |
| Hash pins | Release notes cover only up to the latest tag on the commit; later changes are not covered. |
| Impact hints | Search `known_good.json`, `.bazelrc`, `bazel_common`, `patches`, `images`, `showcases` and the integration tests; they do not understand code. |

## 9. Validation and report

Checks:

- [ ] `grep -n "AI-FILL" <note>` is empty.
- [ ] Overview has the `.. figure::` with `:width:` `DIAGRAM_WIDTH`; the SVG
      was written by this run and is committed with the note.
- [ ] Every software module has a maturity badge; the generator printed
      `maturity (DR-003): ...`; the Overview links DR-003.
- [ ] The note is the last entry of the release-note `toctree` in
      `releases.rst` (explicit list; a glob would sort `v0_10` before `v0_5`).
- [ ] The Download column links every image of `IMAGE_DOWNLOADS`.
- [ ] Every `~~~` item and bullet has a PR, issue, commit or release-note link.
- [ ] Every new module of the `--changes` table and every removed mechanism of
      reference_integration is in the note or in the report.
- [ ] Every breaking candidate of 8.2 is in the note or in the omitted list
      of the report (8.3, step 4).
- [ ] No generator warnings on stderr.
- [ ] Scope links point to the release tag.
- [ ] Optional (heavy, CI runs it): `bazel run --lockfile_mode=error //:docs_shim -- --github_user=eclipse-score --github_repo=reference_integration`.

Report:

- Omitted candidates, each with module, release, link and reason (8.3, step 4).
- Items that disappeared or changed compared to the previous version of the
  note (6).
- Modules without releases in the range, and modules without module-level
  evidence.
- `(unreleased)` rows (hash pins) with a proposed `version` pin.
- PRs read per module.
