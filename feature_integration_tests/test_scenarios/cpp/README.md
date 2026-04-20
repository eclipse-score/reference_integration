# C++ Feature Integration Test Scenarios

This directory contains the C++ implementation of feature integration test scenarios.

Current scope is persistency-focused scenarios.

## Structure

- src/main.cpp
  - CLI entry point for scenario execution.
  - Uses shared test scenario framework from `@score_test_scenarios//test_scenarios_cpp`.
  - Supports listing scenarios and running a scenario with JSON input.
- src/internals/persistency/
  - kvs_parameters.h/.cpp
    - Parses KVS config sections from JSON input.
  - kvs_instance.h/.cpp
    - Wraps C++ KVS builder/API operations.
    - Provides typed set/get helpers.
    - Normalizes snapshot JSON to Rust-compatible top-level envelope.
    - Canonicalizes noisy f64 literals in snapshots (for example 111.099998 -> 111.1)
      so Python FIT checks can keep strict value equality.
- src/scenarios/
  - mod.cpp
    - Registers root and persistency scenario groups.
  - persistency/multiple_kvs_per_app.cpp
    - Scenario implementation for multi-instance KVS validation.

## Build Targets

Defined in BUILD:

- cpp_test_scenarios (cc_binary)

## Available Scenario

- persistency.multiple_kvs_per_app

## Scenario Contract

persistency.multiple_kvs_per_app expects JSON with:

- kvs_parameters_1.kvs_parameters
- kvs_parameters_2.kvs_parameters
- test
  - key
  - value_1
  - value_2

Behavior:

1. Creates two KVS instances with different instance IDs.
2. Writes different values for the same key.
3. Flushes both instances.
4. Reopens both instances.
5. Reads values back and emits INFO logs.
6. Normalizes written snapshot files to Rust-compatible envelope format.
7. Canonicalizes persisted f64 literals that carry float-noise artifacts.

## Notes

- C++ persistency snapshots may expose float-noise literals even for semantic decimal inputs.
  The scenario adapter normalizes these values during snapshot envelope conversion so
  FIT assertions in Python can remain strict (`==`) instead of using tolerances.

## Traceability

The C++ scenario `persistency.multiple_kvs_per_app` is validated by the FIT test module:

- `feature_integration_tests/test_cases/tests/persistency/test_multiple_kvs_per_app.py`

Verification metadata in that test currently declares:

- `partially_verifies = ["feat_req__persistency__multiple_kvs"]`
- `test_type = "requirements-based"`
- `derivation_technique = "requirements-analysis"`

This keeps the scenario name, test input contract, and requirement linkage aligned across
the C++ scenario runner and the Python FIT layer.

## Usage

Build:

```sh
bazel build //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios
```

List scenarios:

```sh
bazel run //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- --list-scenarios
```

Run scenario:

```sh
bazel run //feature_integration_tests/test_scenarios/cpp:cpp_test_scenarios -- \
  --name persistency.multiple_kvs_per_app \
  --input '{
    "kvs_parameters_1": {"kvs_parameters": {"instance_id": 1, "dir": "/tmp/cpp_fit"}},
    "kvs_parameters_2": {"kvs_parameters": {"instance_id": 2, "dir": "/tmp/cpp_fit"}},
    "test": {"key": "number", "value_1": 111.1, "value_2": 222.2}
  }'
```

Run the C++ persistency-focused FIT target:

```sh
bazel test //feature_integration_tests/test_cases:fit_cpp
```
