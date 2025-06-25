#!/usr/bin/env python3

import sys
import os
import argparse
import runpy

# --- Resolve project root and fix sys.path + cwd ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)  # Force working directory to project root

def run_module(module_path):
    try:
        runpy.run_module(module_path, run_name="__main__")
    except ModuleNotFoundError as e:
        print(f"❌ Module '{module_path}' not found.\n{e}")
    except Exception as e:
        print(f"❌ Error running module '{module_path}':\n{e}")

def main():
    parser = argparse.ArgumentParser(description="Run project module")
    parser.add_argument("-m", "--module", help="Module path to run", required=True)
    args, unknown = parser.parse_known_args()

    # Simulate command-line args for the module being run
    sys.argv = [args.module] + unknown
    run_module(args.module)

if __name__ == "__main__":
    main()
