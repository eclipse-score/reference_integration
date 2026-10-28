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

        /// Comma-separated list of checks to run (sbom,api,behavioral)
        #[arg(long, default_value = "sbom")]
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
    println!("Architecture: {}", config.dist.arch);
    println!("Checks: {}", checks);
    println!();

    // Create report directory
    std::fs::create_dir_all(&report_dir)?;

    let mut report = report::Report::new(&config);

    // Run SBOM check if enabled
    if checks.contains("sbom") {
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
    println!("SBOM path: {}", config.dist.paths.sbom_file.display());
    Ok(())
}
