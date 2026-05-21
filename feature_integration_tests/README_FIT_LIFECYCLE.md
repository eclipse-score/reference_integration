# Lifecycle Feature Integration Tests

This document describes the lifecycle feature integration tests implemented in this repository, including the approach taken and the rationale behind design decisions.

## Overview

Lifecycle feature integration tests verify that applications can properly integrate with the S-CORE lifecycle management framework. These tests validate three key capabilities that the Launch Manager provides:

1. **Process Launching Support** — Applications can report execution state to the Launch Manager
2. **Dependency Ordering** — Applications can use sequential health monitoring for ordered initialization
3. **Parallel Launching** — Multiple independent health monitors can run concurrently

## Requirements Tested

The lifecycle FIT tests partially verify the following requirements:

- **feat_req__lifecycle__launch_support** — The Launch Manager shall provide support for launching Processes
- **feat_req__lifecycle__dependency_ordering** — The Launch Manager shall provide support for ordering the launching of Processes based on the dependencies
- **feat_req__lifecycle__parallel_launching** — The Launch Manager shall provide support for launching Processes in parallel

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
- Lifecycle client calls return `false` (C++) or `false` (Rust) instead of panicking
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

## Test Scenarios

### 1. Process Launching Support

**Purpose**: Verify that applications can report execution state to Launch Manager

**Implementation**:
- Calls `report_execution_state_running()` or `ReportExecutionState(kRunning)`
- Logs success or graceful degradation message
- Simulates application work with configurable duration

**Validation**:
- Confirms API was called successfully
- Verifies application completed without errors
- Checks for appropriate log messages

**File Locations**:
- Rust: `test_scenarios/rust/src/scenarios/lifecycle/launch_manager_support.rs`
- C++: `test_scenarios/cpp/src/scenarios/lifecycle/launch_manager_support.cpp`
- Test: `test_cases/tests/lifecycle/test_process_launching.py`

### 2. Dependency Ordering

**Purpose**: Demonstrate sequential initialization patterns for dependency-ordered supervision

**Implementation**:
- Rust: Creates health monitor with sequential deadline monitors
- C++: Demonstrates sequential checkpoint reporting pattern
- Reports checkpoints in sequence: `init_step_0`, `init_step_1`, etc.

**Validation**:
- Confirms all checkpoints reported in correct order
- Verifies sequential execution pattern
- Checks completion message

**File Locations**:
- Rust: `test_scenarios/rust/src/scenarios/lifecycle/launch_manager_support.rs`
- C++: `test_scenarios/cpp/src/scenarios/lifecycle/launch_manager_support.cpp`
- Test: `test_cases/tests/lifecycle/test_dependency_ordering.py`

### 3. Parallel Launching

**Purpose**: Demonstrate that multiple independent health monitors can run concurrently

**Implementation**:
- Creates multiple parallel monitors (configurable count, default 4)
- Each monitor runs in a separate thread
- Demonstrates concurrent monitoring capability
- C++: Uses mutex for thread-safe stdout logging

**Validation**:
- Confirms all parallel monitors started
- Verifies all monitors completed successfully
- Checks for completion confirmation message

**File Locations**:
- Rust: `test_scenarios/rust/src/scenarios/lifecycle/launch_manager_support.rs`
- C++: `test_scenarios/cpp/src/scenarios/lifecycle/launch_manager_support.cpp`
- Test: `test_cases/tests/lifecycle/test_parallel_launching.py`

## Running the Tests

### Run All Lifecycle Tests (Both Languages)

```bash
bazel test --config=linux-x86_64 \
  //feature_integration_tests/test_cases:fit_rust \
  //feature_integration_tests/test_cases:fit_cpp \
  --test_filter="*lifecycle*"
```

### Run Specific Language

```bash
# Rust only
bazel test //feature_integration_tests/test_cases:fit_rust --test_filter="*lifecycle*"

# C++ only
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp --test_filter="*lifecycle*"
```

### Run Specific Scenario

```bash
# Process launching support
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp \
  --test_filter="*process_launching*"

# Dependency ordering
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_rust \
  --test_filter="*dependency_ordering*"

# Parallel launching
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit_cpp \
  --test_filter="*parallel_launching*"
```

### Debug Individual Scenarios

List available scenarios:
```bash
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios
bazel run --config=linux-x86_64 //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- --list-scenarios
```

Run a specific scenario directly:
```bash
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- \
  rust lifecycle.process_launching_support '{"test":{"test_duration_ms":100,"checkpoint_count":3}}'
```

## Test Configuration

All lifecycle tests accept a JSON configuration with the following structure:

```json
{
  "test": {
    "test_duration_ms": 100,
    "checkpoint_count": 3
  }
}
```

**Parameters**:
- `test_duration_ms`: Duration in milliseconds for simulated application work
- `checkpoint_count`: Number of checkpoints/monitors to create (for ordering and parallel tests)

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

**Copyright (c) 2026 Contributors to the Eclipse Foundation**

Licensed under the Apache License, Version 2.0
