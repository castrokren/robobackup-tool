@echo off
REM Self-extracting installer that users can run directly
REM This creates a user-friendly installer that handles admin elevation automatically

setlocal enabledelayedexpansion

echo ====================================================
echo         RoboBackup Tool Installer v1.0
echo ====================================================
echo.
echo Welcome to the RoboBackup Tool installation wizard.
echo This installer will set up RoboBackup Tool on your computer.
echo.

REM Check for MSI file in the same directory
set "MSI_FILE="
for %%f in ("%~dp0RoboBackupTool*.msi") do (
    if exist "%%f" (
        set "MSI_FILE=%%f"
        goto :found_msi
    )
)

echo ERROR: RoboBackupTool MSI file not found!
echo Please ensure this installer is in the same folder as the MSI file.
echo.
pause
exit /b 1

:found_msi
echo Installation package: !MSI_FILE!
echo.

REM Display what will be installed
echo What will be installed:
echo - RoboBackup Tool application
echo - Windows backup service (for scheduled backups)
echo - Start menu shortcuts
echo - Desktop shortcut
echo.

REM Check current privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Status: Running with administrator privileges
    goto :install_direct
) else (
    echo Status: Standard user privileges detected
    echo.
    echo Administrator privileges are required for:
    echo - Installing Windows services
    echo - Writing to Program Files directory
    echo - Creating system-wide shortcuts
    echo.
    goto :request_elevation
)

:request_elevation
echo The installer will now request administrator privileges.
echo.
echo IMPORTANT: When the UAC prompt appears:
echo 1. Click "Yes" to allow the installation
echo 2. This is safe and required for proper installation
echo.
set /p "continue=Press Enter to continue with installation (or Ctrl+C to cancel)..."

REM Try to restart with elevation using PowerShell
echo.
echo Requesting administrator privileges...
powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs -ArgumentList 'elevated'" >nul 2>&1

if %errorLevel% == 0 (
    echo Elevation request sent. This window will close when the elevated installer starts.
    timeout /t 3 >nul
    exit
) else (
    echo.
    echo Automatic elevation failed. Please use one of these methods:
    echo.
    echo METHOD 1 - Right-click method:
    echo 1. Right-click this installer file
    echo 2. Select "Run as administrator"
    echo 3. Click "Yes" when prompted
    echo.
    echo METHOD 2 - Command prompt method:
    echo 1. Press Win+X and select "Command Prompt (Admin)"
    echo 2. Navigate to: cd /d "%~dp0"
    echo 3. Run: "%~nx0"
    echo.
    pause
    exit /b 1
)

:install_direct
if "%1"=="elevated" (
    echo Installation continuing with administrator privileges...
    echo.
)

REM Create installation log
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,8%_%dt:~8,6%"
set "LOG_FILE=%TEMP%\RoboBackup_Install_%timestamp%.log"

echo Starting installation...
echo Log file: !LOG_FILE!
echo.

REM Install the MSI
echo Installing RoboBackup Tool...
msiexec /i "!MSI_FILE!" /qb /l*v "!LOG_FILE!"

set "exit_code=%errorLevel%"

echo.
if !exit_code! == 0 (
    echo ====================================================
    echo      Installation completed successfully!
    echo ====================================================
    echo.
    echo RoboBackup Tool has been installed and is ready to use.
    echo.
    echo You can access the application from:
    echo - Start Menu ^> RoboBackup Tool
    echo - Desktop shortcut
    echo.
    echo The RoboBackup service has been installed and will run
    echo scheduled backups automatically.
    echo.
    echo Installation log saved to: !LOG_FILE!
    echo.
) else (
    echo ====================================================
    echo           Installation failed!
    echo ====================================================
    echo.
    echo Error code: !exit_code!
    echo.
    echo Please check the installation log: !LOG_FILE!
    echo.
    echo Common solutions:
    echo 1. Ensure no antivirus is blocking the installation
    echo 2. Close any running backup applications
    echo 3. Restart your computer and try again
    echo 4. Contact your IT administrator if the problem persists
    echo.
)

echo Installation log location: !LOG_FILE!
echo.
pause
