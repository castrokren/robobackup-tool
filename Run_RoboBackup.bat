@echo off
echo Starting RoboBackup Tool...
echo.
echo For full functionality, make sure to run as Administrator
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges
) else (
    echo [WARNING] Not running as Administrator - some features may be limited
    echo   Right-click this file and select "Run as administrator" for full access
)

echo.
echo Launching RoboBackup...
"dist\RoboBackup.exe"

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Error occurred while running RoboBackup
    echo Check the logs directory for more information
    pause
)
