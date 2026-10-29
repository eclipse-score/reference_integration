# s-core Test Compatibility Kit (TCK)

A portable test kit for verifying SCORE distribution compatibility with platform requirements.

## Overview

The TCK verifies whether a SCORE distribution is compatible with the main platform requirements:

| Check Family | Purpose | Status |
|--------------|---------|--------|
| **SBOM** | Required components, license policy, drift from golden | ✅ Implemented |
| **Version** | Platform version compatibility | ✅ Implemented |
| **Runtime** | Toolchain, libraries, architecture | ✅ Implemented |
| **Behavioral** | Run integration tests against distribution | 🔧 Test definitions ready |
| **API** | Header/symbol validation | 🔧 Definitions ready |

## Quick Start

```bash
# Build the TCK
bazel build //tck:score-tck

# Run against a distribution
./bazel-bin/tck/score-tck run --config my-dist.toml --report ./report

# View results
cat ./report/summary.md
```

## Distribution Configuration

Create a `tck.config.toml` for your distribution:

```toml
[dist]
name = "my-score-dist"
version = "1.0.0"
platform_version = "0.9.0"  # Must be compatible with TCK platform version
arch = "x86_64-linux"
profile = "full"

[dist.paths]
sbom_file = "./dist/sbom.spdx.json"
headers_dir = "./dist/include"
```

## Check Details

### SBOM Check

Verifies:
- All required components from `requirements.toml` are present
- No forbidden components are included
- All licenses are in the approved list
- No drift from golden SBOM (optional)

### Version Check

Ensures the distribution's declared `platform_version` is compatible with the TCK's minimum required version using semver comparison.

### Runtime Check

Validates:
- Target architecture is supported (x86_64-linux, aarch64-linux, qnx-aarch64)
- Toolchain availability (GCC 11+ or Clang 14+)
- Required system libraries (pthread, dl, rt)
- Test harness adapter configuration

## Test Definitions

Behavioral tests reference the existing `feature_integration_tests/`:

```bash
tck/tests/
├── behavioral.toml      # Pytest test mappings
└── api_signatures.toml  # Required header definitions
```

## Requirements Policy

The `tck/reference/policy/requirements.toml` defines:

- **Mandatory SBOM components**: score_baselibs, score_communication, score_persistency, etc.
- **Allowed licenses**: Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, etc.
- **Version requirements**: Platform version compatibility rules

## Output

The TCK produces:

- `report.json` - Machine-readable JSON report
- `summary.md` - Human-readable markdown summary

### Verdicts

| Verdict | Meaning |
|---------|---------|
| `CONFORMANT` | All required checks passed |
| `CONFORMANT-WITH-WARNINGS` | Required checks passed, some warnings |
| `NON-CONFORMANT` | One or more required checks failed |

## Architecture

```
tck/
├── runner/                    # Rust TCK binary
│   ├── src/
│   │   ├── main.rs           # CLI entry point
│   │   ├── sbom.rs           # SBOM check
│   │   ├── version.rs        # Version check
│   │   ├── runtime.rs        # Runtime check + test harness adapter
│   │   ├── config.rs         # Distribution config parsing
│   │   └── report.rs         # Report generation
│   └── Cargo.toml
├── reference/                 # Golden references
│   ├── sbom.spdx.json        # Golden SBOM (162 packages)
│   └── policy/
│       └── requirements.toml # Platform requirements
├── tests/                     # Test definitions
│   ├── behavioral.toml       # Behavioral test mappings
│   └── api_signatures.toml   # API header requirements
└── BUILD                      # Bazel target
```

## Porting Package Concept

Inspired by Jakarta EE TCK, vendors configure a **test harness adapter** that tells the TCK how to run tests against their distribution. This is configured in `runtime.rs`:

```rust
pub struct TestHarnessAdapter {
    pub build_command: Option<String>,
    pub run_command: Option<String>,
    pub showcase_cli_path: Option<PathBuf>,
    // ...
}
```

This ensures the same runtime configuration used in production is used during testing.

## CI Integration

The TCK is built and bundled in `.github/workflows/build_tck.yml`:

- Builds on PR and push to main
- Bundles binary with reference files
- Attaches to releases on tag
