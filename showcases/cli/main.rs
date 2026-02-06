use anyhow::{Context, Result};
use serde::Deserialize;
use std::{
    collections::HashMap,
    env, fs,
    path::Path,
    process::Command,
};

use cliclack::{clear_screen, intro, multiselect, outro, confirm};

#[derive(Debug, Deserialize)]
struct ScoreConfig {
    name: String,
    description: String,
    path: String,
    args: Vec<String>,
    env: HashMap<String, String>,
}

fn print_banner() {
    let color_code = "\x1b[38;5;99m";
    let reset_code = "\x1b[0m";
    
    let banner = r#"
  ███████╗ ██████╗ ██████╗ ██████╗ ███████╗
  ██╔════╝ ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ███████╗█████╗██║     ██║ ██║██████╔╝█████╗  
  ╚════██║╚════╝██║     ██║ ██║██╔══██╗██╔══╝  
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

    let selected: Vec<usize> = multiselect("Select examples to run:")
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
    println!("▶ Running: {}", config.name);
    
    let mut cmd = Command::new(&config.path);
    cmd.args(&config.args);
    cmd.envs(&config.env);
    
    let status = cmd
        .status()
        .with_context(|| format!("Failed to execute {}", config.path))?;
    
    if !status.success() {
        anyhow::bail!(
            "Command `{}` exited with status {}",
            config.path,
            status
        );
    }
    
    Ok(())
}