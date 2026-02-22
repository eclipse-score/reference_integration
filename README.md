# Score Reference Integration

This workspace integrates multiple Eclipse Score modules (baselibs, communication, persistency, orchestrator, etc.) to validate cross-repository builds and detect integration issues early in the development cycle.

## Overview

The reference integration workspace serves as a single Bazel build environment to:

- Validate cross-module dependency graphs
- Detect label and repository boundary issues
- Test toolchain and platform support (Linux, QNX, LLVM/GCC)
- Prepare for release validation workflows

## Get started

Simply run `./score_starter` and select which integration You want to run. Once running, You will be guided by our welcome cli to run selected examples.

## Structure of repo

Intention for each folder is described below

### bazel_common

Used to keep a common bazel functionalities for `images` like:

- toolchain setups
- common tooling deps
- common S-CORE modules deps
- common `.bzl` extensions needed to streamline images

### showcases

Used to keep `S-CORE` wide **showcases** implementation to showcase S-CORE in certain deployments (images). Contains:

- proxy target bundling all `standalone` examples from all `S-CORE` repos to deploy then as single bazel target into image
- implementation of certain **showcases** that shall be deployed into images

#### cli

Contains a CLI tool to be used on runner that is showcasing the S-CORE functionality. It will provide superior user experience and will guide user to run examples.
How to use it in Your image, look [here] (./showcases/cli/README.md)

### images

Used to keep concrete `images` for given target platform as bazel modules. Each platform shall have it's own folder with name `{platform}_{arch}` ie. `qnx_aarch64`.

This `images` shall:

- deploy all `showcases` into image so they can be run inside
- other specific code for given `image`

### runners

Used to keep thin logic ro reuse `runners` between images, like docker runner etc.

## Docs

To generate a full documentation of all integrated modules, run:

```bash
bazel run //:docs_combo_experimental
```

## Operating system integrations

> [!NOTE]
> Please refer to the README documents in the respective sub-directories for details about the specific integration.

- [QNX](./images/qnx_x86_64//README.md)
- [Red Hat AutoSD](./images/autosd_x86_64/build/README.md)
- [Elektrobit corbos Linux for Safety Applications](./images/ebclfsa_aarch64/README.md)
- Linux x86_64

## Workspace support

You can obtain a complete S-CORE workspace, i.e. a git checkout of all modules from `known_good.json`, on the specific branches / commits, integrated into one Bazel build.
This helps with cross-module development, debugging, and generally "trying out things".

> [!NOTE]
> The startup of the [S-CORE devcontainer](https://github.com/eclipse-score/devcontainer) [integrated in this repository](.devcontainer/) already installs supported workspace managers and generates the required metadata.
> You can do this manually as well, of course (e.g. if you do not use the devcontainer).
> Take a look at `.devcontainer/prepare_workspace.sh`, which contains the setup script.

### Initialization of the workspace

1. Switch to local path overrides, using the VSCode Task (`Terminal`->`Run Task...`) "Switch Bazel modules to `local_path_overrides`".
   Note that you can switch back to `git_overrides` (the default) using the task "Switch Bazel modules to `git_overrides`"

   **Command line:**

   ```bash
   python3 scripts/known_good/update_module_from_known_good.py --override-type local_path
   ```

2. Update workspace metadata from known good, using the VSCode Task "Update workspace metadata from known good".
   This will generate the `.gita-workspace.csv` file based on `known_good.json`.

   **Command line:**

   ```bash
   python3 scripts/known_good/known_good_to_workspace_metadata.py
   ```

3. Run VSCode Task "&lt;Name&gt;: Generate workspace", e.g. "Gita: Generate workspace".
   This will clone all modules using the chosen workspace manager.
   The modules will be in sub-directories starting with `score_`.
   Note that the usage of different workspace managers is mutually exclusive.

   **Command line:**

   ```bash
   gita clone --preserve-path --from-file .gita-workspace.csv
   ```

When you now run Bazel, it will use the local working copies of all modules and not download them from git remotes.
You can make local changes to each module, which will be directly reflected in the next Bazel run.

## Known Issues ⚠️

### Communication

**Module:** `score/mw/com/requirements`

**Issues when building from external repository:**

1. **Label inconsistency:** Some `BUILD` files use `@//third_party` instead of `//third_party` (repository-qualified vs. local label). Should standardize on local labels within the module.
2. **Outdated path reference:** `runtime_test.cpp:get_path` checks for `safe_posix_platform` (likely obsolete module name) instead of `external/score_communication+/`.

### Coverage

Running coverage has to be executed on Ubuntu 22.04, newer versions are not supported and might have issues.

## System Dependencies

Install the following system packages:

```bash
sudo apt-get update
sudo apt-get install -y protobuf-compiler libclang-dev lcov
```

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

## IDE support

### Rust

Use `scripts/generate_rust_analyzer_support.sh` to generate rust_analyzer settings that will let VS Code work.
