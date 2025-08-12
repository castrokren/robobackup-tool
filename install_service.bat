@echo off
echo Installing RoboBackup Service...

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - proceeding with installation
) else (
    echo ERROR: This script must be run as administrator
    echo Please right-click and "Run as administrator"
    pause
    exit /b 1
)

REM Change to the script directory
cd /d "%~dp0"

REM Install the service
echo Installing RoboBackup Service...
backup_service.exe install

if %errorLevel% == 0 (
    echo Service installed successfully
    echo.
    echo To start the service, run:
    echo   backup_service.exe start
    echo.
    echo To stop the service, run:
    echo   backup_service.exe stop
    echo.
    echo To remove the service, run:
    echo   backup_service.exe remove
    echo.
    echo The service will now run scheduled backups even when you're not logged in.
) else (
    echo ERROR: Failed to install service
    echo Please check that backup_service.exe is present
)

pause 