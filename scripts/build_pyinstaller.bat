@echo off
echo Building RoboBackup Tool with PyInstaller...
echo.

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "RoboBackups.spec" del RoboBackups.spec

REM Build using the spec file
echo Building executable...
pyinstaller --onefile --windowed --icon=Crap/robot_copier.ico --name RoboBackups --uac-admin --manifest=app.manifest --add-data "robot_copier.ico;." --add-data "config;config" --add-data "logs;logs" --hidden-import win32api --hidden-import win32con --hidden-import win32netcon --hidden-import win32wnet --hidden-import cryptography --hidden-import hashlib --hidden-import secrets --hidden-import stat --hidden-import shutil --hidden-import glob --hidden-import logging --hidden-import json --hidden-import subprocess --hidden-import threading --hidden-import datetime --hidden-import time --hidden-import os --hidden-import sys --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.messagebox --hidden-import tkinter.filedialog backupapp.py

REM Copy executable to current directory
echo Copying executable...
copy "dist\RoboBackups.exe" "RoboBackups.exe"

echo.
echo Build complete! You can now run RoboBackups.exe
echo Right-click and select "Run as administrator" for full functionality.
pause 