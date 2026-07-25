#!/usr/bin/env python3
"""
Lightweight project generator script for django-lightning.
Creates a new ready-to-go Django-Bolt application from this template without Cookiecutter.

Usage:
    python scripts/create-project.py <project_name> [destination_dir]
    uv run python scripts/create-project.py <project_name> [destination_dir]
"""

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


def copy_and_transform(src_dir: Path, dest_dir: Path, slug_name: str, snake_name: str):
    """Copy template files replacing placeholders with new project names."""
    print(f"🚀 Creating new Django-Bolt project '{slug_name}' in '{dest_dir}'...")

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        rel_root = Path(root).relative_to(src_dir)
        target_root = dest_dir / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        for file_name in files:
            if file_name in IGNORED_FILES or file_name.endswith(".pyc"):
                continue

            # Skip release.yml workflow (starter repository specific)
            if rel_root == Path(".github/workflows") and file_name == "release.yml":
                continue

            src_file = Path(root) / file_name
            dest_file = target_root / file_name

            # Skip the generator script itself from being copied into the new project
            if rel_root == Path("scripts") and file_name == "create-project.py":
                continue

            try:
                content = src_file.read_text(encoding="utf-8")
                # Perform name replacements
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

                dest_file.write_text(content, encoding="utf-8")
            except UnicodeDecodeError:
                # Binary files (images, binary assets) copied directly
                shutil.copy2(src_file, dest_file)

            # Preserve executable permissions for scripts and manage.py
            if os.access(src_file, os.X_OK):
                dest_file.chmod(dest_file.stat().st_mode | 0o111)


def initialize_git(dest_dir: Path):
    """Initialize a fresh git repository in the target directory."""
    try:
        subprocess.run(["git", "init"], cwd=dest_dir, check=True, stdout=subprocess.DEVNULL)
        print("  ✓ Initialized new Git repository")
    except Exception:
        print("  ! Skipping git initialization (git CLI not available)")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/create-project.py <project_name> [destination_dir]")
        print("Example: python scripts/create-project.py acme-api ~/code/acme-api")
        sys.exit(1)

    project_input = sys.argv[1]
    slug_name, snake_name = sanitize_names(project_input)

    template_dir = Path(__file__).resolve().parent.parent

    if len(sys.argv) >= 3:
        dest_dir = Path(sys.argv[2]).resolve()
    else:
        dest_dir = (template_dir.parent / slug_name).resolve()

    if dest_dir.exists() and any(dest_dir.iterdir()):
        print(f"❌ Error: Destination directory '{dest_dir}' exists and is not empty!")
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)
    copy_and_transform(template_dir, dest_dir, slug_name, snake_name)
    initialize_git(dest_dir)

    print("\n✨ Project setup complete!")
    print("\nNext steps:")
    print(f"  1. cd {dest_dir}")
    print("  2. uv venv")
    print('  3. uv pip install -e ".[dev]"')
    print("  4. uv run manage.py migrate")
    print("  5. uv run manage.py runbolt --dev")


if __name__ == "__main__":
    main()
