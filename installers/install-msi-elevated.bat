@echo off
setlocal enabledelayedexpansion

echo ========================================
echo RoboBackup Tool MSI Elevated Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - proceeding with installation
    goto :install
) else (
    echo Not running as administrator - attempting elevation...
    goto :elevate
)

:elevate
echo.
echo Attempting to restart with administrator privileges...
echo If UAC prompt appears, click "Yes" to continue.
echo.

REM Try PowerShell elevation first
powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs" && exit

REM If PowerShell fails, show manual instructions
echo.
echo AUTOMATIC ELEVATION FAILED
echo ========================
echo.
echo Please manually run this installer as administrator:
echo 1. Right-click this batch file
echo 2. Select "Run as administrator"
echo 3. Click "Yes" when UAC prompt appears
echo.
echo OR use Command Prompt as Administrator:
echo 1. Press Win+X and select "Command Prompt (Admin)"
echo 2. Navigate to this directory: cd /d "%~dp0"
echo 3. Run: install-msi-elevated.bat
echo.
pause
exit /b 1

:install
echo ========================================
echo Installing MSI with Administrator Rights
echo ========================================
echo.

REM Find MSI file
set "MSI_FILE="
for %%f in ("%~dp0*.msi") do (
    if exist "%%f" (
        set "MSI_FILE=%%f"
        goto :found_msi
    )
)

REM Check parent directory
for %%f in ("%~dp0..\dist\RoboBackupTool*.msi") do (
    if exist "%%f" (
        set "MSI_FILE=%%f"
        goto :found_msi
    )
)

REM Check current directory
for %%f in ("RoboBackupTool*.msi") do (
    if exist "%%f" (
        set "MSI_FILE=%%f"
        goto :found_msi
    )
)

echo ERROR: Could not find RoboBackupTool MSI file!
echo.
echo Please ensure the MSI file is in one of these locations:
echo - Same directory as this batch file
echo - Parent directory's dist folder
echo - Current working directory
echo.
pause
exit /b 1

:found_msi
echo Found MSI file: !MSI_FILE!
echo.

REM Create log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
set "LOG_FILE=%~dp0install_%timestamp%.log"

echo Installing with logging to: !LOG_FILE!
echo.
echo Starting installation...
echo.

REM Install MSI with verbose logging
msiexec /i "!MSI_FILE!" /l*v "!LOG_FILE!"

if %errorLevel% == 0 (
    echo.
    echo ========================================
    echo Installation completed successfully!
    echo ========================================
    echo.
    echo RoboBackup Tool has been installed to:
    echo Program Files\RoboBackup Tool\
    echo.
    echo The RoboBackup Windows Service has been installed and started.
    echo You can now access the application from:
    echo - Start Menu ^> RoboBackup Tool
    echo - Desktop shortcut
    echo.
) else (
    echo.
    echo ========================================
    echo Installation failed with error code: %errorLevel%
    echo ========================================
    echo.
    echo Common error codes:
    echo 1603 - Fatal error during installation
    echo 1619 - Installation package could not be opened
    echo 1633 - Installation package not supported on this platform
    echo.
    echo Check the log file for details: !LOG_FILE!
    echo.
    echo Troubleshooting steps:
    echo 1. Ensure no antivirus is blocking the installation
    echo 2. Close any running instances of RoboBackup Tool
    echo 3. Try running Windows Installer troubleshooter
    echo 4. Restart computer and try again
    echo.
)

echo.
echo Log file saved to: !LOG_FILE!
echo.
pause
