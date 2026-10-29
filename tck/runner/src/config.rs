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
//! Distribution configuration parsing

use anyhow::{Context, Result};
use std::path::PathBuf;

/// Distribution configuration
#[derive(Debug)]
pub struct Config {
    pub dist: DistConfig,
    pub checks: ChecksConfig,
}

#[derive(Debug)]
pub struct DistConfig {
    pub name: String,
    pub version: String,
    pub arch: String,
    pub profile: String,
    pub platform_version: String,
    pub paths: PathsConfig,
}

#[derive(Debug)]
pub struct PathsConfig {
    pub sbom_file: PathBuf,
    pub headers_dir: Option<PathBuf>,
    pub libs_dir: Option<PathBuf>,
}

#[derive(Debug, Default)]
pub struct ChecksConfig {
    pub enabled: Vec<String>,
}

/// Load a distribution configuration from a TOML file
pub fn load(path: &PathBuf) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read config file: {}", path.display()))?;
    let tables = crate::toml::parse(&content)
        .with_context(|| format!("Failed to parse config file: {}", path.display()))?;
    let dist = tables.get("dist");
    let paths = tables.get("dist.paths");
    let checks = tables.get("checks");

    Ok(Config {
        dist: DistConfig {
            name: get_string(dist, "name")?.unwrap_or_else(|| "unknown-distribution".to_string()),
            version: get_string(dist, "version")?.unwrap_or_else(|| "unversioned".to_string()),
            arch: get_string(dist, "arch")?.unwrap_or_else(|| "x86_64-linux".to_string()),
            profile: get_string(dist, "profile")?.unwrap_or_else(|| "full".to_string()),
            platform_version: get_string(dist, "platform_version")?
                .unwrap_or_else(|| "0.9.0".to_string()),
            paths: PathsConfig {
                sbom_file: PathBuf::from(
                    get_string(paths, "sbom_file")?
                        .unwrap_or_else(|| "./sbom.spdx.json".to_string()),
                ),
                headers_dir: get_string(paths, "headers_dir")?.map(PathBuf::from),
                libs_dir: get_string(paths, "libs_dir")?.map(PathBuf::from),
            },
        },
        checks: ChecksConfig {
            enabled: checks
                .and_then(|table| table.get("enabled"))
                .map(|value| crate::toml::string_array(value))
                .transpose()?
                .unwrap_or_default(),
        },
    })
}

fn get_string(
    table: Option<&std::collections::HashMap<String, String>>,
    key: &str,
) -> Result<Option<String>> {
    table
        .and_then(|table| table.get(key))
        .map(|value| crate::toml::string(value))
        .transpose()
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_load_config_minimal() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, r#"[dist]"#).unwrap();
        writeln!(file, r#"name = "my-dist""#).unwrap();
        writeln!(file, r#"version = "2.0.0""#).unwrap();

        let config = load(&file.path().to_path_buf()).unwrap();
        assert_eq!(config.dist.name, "my-dist");
        assert_eq!(config.dist.version, "2.0.0");
    }

    #[test]
    fn test_load_config_with_platform_version() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, r#"[dist]"#).unwrap();
        writeln!(file, r#"name = "test""#).unwrap();
        writeln!(file, r#"platform_version = "0.8.0" # older platform"#).unwrap();

        let config = load(&file.path().to_path_buf()).unwrap();
        assert_eq!(config.dist.platform_version, "0.8.0");
    }

    #[test]
    fn test_load_checks_and_nested_paths() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "[dist]").unwrap();
        writeln!(file, r#"name = "test""#).unwrap();
        writeln!(file, r#"profile = "minimal""#).unwrap();
        writeln!(file, "[dist.paths]").unwrap();
        writeln!(file, r#"sbom_file = "./sbom.json" # path"#).unwrap();
        writeln!(file, "[checks]").unwrap();
        writeln!(file, r#"enabled = ["sbom"]"#).unwrap();

        let config = load(&file.path().to_path_buf()).unwrap();
        assert_eq!(config.dist.paths.sbom_file, PathBuf::from("./sbom.json"));
        assert_eq!(config.checks.enabled, vec!["sbom"]);
    }

    #[test]
    fn test_invalid_toml_is_reported() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "[dist").unwrap();
        assert!(load(&file.path().to_path_buf()).is_err());
    }

    #[test]
    fn test_load_config_file_not_found() {
        let result = load(&PathBuf::from("/nonexistent/config.toml"));
        assert!(result.is_err());
    }
}
