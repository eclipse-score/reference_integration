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
//! SBOM comparison check

use anyhow::{bail, Context, Result};
use serde::Deserialize;
use std::collections::HashSet;
use std::path::{Path, PathBuf};

use crate::config::Config;
use crate::report::{CheckReport, CheckResult};

#[derive(Debug, Deserialize)]
pub struct SpdxDocument {
    #[serde(rename = "spdxVersion")]
    spdx_version: Option<String>,
    #[serde(rename = "dataLicense")]
    data_license: Option<String>,
    #[serde(rename = "SPDXID")]
    spdx_id: Option<String>,
    name: Option<String>,
    #[serde(rename = "documentNamespace")]
    document_namespace: Option<String>,
    #[serde(rename = "creationInfo")]
    creation_info: Option<SpdxCreationInfo>,
    #[serde(default)]
    pub packages: Vec<SpdxPackage>,
    #[serde(default)]
    relationships: Vec<SpdxRelationship>,
}

#[derive(Debug, Deserialize)]
struct SpdxCreationInfo {
    created: Option<String>,
    creators: Option<Vec<String>>,
}

#[derive(Debug, Deserialize)]
struct SpdxRelationship {
    #[serde(rename = "spdxElementId")]
    spdx_element_id: String,
    #[serde(rename = "relationshipType")]
    relationship_type: String,
    #[serde(rename = "relatedSpdxElement")]
    related_spdx_element: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct SpdxPackage {
    #[serde(rename = "SPDXID")]
    spdx_id: Option<String>,
    pub name: String,
    #[serde(default)]
    #[serde(rename = "versionInfo")]
    pub version_info: Option<String>,
    #[serde(default)]
    #[serde(rename = "licenseConcluded")]
    pub license_concluded: Option<String>,
    #[serde(default)]
    pub supplier: Option<String>,
    #[serde(default)]
    checksums: Vec<SpdxChecksum>,
}

#[derive(Debug, Deserialize, Clone, Eq, PartialEq)]
struct SpdxChecksum {
    algorithm: String,
    #[serde(rename = "checksumValue")]
    checksum_value: String,
}

#[derive(Debug)]
pub struct SbomPolicy {
    required_modules: HashSet<String>,
    allowed_licenses: HashSet<String>,
    forbidden_components: HashSet<String>,
}

impl SbomPolicy {
    pub fn load(path: &Path) -> Result<Self> {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read SBOM policy: {}", path.display()))?;
        let tables = crate::toml::parse(&content)
            .with_context(|| format!("Failed to parse SBOM policy: {}", path.display()))?;

        let entries = |name: &str| {
            tables
                .get(name)
                .with_context(|| format!("Missing [{}] in SBOM policy", name))
        };
        let required_modules = entries("sbom.required_components")?
            .keys()
            .map(|name| name.to_lowercase())
            .collect();
        let allowed_licenses = entries("sbom.allowed_licenses")?
            .iter()
            .filter_map(
                |(name, value)| match crate::toml::inline_bool(value, "approved") {
                    Ok(Some(true)) => Some(Ok(Some(name.clone()))),
                    Ok(Some(false)) => None,
                    Ok(None) => Some(Err(anyhow::anyhow!(
                        "Missing 'approved' flag for license '{}'",
                        name
                    ))),
                    Err(error) => Some(Err(error)),
                },
            )
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .flatten()
            .collect();
        let forbidden_components = entries("sbom.forbidden_components")?
            .keys()
            .filter(|name| name.as_str() != "_placeholder")
            .map(|name| name.to_lowercase())
            .collect();

        Ok(Self {
            required_modules,
            allowed_licenses,
            forbidden_components,
        })
    }
}

/// SBOM comparison checker
pub struct SBOMChecker {
    golden_packages: Vec<SpdxPackage>,
    policy: SbomPolicy,
}

impl SBOMChecker {
    pub fn new(golden_sbom_path: PathBuf, policy: SbomPolicy) -> Result<Self> {
        let golden = load_spdx(&golden_sbom_path).with_context(|| {
            format!("Failed to load golden SBOM: {}", golden_sbom_path.display())
        })?;
        Ok(Self {
            golden_packages: extract_packages(&golden),
            policy,
        })
    }

    /// Run the SBOM check against a distribution's SBOM
    pub fn check(&self, dist_sbom_path: &Path) -> CheckReport {
        match load_spdx(dist_sbom_path) {
            Ok(document) => self.run_checks(&extract_packages(&document)),
            Err(error) => CheckReport {
                family: "sbom".to_string(),
                verdict: "NON-CONFORMANT".to_string(),
                checks: vec![CheckResult {
                    id: "sbom.error".to_string(),
                    status: "fail".to_string(),
                    severity: "required".to_string(),
                    message: format!("Failed to load SBOM: {}", error),
                    details: vec![],
                }],
            },
        }
    }

    fn run_checks(&self, packages: &[SpdxPackage]) -> CheckReport {
        let checks = vec![
            self.check_required_components(packages),
            self.check_forbidden_components(packages),
            self.check_license_policy(packages),
            self.check_drift(packages),
        ];
        let verdict = if checks
            .iter()
            .any(|check| check.status == "fail" && check.severity == "required")
        {
            "NON-CONFORMANT"
        } else if checks.iter().any(|check| check.status == "warn") {
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

    fn check_required_components(&self, packages: &[SpdxPackage]) -> CheckResult {
        let missing: Vec<_> = self
            .policy
            .required_modules
            .iter()
            .filter(|required| {
                !packages
                    .iter()
                    .any(|package| package.name.eq_ignore_ascii_case(required))
            })
            .cloned()
            .collect();
        if missing.is_empty() {
            CheckResult {
                id: "sbom.required_components".to_string(),
                status: "pass".to_string(),
                severity: "required".to_string(),
                message: format!(
                    "All {} required components present",
                    self.policy.required_modules.len()
                ),
                details: self
                    .policy
                    .required_modules
                    .iter()
                    .map(|module| serde_json::json!({"module": module, "found": true}))
                    .collect(),
            }
        } else {
            CheckResult {
                id: "sbom.required_components".to_string(),
                status: "fail".to_string(),
                severity: "required".to_string(),
                message: format!("Missing {} required component(s)", missing.len()),
                details: missing
                    .iter()
                    .map(|module| serde_json::json!({"module": module}))
                    .collect(),
            }
        }
    }

    fn check_forbidden_components(&self, packages: &[SpdxPackage]) -> CheckResult {
        let found: Vec<_> = self
            .policy
            .forbidden_components
            .iter()
            .filter(|forbidden| {
                packages
                    .iter()
                    .any(|package| package.name.eq_ignore_ascii_case(forbidden))
            })
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
                details: found
                    .iter()
                    .map(|component| serde_json::json!({"component": component}))
                    .collect(),
            }
        }
    }

    fn check_license_policy(&self, packages: &[SpdxPackage]) -> CheckResult {
        let violations: Vec<_> = packages
            .iter()
            .filter_map(|package| {
                let license = package
                    .license_concluded
                    .as_deref()
                    .unwrap_or("NOASSERTION");
                (!license_expression_is_allowed(license, &self.policy.allowed_licenses))
                    .then(|| serde_json::json!({"component": package.name, "license": license}))
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
                status: "fail".to_string(),
                severity: "required".to_string(),
                message: format!("Found {} license policy violation(s)", violations.len()),
                details: violations,
            }
        }
    }

    fn check_drift(&self, packages: &[SpdxPackage]) -> CheckResult {
        let mut matched = vec![false; self.golden_packages.len()];
        let mut drift = Vec::new();
        for package in packages {
            let matching = self
                .golden_packages
                .iter()
                .enumerate()
                .filter(|(index, golden)| {
                    !matched[*index] && golden.name.eq_ignore_ascii_case(&package.name)
                })
                .min_by_key(|(_, golden)| {
                    golden.version_info != package.version_info
                        || normalized_checksums(&golden.checksums)
                            != normalized_checksums(&package.checksums)
                });
            if let Some((index, golden)) = matching {
                matched[index] = true;
                let version_changed = golden.version_info != package.version_info;
                let checksum_changed = normalized_checksums(&golden.checksums)
                    != normalized_checksums(&package.checksums);
                if version_changed || checksum_changed {
                    drift.push(serde_json::json!({
                        "component": package.name,
                        "type": "change",
                        "golden_version": golden.version_info,
                        "distribution_version": package.version_info,
                        "checksum_changed": checksum_changed
                    }));
                }
            } else {
                drift.push(serde_json::json!({
                    "component": package.name,
                    "type": "addition"
                }));
            }
        }
        for (index, golden) in self.golden_packages.iter().enumerate() {
            if !matched[index] {
                drift.push(serde_json::json!({
                    "component": golden.name,
                    "type": "removal"
                }));
            }
        }
        drift.truncate(50);
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

fn normalized_checksums(checksums: &[SpdxChecksum]) -> Vec<(String, String)> {
    let mut checksums: Vec<_> = checksums
        .iter()
        .map(|checksum| {
            (
                checksum.algorithm.to_ascii_uppercase(),
                checksum.checksum_value.to_ascii_lowercase(),
            )
        })
        .collect();
    checksums.sort();
    checksums
}

fn license_expression_is_allowed(expression: &str, allowed: &HashSet<String>) -> bool {
    let mut tokens = Vec::new();
    let mut token = String::new();
    for character in expression.chars() {
        match character {
            '(' | ')' => {
                if !token.is_empty() {
                    tokens.push(std::mem::take(&mut token));
                }
                tokens.push(character.to_string());
            }
            character if character.is_whitespace() => {
                if !token.is_empty() {
                    tokens.push(std::mem::take(&mut token));
                }
            }
            _ => token.push(character),
        }
    }
    if !token.is_empty() {
        tokens.push(token);
    }
    let mut parser = LicenseExpressionParser {
        tokens: &tokens,
        position: 0,
        allowed,
    };
    parser.parse_or().unwrap_or(false) && parser.position == tokens.len()
}

struct LicenseExpressionParser<'a> {
    tokens: &'a [String],
    position: usize,
    allowed: &'a HashSet<String>,
}

impl LicenseExpressionParser<'_> {
    fn parse_or(&mut self) -> Option<bool> {
        let mut result = self.parse_and()?;
        while self.take("OR") {
            result = self.parse_and()? | result;
        }
        Some(result)
    }

    fn parse_and(&mut self) -> Option<bool> {
        let mut result = self.parse_primary()?;
        while self.take("AND") {
            result = self.parse_primary()? & result;
        }
        Some(result)
    }

    fn parse_primary(&mut self) -> Option<bool> {
        if self.take("(") {
            let result = self.parse_or()?;
            if !self.take(")") {
                return None;
            }
            return Some(result);
        }
        let license = self.tokens.get(self.position)?;
        if matches!(license.as_str(), "AND" | "OR" | "WITH" | ")") {
            return None;
        }
        self.position += 1;
        let allowed = self.allowed.contains(license);
        if self.take("WITH") {
            if self.tokens.get(self.position).is_none() {
                return None;
            }
            self.position += 1;
            return Some(false);
        }
        Some(allowed)
    }

    fn take(&mut self, token: &str) -> bool {
        if self.tokens.get(self.position).map(String::as_str) == Some(token) {
            self.position += 1;
            true
        } else {
            false
        }
    }
}

/// Load and validate an SPDX JSON document.
pub fn load_spdx(path: &Path) -> Result<SpdxDocument> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read SPDX file: {}", path.display()))?;
    let document: SpdxDocument = serde_json::from_str(&content)
        .with_context(|| format!("Failed to parse SPDX JSON: {}", path.display()))?;
    validate_spdx(&document)?;
    Ok(document)
}

fn validate_spdx(document: &SpdxDocument) -> Result<()> {
    if !document
        .spdx_version
        .as_deref()
        .is_some_and(valid_spdx_version)
        || document.data_license.as_deref() != Some("CC0-1.0")
        || document.spdx_id.as_deref() != Some("SPDXRef-DOCUMENT")
        || document.name.as_deref().is_none_or(str::is_empty)
        || document
            .document_namespace
            .as_deref()
            .is_none_or(str::is_empty)
    {
        bail!("SPDX document is missing required document metadata");
    }
    let creation = document
        .creation_info
        .as_ref()
        .context("SPDX document is missing creationInfo")?;
    if creation.created.as_deref().is_none_or(str::is_empty)
        || creation
            .creators
            .as_ref()
            .is_none_or(|creators| creators.is_empty())
    {
        bail!("SPDX document has incomplete creationInfo");
    }
    if document.packages.is_empty() {
        bail!("SPDX document contains no packages");
    }
    let mut package_ids = HashSet::new();
    for package in &document.packages {
        let id = package
            .spdx_id
            .as_deref()
            .filter(|id| valid_spdx_id(id))
            .context("SPDX package is missing a valid SPDXID")?;
        if !package_ids.insert(id) {
            bail!("SPDX document contains duplicate package SPDXID '{}'", id);
        }
    }
    let describes_root = document.relationships.iter().any(|relationship| {
        relationship.spdx_element_id == "SPDXRef-DOCUMENT"
            && relationship.relationship_type == "DESCRIBES"
            && package_ids.contains(relationship.related_spdx_element.as_str())
    });
    if !describes_root {
        bail!("SPDX document does not describe a root package");
    }
    Ok(())
}

fn valid_spdx_version(version: &str) -> bool {
    let Some(version) = version.strip_prefix("SPDX-") else {
        return false;
    };
    let mut parts = version.split('.');
    matches!(
        (parts.next(), parts.next(), parts.next()),
        (Some("2"), Some(minor), None)
            if !minor.is_empty()
                && !(minor.len() > 1 && minor.starts_with('0'))
                && minor.bytes().all(|byte| byte.is_ascii_digit())
    )
}

fn valid_spdx_id(id: &str) -> bool {
    let Some(suffix) = id.strip_prefix("SPDXRef-") else {
        return false;
    };
    !suffix.is_empty()
        && suffix.as_bytes()[0].is_ascii_alphanumeric()
        && suffix.as_bytes()[suffix.len() - 1].is_ascii_alphanumeric()
        && suffix
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'.'))
        && !suffix.ends_with('-')
}

pub fn extract_packages(document: &SpdxDocument) -> Vec<SpdxPackage> {
    document.packages.clone()
}

/// Run the SBOM check using the packaged reference SBOM and policy.
pub fn run(config: &Config, golden_path: &Path, policy: SbomPolicy) -> Result<CheckReport> {
    let checker = SBOMChecker::new(golden_path.to_path_buf(), policy)?;
    Ok(checker.check(&config.dist.paths.sbom_file))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn package(name: &str, version: &str, license: &str, checksum: &str) -> SpdxPackage {
        SpdxPackage {
            spdx_id: Some(format!("SPDXRef-{name}-{version}")),
            name: name.to_string(),
            version_info: Some(version.to_string()),
            license_concluded: Some(license.to_string()),
            supplier: None,
            checksums: vec![SpdxChecksum {
                algorithm: "SHA256".to_string(),
                checksum_value: checksum.to_string(),
            }],
        }
    }

    fn checker(packages: Vec<SpdxPackage>, allowed: &[&str]) -> SBOMChecker {
        SBOMChecker {
            golden_packages: packages,
            policy: SbomPolicy {
                required_modules: HashSet::new(),
                allowed_licenses: allowed.iter().map(|license| license.to_string()).collect(),
                forbidden_components: HashSet::new(),
            },
        }
    }

    #[test]
    fn license_expression_obeys_and_or_precedence() {
        let allowed = ["MIT", "BSD-3-Clause"]
            .iter()
            .map(|license| license.to_string())
            .collect();
        assert!(license_expression_is_allowed(
            "GPL-3.0-only OR MIT",
            &allowed
        ));
        assert!(!license_expression_is_allowed(
            "GPL-2.0-only OR GPL-3.0-only",
            &allowed
        ));
        assert!(!license_expression_is_allowed(
            "(MIT OR GPL-3.0-only) AND GPL-2.0-only",
            &allowed
        ));
        assert!(license_expression_is_allowed(
            "MIT AND BSD-3-Clause",
            &allowed
        ));
        assert!(!license_expression_is_allowed(
            "MIT WITH LLVM-exception",
            &allowed
        ));
    }

    #[test]
    fn packages_with_duplicate_names_are_all_checked_for_licenses() {
        let checker = checker(vec![], &["MIT"]);
        let report = checker.run_checks(&[
            package("duplicate", "1.0.0", "MIT", "one"),
            package("duplicate", "2.0.0", "GPL-3.0-only", "two"),
        ]);
        assert_eq!(report.checks[2].status, "fail");
        assert_eq!(report.checks[2].details.len(), 1);
    }

    #[test]
    fn drift_detects_versions_and_checksums() {
        let checker = checker(vec![package("component", "1.0.0", "MIT", "same")], &["MIT"]);
        let report = checker.run_checks(&[package("component", "2.0.0", "MIT", "changed")]);
        assert_eq!(report.checks[3].status, "warn");
        assert_eq!(report.checks[3].details[0]["type"], "change");
        assert_eq!(report.checks[3].details[0]["checksum_changed"], true);
    }

    #[test]
    fn golden_sbom_load_failure_is_propagated() {
        let policy = SbomPolicy {
            required_modules: HashSet::new(),
            allowed_licenses: HashSet::new(),
            forbidden_components: HashSet::new(),
        };
        assert!(SBOMChecker::new(PathBuf::from("missing-golden.json"), policy).is_err());
    }

    #[test]
    fn policy_uses_approved_licenses_and_component_tables() {
        let file = tempfile::NamedTempFile::new().unwrap();
        std::fs::write(
            file.path(),
            r#"
[sbom.required_components]
score_core = { description = "core", critical = true }

[sbom.allowed_licenses]
MIT = { category = "permissive", approved = true }
NOASSERTION = { category = "unknown", approved = false }

[sbom.forbidden_components]
blocked = { reason = "not allowed" }
"#,
        )
        .unwrap();
        let policy = SbomPolicy::load(file.path()).unwrap();
        assert!(policy.required_modules.contains("score_core"));
        assert!(policy.allowed_licenses.contains("MIT"));
        assert!(!policy.allowed_licenses.contains("NOASSERTION"));
        assert!(policy.forbidden_components.contains("blocked"));
    }

    #[test]
    fn malformed_or_incomplete_spdx_documents_are_rejected() {
        let malformed =
            serde_json::from_str::<SpdxDocument>(r#"{"packages":[{"name":"only-package"}]}"#)
                .unwrap();
        assert!(validate_spdx(&malformed).is_err());
        assert!(serde_json::from_str::<SpdxDocument>(r#"{"packages":[{}]}"#).is_err());
        assert!(!valid_spdx_version("SPDX-2.invalid"));
        assert!(!valid_spdx_version("SPDX-2.03"));
        assert!(!valid_spdx_id("SPDXRef-"));
        assert!(!valid_spdx_id("SPDXRef-root!"));
    }

    #[test]
    fn valid_spdx_document_requires_and_accepts_a_described_root_package() {
        let document: SpdxDocument = serde_json::from_str(
            r#"{
                "spdxVersion":"SPDX-2.3",
                "dataLicense":"CC0-1.0",
                "SPDXID":"SPDXRef-DOCUMENT",
                "name":"test",
                "documentNamespace":"https://example.test/sbom",
                "creationInfo":{"created":"2026-01-01T00:00:00Z","creators":["Tool: test"]},
                "packages":[{"SPDXID":"SPDXRef-root","name":"root"}],
                "relationships":[{
                    "spdxElementId":"SPDXRef-DOCUMENT",
                    "relationshipType":"DESCRIBES",
                    "relatedSpdxElement":"SPDXRef-root"
                }]
            }"#,
        )
        .unwrap();
        assert!(validate_spdx(&document).is_ok());
        let missing_root: SpdxDocument = serde_json::from_str(
            r#"{
                "spdxVersion":"SPDX-2.3",
                "dataLicense":"CC0-1.0",
                "SPDXID":"SPDXRef-DOCUMENT",
                "name":"test",
                "documentNamespace":"https://example.test/sbom",
                "creationInfo":{"created":"2026-01-01T00:00:00Z","creators":["Tool: test"]},
                "packages":[{"SPDXID":"SPDXRef-root","name":"root"}],
                "relationships":[]
            }"#,
        )
        .unwrap();
        assert!(validate_spdx(&missing_root).is_err());
    }
}
