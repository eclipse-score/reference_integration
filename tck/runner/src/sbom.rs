//! SBOM comparison check

use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::collections::{HashMap, HashSet};

use crate::config::Config;
use crate::report::{CheckReport, CheckResult};

/// SPDX document structure (minimal)
#[derive(Debug, Deserialize)]
pub struct SpdxDocument {
    #[serde(default)]
    pub packages: Vec<SpdxPackage>,
    #[serde(default)]
    pub name: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct SpdxPackage {
    pub name: String,
    #[serde(default)]
    pub versionInfo: Option<String>,
    #[serde(default)]
    pub licenseConcluded: Option<String>,
    #[serde(default)]
    pub supplier: Option<String>,
}

/// SBOM comparison checker
pub struct SBOMChecker {
    golden_sbom_path: PathBuf,
    golden_packages: HashMap<String, SpdxPackage>,
    required_modules: HashSet<String>,
    allowed_licenses: HashSet<String>,
    forbidden_components: HashSet<String>,
}

impl SBOMChecker {
    /// Create a new SBOM checker with the given configuration
    pub fn new(
        golden_sbom_path: PathBuf,
        required_modules: HashSet<String>,
        allowed_licenses: HashSet<String>,
        forbidden_components: HashSet<String>,
    ) -> Self {
        // Load golden SBOM
        let golden_packages = match load_spdx(&golden_sbom_path) {
            Ok(spdx) => extract_packages(&spdx),
            Err(_) => HashMap::new(),
        };

        // Default allowed licenses if not specified
        let allowed = if allowed_licenses.is_empty() {
            DEFAULT_ALLOWED_LICENSES.iter().map(|s| s.to_string()).collect()
        } else {
            allowed_licenses
        };

        Self {
            golden_sbom_path,
            golden_packages,
            required_modules,
            allowed_licenses: allowed,
            forbidden_components,
        }
    }

    /// Run the SBOM check against a distribution's SBOM
    pub fn check(&self, dist_sbom_path: &Path) -> CheckReport {
        let dist_result = load_spdx(dist_sbom_path);
        
        match dist_result {
            Ok(dist_spdx) => {
                let dist_packages = extract_packages(&dist_spdx);
                self.run_checks(&dist_packages)
            }
            Err(e) => {
                CheckReport {
                    family: "sbom".to_string(),
                    verdict: "NON-CONFORMANT".to_string(),
                    checks: vec![CheckResult {
                        id: "sbom.error".to_string(),
                        status: "fail".to_string(),
                        severity: "required".to_string(),
                        message: format!("Failed to load SBOM: {}", e),
                        details: vec![],
                    }],
                }
            }
        }
    }

    fn run_checks(&self, dist_packages: &HashMap<String, SpdxPackage>) -> CheckReport {
        let mut checks = Vec::new();

        // Check 1: Required components present
        checks.push(self.check_required_components(dist_packages));

        // Check 2: No forbidden components
        checks.push(self.check_forbidden_components(dist_packages));

        // Check 3: License policy
        checks.push(self.check_license_policy(dist_packages));

        // Check 4: Drift from golden
        checks.push(self.check_drift(dist_packages));

        // Compute verdict
        let verdict = if checks.iter().any(|c| c.status == "fail" && c.severity == "required") {
            "NON-CONFORMANT"
        } else if checks.iter().any(|c| c.status == "warn") {
            "CONFORMANT-WITH-WARNINGS"
        } else {
            "CONFORMANT"
        };

        CheckReport {
            family: "sbom".to_string(),
            verdict: verdict.to_string(),
            checks,
        }
    }

    fn check_required_components(&self, dist_packages: &HashMap<String, SpdxPackage>) -> CheckResult {
        let missing: Vec<String> = self.required_modules
            .iter()
            .filter(|m| !dist_packages.contains_key(&m.to_lowercase()))
            .cloned()
            .collect();

        if missing.is_empty() {
            CheckResult {
                id: "sbom.required_components".to_string(),
                status: "pass".to_string(),
                severity: "required".to_string(),
                message: format!("All {} required components present", self.required_modules.len()),
                details: self.required_modules.iter()
                    .map(|m| serde_json::json!({"module": m, "found": true}))
                    .collect(),
            }
        } else {
            CheckResult {
                id: "sbom.required_components".to_string(),
                status: "fail".to_string(),
                severity: "required".to_string(),
                message: format!("Missing {} required component(s)", missing.len()),
                details: missing.iter()
                    .map(|m| serde_json::json!({"module": m}))
                    .collect(),
            }
        }
    }

    fn check_forbidden_components(&self, dist_packages: &HashMap<String, SpdxPackage>) -> CheckResult {
        let found: Vec<String> = self.forbidden_components
            .iter()
            .filter(|f| dist_packages.contains_key(&f.to_lowercase()))
            .cloned()
            .collect();

        if found.is_empty() {
            CheckResult {
                id: "sbom.forbidden_components".to_string(),
                status: "pass".to_string(),
                severity: "required".to_string(),
                message: "No forbidden components found".to_string(),
                details: vec![],
            }
        } else {
            CheckResult {
                id: "sbom.forbidden_components".to_string(),
                status: "fail".to_string(),
                severity: "required".to_string(),
                message: format!("Found {} forbidden component(s)", found.len()),
                details: found.iter()
                    .map(|c| serde_json::json!({"component": c}))
                    .collect(),
            }
        }
    }

    fn check_license_policy(&self, dist_packages: &HashMap<String, SpdxPackage>) -> CheckResult {
        let violations: Vec<serde_json::Value> = dist_packages
            .iter()
            .filter_map(|(name, pkg)| {
                let license = pkg.licenseConcluded.as_deref().unwrap_or("NOASSERTION");
                if !self.allowed_licenses.contains(license) && !license.contains("OR") {
                    Some(serde_json::json!({
                        "component": name,
                        "license": license,
                    }))
                } else {
                    None
                }
            })
            .take(20)
            .collect();

        if violations.is_empty() {
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
                details: violations,
            }
        }
    }

    fn check_drift(&self, dist_packages: &HashMap<String, SpdxPackage>) -> CheckResult {
        let drift: Vec<serde_json::Value> = dist_packages
            .keys()
            .filter(|name| !self.golden_packages.contains_key(*name))
            .map(|name| serde_json::json!({
                "component": name,
                "type": "addition",
            }))
            .take(50)
            .collect();

        if drift.is_empty() {
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
                details: drift,
            }
        }
    }
}

/// Default allowed licenses
const DEFAULT_ALLOWED_LICENSES: [&str; 9] = [
    "Apache-2.0",
    "MIT",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "CC0-1.0",
    "ISC",
    "Zlib",
    "BSL-1.0",
    "NOASSERTION",
];

/// Load an SPDX document from a JSON file
pub fn load_spdx(path: &Path) -> Result<SpdxDocument> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read SPDX file: {}", path.display()))?;
    
    let spdx: SpdxDocument = serde_json::from_str(&content)
        .with_context(|| "Failed to parse SPDX JSON")?;
    
    Ok(spdx)
}

/// Extract packages as a map keyed by lowercase name
pub fn extract_packages(spdx: &SpdxDocument) -> HashMap<String, SpdxPackage> {
    spdx.packages
        .iter()
        .map(|p| (p.name.to_lowercase(), p.clone()))
        .collect()
}

/// Run the SBOM check from a config (convenience function)
pub fn run(config: &Config, _report_dir: &Path) -> Result<CheckReport> {
    // Look for golden SBOM relative to current directory
    let golden_candidates = [
        PathBuf::from("tck/reference/sbom.spdx.json"),
        PathBuf::from("reference/sbom.spdx.json"),
    ];
    
    let golden_path = golden_candidates
        .iter()
        .find(|p| p.exists())
        .cloned()
        .unwrap_or_else(|| PathBuf::from("tck/reference/sbom.spdx.json"));

    let required_modules: HashSet<String> = [
        "score_baselibs",
        "score_communication",
        "score_persistency",
        "score_kyron",
        "score_lifecycle",
        "score_logging",
        "score_time",
    ].iter().map(|s| s.to_string()).collect();

    let checker = SBOMChecker::new(
        golden_path,
        required_modules,
        Default::default(),
        Default::default(),
    );

    Ok(checker.check(&config.dist.paths.sbom_file))
}
