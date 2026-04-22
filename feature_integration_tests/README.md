# Feature Integration Tests

This directory contains Feature Integration Tests for the S-CORE project. It includes Python test cases that orchestrate test scenarios implemented in Rust and C++ to validate that features work together correctly.

## Structure

- `test_cases/` — Python-based integration test cases
  - `conftest.py` — Pytest configuration and fixtures
  - `fit_scenario.py` — Base scenario class
  - `requirements.txt` — Python dependencies
  - `BUILD` — Bazel build and test definitions
  - `tests/` — Test cases organized by feature area
- `test_scenarios/` — Test scenario implementations
  - `rust/` — Rust-based test scenarios
  - `cpp/` — C++-based test scenarios
- `itf/` — Integration Test Framework tests (run on QEMU targets)
  - `test_showcases.py` — Showcase validation tests
  - `test_remote_logging.py` — Remote logging tests
  - `test_ssh.py` — SSH connectivity tests
- `configs/` — Configuration files for ITF execution (DLT, QEMU bridge, etc.)

## Running Tests

### Python Test Cases (scenario-based FIT)

Python tests are managed with Bazel and Pytest. To run all integration tests:

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit
```

To run specific test suites:

```sh
bazel test //feature_integration_tests/test_cases:fit_rust
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp
```

### ITF Tests (QEMU-based)

ITF tests run on a QEMU target and require the `itf-qnx-x86_64` config:

```sh
bazel test --config=itf-qnx-x86_64 //feature_integration_tests/itf
```

### Test Scenarios

Test scenarios can be listed and run directly for debugging:

```sh
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
bazel run --config=linux-x86_64 //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- --list-scenarios
```

## Updating Python Requirements

To update Python dependencies:

```sh
bazel run //feature_integration_tests/test_cases:requirements.update
```
