@echo off
setlocal enabledelayedexpansion

echo ================================================
echo RoboBackup Tool Enterprise Deployment Package
echo ================================================
echo.
echo This script creates a complete deployment package
echo for enterprise distribution of RoboBackup Tool.
echo.

REM Set variables
set "PROJECT_ROOT=%~dp0.."
set "BUILD_DIR=%PROJECT_ROOT%\build"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "DEPLOY_DIR=%PROJECT_ROOT%\deployment-package"
set "VERSION=1.0.0.0"

echo Creating deployment package...
echo.

REM Create deployment directory structure
if exist "%DEPLOY_DIR%" rmdir /s /q "%DEPLOY_DIR%"
mkdir "%DEPLOY_DIR%"
mkdir "%DEPLOY_DIR%\installers"
mkdir "%DEPLOY_DIR%\scripts"
mkdir "%DEPLOY_DIR%\documentation"

echo ✓ Created directory structure

REM Check if MSI exists
if not exist "%DIST_DIR%\RoboBackupTool-%VERSION%.msi" (
    echo.
    echo ERROR: MSI file not found!
    echo Please run build-msi.bat first to create the MSI installer.
    echo Expected location: %DIST_DIR%\RoboBackupTool-%VERSION%.msi
    echo.
    pause
    exit /b 1
)

REM Copy MSI installer
copy "%DIST_DIR%\RoboBackupTool-%VERSION%.msi" "%DEPLOY_DIR%\RoboBackupTool.msi"
echo ✓ Copied MSI installer

REM Copy user-friendly installers
copy "%~dp0RoboBackupInstaller.exe.bat" "%DEPLOY_DIR%\RoboBackupInstaller.bat"
copy "%~dp0install-msi-admin.ps1" "%DEPLOY_DIR%\installers\"
copy "%~dp0install-msi-elevated.bat" "%DEPLOY_DIR%\installers\"
echo ✓ Copied user installers

REM Copy enterprise deployment scripts
copy "%~dp0Deploy-RoboBackup-Enterprise.ps1" "%DEPLOY_DIR%\scripts\"
copy "%~dp0fix-msi-context-menu.bat" "%DEPLOY_DIR%\scripts\"
copy "%~dp0add-run-as-admin.reg" "%DEPLOY_DIR%\scripts\"
echo ✓ Copied enterprise scripts

REM Copy documentation
copy "%~dp0Group-Policy-Deployment-Guide.md" "%DEPLOY_DIR%\documentation\"
copy "%~dp0MSI_PACKAGING_README.md" "%DEPLOY_DIR%\documentation\"
echo ✓ Copied documentation

REM Create main README for deployment package
echo Creating deployment README...
(
echo # RoboBackup Tool - Enterprise Deployment Package
echo.
echo This package contains everything needed to deploy RoboBackup Tool in an enterprise environment.
echo.
echo ## Package Contents
echo.
echo ### Main Installer
echo - `RoboBackupTool.msi` - Main MSI installer package
echo - `RoboBackupInstaller.bat` - User-friendly installer with automatic elevation
echo.
echo ### For IT Administrators
echo - `scripts/Deploy-RoboBackup-Enterprise.ps1` - PowerShell enterprise deployment script
echo - `scripts/fix-msi-context-menu.bat` - Adds "Run as administrator" context menu
echo - `scripts/add-run-as-admin.reg` - Registry file for context menu fix
echo.
echo ### For End Users
echo - `installers/install-msi-elevated.bat` - Self-elevating installer
echo - `installers/install-msi-admin.ps1` - PowerShell installer with admin checks
echo.
echo ### Documentation
echo - `documentation/Group-Policy-Deployment-Guide.md` - Complete Group Policy setup guide
echo - `documentation/MSI_PACKAGING_README.md` - Technical MSI information
echo.
echo ## Quick Start
echo.
echo ### For End Users
echo 1. Double-click `RoboBackupInstaller.bat`
echo 2. Click "Yes" when UAC prompt appears
echo 3. Follow installation wizard
echo.
echo ### For IT Administrators - Group Policy Deployment
echo 1. Read `documentation/Group-Policy-Deployment-Guide.md`
echo 2. Copy `RoboBackupTool.msi` to network share
echo 3. Create Group Policy Object for software installation
echo 4. Deploy to target computers/users
echo.
echo ### For IT Administrators - Script Deployment
echo 1. Run PowerShell as Administrator
echo 2. Execute: `scripts/Deploy-RoboBackup-Enterprise.ps1`
echo 3. Monitor deployment logs
echo.
echo ## System Requirements
echo - Windows 10 1809 or later / Windows Server 2019 or later
echo - Administrator privileges for installation
echo - .NET Framework 4.7.2 or later
echo - 512 MB RAM minimum
echo - 100 MB disk space
echo.
echo ## Enterprise Features
echo - Silent installation support
echo - Group Policy deployment ready
echo - Windows Service installation
echo - Automatic privilege elevation
echo - Comprehensive logging
echo - SCCM/Intune compatible
echo.
echo ## Support
echo For technical support or questions:
echo 1. Check the documentation folder
echo 2. Review installation logs
echo 3. Contact your IT administrator
echo.
echo Generated on: %DATE% %TIME%
echo Package Version: %VERSION%
) > "%DEPLOY_DIR%\README.md"

echo ✓ Created deployment README

REM Create batch file for quick IT deployment
(
echo @echo off
echo echo ================================================
echo echo RoboBackup Tool - Quick IT Deployment
echo echo ================================================
echo echo.
echo echo This script provides quick deployment options for IT administrators.
echo echo.
echo echo Choose deployment method:
echo echo 1. Deploy to local computer
echo echo 2. Deploy via Group Policy ^(manual setup required^)
echo echo 3. Fix MSI context menu for all users
echo echo 4. Enterprise PowerShell deployment
echo echo.
echo set /p choice="Enter choice (1-4): "
echo.
echo if "%%choice%%"=="1" (
echo     echo Deploying to local computer...
echo     msiexec /i RoboBackupTool.msi /qb /l*v install.log
echo     echo Installation completed. Check install.log for details.
echo ^) else if "%%choice%%"=="2" (
echo     echo Group Policy deployment requires manual setup.
echo     echo Please read: documentation\Group-Policy-Deployment-Guide.md
echo     start documentation\Group-Policy-Deployment-Guide.md
echo ^) else if "%%choice%%"=="3" (
echo     echo Adding MSI context menu option...
echo     scripts\fix-msi-context-menu.bat
echo ^) else if "%%choice%%"=="4" (
echo     echo Starting enterprise PowerShell deployment...
echo     powershell -ExecutionPolicy Bypass -File scripts\Deploy-RoboBackup-Enterprise.ps1
echo ^) else (
echo     echo Invalid choice. Please run again.
echo ^)
echo.
echo pause
) > "%DEPLOY_DIR%\Quick-Deploy-IT.bat"

echo ✓ Created quick deployment script

REM Create installation verification script
(
echo @echo off
echo echo Verifying RoboBackup Tool installation...
echo echo.
echo.
echo REM Check if MSI is installed
echo for /f "tokens=*" %%%%a in ^('wmic product where "Name like '%%RoboBackup%%'" get Name /value 2^>nul'^) do (
echo     echo %%%%a | findstr "Name=" >nul && echo ✓ RoboBackup Tool is installed
echo ^)
echo.
echo REM Check service status
echo sc query RoboBackupService >nul 2>&1
echo if %%errorlevel%% == 0 (
echo     echo ✓ RoboBackup Service is installed
echo     for /f "tokens=3" %%%%a in ^('sc query RoboBackupService ^| findstr STATE'^) do (
echo         echo   Service Status: %%%%a
echo     ^)
echo ^) else (
echo     echo ✗ RoboBackup Service not found
echo ^)
echo.
echo REM Check installation directory
echo if exist "%ProgramFiles%\RoboBackup Tool\backupapp.exe" (
echo     echo ✓ Application files found in Program Files
echo ^) else (
echo     echo ✗ Application files not found
echo ^)
echo.
echo echo Installation verification completed.
echo pause
) > "%DEPLOY_DIR%\Verify-Installation.bat"

echo ✓ Created verification script

echo.
echo ================================================
echo Deployment package created successfully!
echo ================================================
echo.
echo Package location: %DEPLOY_DIR%
echo.
echo Package contents:
echo - Main MSI installer: RoboBackupTool.msi
echo - User installer: RoboBackupInstaller.bat
echo - IT deployment scripts in 'scripts' folder
echo - Complete documentation in 'documentation' folder
echo - Quick deployment: Quick-Deploy-IT.bat
echo - Installation verification: Verify-Installation.bat
echo.
echo This package is ready for enterprise distribution!
echo.
echo Next steps:
echo 1. Test the package in your environment
echo 2. Distribute to IT administrators
echo 3. Set up Group Policy deployment (see documentation)
echo 4. Train end users on the simple installer
echo.
pause
