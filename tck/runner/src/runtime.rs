//! Runtime compatibility check and test harness adapter
//!
//! This module ensures that the distribution's runtime environment is compatible
//! with the TCK's test execution requirements. It provides:
//! - Runtime version checking (toolchain, libraries)
//! - Test harness adapter configuration
//! - Execution environment validation
//!
//! Inspired by Jakarta TCK's porting package concept - vendors provide adapters
//! that tell the TCK how to execute tests in their environment.

use anyhow::{Result, Context};
use std::path::{Path, PathBuf};
use std::process::Command;

use crate::config::Config;
use crate::report::{CheckReport, CheckResult};

/// Runtime environment requirements
#[derive(Debug, Clone)]
pub struct RuntimeRequirements {
    /// Minimum toolchain version (e.g., "GCC 11", "Clang 14", "Rust 1.70")
    pub min_toolchain_version: String,
    
    /// Required runtime libraries
    pub required_libraries: Vec<String>,
    
    /// Required environment variables
    pub required_env_vars: Vec<String>,
    
    /// Target platform triplet
    pub target_triple: String,
}

impl Default for RuntimeRequirements {
    fn default() -> Self {
        Self {
            min_toolchain_version: "GCC 11+ or Clang 14+".to_string(),
            required_libraries: vec![
                "pthread".to_string(),
                "dl".to_string(),
            ],
            required_env_vars: vec![],
            target_triple: "x86_64-linux-gnu".to_string(),
        }
    }
}

/// Test harness adapter configuration
/// 
/// This is the SCORE equivalent of Jakarta's "porting package".
/// Vendors configure how the TCK should build and run tests against their distribution.
#[derive(Debug, Clone, Default)]
pub struct TestHarnessAdapter {
    /// Command to build tests for this distribution
    pub build_command: Option<String>,
    
    /// Command to run a test binary
    pub run_command: Option<String>,
    
    /// Working directory for test execution
    pub working_directory: Option<PathBuf>,
    
    /// Environment variables to set for test execution
    pub env_vars: Vec<(String, String)>,
    
    /// Timeout for test execution (seconds)
    pub timeout_seconds: u64,
    
    /// Path to the showcase CLI binary (for behavioral tests)
    pub showcase_cli_path: Option<PathBuf>,
    
    /// Showcase examples to run
    pub showcase_examples: Vec<String>,
}

impl TestHarnessAdapter {
    /// Create adapter from distribution config
    pub fn from_config(config: &Config) -> Self {
        Self {
            timeout_seconds: 300, // 5 minutes default
            showcase_examples: vec![
                "LoggingApp Demo".to_string(),
                "ComApiExample".to_string(),
            ],
            ..Default::default()
        }
    }
    
    /// Validate that the adapter is configured correctly for test execution
    pub fn validate(&self) -> Result<Vec<String>> {
        let mut warnings = Vec::new();
        
        if self.build_command.is_none() {
            warnings.push("No build_command configured - behavioral tests will be skipped".to_string());
        }
        
        if self.showcase_cli_path.is_none() {
            warnings.push("No showcase_cli_path configured - will attempt to discover".to_string());
        }
        
        Ok(warnings)
    }
    
    /// Execute a showcase example and return success/failure
    pub fn run_showcase(&self, example: &str) -> Result<ShowcaseResult> {
        let cli_path = match &self.showcase_cli_path {
            Some(p) => p.clone(),
            None => return Err(anyhow::anyhow!("Showcase CLI path not configured")),
        };
        
        if !cli_path.exists() {
            return Err(anyhow::anyhow!("Showcase CLI not found at {:?}", cli_path));
        }
        
        let output = Command::new(&cli_path)
            .arg("--examples")
            .arg(example)
            .output()
            .context("Failed to execute showcase CLI")?;
        
        let stdout = String::from_utf8_lossy(&output.stdout);
        let success = output.status.success() 
            && stdout.contains(&format!("Example '{}' finished successfully", example));
        
        Ok(ShowcaseResult {
            example: example.to_string(),
            success,
            exit_code: output.status.code().unwrap_or(-1),
            output: stdout.to_string(),
        })
    }
}

/// Result of running a showcase example
#[derive(Debug)]
pub struct ShowcaseResult {
    pub example: String,
    pub success: bool,
    pub exit_code: i32,
    pub output: String,
}

/// Run runtime compatibility check
pub fn run(config: &Config, requirements: &RuntimeRequirements) -> Result<CheckReport> {
    let mut checks = Vec::new();
    
    // Check 1: Architecture compatibility
    checks.push(check_architecture(config, &requirements.target_triple));
    
    // Check 2: Toolchain availability
    checks.push(check_toolchain(&requirements.min_toolchain_version));
    
    // Check 3: Required libraries
    checks.push(check_libraries(&requirements.required_libraries));
    
    // Check 4: Environment variables (if configured)
    if !requirements.required_env_vars.is_empty() {
        checks.push(check_env_vars(&requirements.required_env_vars));
    }
    
    // Compute verdict
    let verdict = if checks.iter().any(|c| c.status == "fail" && c.severity == "required") {
        "NON-CONFORMANT"
    } else if checks.iter().any(|c| c.status == "warn") {
        "CONFORMANT-WITH-WARNINGS"
    } else {
        "CONFORMANT"
    };
    
    Ok(CheckReport {
        family: "runtime".to_string(),
        verdict: verdict.to_string(),
        checks,
    })
}

fn check_architecture(config: &Config, expected_triple: &str) -> CheckResult {
    let arch = &config.dist.arch;
    
    // Map arch names to triples
    let expected = match arch.as_str() {
        "x86_64-linux" => "x86_64-linux-gnu",
        "aarch64-linux" => "aarch64-linux-gnu",
        "qnx-aarch64" => "aarch64-qnx",
        _ => arch,
    };
    
    // For now, just check the arch is recognized
    let known_archs = ["x86_64-linux", "aarch64-linux", "qnx-aarch64"];
    if known_archs.contains(&arch.as_str()) {
        CheckResult {
            id: "runtime.architecture".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("Target architecture '{}' is supported", arch),
            details: vec![serde_json::json!({"arch": arch, "triple": expected})],
        }
    } else {
        CheckResult {
            id: "runtime.architecture".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!("Unknown target architecture '{}'", arch),
            details: vec![serde_json::json!({"known_archs": known_archs})],
        }
    }
}

fn check_toolchain(min_version: &str) -> CheckResult {
    // Try to detect compiler
    let gcc_version = Command::new("gcc").arg("--version").output().ok();
    let clang_version = Command::new("clang").arg("--version").output().ok();
    
    let (compiler, version) = if let Some(output) = gcc_version {
        if output.status.success() {
            let v = String::from_utf8_lossy(&output.stdout).lines().next()
                .unwrap_or("unknown")
                .to_string();
            ("GCC", v)
        } else {
            ("unknown", "not found".to_string())
        }
    } else if let Some(output) = clang_version {
        if output.status.success() {
            let v = String::from_utf8_lossy(&output.stdout).lines().next()
                .unwrap_or("unknown")
                .to_string();
            ("Clang", v)
        } else {
            ("unknown", "not found".to_string())
        }
    } else {
        ("unknown", "not found".to_string())
    };
    
    if compiler != "unknown" {
        CheckResult {
            id: "runtime.toolchain".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("Detected {}: {}", compiler, version.split_whitespace().take(3).collect::<Vec<_>>().join(" ")),
            details: vec![
                serde_json::json!({"compiler": compiler, "version": version, "min_required": min_version})
            ],
        }
    } else {
        CheckResult {
            id: "runtime.toolchain".to_string(),
            status: "warn".to_string(),
            severity: "required".to_string(),
            message: "Could not detect C/C++ toolchain".to_string(),
            details: vec![serde_json::json!({"min_required": min_version})],
        }
    }
}

fn check_libraries(required: &[String]) -> CheckResult {
    // Check for required libraries by trying to link against them
    let mut missing = Vec::new();
    
    for lib in required {
        // Simple check - see if the library exists in standard locations
        let found = ["/lib", "/usr/lib", "/usr/local/lib"].iter().any(|dir| {
            Path::new(dir).join(format!("lib{}.so", lib)).exists() ||
            Path::new(dir).join(format!("lib{}.a", lib)).exists()
        });
        
        if !found {
            missing.push(lib.clone());
        }
    }
    
    if missing.is_empty() {
        CheckResult {
            id: "runtime.libraries".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: format!("All {} required libraries found", required.len()),
            details: required.iter().map(|l| serde_json::json!({"library": l, "found": true})).collect(),
        }
    } else {
        CheckResult {
            id: "runtime.libraries".to_string(),
            status: "warn".to_string(),
            severity: "required".to_string(),
            message: format!("{} required libraries not found: {}", missing.len(), missing.join(", ")),
            details: missing.iter().map(|l| serde_json::json!({"library": l, "found": false})).collect(),
        }
    }
}

fn check_env_vars(required: &[String]) -> CheckResult {
    let missing: Vec<String> = required.iter()
        .filter(|v| std::env::var(v).is_err())
        .cloned()
        .collect();
    
    if missing.is_empty() {
        CheckResult {
            id: "runtime.env_vars".to_string(),
            status: "pass".to_string(),
            severity: "required".to_string(),
            message: "All required environment variables set".to_string(),
            details: required.iter().map(|v| {
                serde_json::json!({"var": v, "value": std::env::var(v).unwrap_or_default()})
            }).collect(),
        }
    } else {
        CheckResult {
            id: "runtime.env_vars".to_string(),
            status: "fail".to_string(),
            severity: "required".to_string(),
            message: format!("Missing environment variables: {}", missing.join(", ")),
            details: missing.iter().map(|v| serde_json::json!({"var": v, "set": false})).collect(),
        }
    }
}
