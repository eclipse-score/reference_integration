//! s-core TCK - Test Compatibility Kit for SCORE Platform Distributions
//!
//! This library provides the core check implementations for verifying
//! SCORE distribution compatibility.

pub mod config;
pub mod sbom;
pub mod report;

pub use config::Config;
pub use sbom::SBOMChecker;
pub use report::{Report, CheckReport, CheckResult};
