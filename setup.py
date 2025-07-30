import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "tkinter", 
        "os", 
        "sys", 
        "json", 
        "subprocess", 
        "threading", 
        "datetime", 
        "time",
        "win32api",
        "win32con",
        "win32netcon",
        "win32wnet",
        "cryptography",
        "hashlib",
        "secrets",
        "stat",
        "shutil",
        "glob",
        "logging",
        "pystray",
        "PIL",
        "qrcode",
        "pyotp",
        "numpy",
        "psutil",
        "urllib3",
        "certifi"
    ],
    "excludes": [],
    "include_files": [
        ("assets/robot_copier.ico", "robot_copier.ico"),
        ("config/", "config/"),
        ("logs/", "logs/"),
        ("app.manifest", "app.manifest")
    ] if os.path.exists("app.manifest") else [
        ("assets/robot_copier.ico", "robot_copier.ico"),
        ("config/", "config/"),
        ("logs/", "logs/")
    ]
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="RoboBackup Tool",
    version="1.0.0",
    description="Secure Backup Application with Network Support",
    author="Your Name",
    author_email="your.email@example.com",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "backupapp.py", 
            base=base,
            icon="assets/robot_copier.ico" if os.path.exists("assets/robot_copier.ico") else None,
            target_name="RoboBackupApp.exe",
            shortcut_name="RoboBackup Tool",
            shortcut_dir="DesktopFolder",
            manifest="app.manifest" if os.path.exists("app.manifest") else None
        )
    ]
) 