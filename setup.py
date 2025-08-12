#!/usr/bin/env python3
"""
Build script for RoboBackup Tool executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",  # No console window
        "--name=RoboBackupApp"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=assets/robot_copier.ico;.",
        "--add-data=backup_service.py;.",
        "--add-data=service_manager.bat;.",
        "--add-data=install_service.bat;.",
        "--add-data=create_scheduled_task.ps1;.",

        "--add-data=config;config",
        "--add-data=logs;logs",
        "backupapp.py"
    ])
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    try:
        subprocess.check_call(cmd)
        print("OK Build completed successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "RoboBackupApp.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "RoboBackupApp.exe")
            print("OK Executable copied to current directory")
            return True
        
        print("FAIL Could not find built executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Build failed: {e}")
        return False

def main():
    """Main build process"""
    print("=== RoboBackup Tool Build Process ===\n")
    
    # Build executable
    if not build_executable():
        print("\nFAIL Failed to build executable")
        return 1
    
    print("\n=== Build Complete ===")
    print("OK RoboBackupApp.exe created")
    print("OK You can now run the executable with proper metadata")
    print("OK Right-click and 'Run as administrator' for full functionality")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 