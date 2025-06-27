#!/usr/bin/env python3
"""
Python environment wrapper script to replace make.bat
Processes A2L files using a2l2pid.py with enhanced features including dry-run mode.
"""

import os
import sys
import subprocess
import argparse
import glob
from pathlib import Path


def setup_environment(venv_path):
    """Activate virtual environment if specified."""
    if not venv_path:
        return
    
    venv_path = Path(venv_path)
    if not venv_path.exists():
        print(f"Error: Virtual environment path does not exist: {venv_path}")
        sys.exit(1)
    
    # Determine activation script based on platform
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        if not activate_script.exists():
            activate_script = venv_path / "Scripts" / "Activate.ps1"
    else:  # Unix-like (macOS, Linux)
        activate_script = venv_path / "bin" / "activate"
    
    if not activate_script.exists():
        print(f"Error: Could not find activation script in virtual environment: {venv_path}")
        sys.exit(1)
    
    print(f"Using virtual environment: {venv_path}")


def validate_paths(input_dir, output_dir, template_file):
    """Validate that required paths and files exist."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    template_path = Path(template_file)
    
    errors = []
    
    # Check if input directory exists
    if not input_path.exists():
        errors.append(f"Input directory does not exist: {input_path}")
    elif not input_path.is_dir():
        errors.append(f"Input path is not a directory: {input_path}")
    
    # Check if template file exists
    if not template_path.exists():
        errors.append(f"Template file does not exist: {template_path}")
    elif not template_path.is_file():
        errors.append(f"Template path is not a file: {template_path}")
    
    # Check if a2l2pid.py exists
    a2l_script = Path("a2l2pid.py")
    if not a2l_script.exists():
        errors.append(f"Required script does not exist: {a2l_script}")
    
    # Create output directory if it doesn't exist
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"Created output directory: {output_path}")
        except Exception as e:
            errors.append(f"Could not create output directory {output_path}: {e}")
    
    return errors


def find_input_files(input_dir):
    """Find all files in the input directory."""
    input_path = Path(input_dir)
    files = []
    
    # Get all files in the input directory (not subdirectories)
    for file_path in input_path.iterdir():
        if file_path.is_file():
            files.append(file_path)
    
    return sorted(files)


def process_files(input_files, input_dir, output_dir, template_file, dry_run=False):
    """Process all input files or show what would be processed in dry-run mode."""
    if not input_files:
        print("No files found in input directory.")
        return
    
    print(f"Found {len(input_files)} file(s) to process:")
    
    for i, input_file in enumerate(input_files, 1):
        # Generate output filename (same base name as input, but with .csv extension)
        output_filename = input_file.stem + ".csv"
        output_file = Path(output_dir) / output_filename
        
        # Construct the command
        cmd = [
            sys.executable,  # Use the same Python interpreter
            "a2l2pid.py",
            str(input_file),
            str(template_file),
            str(output_file)
        ]
        
        cmd_str = " ".join(cmd)
        
        if dry_run:
            print(f"[{i}/{len(input_files)}] Would execute: {cmd_str}")
        else:
            print(f"[{i}/{len(input_files)}] Processing: {input_file.name} -> {output_filename}")
            print(f"  Command: {cmd_str}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"  ✓ Success")
                
                # Show any output from the script
                if result.stdout.strip():
                    print(f"  Output: {result.stdout.strip()}")
                    
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Error: Command failed with return code {e.returncode}")
                if e.stdout:
                    print(f"  Stdout: {e.stdout}")
                if e.stderr:
                    print(f"  Stderr: {e.stderr}")
            except Exception as e:
                print(f"  ✗ Error: {e}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Python environment wrapper for processing A2L files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                           # Use default settings
  python run.py --dry-run                 # Preview what would be processed
  python run.py --input-dir data/         # Use custom input directory
  python run.py --venv ./venv             # Use virtual environment
  python run.py --template custom.csv     # Use custom template file
        """
    )
    
    parser.add_argument(
        "--input-dir",
        default="input",
        help="Directory containing A2L files to process (default: input)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for output CSV files (default: output)"
    )
    
    parser.add_argument(
        "--venv",
        help="Path to Python virtual environment to activate"
    )
    
    parser.add_argument(
        "--template",
        default="pidlist.csv",
        help="Template CSV file (default: pidlist.csv)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without executing"
    )
    
    args = parser.parse_args()
    
    print("A2L to PID List Processor")
    print("=" * 40)
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be processed")
        print()
    
    # Setup virtual environment if specified
    setup_environment(args.venv)
    
    # Validate paths and files
    errors = validate_paths(args.input_dir, args.output_dir, args.template)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  ✗ {error}")
        sys.exit(1)
    
    # Find input files
    input_files = find_input_files(args.input_dir)
    
    # Process files (or show what would be processed)
    process_files(input_files, args.input_dir, args.output_dir, args.template, args.dry_run)
    
    if args.dry_run:
        print()
        print("Dry run completed. Use without --dry-run to actually process files.")
    else:
        print()
        print("Processing completed.")


if __name__ == "__main__":
    main()
