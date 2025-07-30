#!/usr/bin/env python3
"""
Build script for RoboBackup Tool executable
"""

import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install required packages for building"""
    print("Installing build requirements...")
    requirements = [
        "cx_Freeze",
        "pywin32",
        "cryptography"
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"OK Installed {req}")
        except subprocess.CalledProcessError:
            print(f"FAIL Failed to install {req}")
            return False
    return True

def build_executable():
    """Build the executable"""
    print("Building executable...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    try:
        # Build the executable
        subprocess.check_call([sys.executable, "setup.py", "build"])
        print("OK Build completed successfully")
        
        # Copy executable to current directory
        build_dir = None
        for item in os.listdir("build"):
            if item.startswith("exe."):
                build_dir = os.path.join("build", item)
                break
        
        if build_dir and os.path.exists(build_dir):
            exe_path = os.path.join(build_dir, "RoboBackupApp.exe")
            if os.path.exists(exe_path):
                shutil.copy2(exe_path, "RoboBackupApp.exe")
                print("OK Executable copied to current directory")
                return True
        
        print("FAIL Could not find built executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Build failed: {e}")
        return False

def create_installer():
    """Create an installer using NSIS"""
    print("Creating installer...")
    
    # Check if NSIS is available
    try:
        subprocess.check_call(["makensis", "/VERSION"], capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARN NSIS not found. Installer creation skipped.")
        print("  Download NSIS from: https://nsis.sourceforge.io/Download")
        return False
    
    try:
        # Create installer
        subprocess.check_call(["makensis", "installer.nsi"])
        print("OK Installer created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"FAIL Installer creation failed: {e}")
        return False

def main():
    """Main build process"""
    print("=== RoboBackup Tool Build Process ===\n")
    
    # Install requirements
    if not install_requirements():
        print("\nFAIL Failed to install requirements")
        return 1
    
    # Build executable
    if not build_executable():
        print("\nFAIL Failed to build executable")
        return 1
    
    # Create installer (optional)
    create_installer()
    
    print("\n=== Build Complete ===")
    print("OK RoboBackupApp.exe created")
    print("OK You can now run the executable with proper metadata")
    print("OK Right-click and 'Run as administrator' for full functionality")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 