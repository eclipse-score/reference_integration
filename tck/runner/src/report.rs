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
//! Report generation

use serde::{Deserialize, Serialize};
use std::path::Path;

use crate::config::Config;

/// Full TCK report
#[derive(Debug, Serialize)]
pub struct Report {
    pub tck_version: String,
    pub platform_version: String,
    pub dist_name: String,
    pub dist_version: String,
    pub dist_arch: String,
    pub verdict: String,
    pub checks: Vec<CheckReport>,
}

/// Per-check-family report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckReport {
    pub family: String,
    pub verdict: String,
    pub checks: Vec<CheckResult>,
}

/// Individual check result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CheckResult {
    pub id: String,
    pub status: String,
    pub severity: String,
    pub message: String,
    pub details: Vec<serde_json::Value>,
}

impl Report {
    pub fn new(config: &Config) -> Self {
        Self {
            tck_version: env!("CARGO_PKG_VERSION").to_string(),
            platform_version: "0.9.0".to_string(),
            dist_name: config.dist.name.clone(),
            dist_version: config.dist.version.clone(),
            dist_arch: config.dist.arch.clone(),
            verdict: "CONFORMANT".to_string(),
            checks: Vec::new(),
        }
    }

    pub fn add_check(&mut self, check: CheckReport) {
        // Update overall verdict
        if check.verdict == "NON-CONFORMANT" {
            self.verdict = "NON-CONFORMANT".to_string();
        } else if check.verdict == "CONFORMANT-WITH-WARNINGS" && self.verdict != "NON-CONFORMANT" {
            self.verdict = "CONFORMANT-WITH-WARNINGS".to_string();
        }

        self.checks.push(check);
    }

    pub fn write_json(&self, path: &Path) -> anyhow::Result<()> {
        let content = serde_json::to_string_pretty(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    pub fn write_markdown(&self, path: &Path) -> anyhow::Result<()> {
        let mut lines = vec![
            format!("# s-core TCK Compatibility Report"),
            String::new(),
            format!(
                "**Distribution**: {} v{} (`{}`)",
                self.dist_name, self.dist_version, self.dist_arch
            ),
            format!("**TCK Version**: {}", self.tck_version),
            format!("**Platform Version**: {}", self.platform_version),
            String::new(),
            format!("## Verdict: **{}**", self.verdict),
            String::new(),
        ];

        for check in &self.checks {
            lines.push(format!(
                "### {} Check - {}",
                check.family.to_uppercase(),
                check.verdict
            ));
            lines.push(String::new());

            for result in &check.checks {
                let icon = match result.status.as_str() {
                    "pass" => "✅",
                    "fail" => "❌",
                    "warn" => "⚠️",
                    _ => "⏭️",
                };
                lines.push(format!("- {} **{}**: {}", icon, result.id, result.message));

                for detail in &result.details {
                    lines.push(format!(
                        "  - `{}`",
                        serde_json::to_string(detail).unwrap_or_default()
                    ));
                }
            }
            lines.push(String::new());
        }

        std::fs::write(path, lines.join("\n"))?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::{ChecksConfig, Config, DistConfig, PathsConfig};
    use std::path::PathBuf;
    use tempfile::tempdir;

    fn make_test_config() -> Config {
        Config {
            dist: DistConfig {
                name: "test-dist".to_string(),
                version: "1.0.0".to_string(),
                arch: "x86_64-linux".to_string(),
                profile: "full".to_string(),
                platform_version: "0.9.0".to_string(),
                paths: PathsConfig {
                    sbom_file: PathBuf::from("./sbom.json"),
                    headers_dir: None,
                    libs_dir: None,
                },
            },
            checks: ChecksConfig::default(),
        }
    }

    #[test]
    fn test_report_new() {
        let config = make_test_config();
        let report = Report::new(&config);
        assert_eq!(report.dist_name, "test-dist");
        assert_eq!(report.verdict, "CONFORMANT");
        assert!(report.checks.is_empty());
    }

    #[test]
    fn test_add_check_conformant() {
        let config = make_test_config();
        let mut report = Report::new(&config);

        report.add_check(CheckReport {
            family: "sbom".to_string(),
            verdict: "CONFORMANT".to_string(),
            checks: vec![],
        });

        assert_eq!(report.verdict, "CONFORMANT");
        assert_eq!(report.checks.len(), 1);
    }

    #[test]
    fn test_add_check_non_conformant() {
        let config = make_test_config();
        let mut report = Report::new(&config);

        report.add_check(CheckReport {
            family: "sbom".to_string(),
            verdict: "NON-CONFORMANT".to_string(),
            checks: vec![],
        });

        assert_eq!(report.verdict, "NON-CONFORMANT");
    }

    #[test]
    fn test_add_check_warnings() {
        let config = make_test_config();
        let mut report = Report::new(&config);

        report.add_check(CheckReport {
            family: "runtime".to_string(),
            verdict: "CONFORMANT-WITH-WARNINGS".to_string(),
            checks: vec![],
        });

        assert_eq!(report.verdict, "CONFORMANT-WITH-WARNINGS");
    }

    #[test]
    fn test_write_json() {
        let dir = tempdir().unwrap();
        let config = make_test_config();
        let report = Report::new(&config);

        let path = dir.path().join("report.json");
        report.write_json(&path).unwrap();

        assert!(path.exists());
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("test-dist"));
    }

    #[test]
    fn test_write_markdown() {
        let dir = tempdir().unwrap();
        let config = make_test_config();
        let mut report = Report::new(&config);

        report.add_check(CheckReport {
            family: "version".to_string(),
            verdict: "CONFORMANT".to_string(),
            checks: vec![CheckResult {
                id: "version.compatibility".to_string(),
                status: "pass".to_string(),
                severity: "required".to_string(),
                message: "Version compatible".to_string(),
                details: vec![],
            }],
        });

        let path = dir.path().join("summary.md");
        report.write_markdown(&path).unwrap();

        assert!(path.exists());
        let content = std::fs::read_to_string(&path).unwrap();
        assert!(content.contains("test-dist"));
        assert!(content.contains("VERSION"));
        assert!(content.contains("✅"));
    }
}
