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

## Lifecycle FIT Summary

Lifecycle Feature Integration Tests validate end-to-end integration patterns for the S-CORE lifecycle stack across Rust and C++ scenarios.

- Coverage: 85/92 lifecycle requirements (92%)
- Modes:
  - API integration mode (no running daemon required)
  - Daemon integration mode (real Launch Manager behavior)
- Main validated areas:
  - Process launching and dependency ordering (sequential/parallel)
  - Conditional launching and run targets
  - Process security/resources/termination
  - Monitoring, recovery, control interface, logging, and configuration handling

For full lifecycle requirement mapping and detailed rationale, see `feature_integration_tests/LIFECYCLE_TESTS_SUMMARY.md`.

## Running Tests

### Python Test Cases (scenario-based FIT)

Python tests are managed with Bazel and Pytest. To run all integration tests:

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon
```

To run lifecycle integration tests by language:

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon_lifecycle_arc_rust
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon_lifecycle_arc_cpp
```

Pytest direct local runs are also supported:

```sh
# All lifecycle tests (rust + cpp)
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ -q -v

# Rust only
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ -q -v -m rust

# C++ only
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ -q -v -m cpp
```

To build scenario executables from pytest before running tests:

```sh
# Default Bazel config: linux-x86_64
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  --build-scenarios-timeout=600 \
  -q -v

# Explicit Bazel config
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  --bazel-config=linux-x86_64 \
  --build-scenarios-timeout=600 \
  -q -v

# Or via environment override
FIT_BAZEL_CONFIG=linux-x86_64 \
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  --build-scenarios-timeout=600 \
  -q -v
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
