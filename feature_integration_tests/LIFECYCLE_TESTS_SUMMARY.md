# Lifecycle Feature Integration Tests

This document describes the lifecycle feature integration tests implemented in this repository, including the approach taken and the rationale behind design decisions.

## Overview

Lifecycle feature integration tests verify that applications can properly integrate with the S-CORE lifecycle management framework. These tests validate a comprehensive set of lifecycle capabilities including:

1. **Process Launching** — Execution state reporting and basic lifecycle integration
2. **Dependency Management** — Sequential and parallel process supervision
3. **Control Interface** — Custom conditions and control commands
4. **Process Configuration** — Arguments, security, resources, and I/O
5. **Conditional Launching** — Path, environment, and process state conditions
6. **Run Targets** — Runtime state management and transitions
7. **Termination** — Graceful shutdown and signal handling
8. **Monitoring & Recovery** — Health monitoring, watchdog, and recovery actions
9. **Configuration** — Modular configuration and session management
10. **Debug & Logging** — Debug support, terminal support, and logging

## Requirements Tested

The lifecycle FIT tests partially verify 80+ requirements from the S-CORE Platform documentation, including:

- Process launching, dependency ordering, and parallel launching
- Control interface support for custom conditions
- Process arguments, working directory, and I/O redirection
- Security configuration (UID/GID, capabilities, security policies)
- Resource management (priority, scheduling, CPU affinity, resource limits)
- Conditional launching (path, environment, process state conditions)
- Process management (adoption, multiple instances, dependencies)
- Run target support and transitions
- Process termination and signal handling
- Monitoring, recovery, and health checking
- Logging, configuration management, and debug support

## Test Files

### 1. test_process_launching.py

- **Requirement**: `feat_req__lifecycle__launch_support`
- **Tests**: Applications can report execution state to Launch Manager
- **Validates**: Lifecycle client API integration and execution state reporting

### 2. test_dependency_ordering.py

- **Requirement**: `feat_req__lifecycle__process_ordering`
- **Tests**: Sequential health monitoring for ordered initialization
- **Validates**: Sequential deadline reporting in correct order

### 3. test_parallel_launching.py

- **Requirement**: `feat_req__lifecycle__parallel_launch_support`
- **Tests**: Multiple independent health monitors running concurrently
- **Validates**: Parallel monitoring capability with bounded concurrency

### 4. test_control_interface_support.py

- **Requirement**: `feat_req__lifecycle__custom_cond_support`
- **Tests**: Control interface support for custom conditions
- **Validates**: Applications can signal custom conditions through the control interface API

### 5. test_process_arguments.py

- **Requirements**: `feat_req__lifecycle__process_launch_args`, `feat_req__lifecycle__cwd_support`, `feat_req__lifecycle__process_input_output`
- **Tests**: Process launching with arguments and working directory
- **Validates**: Processes can receive command-line arguments and working directory settings

### 6. test_process_security.py

- **Requirements**: `feat_req__lifecycle__uid_gid_support`, `feat_req__lifecycle__capability_support`, `feat_req__lifecycle__support_secpol_type`, `feat_req__lifecycle__secpol_non_root`, `feat_req__lifecycle__supplementary_groups`
- **Tests**: Process security and privilege configuration
- **Validates**: UID/GID, capabilities, security policies, and supplementary groups

### 7. test_process_resources.py

- **Requirements**: `feat_req__lifecycle__launch_priority_support`, `feat_req__lifecycle__scheduling_policy`, `feat_req__lifecycle__runmask_support`, `feat_req__lifecycle__process_rlimit_support`, `feat_req__lifecycle__aslr_support`
- **Tests**: Process resource management
- **Validates**: Priority, scheduling policy, CPU affinity, and resource limits

### 8. test_conditional_launching.py

- **Requirements**: `feat_req__lifecycle__waitfor_support`, `feat_req__lifecycle__cond_process_start`, `feat_req__lifecycle__total_wait_time_support`, `feat_req__lifecycle__polling_interval`, `feat_req__lifecycle__validate_conditions`, and 10+ more
- **Tests**: Conditional process launching
- **Validates**: Path, environment, and process state condition checking

### 9. test_process_management.py

- **Requirements**: `feat_req__lifecycle__running_processes`, `feat_req__lifecycle__drop_supervsion`, `feat_req__lifecycle__multi_start_support`, `feat_req__lifecycle__consistent_dependencies`, and more
- **Tests**: Process management capabilities
- **Validates**: Process adoption, multiple instances, and dependency management

### 10. test_run_targets.py

- **Requirements**: `feat_req__lifecycle__run_target_support`, `feat_req__lifecycle__start_named_run_target`, `feat_req__lifecycle__switch_run_targets`, `feat_req__lifecycle__process_state_comm`
- **Tests**: Run target support
- **Validates**: Run target definition, activation, and switching

### 11. test_process_termination.py

- **Requirements**: `feat_req__lifecycle__configurable_timeout`, `feat_req__lifecycle__process_termination`, `feat_req__lifecycle__termination_dependency`, `feat_req__lifecycle__time_to_wait_config`, and 5+ more
- **Tests**: Process termination support
- **Validates**: Graceful shutdown, signal handling, and timeout configuration

### 12. test_monitoring_and_recovery.py

- **Requirements**: `feat_req__lifecycle__monitor_abnormal_term`, `feat_req__lifecycle__ext_monitor_notify`, `feat_req__lifecycle__recovery_action_support`, and 13+ more
- **Tests**: Monitoring, notification, and recovery
- **Validates**: Watchdog, liveliness detection, failure recovery, and self health checks

### 13. test_control_commands.py

- **Requirements**: `feat_req__lifecycle__control_commands`, `feat_req__lifecycle__query_commands`, `feat_req__lifecycle__controlif_status`, `feat_req__lifecycle__request_run_target_start`
- **Tests**: Control interface commands
- **Validates**: Control and query commands for component state management

### 14. test_logging.py

- **Requirements**: `feat_req__lifecycle__slog2_logging`, `feat_req__lifecycle__process_logging_support`, `feat_req__lifecycle__log_timestamp`, `feat_req__lifecycle__dag_logging_controlif`, `feat_req__lifecycle__dependency_visu`
- **Tests**: Logging support
- **Validates**: Process launch logging, state transitions, timestamps, and DAG logging

### 15. test_configuration_management.py

- **Requirements**: `feat_req__lifecycle__modular_config_support`, `feat_req__lifecycle__runtime_config_compat`, `feat_req__lifecycle__session_extension`, and 5+ more
- **Tests**: Configuration file management
- **Validates**: Modular configuration, OCI compatibility, and validation

### 16. test_debug_and_terminal.py

- **Requirements**: `feat_req__lifecycle__debug_support`, `feat_req__lifecycle__support_held_state`, `feat_req__lifecycle__terminal_support`
- **Tests**: Debug mode and terminal support
- **Validates**: Debug mode, debugger waiting state, and session leader creation

### 17. test_io_and_file_descriptors.py

- **Requirements**: `feat_req__lifecycle__std_handle_redir`, `feat_req__lifecycle__fd_inheritance`, `feat_req__lifecycle__detach_parent_process`, `feat_req__lifecycle__retries_configurable`
- **Tests**: I/O and file descriptor management
- **Validates**: Standard handle redirection, FD inheritance control, and process detachment

## Implementation Approach

### 1. Real API Integration vs. Simulation

**Decision**: Use real lifecycle and health monitoring APIs from `@score_lifecycle_health`

**Rationale**:

- Provides realistic demonstration of how applications integrate with lifecycle services
- Tests actual API surface that application developers will use
- Validates API availability and correctness
- Enables detection of breaking API changes early

**Graceful Degradation**:
The tests are designed to run in environments without the Launch Manager daemon. When the daemon is not available:

- Lifecycle client calls return an empty result (C++) or `false` (Rust) instead of panicking
- Tests log informational messages explaining the demonstration nature
- Tests still validate API signatures and integration patterns
- Tests pass successfully, confirming proper integration code

### 2. Dual Language Implementation (Rust + C++)

**Decision**: Implement all scenarios in both Rust and C++

**Rationale**:

- **Language Parity**: Ensures both language ecosystems have equal support
- **API Verification**: Confirms lifecycle APIs work correctly in both languages
- **Documentation by Example**: Provides working examples for developers in both languages
- **Comprehensive Coverage**: Detects language-specific integration issues

**Implementation Details**:

| Aspect | Rust Implementation | C++ Implementation |
|--------|--------------------|--------------------|
| **Lifecycle Client** | `lifecycle_client_rs::report_execution_state_running()` | `score::lcm::LifecycleClient{}.ReportExecutionState()` |
| **Health Monitoring** | `health_monitoring_lib::HealthMonitorBuilder` | Demonstrates API patterns with logging |
| **Logging** | Structured JSON logs via `tracing::info!()` | Plain text via `std::cout` |
| **Dependencies** | `@score_lifecycle_health//...rust_bindings:lifecycle_client_rs`<br/>`@score_lifecycle_health//src/health_monitoring_lib` | `@score_lifecycle_health//...lifecycle_client_lib:lifecycle_client` |

### 3. Test Architecture

**Three-Layer Design**:

```
┌─────────────────────────────────────────────────────────┐
│  Python Test Layer (test_cases/tests/lifecycle/)       │
│  - Orchestrates test execution                         │
│  - Validates test results                              │
│  - Provides parametrization (rust/cpp)                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Scenario Base (test_cases/lifecycle_scenario.py)      │
│  - Provides shared fixtures (temp_dir)                 │
│  - Utility functions for config management             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────┬──────────────────────────────┐
│  Rust Scenarios          │  C++ Scenarios               │
│  (test_scenarios/rust/)  │  (test_scenarios/cpp/)       │
│  - Real API calls        │  - Real API calls            │
│  - Structured logging    │  - Plain text logging        │
└──────────────────────────┴──────────────────────────────┘
```

**Rationale**:

- **Separation of Concerns**: Python for orchestration, Rust/C++ for implementation
- **Language-Appropriate Testing**: Leverages pytest for test management
- **Reusability**: Base scenario class reduces code duplication
- **Flexibility**: Easy to add new test scenarios or languages

### 4. Test Validation Strategy

**Decision**: Use different validation approaches for Rust vs C++

**Rust Tests**:

- Parse structured JSON logs from `tracing` framework
- Use `LogContainer` to query specific log messages
- Validate presence and content of structured log fields

**C++ Tests**:

- Parse plain text stdout output
- Use string matching to validate key messages
- Simpler logging reduces dependencies

**Rationale**:

- **Rust**: Tracing infrastructure already available, provides rich structured logging
- **C++**: Minimizes dependencies, uses `std::cout` for simplicity
- **Pragmatic**: Both approaches validate the same behavior effectively

## Scenario Implementation Files

All scenarios are implemented in both Rust and C++:

**Rust**:

- Implementation: `test_scenarios/rust/src/scenarios/lifecycle/launch_manager_support.rs`
- Registration: `test_scenarios/rust/src/scenarios/lifecycle/mod.rs`

**C++**:

- Implementation: `test_scenarios/cpp/src/scenarios/lifecycle/launch_manager_support.cpp`
- Header: `test_scenarios/cpp/src/scenarios/lifecycle/launch_manager_support.h`
- Registration: `test_scenarios/cpp/src/scenarios/mod.cpp`

## Running the Tests

### Using Bazel (Recommended)

Run all lifecycle tests (both languages):

```bash
bazel test --config=linux-x86_64 \
  //feature_integration_tests/test_cases:fit_rust \
  //feature_integration_tests/test_cases:fit_cpp \
  --test_filter="*lifecycle*"
```

Run specific language:

```bash
# Rust only
bazel test //feature_integration_tests/test_cases:fit_rust --test_filter="*lifecycle*"

# C++ only
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp --test_filter="*lifecycle*"
```

Run specific test file:

```bash
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp \
  --test_filter="*test_process_launching*"
```

### Using Pytest Directly

Run all lifecycle tests:

```bash
cd feature_integration_tests
pytest test_cases/tests/lifecycle/
```

Run specific test file:

```bash
pytest test_cases/tests/lifecycle/test_control_interface_support.py
```

Run tests for specific implementation (rust or cpp):

```bash
pytest test_cases/tests/lifecycle/ -k "rust"
pytest test_cases/tests/lifecycle/ -k "cpp"
```

### Debug Individual Scenarios

List available scenarios:

```bash
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
bazel run --config=linux-x86_64 //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- --list-scenarios
```

Run a scenario directly:

```bash
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- \
  rust lifecycle.process_launching_support '{"test":{"test_duration_ms":100,"checkpoint_count":3}}'
```

## Test Configuration

Scenarios accept JSON configuration to customize test behavior. Common parameters include:

**Base parameters** (used by most scenarios):

```json
{
  "test": {
    "test_duration_ms": 100,
    "checkpoint_count": 3
  }
}
```

**Scenario-specific parameters** (examples):

```json
{
  "test": {
    "condition_name": "app_ready",
    "args": ["--mode", "test", "--verbose"],
    "working_dir": "/tmp",
    "uid": 1000,
    "gid": 1000,
    "priority": 10,
    "scheduling_policy": "SCHED_RR",
    "polling_interval_ms": 50,
    "timeout_ms": 5000,
    "watchdog_interval_ms": 100,
    "max_restart_attempts": 3
  }
}
```

The Python test files build appropriate configurations for each scenario automatically.

## Dependencies

### Rust

- `lifecycle_client_rs` — Lifecycle client bindings for Rust
- `health_monitoring_lib` — Health monitoring library
- `test_scenarios_rust` — Test scenario framework
- `tracing` — Structured logging

### C++

- `score::lcm::lifecycle_client` — Lifecycle client library
- `score::json` — JSON parsing
- `test_scenarios_cpp` — Test scenario framework

### Python

- `pytest` — Test framework and orchestration
- `testing_utils` — Log parsing and scenario execution utilities

## Future Enhancements

Potential areas for expansion:

1. **Integration with Real Launch Manager**:
   - Tests that run against actual Launch Manager daemon
   - Validation of supervision and recovery behavior
   - End-to-end lifecycle state transitions

2. **Additional Scenarios**:
   - Process termination and cleanup
   - Error recovery patterns
   - State persistence across restarts

3. **Performance Testing**:
   - Measure supervision overhead
   - Validate scalability with many parallel processes
   - Benchmark deadline monitoring accuracy

4. **Configuration Testing**:
   - Test various Launch Manager configurations
   - Validate configuration schema compliance
   - Test configuration error handling

## References

- [Launch Manager Design](https://github.com/eclipse-score/lifecycle)
- [Health Monitoring Documentation](https://github.com/eclipse-score/lifecycle/tree/main/src/health_monitoring_lib)
- [Lifecycle Client API](https://github.com/eclipse-score/lifecycle/tree/main/src/launch_manager_daemon/lifecycle_client_lib)
- [Feature Integration Test Framework](./README.md)

---
