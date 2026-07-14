# Lifecycle Cross-Module Integration Tests

This document describes the **cross-module lifecycle integration tests** in the `saumya_feature_integration_lifecycle` branch. These tests validate interactions between Lifecycle and other S-CORE modules with full daemon supervision.

> **Note**: API-level lifecycle integration tests (17 test files covering all 92 lifecycle requirements) are maintained in the [`saumya_lifecycle_fit` branch](https://github.com/qorix-group/reference_integration/tree/saumya_lifecycle_fit/feature_integration_tests/test_cases/tests/lifecycle). This branch focuses exclusively on cross-module integration scenarios that require daemon-level coordination.

## Overview

Cross-module integration tests verify that lifecycle management integrates correctly with other S-CORE modules in end-to-end scenarios:

- **Lifecycle ↔ Persistency** — Data persistence across recovery actions
- **Lifecycle ↔ State Manager** — Control interface and run-target management
- **Lifecycle ↔ Communication** (planned) — Dependency-gated activation
- **Lifecycle ↔ Logging** (planned) — Failure correlation with logs
- **Lifecycle ↔ Time** (planned) — Timestamp synchronization
- **Lifecycle ↔ Security/Crypto** (planned) — Security policy enforcement

## Branch Structure

This branch (`saumya_feature_integration_lifecycle`) contains:

```
feature_integration_tests/test_cases/tests/lifecycle/
├── test_lifecycle_persistency_recovery.py  (Cross-module: Lifecycle ↔ Persistency)
└── test_lifecycle_state_manager_if.py      (Cross-module: Lifecycle ↔ State Manager)
```

**Related branches:**

- [`saumya_lifecycle_fit`](https://github.com/qorix-group/reference_integration/tree/saumya_lifecycle_fit) — API-level integration tests (17 files, 92 requirements)
- [`eclipse-score/lifecycle`](https://github.com/eclipse-score/lifecycle/tree/main/tests) — Upstream lifecycle repository tests

## Comparison with Other Branches

### Test Distribution Across Branches

| Branch | Focus | Test Files | Requirements Coverage |
|--------|-------|------------|----------------------|
| **saumya_lifecycle_fit** | API-level lifecycle integration | 17 files | 92 lifecycle requirements (100% API coverage) |
| **saumya_feature_integration_lifecycle** (this branch) | Cross-module daemon integration | 2 files | Cross-module architectural boundaries |
| **eclipse-score/lifecycle** | Upstream lifecycle tests | 8 integration scenarios | Lifecycle implementation validation |

### Unique Tests in This Branch

The following tests are **unique to this branch** and not present in `saumya_lifecycle_fit`:

1. `test_lifecycle_persistency_recovery.py` — Persistency continuity across lifecycle recovery
2. `test_lifecycle_state_manager_if.py` — State Manager control interface coordination

### Tests Available in saumya_lifecycle_fit Branch

The following API integration tests are maintained in the `saumya_lifecycle_fit` branch and **removed from this branch** to avoid duplication:

<details>
<summary>17 API Integration Test Files (click to expand)</summary>

1. `test_process_launching.py` — Basic lifecycle API integration
2. `test_dependency_ordering.py` — Sequential health monitoring
3. `test_parallel_launching.py` — Concurrent monitoring
4. `test_control_interface_support.py` — Custom condition signaling
5. `test_process_arguments.py` — Arguments and working directory
6. `test_process_security.py` — Security and privilege config
7. `test_process_resources.py` — Resource management
8. `test_conditional_launching.py` — Conditional process launching
9. `test_process_management.py` — Process adoption and management
10. `test_run_targets.py` — Run target definition and switching
11. `test_process_termination.py` — Graceful shutdown and signals
12. `test_monitoring_and_recovery.py` — Watchdog, liveliness, recovery
13. `test_control_commands.py` — Control and query commands
14. `test_logging.py` — Logging and timestamps
15. `test_configuration_management.py` — Config management and OCI compliance
16. `test_debug_and_terminal.py` — Debug mode and terminal support
17. `test_io_and_file_descriptors.py` — I/O redirection and FD control

</details>

## Current Test Implementation

### Cross-Module Integration Tests (Implemented)

| Test File | Module Integration | Requirements Covered | Status | Description |
|-----------|-------------------|---------------------|--------|-------------|
| `test_lifecycle_persistency_recovery.py` | Lifecycle ↔ Persistency | `feat_req__lifecycle__process_failure_react`, `feat_req__lifecycle__monitor_abnormal_term`, `feat_req__persistency__store_data`, `feat_req__lifecycle__recov_run_target_switch` | ✅ Implemented | Validates that persistency storage remains stable around a real supervised-app crash and switch-to-fallback recovery |
| `test_lifecycle_state_manager_if.py` | Launch Manager ↔ State Manager | `logic_arc_int__lifecycle__controlif`, `feat_req__lifecycle__request_run_target_start` | ✅ Implemented (activate_target); status-query intentionally skipped | Sends a real `activate_target` request via the `lmcontrol` control-interface client; the status-query leg has no implemented query/response protocol in this codebase and is skipped with an explicit reason rather than asserted on log substrings |

### Test Capabilities

**test_lifecycle_persistency_recovery.py:**

- **`test_persistency_continuity_across_sequential_writes`**: Baseline — verifies persistency snapshot stability across two sequential writer processes (no supervision, no crash/recovery)
- **`test_persistency_recovery_with_daemon_supervision`**: Force-kills the daemon-supervised app, verifies the LCM logs 'unexpected termination' and a completed transition into `fallback_run_target` (the schema's recovery action — not a "restart"), and that persistency storage colocated in the same daemon workspace remains intact and writable throughout
- **`test_supervised_app_crash_persistency_recovery`**: Verifies persistency continuity across abnormal process termination — freezes a live probe process holding KVS storage open and SIGKILLs it, then validates data integrity remains intact
- Tests recovery action integration with persistency snapshots
- Validates data integrity after abnormal process termination and switch-to-fallback recovery (crash/recovery simulation)

Note: the recovery action exercised here is `switch_run_target` to the reserved `fallback_run_target` — there is no "restart the same process in place" primitive in this configuration schema. The supervised example app binaries (`rust_supervised_app`/`cpp_supervised_app`, from the external `score_lifecycle_health` repository) do not themselves open persistency storage, so the persistency probe remains an independent process colocated with the supervised app rather than the same process; see the test module docstring for the precise claim being verified.

**test_lifecycle_state_manager_if.py:**

- Tests control interface IPC boundary
- Validates `activate_target` routing via the real `lmcontrol` CLI client
- Status-query coverage is intentionally skipped: no query/response protocol exists yet in this codebase's control interface

## Running the Tests

### Prerequisites

These tests require a full daemon environment with:

- Launch Manager daemon binary
- Supervised application binaries
- State Manager component with control interface
- Flatbuffer configuration pipeline

### Using Bazel

**Run all cross-module tests (Rust):**

```bash
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon_lifecycle_arc_rust
```

**Run all cross-module tests (C++):**

```bash
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon_lifecycle_arc_cpp
```

**Run both language implementations:**

```bash
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_daemon
```

**With detailed output:**

```bash
bazel test --config=linux-x86_64 \
  //feature_integration_tests/test_cases:fit_daemon_lifecycle_arc_rust \
  --test_output=all
```

### Using Pytest (Local Development)

**Run with setcap mode (required for daemon tests):**

```bash
FIT_ENABLE_SETCAP=1 python3 -m pytest \
  feature_integration_tests/test_cases/tests/lifecycle/ \
  -q -v
```

**Run specific test:**

```bash
FIT_ENABLE_SETCAP=1 python3 -m pytest \
  feature_integration_tests/test_cases/tests/lifecycle/test_lifecycle_persistency_recovery.py \
  -q -v
```

**Run Rust tests only:**

```bash
FIT_ENABLE_SETCAP=1 python3 -m pytest \
  feature_integration_tests/test_cases/tests/lifecycle/ \
  -q -v -m rust
```

**Run C++ tests only:**

```bash
FIT_ENABLE_SETCAP=1 python3 -m pytest \
  feature_integration_tests/test_cases/tests/lifecycle/ \
  -q -v -m cpp
```

## Planned Integration Tests

The following cross-module integration tests are planned for future implementation:

### High Priority

| Test File (Planned) | Module Integration | Requirements to Cover | Description |
|---------------------|-------------------|----------------------|-------------|
| `test_lifecycle_application_if.py` | Launch Manager ↔ SCORE Application | `logic_arc_int__lifecycle__lifecycle_if`, `feat_req__lifecycle__process_state_comm` | State reporting and conditional signaling with daemon |
| `test_lifecycle_ipc_alive_if.py` | Health Monitor ↔ Launch Manager | `logic_arc_int__lifecycle__alive_if`, `feat_req__lifecycle__liveliness_detection` | Heartbeat IPC and failure propagation |
| `test_lifecycle_security_isolation.py` | Lifecycle ↔ Security/Crypto | `feat_req__lifecycle__secpol_non_root`, `feat_req__lifecycle__support_secpol_type`, `feat_req__security__sandbox_isolation` | Validate security policy enforcement and privilege isolation |

### Medium Priority

| Test File (Planned) | Module Integration | Requirements to Cover | Description |
|---------------------|-------------------|----------------------|-------------|
| `test_lifecycle_comm_dependency_activation.py` | Lifecycle ↔ Communication | `feat_req__lifecycle__dependency_check`, `feat_req__lifecycle__check_dependency_exec` | Dependency-gated activation for comm components |
| `test_lifecycle_logging_correlation.py` | Lifecycle ↔ Logging | `feat_req__lifecycle__process_logging_support`, `feat_req__lifecycle__log_timestamp` | Failure diagnostics correlated with timestamped daemon logs |
| `test_lifecycle_ipc_controlif.py` | Lifecycle ↔ Communication | `logic_arc_int__lifecycle__controlif` | Control/query IPC routing validation |
| `test_lifecycle_ipc_deadline_monitor_if.py` | Health Monitor ↔ Launch Manager | `logic_arc_int__lifecycle__deadline_monitor_if`, `logical_monitor_if` | Deadline monitor checkpoint IPC |
| `test_lifecycle_time_sync.py` | Lifecycle ↔ Time | `feat_req__lifecycle__log_timestamp`, `feat_req__time__monotonic_clock` | Validate timestamp consistency between lifecycle events and system time |

### Low Priority

| Test File (Planned) | Module Integration | Requirements to Cover | Description |
|---------------------|-------------------|----------------------|-------------|
| `test_lifecycle_orchestrator_sync.py` | Lifecycle ↔ Orchestrator | `feat_req__lifecycle__run_target_support`, `feat_req__lifecycle__switch_run_targets` | Ensure run-target transitions remain synchronized with orchestrator-visible process states |
| `test_lifecycle_multi_instance_isolation.py` | Lifecycle (Multi-instance) | `feat_req__lifecycle__multi_instance_support` | Validate supervision and monitoring isolation across multiple Launch Manager instances |
| `test_lifecycle_config_validation_gate.py` | Lifecycle (Config) | `feat_req__lifecycle__offline_config_valid`, `feat_req__lifecycle__consistent_dependencies` | Verify invalid lifecycle configurations are rejected offline and valid configs remain executable |
| `test_lifecycle_baselibs_integration.py` | Lifecycle ↔ Baselibs | Various baselibs requirements | Test lifecycle integration with common baselibs utilities |

## Implementation Prerequisites

All planned daemon integration tests require:

1. **Full Daemon Configuration Support**
   - state_manager component with control interface
   - Flatbuffer configuration pipeline with all components enabled
   - Support for both setcap and non-setcap execution modes

2. **Supervised Application Binaries**
   - Example applications demonstrating lifecycle APIs
   - Applications with configurable health reporting
   - Applications with deadline monitoring support

3. **Communication Infrastructure**
   - Control interface IPC channels
   - State reporting IPC channels
   - Health monitoring IPC channels

4. **Test Infrastructure**
   - Enhanced daemon fixture supporting full configuration
   - Helper utilities for IPC validation
   - Log parsing utilities for structured daemon logs

## Test Architecture

### Daemon Fixture

Cross-module tests use the `launch_manager_daemon` fixture (from `daemon_helpers.py`) which provides:

- Automated daemon configuration generation
- Binary capability management (setcap for uid/gid switching)
- Config directory isolation
- Daemon process lifecycle management
- Automatic cleanup

### Configuration Pipeline

Tests use the flatbuffer configuration pipeline:

1. JSON config input → `lifecycle_config` tool
2. Intermediate JSON → `flatc` compiler
3. FlatBuffer .bin files (hmcore.bin, hm_demo.bin, lm_demo.bin)

### Environment Variables

- **FIT_ENABLE_SETCAP=1** — Enables setcap mode for daemon tests (required)
- **FIT_BAZEL_CONFIG** — Override Bazel config (default: linux-x86_64)

## References

- **API Integration Tests**: See [`saumya_lifecycle_fit` branch](https://github.com/qorix-group/reference_integration/tree/saumya_lifecycle_fit/feature_integration_tests/test_cases/tests/lifecycle)
- **Upstream Tests**: See [`eclipse-score/lifecycle`](https://github.com/eclipse-score/lifecycle/tree/main/tests)
- **Requirements**: [S-CORE Lifecycle Requirements](https://eclipse-score.github.io/reference_integration/main/_collections/score_platform/docs/features/lifecycle/requirements/index.html)

---
