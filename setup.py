#!/usr/bin/env python3
"""
Build script for RoboBackup Tool unified executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_executables():
    """Build GUI executable using PyInstaller"""
    print("Building Data Sync Tool GUI application with PyInstaller...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Build main GUI application
    success = build_main_app()
    
    return success

def build_main_app():
    """Build the main GUI application"""
    print("Building main GUI application...")
    
    # PyInstaller command for main app
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",  # No console window for GUI
        "--version-file=pyinstaller_version.txt",
        "--name=DataSyncTool"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=assets;assets",
        "--add-data=config;config",
        "--add-data=resources;resources",
        "--add-data=utils;utils",
        "backupapp.py"
    ])
    
    try:
        subprocess.check_call(cmd)
        print("OK Main application built successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "DataSyncTool.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "DataSyncTool.exe")
            print("OK Main executable copied to current directory")
            return True
        
        print("FAIL Could not find built main executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Main app build failed: {e}")
        return False





def main():
    """Main build process"""
    print("=== Data Sync Tool v2.0.0 Build Process ===\n")
    
    # Build GUI executable
    if not build_executables():
        print("\nFAIL Failed to build executable")
        return 1
    
    print("\n=== Build Complete ===")
    print("OK GUI executable created:")
    print("   - DataSyncTool.exe (Main GUI application)")
    print()
    print("Features included in v2.0.0:")
    print("   • Manual backup execution")
    print("   • Robocopy integration")
    print("   • Network drive mapping") 
    print("   • Encrypted credential storage")
    print("   • Comprehensive logging")
    print()
    print("OK Ready for distribution!")
    print("Note: Service functionality will be available in v1.1.0")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 