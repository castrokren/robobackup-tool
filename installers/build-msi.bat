@echo off
setlocal enabledelayedexpansion

echo ========================================
echo RoboBackup Tool MSI Installer Builder
echo ========================================

:: Check if WiX Toolset is installed
set "WIX_PATH=C:\Program Files\WiX Toolset v6.0\bin"
if not exist "%WIX_PATH%\wix.exe" (
    echo ERROR: WiX Toolset v6.0 not found at %WIX_PATH%!
    echo Please install WiX Toolset v6.0 from: https://wixtoolset.org/releases/
    pause
    exit /b 1
)
echo WiX Toolset v6.0 found at: %WIX_PATH%

:: Check if PyInstaller is available
where pyinstaller.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not found!
    echo Please install PyInstaller: pip install pyinstaller
    pause
    exit /b 1
)

:: Set variables
set "PROJECT_ROOT=%~dp0.."
set "BUILD_DIR=%PROJECT_ROOT%\build"
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "INSTALLER_DIR=%PROJECT_ROOT%\installers"
set "VERSION=1.0.0.0"

echo.
echo Building executable files...
echo ========================================

:: Create build directories
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

:: Build main application
echo Building main application...
pyinstaller --onefile --windowed --icon="%PROJECT_ROOT%\assets\robot_copier.ico" --name="backupapp" "%PROJECT_ROOT%\backupapp.py"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build main application!
    pause
    exit /b 1
)

:: Build service executable
echo Building service executable...
pyinstaller --onefile --console --icon="%PROJECT_ROOT%\assets\robot_copier.ico" --name="backup_service" "%PROJECT_ROOT%\backup_service.py"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build service executable!
    pause
    exit /b 1
)

:: Build core module
echo Building core module...
pyinstaller --onefile --console --icon="%PROJECT_ROOT%\assets\robot_copier.ico" --name="backup_core" "%PROJECT_ROOT%\backup_core.py"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build core module!
    pause
    exit /b 1
)

echo.
echo Building MSI installer...
echo ========================================

:: Copy files to build directory for MSI
set "MSI_SOURCE_DIR=%BUILD_DIR%\msi-source"
if exist "%MSI_SOURCE_DIR%" rmdir /s /q "%MSI_SOURCE_DIR%"
mkdir "%MSI_SOURCE_DIR%"

:: Copy executables
copy "dist\backupapp.exe" "%MSI_SOURCE_DIR%\"
copy "dist\backup_service.exe" "%MSI_SOURCE_DIR%\"
copy "dist\backup_core.exe" "%MSI_SOURCE_DIR%\"

:: Copy assets
if not exist "%MSI_SOURCE_DIR%\assets" mkdir "%MSI_SOURCE_DIR%\assets"
copy "%PROJECT_ROOT%\assets\*.*" "%MSI_SOURCE_DIR%\assets\"

:: Copy configuration files
if not exist "%MSI_SOURCE_DIR%\config" mkdir "%MSI_SOURCE_DIR%\config"
copy "%PROJECT_ROOT%\config\*.json" "%MSI_SOURCE_DIR%\config\"

:: Copy documentation
copy "%PROJECT_ROOT%\README.md" "%MSI_SOURCE_DIR%\"
copy "%PROJECT_ROOT%\ABOUT.md" "%MSI_SOURCE_DIR%\"
copy "%PROJECT_ROOT%\LICENSE" "%MSI_SOURCE_DIR%\"

:: Generate GUID for UpgradeCode
for /f "tokens=2 delims={}" %%i in ('powershell -Command "[System.Guid]::NewGuid().ToString()"') do set "UPGRADE_GUID=%%i"

:: Update WiX file with generated GUID
powershell -Command "(Get-Content '%INSTALLER_DIR%\wix-setup.wxs') -replace 'PUT-GUID-HERE-1234-5678-9ABC-DEF012345678', '%UPGRADE_GUID%' | Set-Content '%INSTALLER_DIR%\wix-setup.wxs'"

:: Build MSI using WiX v6.0
echo Building MSI using WiX v6.0...
"%WIX_PATH%\wix.exe" build "%INSTALLER_DIR%\wix-setup.wxs" -out "%DIST_DIR%\RoboBackupTool-%VERSION%.msi" -d SourceDir="%MSI_SOURCE_DIR%" -d Version="%VERSION%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to build MSI installer!
    pause
    exit /b 1
)

echo.
echo ========================================
echo MSI Installer created successfully!
echo ========================================
echo.
echo Installer location: %DIST_DIR%\RoboBackupTool-%VERSION%.msi
echo.
echo The installer includes:
echo - Main application (backupapp.exe)
echo - Windows service (backup_service.exe)
echo - Core backup engine (backup_core.exe)
echo - Configuration files
echo - Start menu shortcuts
echo - Desktop shortcut
echo - Automatic service installation and startup
echo.
echo To install, run the MSI file as Administrator.
echo.

:: Clean up temporary files
echo Cleaning up temporary files...
if exist "%BUILD_DIR%\wix-setup.wixobj" del "%BUILD_DIR%\wix-setup.wixobj"
if exist "%BUILD_DIR%\msi-source" rmdir /s /q "%BUILD_DIR%\msi-source"

echo Build completed successfully!
pause
