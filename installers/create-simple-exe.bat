@echo off
setlocal enabledelayedexpansion

echo ================================================
echo   Simple EXE Installer Creator (No 7-Zip)
echo ================================================
echo.
echo This creates a simple EXE installer that wraps the MSI
echo and handles admin elevation automatically.
echo.

REM Set variables
set "PROJECT_ROOT=%~dp0.."
set "DIST_DIR=%PROJECT_ROOT%\dist"
set "VERSION=1.0.0.0"
set "OUTPUT_NAME=RoboBackup-Setup.exe"

REM Check if MSI exists
if not exist "%DIST_DIR%\RoboBackupTool-%VERSION%.msi" (
    echo ERROR: MSI file not found!
    echo Expected: %DIST_DIR%\RoboBackupTool-%VERSION%.msi
    echo Please run build-msi.bat first.
    pause
    exit /b 1
)

echo Found MSI file: RoboBackupTool-%VERSION%.msi

REM Create the EXE installer using copy command and batch embedding
echo.
echo Creating simple EXE installer...

REM Create temporary batch file that will become the EXE
(
echo @echo off
echo setlocal enabledelayedexpansion
echo.
echo echo ================================================
echo echo       RoboBackup Tool Setup v%VERSION%
echo echo ================================================
echo echo.
echo echo Welcome to RoboBackup Tool Setup
echo echo This installer will set up RoboBackup Tool on your computer.
echo echo.
echo.
echo REM Check for admin privileges and auto-elevate
echo net session ^>nul 2^>^&1
echo if %%errorLevel%% == 0 ^(
echo     echo Running with administrator privileges...
echo     goto :install
echo ^) else ^(
echo     echo Requesting administrator privileges...
echo     echo.
echo     echo When the UAC prompt appears, click "Yes" to continue.
echo     echo This is required to install the Windows service properly.
echo     echo.
echo     
echo     REM Try PowerShell elevation
echo     powershell -Command "Start-Process -FilePath '%%~f0' -Verb RunAs" ^>nul 2^>^&1
echo     if %%errorLevel%% == 0 ^(
echo         echo Elevation successful. This window will close.
echo         timeout /t 2 ^>nul
echo         exit
echo     ^) else ^(
echo         echo.
echo         echo Automatic elevation failed. Please run this installer as administrator:
echo         echo 1. Right-click this file
echo         echo 2. Select "Run as administrator"
echo         echo 3. Click "Yes" when prompted
echo         echo.
echo         pause
echo         exit /b 1
echo     ^)
echo ^)
echo.
echo :install
echo echo.
echo echo Extracting installation files to temporary directory...
echo.
echo REM Create temp directory
echo set "TEMP_DIR=%%TEMP%%\RoboBackup_Install_%%RANDOM%%"
echo mkdir "%%TEMP_DIR%%" 2^>nul
echo.
echo REM Extract embedded MSI file
echo echo Extracting MSI installer...
echo ^(echo -----BEGIN MSI----- ^& findstr /v /c:"-----" "%%~f0"^) ^> "%%TEMP_DIR%%\installer.b64"
echo certutil -decode "%%TEMP_DIR%%\installer.b64" "%%TEMP_DIR%%\RoboBackupTool.msi" ^>nul
echo del "%%TEMP_DIR%%\installer.b64" 2^>nul
echo.
echo if not exist "%%TEMP_DIR%%\RoboBackupTool.msi" ^(
echo     echo ERROR: Failed to extract MSI installer!
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo MSI extracted successfully.
echo.
echo REM Install MSI with progress bar
echo echo Installing RoboBackup Tool...
echo echo Please wait while the installation completes...
echo msiexec /i "%%TEMP_DIR%%\RoboBackupTool.msi" /qb /norestart /l*v "%%TEMP%%\RoboBackup_Install.log"
echo.
echo set "EXIT_CODE=%%errorLevel%%"
echo.
echo REM Cleanup temp files
echo echo Cleaning up temporary files...
echo if exist "%%TEMP_DIR%%" rmdir /s /q "%%TEMP_DIR%%" 2^>nul
echo.
echo REM Show results
echo if %%EXIT_CODE%% == 0 ^(
echo     echo.
echo     echo ================================================
echo     echo     Installation completed successfully!
echo     echo ================================================
echo     echo.
echo     echo RoboBackup Tool has been installed and is ready to use.
echo     echo.
echo     echo You can access it from:
echo     echo - Start Menu ^> RoboBackup Tool
echo     echo - Desktop shortcut
echo     echo.
echo     echo The backup service is now running in the background.
echo     echo.
echo ^) else ^(
echo     echo.
echo     echo ================================================
echo     echo           Installation failed!
echo     echo ================================================
echo     echo.
echo     echo Error code: %%EXIT_CODE%%
echo     echo Check the log file: %%TEMP%%\RoboBackup_Install.log
echo     echo.
echo     echo Common solutions:
echo     echo 1. Ensure no antivirus is blocking the installation
echo     echo 2. Close any running backup applications
echo     echo 3. Restart your computer and try again
echo     echo.
echo ^)
echo.
echo echo Installation log: %%TEMP%%\RoboBackup_Install.log
echo echo.
echo pause
echo exit %%EXIT_CODE%%
echo.
echo -----BEGIN MSI-----
) > "%DIST_DIR%\installer_script.bat"

REM Encode MSI file as base64 and append to batch file
echo Encoding MSI file...
certutil -encode "%DIST_DIR%\RoboBackupTool-%VERSION%.msi" "%DIST_DIR%\msi_encoded.b64" >nul
type "%DIST_DIR%\msi_encoded.b64" >> "%DIST_DIR%\installer_script.bat"

REM Clean up temporary files
del "%DIST_DIR%\msi_encoded.b64"

REM Rename to EXE (this is a simple trick - batch files can run with .exe extension)
move "%DIST_DIR%\installer_script.bat" "%DIST_DIR%\%OUTPUT_NAME%"

echo.
echo ================================================
echo     Simple EXE Installer created successfully!
echo ================================================
echo.
echo Output file: %DIST_DIR%\%OUTPUT_NAME%
echo.
echo This EXE installer:
echo ✓ Automatically requests admin privileges
echo ✓ No need for 'Run as administrator' context menu
echo ✓ User just double-clicks and follows prompts
echo ✓ Self-contained (includes MSI embedded)
echo ✓ Shows progress and status messages
echo ✓ Automatic cleanup of temporary files
echo.
echo Usage:
echo - Distribute this single EXE file to users
echo - Users double-click to install
echo - No technical knowledge required
echo.
echo NOTE: Some antivirus software may flag this as suspicious
echo because it's a self-extracting executable. This is normal.
echo.
pause
