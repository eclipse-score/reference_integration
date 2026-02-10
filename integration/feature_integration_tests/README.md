# Feature Integration Tests

This directory contains Feature Integration Tests for the S-CORE project. It includes both Python test cases and Rust test scenarios to validate features work together.

## Structure

- `test_cases/` — Python-based integration test cases
  - `conftest.py` — Pytest configuration and fixtures
  - `fit_scenario.py` — Base scenario class
  - `requirements.txt` — Python dependencies
  - `BUILD` — Bazel build and test definitions
  - `tests/` — Test cases (e.g., orchestration with persistency)
- `test_scenarios/` — Location of test scenarios
  - `rust/` — Rust-based integration test scenarios
    - `src/` — Rust source code for test scenarios
    - `BUILD` — Bazel build definitions

## Running Tests

### Python Test Cases

Python tests are managed with Bazel and Pytest. To run the main test target:

```sh
bazel test //feature_integration_tests/test_cases:fit
```

### Rust Test Scenarios

Rust test scenarios are defined in `test_scenarios/rust/src/scenarios`. Build and run them using Bazel:

```sh
bazel build //feature_integration_tests/test_scenarios/rust:rust_test_scenarios
```

```sh
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
```

## Updating Python Requirements

To update Python dependencies:

```sh
bazel run //feature_integration_tests/test_cases:requirements.update
```
