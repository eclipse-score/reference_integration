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
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_rust
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp
```

### Lifecycle ↔ persistency tests

`tests/lifecycle/test_lifecycle_persistency_integration.py` starts a real Launch Manager with
`configs/lifecycle_persistency_config.json`. Launch Manager launches the FIT scenario binary
(`persistency.restart_counter`) as KVS-owning components. The test drives run targets through
`lmcontrol` → `control_daemon`, crashes a supervised app to trigger recovery, and checks the KVS
files and Launch Manager's log. It runs once per language:

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_rust_lifecycle_persistency
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp_lifecycle_persistency
```

Both targets are `exclusive`: Launch Manager and `control_daemon` use host-wide names in `/dev/shm`.

`test_components_run_with_configured_sandbox_identity` skips unless Launch Manager can be granted
`cap_setuid`/`cap_setgid` and a `cap_kill` copy of `kill` can be staged. CI doesn't do this, so the
test carries no requirement claim. To run it locally, you need a passwordless sudoers rule for
`setcap` and a run outside the Bazel sandbox:

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit \
  --spawn_strategy=local --test_env=FIT_ENABLE_SETCAP=1 --test_arg=-rs
```

Requirement coverage is listed in [docs/lifecycle_persistency_traceability.md](docs/lifecycle_persistency_traceability.md).

## Quick try

Run a quick smoke of the FIT harness (lists scenarios or runs a small subset):

```bash
# List available Rust scenarios
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios

# Run all FIT tests (streaming output)
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit --test_output=streamed
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
