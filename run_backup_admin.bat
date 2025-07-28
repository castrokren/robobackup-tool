@echo off
echo Starting Backup App as Administrator...
cd /d "%~dp0"
python backupapp.py
pause 