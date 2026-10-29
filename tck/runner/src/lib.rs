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
pub mod report;
pub mod runtime;
pub mod sbom;
pub(crate) mod toml;
pub mod version;

pub use config::Config;
pub use report::{CheckReport, CheckResult, Report};
pub use runtime::{RuntimeRequirements, ShowcaseResult, TestHarnessAdapter};
pub use sbom::SBOMChecker;
pub use version::{load_policy as load_version_policy, VersionPolicy};
