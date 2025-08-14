@echo off
echo ========================================
echo Creating Portable RoboBackup Tool Installer
echo ========================================

:: Set variables
set "VERSION=1.0.0.0"
set "INSTALLER_NAME=RoboBackupTool-Portable-%VERSION%.zip"
set "SOURCE_DIR=..\dist"
set "BUILD_DIR=..\build"
set "OUTPUT_DIR=..\dist"

echo Creating portable installer...
echo Version: %VERSION%
echo Source: %SOURCE_DIR%
echo Output: %OUTPUT_DIR%\%INSTALLER_NAME%

:: Create build directory if it doesn't exist
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

:: Create portable directory structure
set "PORTABLE_DIR=%BUILD_DIR%\RoboBackupTool-Portable"
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%"

echo.
echo Copying application files...

:: Copy main executable
copy "%SOURCE_DIR%\backupapp.exe" "%PORTABLE_DIR%\"

:: Copy assets directory
if exist "%SOURCE_DIR%\assets" (
    xcopy "%SOURCE_DIR%\assets" "%PORTABLE_DIR%\assets\" /E /I /Y
)

:: Copy config directory
if exist "%SOURCE_DIR%\config" (
    xcopy "%SOURCE_DIR%\config" "%PORTABLE_DIR%\config\" /E /I /Y
)

:: Copy logs directory
if exist "%SOURCE_DIR%\logs" (
    xcopy "%SOURCE_DIR%\logs" "%PORTABLE_DIR%\logs\" /E /I /Y
)

:: Copy documentation
if exist "..\README.md" copy "..\README.md" "%PORTABLE_DIR%\"
if exist "..\ABOUT.md" copy "..\ABOUT.md" "%PORTABLE_DIR%\"
if exist "..\LICENSE" copy "..\LICENSE" "%PORTABLE_DIR%\"

:: Create installation script
echo Creating installation script...
(
echo @echo off
echo echo ========================================
echo echo RoboBackup Tool - Portable Installation
echo echo ========================================
echo echo.
echo echo This will install RoboBackup Tool to your user profile.
echo echo No administrator privileges required.
echo echo.
echo set /p "CONTINUE=Press any key to continue or Ctrl+C to cancel..."
echo.
echo :: Set installation directory
echo set "INSTALL_DIR=%%USERPROFILE%%\AppData\Local\RoboBackup Tool"
echo.
echo :: Create installation directory
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%"
echo.
echo echo Installing to: %%INSTALL_DIR%%
echo.
echo :: Copy all files
echo xcopy ".\*" "%%INSTALL_DIR%%\" /E /I /Y
echo.
echo :: Create Start Menu shortcut
echo set "START_MENU=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\RoboBackup Tool"
echo if not exist "%%START_MENU%%" mkdir "%%START_MENU%%"
echo.
echo echo Creating Start Menu shortcut...
echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut\('%%START_MENU%%\RoboBackup Tool.lnk'\); $Shortcut.TargetPath = '%%INSTALL_DIR%%\backupapp.exe'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.Description = 'RoboBackup Tool - Professional Windows Backup Solution v1.0.0'; $Shortcut.Save\(\)"
echo.
echo :: Create Desktop shortcut
echo echo Creating Desktop shortcut...
echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut\('%%USERPROFILE%%\Desktop\RoboBackup Tool.lnk'\); $Shortcut.TargetPath = '%%INSTALL_DIR%%\backupapp.exe'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.Description = 'RoboBackup Tool - Professional Windows Backup Solution v1.0.0'; $Shortcut.Save\(\)"
echo.
echo echo.
echo echo ========================================
echo echo Installation Complete!
echo echo ========================================
echo echo.
echo echo RoboBackup Tool has been installed to:
echo echo %%INSTALL_DIR%%
echo echo.
echo echo Shortcuts created:
echo echo - Start Menu: %%START_MENU%%
echo echo - Desktop: %%USERPROFILE%%\Desktop
echo echo.
echo echo You can now run RoboBackup Tool from the Start Menu or Desktop.
echo echo.
echo pause
) > "%PORTABLE_DIR%\install.bat"

:: Create uninstall script
echo Creating uninstall script...
(
echo @echo off
echo echo ========================================
echo echo RoboBackup Tool - Uninstall
echo echo ========================================
echo echo.
echo set "INSTALL_DIR=%%USERPROFILE%%\AppData\Local\RoboBackup Tool"
echo set "START_MENU=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\RoboBackup Tool"
echo.
echo echo This will remove RoboBackup Tool from your system.
echo echo.
echo set /p "CONFIRM=Are you sure you want to uninstall? (y/N): "
echo if /i not "%%CONFIRM%%"=="y" goto :cancel
echo.
echo echo Removing RoboBackup Tool...
echo.
echo :: Remove shortcuts
echo if exist "%%USERPROFILE%%\Desktop\RoboBackup Tool.lnk" del "%%USERPROFILE%%\Desktop\RoboBackup Tool.lnk"
echo if exist "%%START_MENU%%\RoboBackup Tool.lnk" del "%%START_MENU%%\RoboBackup Tool.lnk"
echo if exist "%%START_MENU%%" rmdir "%%START_MENU%%"
echo.
echo :: Remove installation directory
echo if exist "%%INSTALL_DIR%%" rmdir /s /q "%%INSTALL_DIR%%"
echo.
echo echo.
echo echo ========================================
echo echo Uninstall Complete!
echo echo ========================================
echo echo.
echo echo RoboBackup Tool has been removed from your system.
echo echo.
echo pause
echo goto :end
echo.
echo :cancel
echo echo Uninstall cancelled.
echo pause
echo.
echo :end
) > "%PORTABLE_DIR%\uninstall.bat"

:: Create README for portable version
echo Creating README...
(
echo # RoboBackup Tool - Portable Version %VERSION%
echo.
echo ## Installation
echo.
echo 1. Extract this ZIP file to any location
echo 2. Run `install.bat` to install to your user profile
echo 3. No administrator privileges required!
echo.
echo ## Features
echo.
echo - **Per-user installation** - Installs to your user profile only
echo - **No admin rights required** - Works on restricted systems
echo - **Portable** - Can be run from any location
echo - **Easy uninstall** - Run `uninstall.bat` to remove
echo - **GUI-focused** - Manual backup operations (service functionality in v1.1.0)
echo.
echo ## Installation Location
echo.
echo The application will be installed to:
echo `%%USERPROFILE%%\AppData\Local\RoboBackup Tool`
echo.
echo ## Shortcuts
echo.
echo - Start Menu: `%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\RoboBackup Tool`
echo - Desktop: `%%USERPROFILE%%\Desktop`
echo.
echo ## Uninstall
echo.
echo Run `uninstall.bat` to completely remove the application.
echo.
echo ## Support
echo.
echo For support and updates, visit:
echo https://github.com/castrokren/robobackup-tool
) > "%PORTABLE_DIR%\README-PORTABLE.md"

:: Create ZIP file
echo.
echo Creating ZIP installer...
if exist "%OUTPUT_DIR%\%INSTALLER_NAME%" del "%OUTPUT_DIR%\%INSTALLER_NAME%"

:: Use PowerShell to create ZIP (Windows 10+)
powershell -Command "Compress-Archive -Path '%PORTABLE_DIR%\*' -DestinationPath '%OUTPUT_DIR%\%INSTALLER_NAME%' -Force"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Portable Installer Created Successfully!
    echo ========================================
    echo.
    echo Installer: %OUTPUT_DIR%\%INSTALLER_NAME%
    echo Size: 
    for %%A in ("%OUTPUT_DIR%\%INSTALLER_NAME%") do echo %%~zA bytes
    echo.
    echo Installation Instructions:
    echo 1. Extract the ZIP file
    echo 2. Run install.bat
    echo 3. No admin privileges required!
    echo.
) else (
    echo.
    echo ERROR: Failed to create ZIP installer!
    echo.
)

:: Clean up
echo Cleaning up temporary files...
if exist "%PORTABLE_DIR%" rmdir /s /q "%PORTABLE_DIR%"

echo.
echo Done!
pause
