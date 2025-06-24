#!/usr/bin/env python3

import os
from pathlib import Path

# -----------------------------------------
# Project root is assumed to be one directory above this script's location.
# For example: if this script is in mock-offseason-tools/scripts/, then
# PROJECT_ROOT becomes mock-offseason-tools/
# -----------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# This defines the file pattern we're scanning for — all Python source files.
PY_EXT = "*.py"


def get_import_renames():
    """
    Prompt the user to enter old → new module rename pairs.
    Each entry is stored in a dictionary with an optional note.

    Returns:
        A dictionary structured as:
        {
            "old_module_name": {
                "new": "new_module_name",
                "note": "description of change"
            },
            ...
        }
    """
    print("🛠️  Enter old → new module rename pairs (press ENTER to finish):")
    renames = {}

    # Keep collecting mappings until the user enters nothing
    while True:
        old = input("Old module name (or ENTER to finish): ").strip()
        if not old:
            break  # Done entering renames
        new = input(f"New name for '{old}': ").strip()
        note = input("Optional note for this rename: ").strip()

        # Save the rename entry and fallback note
        renames[old] = {
            "new": new,
            "note": note or "No note provided."
        }

        print(f"✔️  Queued: '{old}' → '{new}'\n")

    return renames


def update_imports_in_file(filepath, renames):
    """
    Reads a file and replaces import statements based on the rename mappings.
    Only performs substitutions for:
    - `from old_module`
    - `import old_module`

    Args:
        filepath (Path): The full path to the file to be updated.
        renames (dict): The mapping of old → new imports.
    """
    # Read the entire file content into memory
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content  # Used to detect if changes were made

    # Apply substitutions for each rename entry
    for old, meta in renames.items():
        new = meta["new"]
        # Replace exact string matches for import patterns
        content = content.replace(f"from {old}", f"from {new}")
        content = content.replace(f"import {old}", f"import {new}")

    # Only write the file back if changes were actually made
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Updated: {filepath.relative_to(PROJECT_ROOT)}")

        # Optionally report the renames applied to this file
        for old, meta in renames.items():
            if f"{meta['new']}" in content and f"{old}" not in content:
                print(f"   ↪ Renamed '{old}' → '{meta['new']}'  — {meta['note']}")


def scan_and_update(renames):
    """
    Recursively search the project directory for Python files and apply renames.
    Excludes common virtual environment and config directories to avoid accidental edits.

    Args:
        renames (dict): The mapping of old → new module names.
    """
    print("🔍 Scanning for Python files...\n")

    # Set of directory names to ignore during scanning
    ignored_dirs = {"venv", ".venv", "env", ".env", "envs", ".envs"}

    # Walk the entire project and apply changes to relevant files
    for path in PROJECT_ROOT.rglob(PY_EXT):
        if any(part in ignored_dirs for part in path.parts):
            continue  # Skip files inside ignored directories
        update_imports_in_file(path, renames)


if __name__ == "__main__":
    """
    Entry point for the script. Runs the interactive renamer,
    and triggers the scan-and-update process.
    """
    print("🚀 Interactive Import Renamer")

    # Prompt the user to define old → new import pairs
    renames = get_import_renames()

    # If nothing entered, do nothing
    if not renames:
        print("⚠️  No renames entered. Exiting.")
    else:
        # Apply import renaming project-wide
        scan_and_update(renames)
        print("\n✅ All done.")
