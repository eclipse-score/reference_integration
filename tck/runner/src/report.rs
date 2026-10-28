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
            format!("**Distribution**: {} v{} (`{}`)", self.dist_name, self.dist_version, self.dist_arch),
            format!("**TCK Version**: {}", self.tck_version),
            format!("**Platform Version**: {}", self.platform_version),
            String::new(),
            format!("## Verdict: **{}**", self.verdict),
            String::new(),
        ];

        for check in &self.checks {
            lines.push(format!("### {} Check - {}", check.family.to_uppercase(), check.verdict));
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
                    lines.push(format!("  - `{}`", serde_json::to_string(detail).unwrap_or_default()));
                }
            }
            lines.push(String::new());
        }

        std::fs::write(path, lines.join("\n"))?;
        Ok(())
    }
}
