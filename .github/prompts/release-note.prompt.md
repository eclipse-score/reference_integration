---
description: "Create or refresh the S-CORE platform release note as draft or final."
name: "release-note"
argument-hint: "release=v0.10.0 origin=v0.9.0 state=draft|final"
agent: "Release Note"
---
Create the platform release note for release `${input:release:Release tag, e.g. v0.10.0}`
compared to the previous release `${input:origin:Origin tag, e.g. v0.9.0}`.

State: `${input:state:draft or final}`

- `draft`: run the generator without `--final`.
- `final`: run the generator with `--final`.
- Any other value: stop and ask for `draft` or `final`.

Follow the workflow of the agent and the [release-note skill](../skills/release-note/SKILL.md).
If the note file already exists, refresh it as described in the skill: regenerate
everything outside "Changes to the Platform" and keep the reviewed narrative,
unless I ask for a full rewrite.
