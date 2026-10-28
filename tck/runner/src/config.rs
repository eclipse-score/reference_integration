//! Distribution configuration parsing

use anyhow::{Result, Context};
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
/// Uses simple string parsing to avoid external dependencies
pub fn load(path: &PathBuf) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read config file: {}", path.display()))?;

    // Parse using simple string matching
    let name = extract_string_value(&content, "name").unwrap_or_else(|| "unknown-distribution".to_string());
    let version = extract_string_value(&content, "version").unwrap_or_else(|| "unversioned".to_string());
    let arch = extract_string_value(&content, "arch").unwrap_or_else(|| "x86_64-linux".to_string());
    let profile = extract_string_value(&content, "profile").unwrap_or_else(|| "full".to_string());
    let platform_version = extract_string_value(&content, "platform_version").unwrap_or_else(|| "0.9.0".to_string());
    let sbom_file = extract_string_value(&content, "sbom_file").unwrap_or_else(|| "./sbom.spdx.json".to_string());

    Ok(Config {
        dist: DistConfig {
            name,
            version,
            arch,
            profile,
            platform_version,
            paths: PathsConfig {
                sbom_file: PathBuf::from(sbom_file),
                headers_dir: None,
                libs_dir: None,
            },
        },
        checks: ChecksConfig::default(),
    })
}

/// Extract a string value from TOML content using simple pattern matching
fn extract_string_value(content: &str, key: &str) -> Option<String> {
    // Match: key = "value" or key = 'value'
    for line in content.lines() {
        let line = line.trim();
        if line.starts_with('#') { continue; }
        if line.starts_with(key) {
            if let Some(eq_pos) = line.find('=') {
                let value_part = line[eq_pos + 1..].trim();
                // Handle "value" or 'value'
                if (value_part.starts_with('"') && value_part.ends_with('"')) ||
                   (value_part.starts_with("'") && value_part.ends_with("'")) {
                    return Some(value_part[1..value_part.len()-1].to_string());
                }
            }
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;
    
    #[test]
    fn test_extract_string_value_double_quotes() {
        let content = r#"name = "test-dist""#;
        assert_eq!(extract_string_value(content, "name"), Some("test-dist".to_string()));
    }
    
    #[test]
    fn test_extract_string_value_single_quotes() {
        let content = r#"name = 'test-dist'"#;
        assert_eq!(extract_string_value(content, "name"), Some("test-dist".to_string()));
    }
    
    #[test]
    fn test_extract_string_value_missing() {
        let content = r#"version = "1.0.0""#;
        assert_eq!(extract_string_value(content, "name"), None);
    }
    
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
        writeln!(file, r#"platform_version = "1.5.0""#).unwrap();
        
        let config = load(&file.path().to_path_buf()).unwrap();
        assert_eq!(config.dist.platform_version, "1.5.0");
    }
    
    #[test]
    fn test_load_config_file_not_found() {
        let result = load(&PathBuf::from("/nonexistent/config.toml"));
        assert!(result.is_err());
    }
}
