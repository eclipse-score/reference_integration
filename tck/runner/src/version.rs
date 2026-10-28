//! Version compatibility check

use anyhow::Result;
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
    if !policy_path.exists() {
        return Ok(VersionPolicy::default());
    }
    
    let content = std::fs::read_to_string(policy_path)?;
    parse_version_section(&content)
}

/// Parse [version] section from TOML content
fn parse_version_section(content: &str) -> Result<VersionPolicy> {
    let mut policy = VersionPolicy::default();
    
    for line in content.lines() {
        let line = line.trim();
        if line.starts_with('#') || line.is_empty() {
            continue;
        }
        
        if line.starts_with("platform_version") {
            policy.platform_version = extract_string_value(line);
        } else if line.starts_with("min_platform_version") {
            policy.min_platform_version = extract_string_value(line);
        } else if line.starts_with("tck_version") {
            policy.tck_version = extract_string_value(line);
        } else if line.starts_with("version_policy") {
            policy.version_policy = extract_string_value(line);
        }
    }
    
    Ok(policy)
}

fn extract_string_value(line: &str) -> String {
    if let Some(eq_pos) = line.find('=') {
        let value = line[eq_pos + 1..].trim();
        if (value.starts_with('"') && value.ends_with('"')) ||
           (value.starts_with("'") && value.ends_with("'")) {
            return value[1..value.len()-1].to_string();
        }
        return value.to_string();
    }
    String::new()
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
            status: "fail".to_string(),  // Unknown policy must fail, not warn
            severity: "required".to_string(),
            message: format!("Unknown version policy: '{}'. Must be 'exact', 'compatible', or 'any'", policy.version_policy),
            details: vec![],
        },
    };
    
    let verdict = if check.status == "fail" { "NON-CONFORMANT" } else { "CONFORMANT" };
    
    Ok(CheckReport {
        family: "version".to_string(),
        verdict: verdict.to_string(),
        checks: vec![check],
    })
}

fn check_exact(dist_version: &str, required_version: &str) -> CheckResult {
    if dist_version == required_version {
        CheckResult {
            id: "version.compatibility".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("Platform version {} matches required version", dist_version),
            details: vec![
                serde_json::json!({"dist_version": dist_version, "required_version": required_version})
            ],
        }
    } else {
        CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!("Platform version {} does not match required version {}", dist_version, required_version),
            details: vec![
                serde_json::json!({"dist_version": dist_version, "required_version": required_version})
            ],
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
            details: vec![
                serde_json::json!({"dist_version": dist_version, "min_version": min_version})
            ],
        },
        Ok(false) => CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!("Platform version {} is below minimum required version {}", dist_version, min_version),
            details: vec![
                serde_json::json!({"dist_version": dist_version, "min_version": min_version})
            ],
        },
        Err(e) => CheckResult {
            id: "version.compatibility".to_string(),
            status: "fail".to_string(),  // Parse errors must fail, not warn
            severity: "required".to_string(),
            message: format!("Invalid version format: {}", e),
            details: vec![
                serde_json::json!({"dist_version": dist_version, "min_version": min_version, "error": e})
            ],
        },
    }
}

/// Compare two semver-like version strings
/// Returns Ok(true) if v1 >= v2
/// 
/// Note: This is a simplified comparison. Proper semver comparison including
/// prerelease/build metadata should use a proper semver library.
fn compare_versions(v1: &str, v2: &str) -> Result<bool, String> {
    // Strip prerelease suffix for basic comparison (e.g., "0.9.0-rc.1" -> "0.9.0")
    // This treats prereleases as equal to their release version, which is conservative.
    // A proper semver library would compare prereleases correctly.
    let v1_base = v1.split('-').next().unwrap_or(v1);
    let v2_base = v2.split('-').next().unwrap_or(v2);
    
    let parts1: Vec<u32> = v1_base.split('.')
        .filter_map(|s| s.parse().ok())
        .collect();
    let parts2: Vec<u32> = v2_base.split('.')
        .filter_map(|s| s.parse().ok())
        .collect();
    
    if parts1.is_empty() || parts2.is_empty() {
        return Err(format!("Invalid version format: '{}' or '{}'", v1, v2));
    }
    
    // Compare major.minor.patch
    for i in 0..3 {
        let p1 = parts1.get(i).copied().unwrap_or(0);
        let p2 = parts2.get(i).copied().unwrap_or(0);
        
        if p1 > p2 {
            return Ok(true);
        } else if p1 < p2 {
            return Ok(false);
        }
    }
    
    Ok(true) // Equal versions
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
        assert_eq!(compare_versions("0.9", "0.9.0").unwrap(), true);
        assert_eq!(compare_versions("0.9.0", "0.9").unwrap(), true);
    }
    
    #[test]
    fn test_compare_versions_prerelease() {
        // Prerelease versions should be treated as their base version
        assert_eq!(compare_versions("0.9.0-rc.1", "0.9.0").unwrap(), true);
        assert_eq!(compare_versions("0.9.0", "0.9.0-rc.1").unwrap(), true);
    }
    
    #[test]
    fn test_compare_versions_invalid() {
        assert!(compare_versions("invalid", "0.9.0").is_err());
        assert!(compare_versions("0.9.0", "invalid").is_err());
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
platform_version = "1.2.3"
min_platform_version = "1.0.0"
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
        use crate::config::{Config, DistConfig, PathsConfig, ChecksConfig};
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
