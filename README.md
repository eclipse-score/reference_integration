# Reference Integration

Integration workspace for the Eclipse Score project. This repository is used to validate cross-module builds (e.g. baselibs, communication, persistency, feo, etc.) from a single Bazel workspace.

## ✅ Working Build Commands

### Baselibs

```bash
bazel build --config bl-x86_64-linux @score-baselibs//score/... --verbose_failures
```

### Communication

```bash
bazel build --config bl-x86_64-linux @communication//score/... @communication//third_party/...  --verbose_failures
```

### Persistency

```bash
bazel build \
    @score_persistency//src/... \
    @score_persistency//tests/cpp_test_scenarios/... \
    @score_persistency//tests/rust_test_scenarios/... \
    --extra_toolchains=@llvm_toolchain//:cc-toolchain-x86_64-linux \
    --copt=-Wno-deprecated-declarations \
    --verbose_failures
```

> Note: Python tests for `@score_persistency` cannot be built from this integration workspace due to Bazel external repository visibility limitations. The pip extension and Python dependencies must be accessed within their defining module.

### Orchestration and `kyron` - async runtime for Rust

```bash
bazel build @score_orchestrator//src/...
```

## Feature showcase examples
The examples that are aiming to showcase features provided by S-CORE are located in `feature_showcase` folder.
You can run them currently for host platform using `--config bl-x86_64-linux`.

Execute `bazel query //feature_showcase/...` to obtain list of targets that You can run.

## ⚠️ Observed Issues

### communication: score/mw/com/requirements
Problems when building from a different repo:
- Some `BUILD` files use `@//third_party` instead of `//third_party` (repository-qualified vs. local label mismatch).
- `runtime_test.cpp:get_path` is checking `safe_posix_platform` (likely an outdated module name) instead of `external/communication+/`.
- fixed in feature/build_from_reference_repo https://github.com/etas-contrib/score_communication.git

### communication: get_git_info
@communication//third_party/... here get_git_info is causing problems because it cannot find github root from e.g.
/home/runner/.bazel/sandbox/processwrapper-sandbox/1689/execroot/_main/bazel-out/k8-opt-exec-ST-8abfa5a323e1/bin/external/communication+/third_party/traceability/tools/source_code_linker/parsed_source_files_for_source_code_linker.runfiles/communication+/third_party/traceability/tools/source_code_linker/get_git_info.py
is this needed? should we fix it?

### Toolchain / Version Drift
- Persistency uses `llvm_toolchain 1.2.0` while baselibs uses `1.4.0`. Aligning versions may reduce incompatibilities. Also Persistency does not work with `1.4.0`.

## 🚧 Not Yet Working

```bash
bazel build @score_persistency//src/cpp/... --extra_toolchains=@llvm_toolchain//:cc-toolchain-x86_64-linux

bazel build @feo//... --verbose_failures
```


```bash
bazel mod graph
```
It is working with latest baselibs (dev_dependency = True for score_toolchains_qnx), but communication is not building with it.

### Missing System Packages (for feo build)
Install required system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y protobuf-compiler libclang-dev
```

## 🧪 To Be Done

```bash
bazel test @itf//...
```

Add test targets once cross-repo visibility constraints are clarified.

Configuration handling (instead of baselibs.bazelrc,...)

## 🌐 Proxy & Dependency Handling

`starpls.bzl` (see: https://github.com/eclipse-score/tooling/blob/main/starpls/starpls.bzl) uses `curl` directly, which:
- Bypasses Bazel's fetch/dependency tracking.
- May fail in a proxy-restricted environment.

### Possible Workaround
Use a `local_path_override` and set proxy environment variables before invoking the rule:

```bash
export http_proxy=http://127.0.0.1:3128
export https_proxy=http://127.0.0.1:3128
export HTTP_PROXY=http://127.0.0.1:3128
export HTTPS_PROXY=http://127.0.0.1:3128
```

Example Bazel module override snippet:
```python
local_path_override(module_name = "score_tooling", path = "../tooling")
```

### Suggested Improvements
- Replace raw `curl` calls with Bazel `http_archive` or `repository_ctx.download` for reproducibility.
- Parameterize proxy usage via environment or Bazel config flags.

## 🔍 Next Investigation Targets
- Normalize third-party label usage (`@//third_party` vs `//third_party`).
- Update `runtime_test.cpp:get_path` logic for new module layout.
- Unify LLVM toolchain versions across modules.
- Introduce integration tests for `@itf` once build succeeds.

## IDE support

### Rust

Use `./generate_rust_analyzer_support.sh` to generate rust_analyzer settings that will let VS Code work.

## 📌 Quick Reference

| Area | Status | Action |
|------|--------|--------|
| baselibs build | ✅ | Keep as baseline |
| communication build | ✅ | Fix label style inconsistencies |
| persistency (Python tests) | 🚫 | Not supported cross-repo |
| feo build | ❌ | Install system deps + inspect failures |
| itf tests | ⏳ | Add after build stabilization |

## 🗂 Notes
Keep this file updated as integration issues are resolved. Prefer converting ad-hoc shell steps into Bazel rules or documented scripts under `tools/` for repeatability.
