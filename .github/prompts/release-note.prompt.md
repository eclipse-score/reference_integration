---
description: "Create the S-CORE platform release note from scratch as draft or final."
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
Always generate the whole note from scratch, also if the note file already
exists (skill, 6).
