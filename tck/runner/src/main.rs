//! s-core TCK - Test Compatibility Kit for SCORE Platform Distributions
//!
//! This binary verifies whether a SCORE distribution is compatible with
//! the main platform requirements: SBOM policy, API surface, and behavioral
//! conformance.

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;

mod sbom;
mod report;
mod config;
mod version;
mod runtime;

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

        /// Comma-separated list of checks to run (sbom,version,runtime,behavioral)
        #[arg(long, default_value = "sbom,version,runtime")]
        checks: String,
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
fn cmd_run(config_path: PathBuf, report_dir: PathBuf, checks: String) -> Result<()> {
    println!("s-core TCK v{}", env!("CARGO_PKG_VERSION"));
    println!();

    // Load distribution configuration
    let config = config::load(&config_path)?;
    println!("Distribution: {} v{}", config.dist.name, config.dist.version);
    println!("Platform version: {}", config.dist.platform_version);
    println!("Architecture: {}", config.dist.arch);
    println!("Checks: {}", checks);
    println!();

    // Create report directory
    std::fs::create_dir_all(&report_dir)?;

    let mut report = report::Report::new(&config);

    // Load version policy
    let policy_path = PathBuf::from("tck/reference/policy/requirements.toml");
    let version_policy = version::load_policy(&policy_path).unwrap_or_default();
    let runtime_requirements = runtime::RuntimeRequirements::default();

    // Check which checks are enabled
    let enabled_checks: Vec<&str> = checks.split(',').map(|s| s.trim()).collect();
    
    // Validate check names - reject unknown checks
    let known_checks = ["sbom", "version", "runtime"];
    let unknown_checks: Vec<&&str> = enabled_checks.iter()
        .filter(|c| !known_checks.contains(c))
        .collect();
    
    if !unknown_checks.is_empty() {
        anyhow::bail!(
            "Unknown check(s): {}. Known checks are: {}",
            unknown_checks.iter().map(|c| c.to_string()).collect::<Vec<_>>().join(", "),
            known_checks.join(", ")
        );
    }
    
    if enabled_checks.is_empty() {
        anyhow::bail!("No checks specified. Known checks are: {}", known_checks.join(", "));
    }

    // Run SBOM check if enabled
    if enabled_checks.contains(&"sbom") {
        println!("Running SBOM check...");
        match sbom::run(&config, &report_dir) {
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
    if enabled_checks.contains(&"version") {
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
    if enabled_checks.contains(&"runtime") {
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

/// Validate a distribution config file
fn cmd_validate_config(config_path: PathBuf) -> Result<()> {
    let config = config::load(&config_path)?;
    println!("Config valid for distribution: {} v{}", config.dist.name, config.dist.version);
    println!("Platform version: {}", config.dist.platform_version);
    println!("SBOM path: {}", config.dist.paths.sbom_file.display());
    Ok(())
}
