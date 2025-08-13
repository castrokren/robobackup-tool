@echo off
echo ========================================
echo RoboBackup Tool - Build and Sign
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

:: Set variables
set "CERT_FILE=RoboBackupTool_CodeSigning.pfx"
set "CERT_PASSWORD=RoboBackup2024!"

:: Check if certificate exists
if not exist "%CERT_FILE%" (
    echo.
    echo ========================================
    echo Creating Code Signing Certificate
    echo ========================================
    call "create_self_signed_cert.bat"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create certificate!
        pause
        exit /b 1
    )
)

echo Certificate ready: %CERT_FILE%

:: Build MSI installer
echo.
echo ========================================
echo Building MSI Installer
echo ========================================

cd ..
cd installers
call "build-msi.bat"

if %errorlevel% neq 0 (
    echo ERROR: Failed to build MSI installer!
    pause
    exit /b 1
)

echo MSI installer built successfully!

:: Sign all executables and MSI
echo.
echo ========================================
echo Signing Executables and MSI
echo ========================================

cd ..
cd scripts
call "sign_executables.bat"

if %errorlevel% neq 0 (
    echo ERROR: Failed to sign executables!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build and Sign Complete!
echo ========================================
echo.
echo Files created and signed:
echo - dist\backupapp.exe
echo - dist\backup_service.exe  
echo - dist\backup_core.exe
echo - dist\RoboBackupTool-1.0.0.0.msi
echo.
echo All files are now signed and ready for distribution!
echo Users will not see "Unknown Publisher" warnings.
echo.

pause
