@echo off
echo ================================================
echo RoboBackup Tool - Quick IT Deployment
echo ================================================
echo.
echo This script provides quick deployment options for IT administrators.
echo.
echo Choose deployment method:
echo 1. Deploy to local computer
echo 2. Deploy via Group Policy (manual setup required)
echo 3. Fix MSI context menu for all users
echo 4. Enterprise PowerShell deployment
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Deploying to local computer...
    msiexec /i RoboBackupTool.msi /qb /l*v install.log
    echo Installation completed. Check install.log for details.
) else if "%choice%"=="2" (
    echo Group Policy deployment requires manual setup.
    echo Please read: documentation\Group-Policy-Deployment-Guide.md
    start documentation\Group-Policy-Deployment-Guide.md
) else if "%choice%"=="3" (
    echo Adding MSI context menu option...
    scripts\fix-msi-context-menu.bat
) else if "%choice%"=="4" (
    echo Starting enterprise PowerShell deployment...
    powershell -ExecutionPolicy Bypass -File scripts\Deploy-RoboBackup-Enterprise.ps1
) else (
    echo Invalid choice. Please run again.
)

pause
