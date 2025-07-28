#!/usr/bin/env python3
"""
GitHub Repository Initialization Script
This script helps set up the initial GitHub repository structure.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Initialize the GitHub repository"""
    print("GitHub Repository Initialization")
    print("=" * 40)
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("Git is not installed or not in PATH. Please install Git first.")
        return False
    
    # Initialize git repository
    if not os.path.exists(".git"):
        if not run_command("git init", "Initializing Git repository"):
            return False
    else:
        print("✓ Git repository already exists")
    
    # Add all files
    if not run_command("git add .", "Adding files to Git"):
        return False
    
    # Create initial commit
    if not run_command('git commit -m "Initial commit: Windows Backup Tool"', "Creating initial commit"):
        return False
    
    print("\nRepository setup completed!")
    print("\nNext steps:")
    print("1. Create a new repository on GitHub")
    print("2. Add the remote origin:")
    print("   git remote add origin https://github.com/yourusername/windows-backup-tool.git")
    print("3. Push to GitHub:")
    print("   git push -u origin main")
    print("\nOptional: Set up branch protection rules and other GitHub settings")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 