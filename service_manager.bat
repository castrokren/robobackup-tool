@echo off
setlocal enabledelayedexpansion

echo RoboBackup Service Manager
echo =========================

if "%1"=="" (
    echo Usage: %0 [start^|stop^|status^|remove^|install]
    echo.
    echo Commands:
    echo   start   - Start the backup service
    echo   stop    - Stop the backup service  
    echo   status  - Check service status
    echo   remove  - Remove the service
    echo   install - Install the service
    echo.
    pause
    exit /b 0
)

REM Check if running as administrator for install/remove operations
if "%1"=="install" (
    net session >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Install requires administrator privileges
        echo Please right-click and "Run as administrator"
        pause
        exit /b 1
    )
)

if "%1"=="remove" (
    net session >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Remove requires administrator privileges
        echo Please right-click and "Run as administrator"
        pause
        exit /b 1
    )
)

REM Change to the script directory
cd /d "%~dp0"

echo Executing: python backup_service.py %1
python backup_service.py %1

if %errorLevel% == 0 (
    echo.
    echo Operation completed successfully
) else (
    echo.
    echo ERROR: Operation failed
)

if "%1"=="start" (
    echo.
    echo The service is now running and will execute scheduled backups
    echo even when you're not logged in.
    echo.
    echo Check logs/backup_service.log for service activity.
)

if "%1"=="install" (
    echo.
    echo Service installed successfully!
    echo.
    echo To start the service, run:
    echo   %0 start
    echo.
    echo The service will now run scheduled backups even when you're not logged in.
)

pause 