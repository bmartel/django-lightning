use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use colored::*;
use dialoguer::{Confirm, Input};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use walkdir::WalkDir;

const REPO_URL: &str = "https://github.com/bmartel/django-lightning.git";

#[derive(Parser)]
#[command(
    name = "create-django-bolt",
    author,
    version,
    about = "Ultra-fast CLI binary to scaffold production-ready Django-Bolt applications"
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Project name
    #[arg(value_name = "PROJECT_NAME")]
    name: Option<String>,

    /// Destination directory
    #[arg(short, long)]
    path: Option<PathBuf>,

    /// Custom template directory or repository URL
    #[arg(short, long)]
    template: Option<String>,
}

#[derive(Subcommand)]
enum Commands {
    /// Scaffold a new Django-Bolt project
    New {
        /// Project name
        name: Option<String>,

        /// Destination directory
        #[arg(short, long)]
        path: Option<PathBuf>,

        /// Custom template directory or repository URL
        #[arg(short, long)]
        template: Option<String>,
    },
}

fn sanitize_names(input: &str) -> (String, String) {
    let clean = input.trim().to_lowercase();
    let slug = clean.replace(['_', ' '], "-");
    let snake = clean.replace(['-', ' '], "_");
    (slug, snake)
}

fn is_dir_empty(path: &Path) -> bool {
    if !path.exists() {
        return true;
    }
    match fs::read_dir(path) {
        Ok(mut entries) => entries.next().is_none(),
        Err(_) => false,
    }
}

fn copy_and_transform_dir(src_dir: &Path, dest_dir: &Path, slug_name: &str, snake_name: &str) -> Result<()> {
    let ignored_dirs = [".git", "git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "staticfiles", "scratch", "target", "cli"];
    let ignored_files = ["db.sqlite3", "db.sqlite3-journal", ".DS_Store"];

    for entry in WalkDir::new(src_dir).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        let rel_path = path.strip_prefix(src_dir)?;

        if rel_path.components().any(|c| {
            let name = c.as_os_str().to_string_lossy();
            ignored_dirs.contains(&name.as_ref())
        }) {
            continue;
        }

        let target_path = dest_dir.join(rel_path);

        if path.is_dir() {
            fs::create_dir_all(&target_path)?;
        } else if path.is_file() {
            let file_name = path.file_name().unwrap_or_default().to_string_lossy();
            if ignored_files.contains(&file_name.as_ref()) || file_name.ends_with(".pyc") {
                continue;
            }

            if let Ok(content) = fs::read_to_string(path) {
                let transformed = content
                    .replace("django-lightning-mcp", &format!("{}-mcp", slug_name))
                    .replace("django-lightning", slug_name)
                    .replace("django_lightning", snake_name)
                    .replace("Django Lightning", &slug_name.replace('-', " "));

                fs::write(&target_path, transformed)?;
            } else {
                fs::copy(path, &target_path)?;
            }
        }
    }
    Ok(())
}

fn transform_in_place(dest_dir: &Path, slug_name: &str, snake_name: &str) -> Result<()> {
    let ignored_dirs = [".git", "git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "staticfiles", "scratch", "target", "cli"];
    let ignored_files = ["db.sqlite3", "db.sqlite3-journal", ".DS_Store"];

    for entry in WalkDir::new(dest_dir).into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        let rel_path = path.strip_prefix(dest_dir)?;

        if rel_path.components().any(|c| {
            let name = c.as_os_str().to_string_lossy();
            ignored_dirs.contains(&name.as_ref())
        }) {
            continue;
        }

        if path.is_file() {
            let file_name = path.file_name().unwrap_or_default().to_string_lossy();
            if ignored_files.contains(&file_name.as_ref()) || file_name.ends_with(".pyc") {
                continue;
            }

            if let Ok(content) = fs::read_to_string(path) {
                let transformed = content
                    .replace("django-lightning-mcp", &format!("{}-mcp", slug_name))
                    .replace("django-lightning", slug_name)
                    .replace("django_lightning", snake_name)
                    .replace("Django Lightning", &slug_name.replace('-', " "));

                fs::write(path, transformed)?;
            }
        }
    }
    Ok(())
}

fn download_template_from_github(dest_dir: &Path) -> Result<()> {
    println!("  {}", "Downloading template from GitHub (bmartel/django-lightning)...".dimmed());
    
    if !dest_dir.exists() {
        let status = Command::new("git")
            .args(["clone", "--depth", "1", REPO_URL, &dest_dir.to_string_lossy()])
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status()
            .context("Failed to execute git clone")?;

        if !status.success() {
            anyhow::bail!("Failed to clone template repository from '{}'", REPO_URL);
        }
    } else {
        let status = Command::new("git")
            .args(["clone", "--depth", "1", REPO_URL, "."])
            .current_dir(dest_dir)
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status()
            .context("Failed to execute git clone")?;

        if !status.success() {
            anyhow::bail!("Failed to clone template repository into existing directory '{}'", dest_dir.display());
        }
    }
    Ok(())
}

fn initialize_git(dest_dir: &Path) {
    let _ = fs::remove_dir_all(dest_dir.join(".git"));

    if Command::new("git")
        .args(["init"])
        .current_dir(dest_dir)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
    {
        println!("  {}", "✓ Initialized Git repository".green());
    }
}

fn setup_uv_env(dest_dir: &Path) {
    println!("\n{}", "⚙ Setting up Python environment with uv...".cyan());

    let venv_status = Command::new("uv")
        .arg("venv")
        .current_dir(dest_dir)
        .status();

    if venv_status.map(|s| s.success()).unwrap_or(false) {
        println!("  {}", "✓ Created virtual environment (.venv)".green());

        let install_status = Command::new("uv")
            .args(["pip", "install", "-e", ".[dev]"])
            .current_dir(dest_dir)
            .status();

        if install_status.map(|s| s.success()).unwrap_or(false) {
            println!("  {}", "✓ Installed dependencies with uv".green());
        }
    } else {
        println!("  {}", "! 'uv' not found or failed. Skipping virtual environment creation.".yellow());
    }
}

fn run_generator(name_opt: Option<String>, path_opt: Option<PathBuf>, template_opt: Option<String>) -> Result<()> {
    println!("{}", "⚡ create-django-bolt".bold().cyan());
    println!("{}", "   High-Performance Django-Bolt Project Generator\n".dimmed());

    let raw_name = match name_opt {
        Some(n) => n,
        None => Input::<String>::new()
            .with_prompt("Project name")
            .default("my-bolt-app".into())
            .interact_text()?,
    };

    let (slug_name, snake_name) = sanitize_names(&raw_name);

    let current_dir = std::env::current_dir()?;
    let dest_dir = match path_opt {
        Some(p) => p,
        None => current_dir.join(&slug_name),
    };

    // Robust check for non-empty existing directory
    if dest_dir.exists() && !is_dir_empty(&dest_dir) {
        anyhow::bail!(
            "Destination directory '{}' already exists and is not empty!\nPlease specify a different name or path (e.g. create-django-bolt new {} -p /path/to/dir).",
            dest_dir.display(),
            slug_name
        );
    }

    println!("🚀 Creating Django-Bolt project '{}' in '{}'...", slug_name.bold().green(), dest_dir.display());

    if let Some(template_path) = template_opt {
        let src_path = PathBuf::from(template_path);
        if !src_path.exists() {
            anyhow::bail!("Template path '{}' does not exist!", src_path.display());
        }
        fs::create_dir_all(&dest_dir)?;
        copy_and_transform_dir(&src_path, &dest_dir, &slug_name, &snake_name)?;
    } else if current_dir.join("manage.py").exists() && current_dir.join("pyproject.toml").exists() {
        // We are executing inside the template repository root itself
        fs::create_dir_all(&dest_dir)?;
        copy_and_transform_dir(&current_dir, &dest_dir, &slug_name, &snake_name)?;
    } else {
        // Download from GitHub template repo
        download_template_from_github(&dest_dir)?;
        transform_in_place(&dest_dir, &slug_name, &snake_name)?;
    }

    initialize_git(&dest_dir);

    let is_tty = dialoguer::console::user_attended_stderr() || dialoguer::console::Term::stdout().is_term();

    let setup_env = if is_tty {
        Confirm::new()
            .with_prompt("Would you like to setup virtual environment and dependencies with 'uv' now?")
            .default(true)
            .interact_opt()?
            .unwrap_or(false)
    } else {
        false
    };

    if setup_env {
        setup_uv_env(&dest_dir);
    }

    println!("\n{}", "✨ Project scaffolding complete!".bold().green());
    println!("\nNext steps:");
    println!("  1. cd {}", dest_dir.display().to_string().bold());
    if !setup_env {
        println!("  2. uv venv");
        println!("  3. uv pip install -e \".[dev]\"");
    }
    println!("  4. uv run manage.py migrate");
    println!("  5. uv run manage.py runbolt --dev");

    Ok(())
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Some(Commands::New { name, path, template }) => run_generator(name, path, template)?,
        None => run_generator(cli.name, cli.path, cli.template)?,
    }

    Ok(())
}
