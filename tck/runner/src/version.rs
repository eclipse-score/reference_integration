// *******************************************************************************
// Copyright (c) 2026 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// <https://www.apache.org/licenses/LICENSE-2.0>
//
// SPDX-License-Identifier: Apache-2.0
// *******************************************************************************
//! Version compatibility check

use anyhow::{Context, Result};
use std::path::Path;

use crate::config::Config;
use crate::report::{CheckReport, CheckResult};

/// Version requirements from policy
#[derive(Debug, Clone)]
pub struct VersionPolicy {
    pub platform_version: String,
    pub min_platform_version: String,
    pub tck_version: String,
    pub version_policy: String,
}

impl Default for VersionPolicy {
    fn default() -> Self {
        Self {
            platform_version: "0.9.0".to_string(),
            min_platform_version: "0.9.0".to_string(),
            tck_version: "0.1.0".to_string(),
            version_policy: "compatible".to_string(),
        }
    }
}

/// Load version policy from requirements.toml
pub fn load_policy(policy_path: &Path) -> Result<VersionPolicy> {
    let content = std::fs::read_to_string(policy_path)
        .with_context(|| format!("Failed to read version policy: {}", policy_path.display()))?;
    parse_version_section(&content)
}

/// Parse [version] section from TOML content
fn parse_version_section(content: &str) -> Result<VersionPolicy> {
    let tables = crate::toml::parse(content)?;
    let version = tables
        .get("version")
        .context("Missing [version] section in requirements.toml")?;
    let required = |key: &str| -> Result<String> {
        let value = version
            .get(key)
            .with_context(|| format!("Missing version policy key '{}'", key))?;
        crate::toml::string(value).with_context(|| format!("Invalid version policy key '{}'", key))
    };

    Ok(VersionPolicy {
        platform_version: required("platform_version")?,
        min_platform_version: required("min_platform_version")?,
        tck_version: required("tck_version")?,
        version_policy: required("version_policy")?,
    })
}

/// Run version compatibility check
pub fn run(config: &Config, policy: &VersionPolicy) -> Result<CheckReport> {
    let dist_version = &config.dist.platform_version;

    let check = match policy.version_policy.as_str() {
        "exact" => check_exact(dist_version, &policy.platform_version),
        "compatible" => check_compatible(dist_version, &policy.min_platform_version),
        "any" => CheckResult {
            id: "version.compatibility".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: "Version checking disabled".to_string(),
            details: vec![],
        },
        _ => CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(), // Unknown policy must fail, not warn
            severity: "required".to_string(),
            message: format!(
                "Unknown version policy: '{}'. Must be 'exact', 'compatible', or 'any'",
                policy.version_policy
            ),
            details: vec![],
        },
    };

    let verdict = if check.status == "fail" {
        "NON-CONFORMANT"
    } else {
        "CONFORMANT"
    };

    Ok(CheckReport {
        family: "version".to_string(),
        verdict: verdict.to_string(),
        checks: vec![check],
    })
}

fn check_exact(dist_version: &str, required_version: &str) -> CheckResult {
    let valid_versions = parse_semver(dist_version).is_ok() && parse_semver(required_version).is_ok();
    if valid_versions && dist_version == required_version {
        CheckResult {
            id: "version.compatibility".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("Platform version {} matches required version", dist_version),
            details: vec![serde_json::json!({"dist_version": dist_version, "required_version": required_version})],
        }
    } else if !valid_versions {
        CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!(
                "Invalid version format: distribution '{}' or required '{}'",
                dist_version, required_version
            ),
            details: vec![serde_json::json!({"dist_version": dist_version, "required_version": required_version})],
        }
    } else {
        CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!(
                "Platform version {} does not match required version {}",
                dist_version, required_version
            ),
            details: vec![serde_json::json!({"dist_version": dist_version, "required_version": required_version})],
        }
    }
}

fn check_compatible(dist_version: &str, min_version: &str) -> CheckResult {
    match compare_versions(dist_version, min_version) {
        Ok(true) => CheckResult {
            id: "version.compatibility".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("Platform version {} is compatible (>= {})", dist_version, min_version),
            details: vec![serde_json::json!({"dist_version": dist_version, "min_version": min_version})],
        },
        Ok(false) => CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!(
                "Platform version {} is below minimum required version {}",
                dist_version, min_version
            ),
            details: vec![serde_json::json!({"dist_version": dist_version, "min_version": min_version})],
        },
        Err(e) => CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(), // Parse errors must fail, not warn
            severity: "required".to_string(),
            message: format!("Invalid version format: {}", e),
            details: vec![serde_json::json!({"dist_version": dist_version, "min_version": min_version, "error": e})],
        },
    }
}

/// Compare two semantic version strings. Build metadata does not affect precedence.
fn compare_versions(v1: &str, v2: &str) -> Result<bool, String> {
    Ok(parse_semver(v1)? >= parse_semver(v2)?)
}

#[derive(Debug, Eq, PartialEq)]
struct SemVer {
    core: [u64; 3],
    prerelease: Vec<Identifier>,
}

#[derive(Debug, Eq, PartialEq)]
enum Identifier {
    Numeric(u64),
    Text(String),
}

impl Ord for SemVer {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.core
            .cmp(&other.core)
            .then_with(|| match (self.prerelease.is_empty(), other.prerelease.is_empty()) {
                (true, true) => std::cmp::Ordering::Equal,
                (true, false) => std::cmp::Ordering::Greater,
                (false, true) => std::cmp::Ordering::Less,
                (false, false) => self.prerelease.cmp(&other.prerelease),
            })
    }
}

impl PartialOrd for SemVer {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Identifier {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        match (self, other) {
            (Self::Numeric(left), Self::Numeric(right)) => left.cmp(right),
            (Self::Numeric(_), Self::Text(_)) => std::cmp::Ordering::Less,
            (Self::Text(_), Self::Numeric(_)) => std::cmp::Ordering::Greater,
            (Self::Text(left), Self::Text(right)) => left.cmp(right),
        }
    }
}

impl PartialOrd for Identifier {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

fn parse_semver(value: &str) -> Result<SemVer, String> {
    let invalid = || format!("Invalid semantic version '{}'", value);
    let (version, build) = value.split_once('+').map_or((value, None), |(v, b)| (v, Some(b)));
    if let Some(build) = build {
        if build.is_empty() || !valid_identifiers(build, false) {
            return Err(invalid());
        }
    }
    let (core, prerelease) = version.split_once('-').map_or((version, None), |(v, p)| (v, Some(p)));
    let parts: Vec<_> = core.split('.').collect();
    if parts.len() != 3 {
        return Err(invalid());
    }
    let mut numbers = [0; 3];
    for (index, part) in parts.iter().enumerate() {
        if part.is_empty()
            || (part.len() > 1 && part.starts_with('0'))
            || !part.bytes().all(|byte| byte.is_ascii_digit())
        {
            return Err(invalid());
        }
        numbers[index] = part.parse().map_err(|_| invalid())?;
    }
    let prerelease = match prerelease {
        None => Vec::new(),
        Some(value) if !valid_identifiers(value, true) => return Err(invalid()),
        Some(value) => value
            .split('.')
            .map(|part| {
                if part.bytes().all(|byte| byte.is_ascii_digit()) {
                    part.parse().map(Identifier::Numeric).map_err(|_| invalid())
                } else {
                    Ok(Identifier::Text(part.to_string()))
                }
            })
            .collect::<Result<_, _>>()?,
    };
    Ok(SemVer {
        core: numbers,
        prerelease,
    })
}

fn valid_identifiers(value: &str, prerelease: bool) -> bool {
    !value.is_empty()
        && value.split('.').all(|part| {
            !part.is_empty()
                && part.bytes().all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
                && (!prerelease
                    || !part.bytes().all(|byte| byte.is_ascii_digit())
                    || part == "0"
                    || !part.starts_with('0'))
        })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compare_versions_equal() {
        assert_eq!(compare_versions("0.9.0", "0.9.0").unwrap(), true);
    }

    #[test]
    fn test_compare_versions_greater_minor() {
        assert_eq!(compare_versions("0.10.0", "0.9.0").unwrap(), true);
    }

    #[test]
    fn test_compare_versions_less_minor() {
        assert_eq!(compare_versions("0.9.0", "0.10.0").unwrap(), false);
    }

    #[test]
    fn test_compare_versions_greater_major() {
        assert_eq!(compare_versions("1.0.0", "0.9.0").unwrap(), true);
    }

    #[test]
    fn test_compare_versions_patch_greater() {
        assert_eq!(compare_versions("0.9.1", "0.9.0").unwrap(), true);
    }

    #[test]
    fn test_compare_versions_missing_patch() {
        assert!(compare_versions("0.9", "0.9.0").is_err());
        assert!(compare_versions("0.9.0", "0.9").is_err());
    }

    #[test]
    fn test_compare_versions_prerelease() {
        assert_eq!(compare_versions("0.9.0-rc.1", "0.9.0").unwrap(), false);
        assert_eq!(compare_versions("0.9.0", "0.9.0-rc.1").unwrap(), true);
        assert_eq!(compare_versions("1.0.0-rc.2", "1.0.0-rc.1").unwrap(), true);
        assert_eq!(compare_versions("1.0.0+build.2", "1.0.0+build.1").unwrap(), true);
    }

    #[test]
    fn test_compare_versions_invalid() {
        assert!(compare_versions("invalid", "0.9.0").is_err());
        assert!(compare_versions("0.9.0", "invalid").is_err());
        assert!(compare_versions("0.9.0-01", "0.9.0").is_err());
    }

    #[test]
    fn test_check_compatible_pass() {
        let result = check_compatible("0.9.0", "0.9.0");
        assert_eq!(result.status, "pass");
    }

    #[test]
    fn test_check_compatible_fail() {
        let result = check_compatible("0.8.0", "0.9.0");
        assert_eq!(result.status, "fail");
    }

    #[test]
    fn test_check_compatible_invalid_version_fails() {
        let result = check_compatible("invalid", "0.9.0");
        assert_eq!(result.status, "fail");
    }

    #[test]
    fn test_check_exact_pass() {
        let result = check_exact("0.9.0", "0.9.0");
        assert_eq!(result.status, "pass");
    }

    #[test]
    fn test_check_exact_fail() {
        let result = check_exact("0.10.0", "0.9.0");
        assert_eq!(result.status, "fail");
    }

    #[test]
    fn test_parse_version_section() {
        let toml = r#"
[version]
platform_version = "1.2.3" # release
min_platform_version = "1.0.0" # baseline
tck_version = "0.5.0"
version_policy = "exact"
"#;
        let policy = parse_version_section(toml).unwrap();
        assert_eq!(policy.platform_version, "1.2.3");
        assert_eq!(policy.min_platform_version, "1.0.0");
        assert_eq!(policy.tck_version, "0.5.0");
        assert_eq!(policy.version_policy, "exact");
    }

    #[test]
    fn test_unknown_policy_fails() {
        let policy = VersionPolicy {
            version_policy: "unknown".to_string(),
            ..Default::default()
        };
        // Unknown policy should produce a fail status
        let result = run(&create_test_config(), &policy).unwrap();
        assert_eq!(result.verdict, "NON-CONFORMANT");
        assert_eq!(result.checks[0].status, "fail");
        assert!(result.checks[0].message.contains("Unknown version policy"));
    }

    fn create_test_config() -> crate::config::Config {
        use crate::config::{ChecksConfig, Config, DistConfig, PathsConfig};
        use std::path::PathBuf;

        Config {
            dist: DistConfig {
                name: "test".to_string(),
                version: "1.0".to_string(),
                platform_version: "0.9.0".to_string(),
                arch: "x86_64-linux".to_string(),
                profile: "full".to_string(),
                paths: PathsConfig {
                    sbom_file: PathBuf::from("test.json"),
                    headers_dir: None,
                    libs_dir: None,
                },
            },
            checks: ChecksConfig::default(),
        }
    }
}
