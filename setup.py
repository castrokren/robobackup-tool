#!/usr/bin/env python3
"""
Build script for RoboBackup Tool unified executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil

def build_executables():
    """Build all three executables using PyInstaller"""
    print("Building RoboBackup executables with PyInstaller...")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    success = True
    
    # Build main GUI application
    success &= build_main_app()
    
    # Build service executable
    success &= build_service()
    
    # Build core executable (if backup_core.py exists)
    if os.path.exists("backup_core.py"):
        success &= build_core()
    
    return success

def build_main_app():
    """Build the main GUI application"""
    print("Building main GUI application...")
    
    # PyInstaller command for main app
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",  # No console window for GUI
        "--name=backupapp"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=assets;assets",
        "--add-data=config;config",
        "--add-data=utils;utils",
        "backupapp.py"
    ])
    
    try:
        subprocess.check_call(cmd)
        print("OK Main application built successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "backupapp.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "backupapp.exe")
            print("OK Main executable copied to current directory")
            return True
        
        print("FAIL Could not find built main executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Main app build failed: {e}")
        return False

def build_service():
    """Build the service executable"""
    print("Building service executable...")
    
    # PyInstaller command for service
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Console window for service
        "--name=backup_service",
        "--hidden-import=win32timezone",
        "--hidden-import=win32serviceutil",
        "--hidden-import=win32service", 
        "--hidden-import=win32event",
        "--hidden-import=servicemanager",
        "--hidden-import=win32api",
        "--hidden-import=win32con",
        "--hidden-import=pywintypes"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=config;config",
        "--add-data=utils;utils",
        "backup_service.py"
    ])
    
    # Also build simple service for NSSM
    success = build_simple_service()
    
    if not success:
        return False
    
    try:
        subprocess.check_call(cmd)
        print("OK Service executable built successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "backup_service.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "backup_service.exe")
            print("OK Service executable copied to current directory")
            return True
        
        print("FAIL Could not find built service executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Service build failed: {e}")
        return False

def build_simple_service():
    """Build the simple service executable for NSSM"""
    print("Building simple service executable for NSSM...")
    
    # PyInstaller command for simple service
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Console window for service
        "--name=service_simple"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=config;config",
        "--add-data=utils;utils",
        "service_simple.py"
    ])
    
    try:
        subprocess.check_call(cmd)
        print("OK Simple service executable built successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "service_simple.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "service_simple.exe")
            print("OK Simple service executable copied to current directory")
            return True
        
        print("FAIL Could not find built simple service executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Simple service build failed: {e}")
        return False

def build_core():
    """Build the core executable"""
    print("Building core executable...")
    
    # PyInstaller command for core
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",  # Console window for core
        "--name=backup_core"
    ]
    
    # Add icon if it exists
    if os.path.exists("assets/robot_copier.ico"):
        cmd.append("--icon=assets/robot_copier.ico")
    
    # Add data files
    cmd.extend([
        "--add-data=config;config",
        "--add-data=utils;utils",
        "backup_core.py"
    ])
    
    try:
        subprocess.check_call(cmd)
        print("OK Core executable built successfully")
        
        # Copy executable to current directory
        exe_path = os.path.join("dist", "backup_core.exe")
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, "backup_core.exe")
            print("OK Core executable copied to current directory")
            return True
        
        print("FAIL Could not find built core executable")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"FAIL Core build failed: {e}")
        return False

def main():
    """Main build process"""
    print("=== RoboBackup Tool Build Process ===\n")
    
    # Build all executables
    if not build_executables():
        print("\nFAIL Failed to build one or more executables")
        return 1
    
    print("\n=== Build Complete ===")
    print("OK All executables created:")
    print("   - backupapp.exe (Main GUI application)")
    print("   - backup_service.exe (Windows Service)")
    if os.path.exists("backup_core.exe"):
        print("   - backup_core.exe (Core engine)")
    print()
    print("Service installation:")
    print("   backup_service.exe install        # Install Windows Service")
    print("   backup_service.exe start          # Start Windows Service")
    print("   backup_service.exe stop           # Stop Windows Service")
    print("   backup_service.exe remove         # Remove Windows Service")
    print()
    print("OK Ready for MSI packaging!")
    print("OK Run 'install_service.bat' as administrator to install service")
    print()
    print("NSSM Alternative (Recommended):")
    print("   1. Run: powershell -ExecutionPolicy Bypass .\\download_nssm.ps1")
    print("   2. Run: install_nssm_service.bat (as administrator)")
    print("   This uses NSSM for simpler service installation")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 