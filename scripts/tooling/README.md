# Tooling scripts

## Running tooling CLI

```bash
bazel run //scripts/tooling -- --help
```

## Updating dependencies

Update a list of requirements in [requirements.in](requirements.in) file and then
regenerate lockfile  [requirements.txt](requirements.txt) with:

```bash
bazel run //scripts/tooling:requirements.update
```
