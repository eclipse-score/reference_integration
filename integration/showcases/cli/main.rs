use anyhow::{Context, Result};
use serde::Deserialize;
use std::{
    collections::HashMap,
    env, fs,
    path::Path,
};

use cliclack::{clear_screen, intro, multiselect, outro, confirm};
use std::time::Duration;
use std::process::Command;
use std::process::Child;

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
    confirm("Press Enter to select examples to run...")
        .initial_value(true)
        .interact()?;
    Ok(())
}

fn main() -> Result<()> {
    print_banner();
    intro("WELCOME TO SHOWCASE ENTRYPOINT")?;
    pause_for_enter()?;

    clear_screen()?;

    let root_dir = env::var("SCORE_CLI_INIT_DIR")
        .unwrap_or_else(|_| "/showcases".to_string());

    let mut configs = Vec::new();
    visit_dir(Path::new(&root_dir), &mut configs)?;

    if configs.is_empty() {
        anyhow::bail!("No *.score.json files found under {}", root_dir);
    }

    // Create options for multiselect
    let options: Vec<(usize, String, String)> = configs
        .iter()
        .enumerate()
        .map(|(i, c)| (i, c.name.clone(), c.description.clone()))
        .collect();

    let selected: Vec<usize> = multiselect("Select examples to run (use space to select (multiselect supported), enter to run examples):")
        .items(&options)
        .interact()?;

    if selected.is_empty() {
        outro("No examples selected. Goodbye!")?;
        return Ok(());
    }

    for index in selected {
        run_score(&configs[index])?;
    }

    outro("All done!")?;
    
    Ok(())
}

fn visit_dir(dir: &Path, configs: &mut Vec<ScoreConfig>) -> Result<()> {
    for entry in fs::read_dir(dir)
        .with_context(|| format!("Failed to read directory {:?}", dir))?
    {
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
            let content = fs::read_to_string(&path)
                .with_context(|| format!("Failed reading {:?}", path))?;
            let config: ScoreConfig = serde_json::from_str(&content)
                .with_context(|| format!("Invalid JSON in {:?}", path))?;
            configs.push(config);
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
                println!("{:?}  App {}: waiting {} seconds before start...", now.elapsed(), i + 1, delay_secs);
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
