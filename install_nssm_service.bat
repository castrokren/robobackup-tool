@echo off
echo Installing RoboBackup Service using NSSM...

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

REM Check if NSSM exists
if not exist "nssm.exe" (
    echo ERROR: nssm.exe not found!
    echo Please download NSSM from https://nssm.cc/download
    echo and place nssm.exe in this directory.
    pause
    exit /b 1
)

REM Check if service executable exists
if not exist "service_simple.exe" (
    echo ERROR: service_simple.exe not found!
    echo Please ensure the service executable is built.
    pause
    exit /b 1
)

REM Remove existing service if it exists
echo Removing any existing RoboBackupService...
nssm remove RoboBackupService confirm >nul 2>&1

REM Install the service
echo Installing RoboBackup Service...
nssm install RoboBackupService "%~dp0service_simple.exe"

if %errorLevel% == 0 (
    echo Service installed successfully!
    
    REM Configure the service
    echo Configuring service settings...
    nssm set RoboBackupService DisplayName "RoboBackup Backup Service"
    nssm set RoboBackupService Description "Runs scheduled backups for RoboBackup Tool"
    nssm set RoboBackupService Start SERVICE_AUTO_START
    nssm set RoboBackupService AppDirectory "%~dp0"
    nssm set RoboBackupService AppStdout "%~dp0logs\service_stdout.log"
    nssm set RoboBackupService AppStderr "%~dp0logs\service_stderr.log"
    
    echo.
    echo Service configuration:
    echo - Service Name: RoboBackupService
    echo - Display Name: RoboBackup Backup Service
    echo - Startup Type: Automatic
    echo - Working Directory: %~dp0
    echo.
    
    echo To start the service now, run:
    echo   nssm start RoboBackupService
    echo.
    echo To stop the service, run:
    echo   nssm stop RoboBackupService
    echo.
    echo To remove the service, run:
    echo   nssm remove RoboBackupService confirm
    echo.
    echo The service will now run scheduled backups even when you're not logged in.
    
) else (
    echo ERROR: Failed to install service
    echo Please check that nssm.exe and service_simple.exe are present
)

pause
