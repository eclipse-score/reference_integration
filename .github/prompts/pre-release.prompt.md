---
description: "Create the pre-release check branch and draft PR with the latest release of every known_good.json module."
name: "pre-release"
argument-hint: "base=main"
agent: "Pre-Release Check"
---
Create the pre-release check for `reference_integration` based on
`${input:base:Base branch, default main}`.

Pin every module of `known_good.json` (target_sw and tooling) to its latest
Bazel registry release (no local build or fixes; the PR's CI verifies),
and open a draft PR whose body contains the module table (version before and
now, commits since the release, OK/NOK column left empty).

Follow the workflow of the agent and the [pre-release skill](../skills/pre-release/SKILL.md).
