#!/usr/bin/env python
"""
Script to identify and remove debugging artifacts from the codebase.

This script scans Python files for common debugging artifacts such as:
- print statements for debugging
- pdb/ipdb breakpoints
- commented-out code blocks
- TODO comments
- Unused imports
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple, Dict


# Patterns to search for
PATTERNS = {
    "print_debug": r'print\([\'"]?DEBUG|TRACE|LOG|TEMP|FIXME|REMOVE|DELETEME[\'"]?',
    "breakpoints": r'(import pdb|import ipdb|pdb\.set_trace\(\)|ipdb\.set_trace\(\)|breakpoint\(\))',
    "commented_code": r'^\s*#\s*(def |class |import |from |if |for |while |try:)',
    "todo_comments": r'# TODO|# FIXME|# XXX|# HACK',
    "unused_imports": r'^\s*(import|from .* import).*# noqa' 
}


def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the given directory, recursively."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip virtual environment directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '.venv']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(os.path.join(root, file)))
                
    return python_files


def scan_file(file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
    """Scan a Python file for debugging artifacts."""
    results = {pattern_name: [] for pattern_name in PATTERNS}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines, 1):
        for pattern_name, pattern in PATTERNS.items():
            if re.search(pattern, line):
                results[pattern_name].append((i, line.rstrip()))
                
    return results


def scan_directory(root_dir: str, fix: bool = False) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """Scan a directory for debugging artifacts."""
    python_files = find_python_files(root_dir)
    results = {}
    
    for file_path in python_files:
        file_results = scan_file(file_path)
        
        # Only include files with at least one match
        if any(matches for matches in file_results.values()):
            results[str(file_path)] = file_results
            
            if fix:
                try:
                    fix_file(file_path, file_results)
                except Exception as e:
                    print(f"Error fixing {file_path}: {e}")
    
    return results


def fix_file(file_path: Path, results: Dict[str, List[Tuple[int, str]]]) -> None:
    """Remove debugging artifacts from a file (only certain types)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create a set of line numbers to remove
    lines_to_remove = set()
    
    # Collect line numbers to remove for certain artifact types
    for pattern_name, matches in results.items():
        if pattern_name in ['print_debug', 'breakpoints']:
            lines_to_remove.update(line_num - 1 for line_num, _ in matches)
    
    # Skip if no lines to remove
    if not lines_to_remove:
        return
        
    # Write the file back, skipping the lines to remove
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            if i not in lines_to_remove:
                f.write(line)
                
    print(f"✅ Fixed {file_path}: removed {len(lines_to_remove)} lines")


def print_results(results: Dict[str, Dict[str, List[Tuple[int, str]]]]) -> None:
    """Print scan results in a readable format."""
    total_issues = 0
    
    for file_path, file_results in results.items():
        file_issues = sum(len(matches) for matches in file_results.values())
        total_issues += file_issues
        
        if file_issues > 0:
            print(f"\n📄 {file_path}: {file_issues} issues")
            
            for pattern_name, matches in file_results.items():
                if matches:
                    print(f"  🔍 {pattern_name}: {len(matches)} matches")
                    for line_num, line in matches[:5]:  # Show max 5 matches per type
                        print(f"    Line {line_num}: {line[:70]}{'...' if len(line) > 70 else ''}")
                    
                    if len(matches) > 5:
                        print(f"    ... and {len(matches) - 5} more")
    
    print(f"\n🔍 Total issues found: {total_issues}")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Find debugging artifacts in Python code")
    parser.add_argument("directory", nargs="?", default="src", help="Directory to scan (default: src)")
    parser.add_argument("--fix", action="store_true", help="Automatically fix certain issues")
    args = parser.parse_args()
    
    print(f"Scanning {args.directory} for debugging artifacts...")
    results = scan_directory(args.directory, fix=args.fix)
    
    if not results:
        print("No debugging artifacts found! 🎉")
        return 0
        
    print_results(results)
    
    if args.fix:
        print("\nSome issues were automatically fixed. Re-run the script to check for remaining issues.")
    else:
        print("\nRun with --fix to automatically remove print statements and breakpoints.")
    
    return 1


if __name__ == "__main__":
    sys.exit(main()) 