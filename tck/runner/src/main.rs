//! s-core TCK - Test Compatibility Kit for SCORE Platform Distributions
//!
//! This binary verifies whether a SCORE distribution is compatible with
//! the main platform requirements: SBOM policy, API surface, and behavioral
//! conformance.

use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use std::path::PathBuf;

mod sbom;
mod report;
mod config;
mod version;
mod runtime;
mod toml;

/// s-core Test Compatibility Kit
#[derive(Parser)]
#[command(name = "score-tck")]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run TCK checks against a distribution
    Run {
        /// Path to distribution config file (tck.config.toml)
        #[arg(short, long)]
        config: PathBuf,

        /// Output directory for reports
        #[arg(short, long, default_value = "./tck-report")]
        report: PathBuf,

        /// Comma-separated list of checks to run (sbom,version,runtime)
        #[arg(long)]
        checks: Option<String>,
    },

    /// Validate a distribution config file
    ValidateConfig {
        /// Path to distribution config file
        config: PathBuf,
    },

    /// Print TCK version information
    Version,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Run { config, report, checks } => {
            cmd_run(config, report, checks)?;
        }
        Commands::ValidateConfig { config } => {
            cmd_validate_config(config)?;
        }
        Commands::Version => {
            println!("s-core TCK v{}", env!("CARGO_PKG_VERSION"));
            println!("Platform: linux-x86_64");
        }
    }

    Ok(())
}

/// Execute TCK checks and produce a report
fn cmd_run(config_path: PathBuf, report_dir: PathBuf, checks: Option<String>) -> Result<()> {
    println!("s-core TCK v{}", env!("CARGO_PKG_VERSION"));
    println!();

    // Load distribution configuration
    let config = config::load(&config_path)?;
    println!("Distribution: {} v{}", config.dist.name, config.dist.version);
    println!("Platform version: {}", config.dist.platform_version);
    println!("Architecture: {}", config.dist.arch);
    let enabled_checks = select_checks(checks.as_deref(), &config)?;
    println!("Checks: {}", enabled_checks.join(","));
    println!();

    std::fs::create_dir_all(&report_dir)?;
    let mut report = report::Report::new(&config);
    let runtime_requirements = runtime::RuntimeRequirements::default();
    let policy_path = if enabled_checks.iter().any(|check| check == "sbom" || check == "version") {
        Some(resolve_reference_file("reference/policy/requirements.toml")?)
    } else {
        None
    };
    let version_policy = if enabled_checks.iter().any(|check| check == "version") {
        Some(version::load_policy(policy_path.as_deref().unwrap())?)
    } else {
        None
    };
    let sbom_policy = if enabled_checks.iter().any(|check| check == "sbom") {
        Some(sbom::SbomPolicy::load(policy_path.as_deref().unwrap())?)
    } else {
        None
    };
    let golden_sbom = if sbom_policy.is_some() {
        Some(resolve_reference_file("reference/sbom.spdx.json")?)
    } else {
        None
    };

    // Run SBOM check if enabled
    if sbom_policy.is_some() {
        println!("Running SBOM check...");
        match sbom::run(&config, golden_sbom.as_deref().unwrap(), sbom_policy.unwrap()) {
            Ok(sbom_report) => {
                println!("  SBOM verdict: {}", sbom_report.verdict);
                report.add_check(sbom_report);
            }
            Err(e) => {
                println!("  Error: {}", e);
                report.add_check(report::CheckReport {
                    family: "sbom".to_string(),
                    verdict: "NON-CONFORMANT".to_string(),
                    checks: vec![report::CheckResult {
                        id: "sbom.error".to_string(),
                        status: "fail".to_string(),
                        severity: "required".to_string(),
                        message: e.to_string(),
                        details: vec![],
                    }],
                });
            }
        }
    }

    // Run version check if enabled
    if let Some(version_policy) = version_policy {
        println!("Running version check...");
        match version::run(&config, &version_policy) {
            Ok(version_report) => {
                println!("  Version verdict: {}", version_report.verdict);
                report.add_check(version_report);
            }
            Err(e) => {
                println!("  Error: {}", e);
                report.add_check(report::CheckReport {
                    family: "version".to_string(),
                    verdict: "NON-CONFORMANT".to_string(),
                    checks: vec![report::CheckResult {
                        id: "version.error".to_string(),
                        status: "fail".to_string(),
                        severity: "required".to_string(),
                        message: e.to_string(),
                        details: vec![],
                    }],
                });
            }
        }
    }

    // Run runtime check if enabled
    if enabled_checks.iter().any(|check| check == "runtime") {
        println!("Running runtime check...");
        match runtime::run(&config, &runtime_requirements) {
            Ok(runtime_report) => {
                println!("  Runtime verdict: {}", runtime_report.verdict);
                report.add_check(runtime_report);
            }
            Err(e) => {
                println!("  Error: {}", e);
                report.add_check(report::CheckReport {
                    family: "runtime".to_string(),
                    verdict: "NON-CONFORMANT".to_string(),
                    checks: vec![report::CheckResult {
                        id: "runtime.error".to_string(),
                        status: "fail".to_string(),
                        severity: "required".to_string(),
                        message: e.to_string(),
                        details: vec![],
                    }],
                });
            }
        }
    }

    // Write reports
    let json_path = report_dir.join("report.json");
    let md_path = report_dir.join("summary.md");
    report.write_json(&json_path)?;
    report.write_markdown(&md_path)?;

    println!();
    println!("Report written to: {}/", report_dir.display());
    println!("Overall verdict: {}", report.verdict);

    if report.verdict == "NON-CONFORMANT" {
        std::process::exit(1);
    }

    Ok(())
}

fn select_checks(explicit: Option<&str>, config: &config::Config) -> Result<Vec<String>> {
    let checks = match explicit {
        Some(checks) => checks.split(',').map(str::trim).map(str::to_string).collect(),
        None if !config.checks.enabled.is_empty() => config.checks.enabled.clone(),
        None if config.dist.profile == "minimal" => vec!["sbom".to_string()],
        None => vec!["sbom".to_string(), "version".to_string(), "runtime".to_string()],
    };
    if checks.is_empty() || checks.iter().any(String::is_empty) {
        bail!("No checks specified. Known checks are: sbom, version, runtime");
    }
    let unknown: Vec<_> = checks
        .iter()
        .filter(|check| !["sbom", "version", "runtime"].contains(&check.as_str()))
        .collect();
    if !unknown.is_empty() {
        bail!(
            "Unknown or unsupported check(s): {}. Known checks are: sbom, version, runtime",
            unknown.iter().map(|check| check.as_str()).collect::<Vec<_>>().join(", ")
        );
    }
    Ok(checks)
}

fn resolve_reference_file(relative_path: &str) -> Result<PathBuf> {
    let executable = std::env::current_exe().context("Failed to locate the TCK executable")?;
    let executable_directory = executable.parent().context("TCK executable has no parent directory")?;
    let current_directory = std::env::current_dir().context("Failed to determine current directory")?;
    let candidates = [
        executable_directory.join("../").join(relative_path),
        executable_directory.join(relative_path),
        current_directory.join("tck").join(relative_path),
        current_directory.join(relative_path),
    ];
    candidates
        .into_iter()
        .map(|path| path.canonicalize().unwrap_or(path))
        .find(|path| path.is_file())
        .with_context(|| format!("Could not find packaged reference file '{}'", relative_path))
}

/// Validate a distribution config file
fn cmd_validate_config(config_path: PathBuf) -> Result<()> {
    let config = config::load(&config_path)?;
    println!("Config valid for distribution: {} v{}", config.dist.name, config.dist.version);
    println!("Platform version: {}", config.dist.platform_version);
    println!("SBOM path: {}", config.dist.paths.sbom_file.display());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use config::{ChecksConfig, DistConfig, PathsConfig};

    fn config(profile: &str, enabled: Vec<&str>) -> config::Config {
        config::Config {
            dist: DistConfig {
                name: "test".to_string(),
                version: "1".to_string(),
                arch: "x86_64-linux".to_string(),
                profile: profile.to_string(),
                platform_version: "0.9.0".to_string(),
                paths: PathsConfig {
                    sbom_file: PathBuf::from("sbom.json"),
                    headers_dir: None,
                    libs_dir: None,
                },
            },
            checks: ChecksConfig {
                enabled: enabled.into_iter().map(str::to_string).collect(),
            },
        }
    }

    #[test]
    fn configured_checks_and_minimal_profile_are_used() {
        assert_eq!(
            select_checks(None, &config("full", vec!["sbom"])).unwrap(),
            vec!["sbom"]
        );
        assert_eq!(
            select_checks(None, &config("minimal", vec![])).unwrap(),
            vec!["sbom"]
        );
        assert_eq!(
            select_checks(Some("runtime"), &config("minimal", vec!["sbom"])).unwrap(),
            vec!["runtime"]
        );
    }

    #[test]
    fn empty_or_unsupported_checks_are_rejected() {
        assert!(select_checks(Some(""), &config("full", vec![])).is_err());
        assert!(select_checks(Some("sbom,,version"), &config("full", vec![])).is_err());
        assert!(select_checks(Some("sbmo"), &config("full", vec![])).is_err());
        assert!(select_checks(Some("behavioral"), &config("full", vec![])).is_err());
    }
}
