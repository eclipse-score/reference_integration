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
use anyhow::{bail, Context, Result};
use std::collections::HashMap;

pub type Tables = HashMap<String, HashMap<String, String>>;

pub fn parse(content: &str) -> Result<Tables> {
    let mut tables = Tables::new();
    let mut table = String::new();
    let mut pending = String::new();
    let mut key = String::new();

    for (line_number, line) in content.lines().enumerate() {
        let line = strip_comment(line)?;
        let line = line.trim();
        if line.is_empty() {
            continue;
        }

        if pending.is_empty() && line.starts_with('[') {
            if !line.ends_with(']') || line.starts_with("[[") {
                bail!("Invalid TOML table header on line {}", line_number + 1);
            }
            table = line[1..line.len() - 1].trim().to_string();
            if table.is_empty() {
                bail!("Empty TOML table header on line {}", line_number + 1);
            }
            tables.entry(table.clone()).or_default();
            continue;
        }

        if pending.is_empty() {
            let Some((parsed_key, value)) = line.split_once('=') else {
                bail!("Expected key/value pair on TOML line {}", line_number + 1);
            };
            key = parsed_key.trim().to_string();
            if key.is_empty() {
                bail!("Empty TOML key on line {}", line_number + 1);
            }
            pending.push_str(value.trim());
        } else {
            pending.push(' ');
            pending.push_str(line);
        }

        if value_is_complete(&pending)? {
            let entries = tables.entry(table.clone()).or_default();
            if entries
                .insert(key.clone(), pending.trim().to_string())
                .is_some()
            {
                bail!("Duplicate TOML key '{}' on line {}", key, line_number + 1);
            }
            pending.clear();
            key.clear();
        }
    }

    if !pending.is_empty() {
        bail!("Incomplete TOML value for '{}'", key);
    }
    Ok(tables)
}

pub fn string(value: &str) -> Result<String> {
    let value = value.trim();
    if value.starts_with('"') {
        serde_json::from_str(value).context("Invalid TOML string")
    } else if value.starts_with('\'') && value.ends_with('\'') && value.len() >= 2 {
        Ok(value[1..value.len() - 1].to_string())
    } else {
        bail!("Expected a TOML string, found '{}'", value)
    }
}

pub fn string_array(value: &str) -> Result<Vec<String>> {
    let value = value.trim();
    if !value.starts_with('[') || !value.ends_with(']') {
        bail!("Expected a TOML array, found '{}'", value);
    }
    let inner = &value[1..value.len() - 1];
    if inner.trim().is_empty() {
        return Ok(Vec::new());
    }
    split_values(inner)?
        .into_iter()
        .map(|value| string(value.trim()))
        .collect()
}

pub fn inline_bool(value: &str, key: &str) -> Result<Option<bool>> {
    let value = value.trim();
    if !value.starts_with('{') || !value.ends_with('}') {
        bail!("Expected a TOML inline table, found '{}'", value);
    }
    for field in split_values(&value[1..value.len() - 1])? {
        let Some((field_key, field_value)) = field.split_once('=') else {
            bail!("Invalid TOML inline table field '{}'", field);
        };
        if field_key.trim() == key {
            return match field_value.trim() {
                "true" => Ok(Some(true)),
                "false" => Ok(Some(false)),
                other => bail!("Expected a boolean for '{}', found '{}'", key, other),
            };
        }
    }
    Ok(None)
}

fn strip_comment(line: &str) -> Result<String> {
    let mut quote = None;
    let mut escaped = false;
    for (index, ch) in line.char_indices() {
        if let Some(q) = quote {
            if q == '"' && ch == '\\' && !escaped {
                escaped = true;
                continue;
            }
            if ch == q && !escaped {
                quote = None;
            }
            escaped = false;
        } else if ch == '"' || ch == '\'' {
            quote = Some(ch);
        } else if ch == '#' {
            return Ok(line[..index].to_string());
        }
    }
    if quote.is_some() {
        bail!("Unterminated quoted string in TOML");
    }
    Ok(line.to_string())
}

fn value_is_complete(value: &str) -> Result<bool> {
    let mut quote = None;
    let mut escaped = false;
    let mut depth = 0i32;
    for ch in value.chars() {
        if let Some(q) = quote {
            if q == '"' && ch == '\\' && !escaped {
                escaped = true;
                continue;
            }
            if ch == q && !escaped {
                quote = None;
            }
            escaped = false;
            continue;
        }
        match ch {
            '"' | '\'' => quote = Some(ch),
            '{' | '[' => depth += 1,
            '}' | ']' => {
                depth -= 1;
                if depth < 0 {
                    bail!("Unbalanced TOML value");
                }
            }
            _ => {}
        }
    }
    Ok(quote.is_none() && depth == 0)
}

fn split_values(value: &str) -> Result<Vec<&str>> {
    let mut parts = Vec::new();
    let mut start = 0;
    let mut quote = None;
    let mut escaped = false;
    let mut depth = 0i32;
    for (index, ch) in value.char_indices() {
        if let Some(q) = quote {
            if q == '"' && ch == '\\' && !escaped {
                escaped = true;
                continue;
            }
            if ch == q && !escaped {
                quote = None;
            }
            escaped = false;
            continue;
        }
        match ch {
            '"' | '\'' => quote = Some(ch),
            '{' | '[' => depth += 1,
            '}' | ']' => depth -= 1,
            ',' if depth == 0 => {
                parts.push(value[start..index].trim());
                start = index + ch.len_utf8();
            }
            _ => {}
        }
    }
    if quote.is_some() || depth != 0 {
        bail!("Malformed TOML array or inline table");
    }
    let last = value[start..].trim();
    if !last.is_empty() {
        parts.push(last);
    }
    Ok(parts)
}
