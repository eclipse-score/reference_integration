use anyhow::{Context, Result};
use inquire::MultiSelect;
use serde::Deserialize;
use std::{
    collections::HashMap,
    env,
    fs,
    path::Path,
    process::Command,
};

#[derive(Debug, Deserialize)]
struct ScoreConfig {
    name: String,
    description: String,
    path: String,
    args: Vec<String>,
    env: HashMap<String, String>,
}

fn print_banner() {
    // Purple-blue ANSI color code
    let color_code = "\x1b[38;5;99m"; // bright purple-blue
    let reset_code = "\x1b[0m";
    // Hand-crafted ASCII banner for "S-CORE"
    let banner = r#"
 ███████╗      ██████╗ ██████╗ ██████╗ ███████╗
 ██╔════╝     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
 ███████╗█████╗██║     ██║   ██║██████╔╝█████╗  
 ╚════██║╚════╝██║     ██║   ██║██╔══██╗██╔══╝  
 ███████║     ╚██████╗╚██████╔╝██║  ██║███████╗
 ╚══════╝      ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
"#;
    println!("{}{}{}", color_code, banner, reset_code);
    // Subtitle
    println!("{}WELCOME TO SHOWCASE ENTRYPOINT{}\n", color_code, reset_code);
}


fn main() -> Result<()> {
    print_banner();

    let mRootDir = env::var("SCORE_CLI_INIT_DIR").unwrap_or_else(|_| "/showcases".to_string());

    let mut mConfigs = Vec::new();
    visit_dir(Path::new(&mRootDir), &mut mConfigs)?;

    if mConfigs.is_empty() {
        anyhow::bail!("No *.score.json files found under {}", mRootDir);
    }

    let mOptions: Vec<String> = mConfigs
        .iter()
        .map(|c| format!("{} — {}", c.name, c.description))
        .collect();

    let mSelected = MultiSelect::new("Select examples to run:", mOptions.clone()).prompt()?;

    for mSelection in mSelected {
        let mIndex = mOptions
            .iter()
            .position(|o| o == &mSelection)
            .expect("selection index missing");

        run_score(&mConfigs[mIndex])?;
    }

    Ok(())
}

fn visit_dir(mDir: &Path, mConfigs: &mut Vec<ScoreConfig>) -> Result<()> {
    for mEntry in fs::read_dir(mDir)
        .with_context(|| format!("Failed to read directory {:?}", mDir))?
    {
        let mEntry = mEntry?;
        let mPath = mEntry.path();

        if mPath.is_symlink() {
            continue;
        }

        if mPath.is_dir() {
            visit_dir(&mPath, mConfigs)?;
            continue;
        }

        if is_score_file(&mPath) {
            let mContent = fs::read_to_string(&mPath)
                .with_context(|| format!("Failed reading {:?}", mPath))?;

            let mConfig: ScoreConfig = serde_json::from_str(&mContent)
                .with_context(|| format!("Invalid JSON in {:?}", mPath))?;

            mConfigs.push(mConfig);
        }
    }

    Ok(())
}

fn is_score_file(mPath: &Path) -> bool {
    mPath
        .file_name()
        .and_then(|n| n.to_str())
        .map(|n| n.ends_with(".score.json"))
        .unwrap_or(false)
}

fn run_score(mConfig: &ScoreConfig) -> Result<()> {
    println!("▶ Running: {}", mConfig.name);

    let mut mCmd = Command::new(&mConfig.path);
    mCmd.args(&mConfig.args);
    mCmd.envs(&mConfig.env);

    let mStatus = mCmd
        .status()
        .with_context(|| format!("Failed to execute {}", mConfig.path))?;

    if !mStatus.success() {
        anyhow::bail!(
            "Command `{}` exited with status {}",
            mConfig.path,
            mStatus
        );
    }

    Ok(())
}
