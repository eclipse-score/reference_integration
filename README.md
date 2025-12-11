# Score Reference Integration

This workspace integrates multiple Eclipse Score modules (baselibs, communication, persistency, orchestrator, feo, etc.) to validate cross-repository builds and detect integration issues early in the development cycle.

## Overview

The reference integration workspace serves as a single Bazel build environment to:
- Validate cross-module dependency graphs
- Detect label and repository boundary issues
- Test toolchain and platform support (Linux, QNX, LLVM/GCC)
- Prepare for release validation workflows

## Docs

To generate a full documentation of all integrated modules, run:
```bash
bazel run //:docs_combo_experimental
```
## Working Builds ✅

The following modules build successfully with the `bl-x86_64-linux` configuration:

### Baselibs
```bash
bazel build --config bl-x86_64-linux @score_baselibs//score/... --verbose_failures
```

### Communication
```bash
bazel build --config bl-x86_64-linux @communication//score/mw/com:com --verbose_failures
```

### Persistency
```bash
bazel build --config bl-x86_64-linux \
  @score_persistency//src/cpp/src/... \
  @score_persistency//src/rust/... \
  --verbose_failures
```

> Note: Python tests for `@score_persistency` cannot be built from this integration workspace due to Bazel external repository visibility limitations. The pip extension and Python dependencies must be accessed within their defining module.

### Orchestration and `kyron` - async runtime for Rust

```bash
bazel build --config bl-x86_64-linux @score_orchestrator//src/...
```

## Clippy

- Clippy runs by default via `.bazelrc` on all Rust targets (Rust tests may be tagged `no-clippy`).
- Use `bazel build //:clippy` if you want an explicit lint-only target, or build the Rust targets normally to see Clippy diagnostics.
- The Clippy config comes from `@score_rust_policies//clippy/strict:clippy.toml`.

## Feature showcase examples
The examples that are aiming to showcase features provided by S-CORE are located in `feature_showcase` folder.
You can run them currently for host platform using `--config bl-x86_64-linux`.

Execute `bazel query //feature_showcase/...` to obtain list of targets that You can run.


```bash
bazel build --config bl-x86_64-linux @score_orchestrator//src/... --verbose_failures
```

## Known Issues ⚠️

### Orchestrator
**Issue:** Direct toolchain loading at `BUILD:14`
```
load("@score_toolchains_qnx//rules/fs:ifs.bzl", "qnx_ifs")
```
**Resolution needed:** Refactor to use proper toolchain resolution instead of direct load statements.

**Issue:** clang needs to be installed
```
sudo apt install clang
```
**Resolution needed:** why is this happening with -extra_toolchains=@gcc_toolchain//:host_gcc_12 ?

### Communication
**Module:** `score/mw/com/requirements`

**Issues when building from external repository:**
1. **Label inconsistency:** Some `BUILD` files use `@//third_party` instead of `//third_party` (repository-qualified vs. local label). Should standardize on local labels within the module.
2. **Outdated path reference:** `runtime_test.cpp:get_path` checks for `safe_posix_platform` (likely obsolete module name) instead of `external/score_communication+/`.

### Persistency
**Test failures in `src/cpp/tests`:**
1. **Dependency misconfiguration:** `google_benchmark` should not be a dev-only dependency if required by tests. Consider separating benchmark targets.
2. **Compiler-specific issue in `test_kvs.cpp`:** Contains GCC-specific self-move handling that is incorrect and fails with GCC (only builds with LLVM). Needs portable fix or removal of undefined behavior.

## Build Blockers 🚧

The following builds are currently failing:

### FEO (Full Build)
```bash
bazel build @feo//... --verbose_failures
```

### Persistency (Full Build)
```bash
bazel build --config bl-x86_64-linux @score_persistency//src/... --verbose_failures
```

## System Dependencies

### Required Packages for FEO
Install the following system packages before building FEO:
```bash
sudo apt-get update
sudo apt-get install -y protobuf-compiler libclang-dev
```

## Pending Tasks 🧪

- [ ] Add test targets once cross-repository visibility constraints are clarified
- [ ] Normalize third-party label usage across all `BUILD` files
- [ ] Resolve FEO build failures
- [ ] Fix Persistency full build
- [ ] Address compiler-specific issues in test suites

## Proxy & External Dependencies 🌐

### Current Issue

The `starpls.bzl` file ([source](https://github.com/eclipse-score/tooling/blob/main/starpls/starpls.bzl)) uses `curl` directly for downloading dependencies, which:
- Bypasses Bazel's managed fetch lifecycle and dependency tracking
- Breaks reproducibility and remote caching expectations
- May fail in corporate proxy-restricted environments

### Workaround

Use a `local_path_override` and configure proxy environment variables before building:

```bash
export http_proxy=http://127.0.0.1:3128
export https_proxy=http://127.0.0.1:3128
export HTTP_PROXY=http://127.0.0.1:3128
export HTTPS_PROXY=http://127.0.0.1:3128
```

Add this to your `MODULE.bazel`:
```python
local_path_override(module_name = "score_tooling", path = "../tooling")
```

### Suggested Improvements
- Replace raw `curl` calls with Bazel `http_archive` or `repository_ctx.download` for reproducibility.
- Parameterize proxy usage via environment or Bazel config flags.

## IDE support

### Rust

Use `./generate_rust_analyzer_support.sh` to generate rust_analyzer settings that will let VS Code work.

## 🗂 Notes
Keep this file updated as integration issues are resolved. Prefer converting ad-hoc shell steps into Bazel rules or documented scripts under `tools/` for repeatability.
