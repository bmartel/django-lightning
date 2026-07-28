#!/usr/bin/env python3
"""
Lightweight project generator script for django-lightning.
Creates a new ready-to-go Django-Bolt application from this template without Cookiecutter.

Usage:
    python scripts/create-project.py <project_name> [destination_dir] [--no-rust]
    uv run python scripts/create-project.py <project_name> [destination_dir] [--no-rust]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "cli",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "staticfiles",
    "scratch",
    "build",
    "dist",
    ".worktrees",
}

IGNORED_FILES = {
    "db.sqlite3",
    "db.sqlite3-journal",
    ".DS_Store",
}


def sanitize_names(name: str):
    """Convert input name into slug and snake_case representations."""
    clean_name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    slug_name = re.sub(r"[_\s]+", "-", clean_name)
    snake_name = re.sub(r"[-\s]+", "_", clean_name)
    return slug_name, snake_name


def copy_and_transform(
    src_dir: Path, dest_dir: Path, slug_name: str, snake_name: str, include_rust: bool = True
):
    """Copy template files replacing placeholders with new project names."""
    print(f"🚀 Creating new Django-Bolt project '{slug_name}' in '{dest_dir}'...")
    if not include_rust:
        print("  ℹ Scaffolding Python-only project (Rust extension core excluded)")
    else:
        print("  ⚡ Including Native Rust extension core (rust_core)")

    ignored_dirs = set(IGNORED_DIRS)
    if not include_rust:
        ignored_dirs.add("rust_core")

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        rel_root = Path(root).relative_to(src_dir)
        target_root = dest_dir / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        for file_name in files:
            if file_name in IGNORED_FILES or file_name.endswith(".pyc"):
                continue

            # Skip release.yml workflow (starter repository specific)
            if rel_root == Path(".github/workflows") and file_name == "release.yml":
                continue

            # Skip Rust demo route if user opted out of Rust
            if not include_rust and rel_root == Path("app/routes") and file_name == "rust_demo.py":
                continue

            src_file = Path(root) / file_name
            dest_file = target_root / file_name

            # Skip generator script itself
            if rel_root == Path("scripts") and file_name == "create-project.py":
                continue

            try:
                content = src_file.read_text(encoding="utf-8")
                content = content.replace("django-lightning-mcp", f"{slug_name}-mcp")
                content = content.replace("django-lightning", slug_name)
                content = content.replace("django_lightning", snake_name)
                content = content.replace("Django Lightning", slug_name.replace("-", " ").title())

                if file_name == "justfile":
                    cli_task = (
                        "\n# Build the Rust CLI tool (create-django-bolt)\n"
                        "build-cli:\n"
                        "    cargo build --manifest-path cli/Cargo.toml --release\n"
                    )
                    content = content.replace(cli_task, "")
                    if not include_rust:
                        rust_tasks = (
                            "# Compile Rust core in debug mode for local development\n"
                            "rust-dev:\n"
                            "    uv run maturin develop\n\n"
                            "# Compile Rust core in release mode for production performance\n"
                            "rust-build:\n"
                            "    uv run maturin develop --release\n\n"
                            "# Run unit tests for Rust native core crate\n"
                            "rust-test:\n"
                            "    cargo test --manifest-path rust_core/Cargo.toml\n"
                        )
                        content = content.replace(rust_tasks, "")

                if not include_rust and file_name == "pyproject.toml":
                    maturin_build = (
                        "[build-system]\n"
                        'requires = ["maturin>=1.5,<2.0"]\n'
                        'build-backend = "maturin"\n\n'
                        "[tool.maturin]\n"
                        'manifest-path = "rust_core/Cargo.toml"\n'
                        'python-packages = ["app"]\n'
                        'module-name = "app.rust_core"\n'
                    )
                    content = content.replace(maturin_build, "")
                    content = content.replace('    "maturin>=1.5.0",\n', "")

                dest_file.write_text(content, encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src_file, dest_file)

            if os.access(src_file, os.X_OK):
                dest_file.chmod(dest_file.stat().st_mode | 0o111)


def initialize_git(dest_dir: Path):
    try:
        subprocess.run(["git", "init"], cwd=dest_dir, check=True, stdout=subprocess.DEVNULL)
        print("  ✓ Initialized new Git repository")
    except Exception:
        print("  ! Skipping git initialization (git CLI not available)")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Django-Bolt application.")
    parser.add_argument("name", help="Project name (e.g. acme-api)")
    parser.add_argument("dest", nargs="?", help="Destination directory path", default=None)
    parser.add_argument(
        "--no-rust", action="store_true", help="Exclude Rust native extension core (rust_core)"
    )

    args = parser.parse_args()
    slug_name, snake_name = sanitize_names(args.name)
    template_dir = Path(__file__).resolve().parent.parent

    if args.dest:
        dest_dir = Path(args.dest).resolve()
    else:
        dest_dir = (template_dir.parent / slug_name).resolve()

    if dest_dir.exists() and any(dest_dir.iterdir()):
        print(f"❌ Error: Destination directory '{dest_dir}' exists and is not empty!")
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)
    copy_and_transform(template_dir, dest_dir, slug_name, snake_name, include_rust=not args.no_rust)
    initialize_git(dest_dir)

    print("\n✨ Project setup complete!")
    print("\nNext steps:")
    print(f"  1. cd {dest_dir}")
    print("  2. uv venv")
    if not args.no_rust:
        print("  3. uv run maturin develop")
        print('  4. uv pip install -e ".[dev]"')
    else:
        print('  3. uv pip install -e ".[dev]"')
    print("  5. uv run manage.py migrate")
    print("  6. uv run manage.py collectstatic --noinput")
    print("  7. uv run manage.py runbolt --dev")


if __name__ == "__main__":
    main()
