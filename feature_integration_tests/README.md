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

Some lifecycle daemon tests (`test_launched_process_uid_gid_matches_config_when_applied`,
`test_launched_process_scheduling_matches_config_when_applied`) verify that `launch_manager`
applies the sandbox `uid`/`gid` and scheduling policy from
`feature_integration_tests/configs/lifecycle_daemon_config.json`. This requires granting
`launch_manager` the `cap_setuid,cap_setgid,cap_sys_nice` file capabilities via `setcap`, which
in turn requires `CAP_SETFCAP` — not available to a non-root test runner by default, so these
tests opt in via the `FIT_ENABLE_SETCAP` env var (backed by a passwordless sudoers rule scoped
to the `setcap` binary, e.g. `<user> ALL=(root) NOPASSWD: /usr/sbin/setcap`, with no trailing
arguments pinned — the target path is a fresh `tmp_path` on every run) and skip otherwise.

Under `bazel test`, undeclared env vars like `FIT_ENABLE_SETCAP` only reach the test process when
passed via `--test_env` (not `--action_env`, which only affects build actions). Two variants of
the full suite are relevant:

```sh
# Default: matches CI/CD exactly (sandboxed, no FIT_ENABLE_SETCAP) — the two capability tests skip.
bazel test --config=linux-x86_64 --nocache_test_results //feature_integration_tests/test_cases:fit \
  --test_output=all --test_arg=-rs --test_verbose_timeout_warnings

# Local verification: also exercises the uid/gid and scheduling-policy grants instead of skipping.
bazel test --config=linux-x86_64 --nocache_test_results //feature_integration_tests/test_cases:fit \
  --spawn_strategy=local --test_env=FIT_ENABLE_SETCAP=1 \
  --test_output=all --test_arg=-rs --test_verbose_timeout_warnings
```

Flag rationale (shared by both commands unless noted):

- `--nocache_test_results`: forces re-execution instead of replaying a cached PASS/SKIP, so a
  fresh `setcap` attempt is made every time.
- `--test_output=all`: prints full stdout/stderr for every test, not just failures, so the
  `sandbox_privileged_reason` and pytest skip-reason diagnostics are visible.
- `--test_arg=-rs`: forwards pytest's `-rs` flag, which prints the reason for every `SKIPPED`
  test instead of just `SKIPPED` with no context.
- `--test_verbose_timeout_warnings`: warns when a test's actual runtime is far from its declared
  `timeout`/`size`, useful for right-sizing `fit_lifecycle_daemon`'s `timeout = "long"`.
- `--spawn_strategy=local` (local-verification command only): runs the test action directly on
  the host instead of inside Bazel's `linux-sandbox`. The sandbox sets `PR_SET_NO_NEW_PRIVS`,
  which makes `setuid` (`sudo`) and file capabilities (`setcap`) inert at exec time even with a
  correctly configured host — the grant is applied but silently dropped when the supervised
  binary later executes. Only unsandboxed execution lets the grant persist.
- `--test_env=FIT_ENABLE_SETCAP=1` (local-verification command only): opts the test process into
  the `sudo -n setcap` attempt; without it these tests always take the plain, non-sudo `setcap`
  path and skip on a non-root runner. `bazel run` inherits the shell environment directly, so
  `export FIT_ENABLE_SETCAP=1` beforehand is sufficient there instead of `--test_env`.

#### Tests skipped in CI/CD

The GitHub Actions runners (`ubuntu-latest`, see `.github/workflows/build_and_test_linux.yml`) run
`bazel test` sandboxed (default `linux-sandbox` strategy) and do not set `FIT_ENABLE_SETCAP` or
provision a passwordless `sudo setcap` rule. As a result, the following subtests in
`fit_lifecycle_daemon` always skip in CI, for both the `rust` and `cpp` supervised-app variants:

- `test_process_launching_with_daemon.py::TestProcessLaunchingWithDaemon::test_launched_process_uid_gid_matches_config_when_applied[rust|cpp]`
- `test_process_launching_with_daemon.py::TestProcessLaunchingWithDaemon::test_launched_process_scheduling_matches_config_when_applied[rust|cpp]`

Reason: both depend on `launch_manager` successfully gaining `cap_setuid,cap_setgid,cap_sys_nice`
via `setcap` (see `daemon_helpers._grant_sandbox_capabilities`), which fails in CI for two
independent reasons, either sufficient on its own:

1. **Sandboxed execution**: `linux-sandbox` sets `PR_SET_NO_NEW_PRIVS`, making any `setuid`/file-capability
   escalation inert at exec time, so even a successful `setcap` call has no effect on the process
   that actually runs.
2. **No opt-in / no sudoers rule**: `FIT_ENABLE_SETCAP` is not set in the CI workflow, so the tests
   never attempt the `sudo -n setcap` path; and the CI runner has no passwordless sudoers entry for
   `setcap` regardless.

This is by design: `_grant_sandbox_capabilities` degrades gracefully (never raises) and the two
capability-dependent subtests self-skip with a diagnostic reason instead of failing the build. All
other subtests in `fit_lifecycle_daemon` only check same-uid process behavior and require no
privilege escalation, so they run and pass normally in CI.

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
