//! s-core TCK - Test Compatibility Kit for SCORE Platform Distributions
//!
//! This library provides the core check implementations for verifying
//! SCORE distribution compatibility.
//!
//! # Check Families
//!
//! - **SBOM**: Validates required components, license policy, and drift from golden
//! - **Version**: Ensures platform version compatibility
//! - **Runtime**: Validates execution environment and test harness adapter
//!
//! # Porting Package Concept
//!
//! Inspired by Jakarta EE TCK, vendors configure a "test harness adapter" that
//! tells the TCK how to run tests against their distribution. This is the RPM
//! equivalent of Jakarta's porting package.

pub mod config;
pub mod sbom;
pub mod report;
pub mod version;
pub mod runtime;

pub use config::Config;
pub use sbom::SBOMChecker;
pub use report::{Report, CheckReport, CheckResult};
pub use version::{VersionPolicy, load_policy as load_version_policy};
pub use runtime::{RuntimeRequirements, TestHarnessAdapter, ShowcaseResult};
