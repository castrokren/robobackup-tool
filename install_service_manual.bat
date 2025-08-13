@echo off
echo ========================================
echo RoboBackup Service Manual Installation
echo ========================================

:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Running as Administrator - OK

:: Check if service executable exists
if not exist "backup_service.exe" (
    echo ERROR: backup_service.exe not found!
    echo Please run this script from the RoboBackup Tool installation directory
    pause
    exit /b 1
)

echo Service executable found - OK

:: Stop and remove existing service if it exists
echo Checking for existing service...
sc query "RoboBackupService" >nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping existing service...
    sc stop "RoboBackupService" >nul 2>&1
    timeout /t 3 /nobreak >nul
    
    echo Removing existing service...
    sc delete "RoboBackupService" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: Install the service
echo Installing RoboBackup Service...
backup_service.exe install

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Service installed successfully!
    echo ========================================
    echo.
    echo To start the service, run:
    echo   sc start RoboBackupService
    echo.
    echo To stop the service, run:
    echo   sc stop RoboBackupService
    echo.
    echo To remove the service, run:
    echo   backup_service.exe remove
    echo.
) else (
    echo.
    echo ========================================
    echo Service installation failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
