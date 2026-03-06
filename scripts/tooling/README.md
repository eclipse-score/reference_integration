# Tooling scripts

## Running tooling CLI

```bash
bazel run //scripts/tooling -- --help
```

```bash
bazel run //scripts/tooling -- misc --help
```

## Creating HTML report

```bash
bazel run //scripts/tooling -- misc html_report
```

## Running tests

```bash
bazel test //scripts/tooling_tests
```

## Updating dependencies

Update a list of requirements in [requirements.in](requirements.in) file and then
regenerate lockfile  [requirements.txt](requirements.txt) with:

```bash
bazel run //scripts/tooling:requirements.update
```
