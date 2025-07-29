#!/usr/bin/env python3
"""
Requirements Pinning Script
Automatically pins requirements to their current installed versions.
"""

import subprocess
import sys
import re
from pathlib import Path

def get_installed_version(package_name):
    """Get the currently installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output to find the version
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
        
        return None
    except subprocess.CalledProcessError:
        return None

def pin_requirements_file(file_path):
    """Pin all requirements in a file to their current versions."""
    if not Path(file_path).exists():
        print(f"File {file_path} not found!")
        return
    
    print(f"Pinning requirements in {file_path}...")
    
    # Read current requirements
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    pinned_lines = []
    updated_count = 0
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            pinned_lines.append(line)
            continue
        
        # Parse package name and version constraint
        match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
        if match:
            package_name = match.group(1)
            version_constraint = match.group(2)
            
            # Get current installed version
            installed_version = get_installed_version(package_name)
            
            if installed_version:
                pinned_lines.append(f"{package_name}=={installed_version}")
                updated_count += 1
                print(f"  Pinned {package_name} to {installed_version}")
            else:
                # Keep original if can't determine version
                pinned_lines.append(line)
                print(f"  Could not determine version for {package_name}, keeping original")
        else:
            pinned_lines.append(line)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write('\n'.join(pinned_lines) + '\n')
    
    print(f"Updated {updated_count} packages in {file_path}")

def main():
    """Main function to pin requirements files."""
    files_to_pin = [
        'requirements-windows.txt',
        'requirements-linux.txt',
        'requirements.txt'
    ]
    
    print("🔧 Requirements Pinning Tool")
    print("=" * 40)
    
    for file_path in files_to_pin:
        if Path(file_path).exists():
            pin_requirements_file(file_path)
            print()
    
    print("✅ Pinning complete!")
    print("\n📋 Next steps:")
    print("1. Test your application with pinned versions")
    print("2. Commit the updated requirements files")
    print("3. Update your SLSA workflow to use pinned versions")

if __name__ == "__main__":
    main() 