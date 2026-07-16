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

## Quick try

Run a quick smoke of the FIT harness (lists scenarios or runs a small subset):

```bash
# List available Rust scenarios
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios

# Run all FIT tests (streaming output)
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit --test_output=streamed
```

The Rust side of this lifecycle-only suite uses a dedicated Bazel target,
`//feature_integration_tests/test_scenarios/rust:rust_lifecycle_test_scenarios`,
which still reuses `test_scenarios/rust/src/main.rs`. It is built with the
`lifecycle_only` cfg so only lifecycle scenarios are compiled for that suite,
while the normal `fit` and `fit_rust` targets continue to use the full scenario tree.

To run the lifecycle tests directly with `pytest` and build the scenario binaries on demand:

```sh
python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  -m rust \
  --rust-target-name=//feature_integration_tests/test_scenarios/rust:rust_lifecycle_test_scenarios \
  -q -v

python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  -m cpp \
  -q -v
```

The Rust override is required because plain `--build-scenarios` defaults to
`//feature_integration_tests/test_scenarios/rust:rust_test_scenarios`, while the
lifecycle tests need the reduced lifecycle-only Rust target.

#### Sandbox uid/gid and scheduling-policy tests

Some lifecycle daemon tests (e.g. `test_launched_process_uid_gid_matches_config_when_applied`,
`test_launched_process_scheduling_matches_config_when_applied`) verify that `launch_manager`
applies the sandbox `uid`/`gid` and scheduling policy from
`feature_integration_tests/configs/lifecycle_daemon_config.json`. This requires granting
`launch_manager` the `cap_setuid,cap_setgid,cap_sys_nice` file capabilities via `setcap`, which
in turn requires `CAP_SETFCAP` — not available to a non-root test runner by default.

Set `FIT_ENABLE_SETCAP=1` to opt in to a `sudo -n setcap` attempt (backed by a passwordless
sudoers rule scoped to the `setcap` binary, e.g. `<user> ALL=(root) NOPASSWD: /usr/sbin/setcap`,
with no trailing arguments pinned — the target path is a fresh `tmp_path` on every run). Without
it, these tests skip with a message identifying the missing capability grant.

```sh
export FIT_ENABLE_SETCAP=1

python3 -m pytest feature_integration_tests/test_cases/tests/lifecycle/ \
  --build-scenarios \
  -m cpp \
  -k "uid_gid or scheduling" \
  -q -v
```

Under `bazel test`, undeclared env vars like `FIT_ENABLE_SETCAP` do not reach the test process
unless passed via `--test_env` (not `--action_env`, which only affects build actions):

```sh
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp \
  --test_env=FIT_ENABLE_SETCAP=1
```

`bazel run` inherits the invoking shell's environment directly, so exporting the variable
beforehand is sufficient there.

### ITF Tests (QEMU-based)

ITF tests run on a QEMU target and require the `itf-qnx-x86_64` config:

```sh
bazel test --config=itf-qnx-x86_64 //feature_integration_tests/itf
```

### Test Scenarios

Test scenarios can be listed and run directly for debugging:

```sh
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
bazel run //feature_integration_tests/test_scenarios/rust:rust_lifecycle_test_scenarios -- --list-scenarios
bazel run --config=linux-x86_64 //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- --list-scenarios
```

## Updating Python Requirements

To update Python dependencies:

```sh
bazel run //feature_integration_tests/test_cases:requirements.update
```
