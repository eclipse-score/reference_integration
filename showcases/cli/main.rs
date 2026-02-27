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
use anyhow::{Context, Result};
use clap::Parser;
use serde::Deserialize;
use std::{collections::HashMap, env, fs, path::Path};

use cliclack::{clear_screen, confirm, intro, multiselect, outro};
use std::process::Child;
use std::process::Command;
use std::time::Duration;

#[derive(Parser)]
#[command(name = "SCORE CLI")]
#[command(about = "SCORE CLI showcase entrypoint", long_about = None)]
struct Args {
    /// Examples to run (comma-separated names, or "all" to run all examples, skips interactive selection)
    #[arg(long)]
    examples: Option<String>,
}

#[derive(Debug, Deserialize, Clone)]
struct AppConfig {
    path: String,
    dir: Option<String>,
    args: Vec<String>,
    env: HashMap<String, String>,
    delay: Option<u64>, // delay in seconds before running the next app
}

#[derive(Debug, Deserialize, Clone)]
struct ScoreConfig {
    name: String,
    description: String,
    apps: Vec<AppConfig>,
}

fn print_banner() {
    let color_code = "\x1b[38;5;99m";
    let reset_code = "\x1b[0m";

    let banner = r#"
   ███████╗       ██████╗ ██████╗ ██████╗ ███████╗
   ██╔════╝      ██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ███████╗█████╗██║     ██║   ██║██████╔╝█████╗  
   ╚════██║╚════╝██║     ██║   ██║██╔══██╗██╔══╝  
   ███████║      ╚██████╗╚██████╔╝██║  ██║███████╗
   ╚══════╝       ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
"#;

    println!("{}{}{}", color_code, banner, reset_code);
}

fn pause_for_enter() -> Result<()> {
    let result = confirm("Do you want to select examples to run?")
        .initial_value(true)
        .interact()?;
    if !result {
        outro("Falling back to the console. Goodbye!")?;
        std::process::exit(0);
    }
    Ok(())
}

fn main() -> Result<()> {
    let args = Args::parse();

    let root_dir = env::var("SCORE_CLI_INIT_DIR").unwrap_or_else(|_| "/showcases".to_string());

    let mut configs = Vec::new();
    visit_dir(Path::new(&root_dir), &mut configs)?;

    if configs.is_empty() {
        anyhow::bail!("No *.score.json files found under {}", root_dir);
    }

    let selected = if let Some(examples_str) = args.examples {
        // Non-interactive mode: use provided examples
        let mut selected_indices = Vec::new();

        if examples_str.to_lowercase() == "all" {
            // Select all available examples
            selected_indices = (0..configs.len()).collect();
            println!("Running all {} examples", configs.len());
        } else {
            // Match specific examples
            let requested_examples: Vec<&str> = examples_str.split(',').map(|s| s.trim()).collect();

            for (i, config) in configs.iter().enumerate() {
                if requested_examples.contains(&config.name.as_str()) {
                    selected_indices.push(i);
                }
            }

            if selected_indices.is_empty() {
                anyhow::bail!(
                    "No examples found matching: {}. Available examples: {}",
                    examples_str,
                    configs.iter().map(|c| c.name.as_str()).collect::<Vec<_>>().join(", ")
                );
            }

            println!("Running examples: {}", examples_str);
        }

        selected_indices
    } else {
        // Interactive mode
        print_banner();
        intro("WELCOME TO SHOWCASE ENTRYPOINT")?;
        pause_for_enter()?;

        clear_screen()?;

        // Create options for multiselect
        let options: Vec<(usize, String, String)> = configs
            .iter()
            .enumerate()
            .map(|(i, c)| (i, c.name.clone(), c.description.clone()))
            .collect();

        let selected: Vec<usize> =
            multiselect("Select examples to run (use space to select (multiselect supported), enter to run examples):")
                .items(&options)
                .interact()?;

        if selected.is_empty() {
            outro("No examples selected. Goodbye!")?;
            return Ok(());
        }

        selected
    };

    for index in selected {
        run_score(&configs[index])?;
    }

    outro("All done!")?;

    Ok(())
}

fn visit_dir(dir: &Path, configs: &mut Vec<ScoreConfig>) -> Result<()> {
    for entry in fs::read_dir(dir).with_context(|| format!("Failed to read directory {:?}", dir))? {
        let entry = entry?;
        let path = entry.path();

        if path.is_symlink() {
            continue;
        }

        if path.is_dir() {
            visit_dir(&path, configs)?;
            continue;
        }

        if is_score_file(&path) {
            let content = fs::read_to_string(&path).with_context(|| format!("Failed reading {:?}", path))?;
            let value: serde_json::Value =
                serde_json::from_str(&content).with_context(|| format!("Invalid JSON in {:?}", path))?;
            if value.is_array() {
                let found: Vec<ScoreConfig> =
                    serde_json::from_value(value).with_context(|| format!("Invalid JSON array in {:?}", path))?;
                configs.extend(found);
            } else {
                let config: ScoreConfig =
                    serde_json::from_value(value).with_context(|| format!("Invalid JSON in {:?}", path))?;
                configs.push(config);
            }
        }
    }
    Ok(())
}

fn is_score_file(path: &Path) -> bool {
    path.file_name()
        .and_then(|n| n.to_str())
        .map(|n| n.ends_with(".score.json"))
        .unwrap_or(false)
}

fn run_score(config: &ScoreConfig) -> Result<()> {
    println!("▶ Running example: {}", config.name);

    let mut children: Vec<(usize, String, Child)> = Vec::new();

    let now = std::time::Instant::now();
    println!("{:?} Starting example '{}'", now.elapsed(), config.name);
    for (i, app) in config.apps.iter().enumerate() {
        let app = app.clone(); // Clone for ownership

        if let Some(delay_secs) = app.delay {
            if delay_secs > 0 {
                println!(
                    "{:?}  App {}: waiting {} seconds before start...",
                    now.elapsed(),
                    i + 1,
                    delay_secs
                );
                std::thread::sleep(Duration::from_secs(delay_secs));
            }
        }

        println!("{:?} App {}: starting {}", now.elapsed(), i + 1, app.path);

        let mut cmd = Command::new(&app.path);
        cmd.args(&app.args);
        cmd.envs(&app.env);
        if let Some(ref dir) = app.dir {
            cmd.current_dir(dir);
        }

        let child = cmd
            .spawn()
            .with_context(|| format!("Failed to start app {}: {}", i + 1, app.path))?;

        println!("App {}: spawned command {:?}", i + 1, cmd);

        children.push((i + 1, app.path.clone(), child));
    }

    // Wait for all children
    for (i, path, mut child) in children {
        let status = child
            .wait()
            .with_context(|| format!("Failed to wait for app {}: {}", i, path))?;

        if !status.success() {
            // anyhow::bail!("App {}: command `{}` exited with status {}", i, path, status);
        }

        println!("App {}: finished {}", i, path);
    }

    println!("✅ Example '{}' finished successfully.", config.name);
    Ok(())
}
