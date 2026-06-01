# Eclipse S-CORE Reference Integration

This workspace integrates multiple Eclipse S-CORE modules (baselibs, communication, persistency, orchestrator, etc.) to validate cross-repository builds and detect integration issues early in the development cycle.

## Overview

The reference integration workspace serves as a unified Bazel build environment for:

- Validating cross-module dependency graphs and boundary issues
- Testing toolchain and platform support (Linux x86_64, QNX x86_64, Elektrobit corbos Linux aarch64, Red Hat AutoSD)
- Running Feature Integration Tests (FIT) and Integration Test Framework (ITF) tests
- Preparing for release validation and integration workflows

For additional documentation covering repository workflows and platform-specific details, see the `docs/` directory.

## Prerequisites

Install required system packages before building or running anything in this repository:

```bash
sudo apt-get update
sudo apt-get install -y protobuf-compiler libclang-18-dev lcov docker.io qemu-system-x86
```

## Quick Start

Simply run:

```bash
./score_starter
```

You will be guided interactively through available integrations, build options, and examples to run.

## Run showcases

Use the interactive helper or Bazel to run showcase binaries. Examples:

```bash
# Interactive helper
./score_starter

# Run a CLI showcase (example target, may vary by workspace state)
bazel run //showcases/cli:cli -- --help
```

See [showcases/cli/README.md](showcases/cli/README.md) for CLI configuration and examples.

## Run tests

Run Feature Integration Tests (FIT) and Integration Test Framework (ITF) with Bazel. Common examples:

```bash
# Run all FIT tests (Rust + C++)
bazel test --config=linux-x86_64 //feature_integration_tests/test_cases:fit --test_output=streamed

# Run only Rust scenarios listing
bazel run //feature_integration_tests/test_scenarios/rust:rust_test_scenarios -- --list-scenarios

# Run ITF tests on Docker (Linux)
bazel test --config=linux-x86_64 //feature_integration_tests/itf --test_output=streamed

# Run ITF tests on QNX (uses the itf-qnx-x86_64 test config)
bazel test --config=itf-qnx-x86_64 //feature_integration_tests/itf --test_output=streamed
```

Notes:
- Use `--config=<name>` to select the correct toolchain/platform (common configs: `linux-x86_64`, `qnx-x86_64`, `eb-aarch64`, `autosd-x86_64`). See `.bazelrc` for all available configs.
- For streaming test output and real-time logs, use `--test_output=streamed` or `--test_output=all`.

## Repository Structure

Intention for each folder is described below.

### `bazel_common/`

Common Bazel configurations and macros used across the workspace:
- Toolchain setups (GCC, Rust, QNX)
- S-CORE module dependency versions
- Bazel extensions and bundling macros

### `feature_integration_tests/`

Feature Integration Tests and test scenarios:
- **`test_cases/`**: Python test orchestration and fixtures
- **`test_scenarios/`**: Rust and C++ scenario implementations
- **`itf/`**: Integration Test Framework (QEMU/Docker-based platform tests)
- **`configs/`**: DLT, QEMU, and target-specific configurations

### `showcases/`

Eclipse S-CORE demonstration applications and examples:
- **`cli/`**: Interactive CLI tool for running examples on deployed systems
- **`standalone/`**: Standalone example binaries (communication, persistence, etc.)
- **`orchestration_persistency/`**: Multi-module orchestration examples
- **`simple_lifecycle/`**: Basic lifecycle management examples

Configuration for CLI autodiscovery is in `name.score.json` files; see [showcases/cli/README.md](showcases/cli/README.md) for details.

### `images/`

Platform-specific target images bundling S-CORE artifacts and showcases:
- **`linux_x86_64/`**: Linux x86_64 Docker image
- **`qnx_x86_64/`**: QNX x86_64 QEMU image
- **`ebclfsa_aarch64/`**: Elektrobit corbos Linux for Safety Applications (aarch64) (see [images/ebclfsa_aarch64/README.md](images/ebclfsa_aarch64/README.md))
- **`autosd/`**: Red Hat AutoSD x86_64

### `runners/`

Thin abstraction layers for Docker and QEMU execution:
- Centralized logic for spawning and interacting with target environments
- Reusable across multiple image definitions

## Documentation

For documentation covering repository workflows, testing frameworks, and platform-specific details, see the `docs/` directory and these entry points:

- **[Feature Integration Tests](feature_integration_tests/README.md)** — FIT and ITF test framework usage
- **[CLI Documentation](showcases/cli/README.md)** — CLI tool configuration and usage
- **Platform-Specific Guides:**
   - [Elektrobit corbos Linux (aarch64)](images/ebclfsa_aarch64/README.md)

To generate HTML documentation for all integrated modules:

```bash
bazel run //:docs_combo_experimental
```

## Supported Platforms

Integration and deployment platforms for S-CORE:

- **QNX x86_64** — QNX RTOS integration (QEMU-based testing)
- **[Elektrobit corbos Linux for Safety Applications (aarch64)](images/ebclfsa_aarch64/README.md)** — Safety-critical automotive Linux
- **Red Hat AutoSD (x86_64)** — Automotive system development
- **Linux x86_64** — Standard Linux development and testing (Docker-based)

## Multi-Module Development Workspace

For cross-module development, you can obtain a complete S-CORE workspace—a local git checkout of all modules pinned in `known_good.json` on specific branches/commits—integrated into a single Bazel build.

This enables:
- Cross-module development and debugging
- Testing changes across multiple modules simultaneously
- Reproducible builds with pinned versions

> [!NOTE]
> The [S-CORE devcontainer](https://github.com/eclipse-score/devcontainer) [integrated in this repository](.devcontainer/) pre-installs workspace managers and generates required metadata.
> Manual setup is also possible; see `.devcontainer/prepare_workspace.sh` for the setup script.

### Initialization Steps

1. **Switch to local path overrides:**
   
   Use the VS Code Task (`Terminal` → `Run Task...`): **"Switch Bazel modules to `local_path_overrides`"**
   
   Command line:
   ```bash
   python3 scripts/known_good/update_module_from_known_good.py --override-type local_path
   ```
   
   To revert to git overrides:
   ```bash
   python3 scripts/known_good/update_module_from_known_good.py --override-type git
   ```

2. **Update workspace metadata from known good:**
   
   Use the VS Code Task: **"Update workspace metadata from known good"**
   
   Command line:
   ```bash
   python3 scripts/known_good/known_good_to_workspace_metadata.py
   ```

3. **Clone all modules:**
   
   Use the VS Code Task: **"Gita: Generate workspace"**
   
   Command line (using gita):
   ```bash
   gita clone --preserve-path --from-file .gita-workspace.csv
   ```

Modules are cloned into subdirectories prefixed with `score_` (e.g., `score_persistency/`, `score_communication/`).

When running Bazel, it will use these local working copies, and your changes will be immediately reflected in the next build.

## Known Issues ⚠️

For a comprehensive list of known issues, limitations, and troubleshooting guidance, see the `docs/` directory.

### Communication Module

**Module:** `score/mw/com/requirements`

**Integration issues when building from external repository:**

1. **Label inconsistency**: Some `BUILD` files use `@//third_party` instead of `//third_party` (repository-qualified vs. local labels). Should standardize on local labels.
2. **Outdated path reference**: `runtime_test.cpp:get_path` checks for obsolete `safe_posix_platform` instead of the current module path structure.

## IDE Support

### Rust

To enable VS Code Rust analyzer support:

```bash
scripts/generate_rust_analyzer_support.sh
```

This generates the necessary Rust analyzer configuration for the workspace.

## Internal Tooling

Internal tooling scripts are currently under development to provide a unified interface for repository operations.

For detailed documentation, see [scripts/tooling/README.md](scripts/tooling/README.md).
