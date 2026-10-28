//! SBOM comparison check

use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::collections::{HashMap, HashSet};

use crate::config::Config;
use crate::report::{CheckReport, CheckResult};

/// SPDX document structure (minimal)
#[derive(Debug, Deserialize)]
struct SpdxDocument {
    #[serde(default)]
    packages: Vec<SpdxPackage>,
    #[serde(default)]
    name: String,
}

#[derive(Debug, Deserialize)]
struct SpdxPackage {
    name: String,
    #[serde(default)]
    versionInfo: Option<String>,
    #[serde(default)]
    licenseConcluded: Option<String>,
    #[serde(default)]
    supplier: Option<String>,
}

/// Run the SBOM check
pub fn run(config: &Config, _report_dir: &Path) -> Result<CheckReport> {
    // Look for golden SBOM relative to current directory or in standard locations
    let golden_candidates = [
        PathBuf::from("tck/reference/sbom.spdx.json"),
        PathBuf::from("reference/sbom.spdx.json"),
    ];
    
    let golden_path = golden_candidates
        .iter()
        .find(|p| p.exists())
        .cloned()
        .unwrap_or_else(|| PathBuf::from("tck/reference/sbom.spdx.json"));

    let dist_path = &config.dist.paths.sbom_file;

    // Load both SBOMs
    let golden = load_spdx(&golden_path)?;
    let dist = load_spdx(dist_path)?;

    let mut checks = Vec::new();

    // Required modules from known_good.json
    let required_modules: HashSet<&str> = [
        "score_baselibs",
        "score_communication",
        "score_persistency",
        "score_kyron",
        "score_lifecycle",
        "score_logging",
        "score_time",
    ].iter().cloned().collect();

    // Extract package names (lowercase for matching)
    let golden_packages: HashMap<String, &SpdxPackage> = golden.packages
        .iter()
        .map(|p| (p.name.to_lowercase(), p))
        .collect();

    let dist_packages: HashMap<String, &SpdxPackage> = dist.packages
        .iter()
        .map(|p| (p.name.to_lowercase(), p))
        .collect();

    // Check 1: Required components present
    let missing: Vec<String> = required_modules
        .iter()
        .filter(|m| !dist_packages.contains_key(&m.to_lowercase()))
        .map(|s| s.to_string())
        .collect();

    checks.push(if missing.is_empty() {
        CheckResult {
            id: "sbom.required_components".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("All {} required components present", required_modules.len()),
            details: required_modules.iter().map(|m| serde_json::json!({"module": m, "found": true})).collect(),
        }
    } else {
        CheckResult {
            id: "sbom.required_components".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!("Missing {} required component(s)", missing.len()),
            details: missing.iter().map(|m| serde_json::json!({"module": m})).collect(),
        }
    });

    // Check 2: License policy
    let allowed_licenses: HashSet<&str> = [
        "Apache-2.0",
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "CC0-1.0",
        "ISC",
        "Zlib",
        "BSL-1.0",
        "NOASSERTION",
    ].iter().cloned().collect();

    let mut violations = Vec::new();
    for (name, pkg) in &dist_packages {
        let license = pkg.licenseConcluded.as_deref().unwrap_or("NOASSERTION");
        if !allowed_licenses.contains(license) && !license.contains("OR") {
            violations.push(serde_json::json!({
                "component": name,
                "license": license,
            }));
        }
    }

    checks.push(if violations.is_empty() {
        CheckResult {
            id: "sbom.license_policy".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: "All licenses comply with policy".to_string(),
            details: vec![],
        }
    } else {
        CheckResult {
            id: "sbom.license_policy".to_string(),
            status: "warn".to_string(),
            severity: "required".to_string(),
            message: format!("Found {} license policy violation(s)", violations.len()),
            details: violations.into_iter().take(20).collect(),
        }
    });

    // Check 3: Drift from golden (informational)
    let mut drift = Vec::new();
    
    // Additions (in dist but not golden)
    for name in dist_packages.keys() {
        if !golden_packages.contains_key(name) {
            drift.push(serde_json::json!({
                "component": name,
                "type": "addition",
            }));
        }
    }

    checks.push(if drift.is_empty() {
        CheckResult {
            id: "sbom.drift".to_string(),
            status: "pass".to_string(),
            severity: "informational".to_string(),
            message: "No drift from golden reference".to_string(),
            details: vec![],
        }
    } else {
        CheckResult {
            id: "sbom.drift".to_string(),
            status: "warn".to_string(),
            severity: "informational".to_string(),
            message: format!("Found {} drift item(s) from golden", drift.len()),
            details: drift.into_iter().take(50).collect(),
        }
    });

    // Compute verdict
    let verdict = if checks.iter().any(|c| c.status == "fail" && c.severity == "required") {
        "NON-CONFORMANT"
    } else if checks.iter().any(|c| c.status == "warn") {
        "CONFORMANT-WITH-WARNINGS"
    } else {
        "CONFORMANT"
    };

    Ok(CheckReport {
        family: "sbom".to_string(),
        verdict: verdict.to_string(),
        checks,
    })
}

fn load_spdx(path: &Path) -> Result<SpdxDocument> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read SPDX file: {}", path.display()))?;
    
    let spdx: SpdxDocument = serde_json::from_str(&content)
        .with_context(|| "Failed to parse SPDX JSON")?;
    
    Ok(spdx)
}
