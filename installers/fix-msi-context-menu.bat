@echo off
echo ========================================
echo MSI Context Menu Fix for RoboBackup Tool
echo ========================================
echo.
echo This script adds "Run as administrator" option to MSI files
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - proceeding with registry fix
    goto :apply_fix
) else (
    echo ERROR: This script must be run as administrator!
    echo.
    echo Please:
    echo 1. Right-click this batch file
    echo 2. Select "Run as administrator"
    echo 3. Click "Yes" when UAC prompt appears
    echo.
    pause
    exit /b 1
)

:apply_fix
echo.
echo Adding MSI context menu entries...

REM Add "Install as Administrator" option
reg add "HKEY_CLASSES_ROOT\Msi.Package\shell\runas" /ve /d "Install as &Administrator" /f >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Added "Install as Administrator" menu option
) else (
    echo ✗ Failed to add menu option
)

REM Add command for the menu option
reg add "HKEY_CLASSES_ROOT\Msi.Package\shell\runas\command" /ve /d "msiexec /i \"%%1\"" /f >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Added menu command
) else (
    echo ✗ Failed to add menu command
)

REM Verify .msi file association
reg add "HKEY_CLASSES_ROOT\.msi" /ve /d "Msi.Package" /f >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Verified MSI file association
) else (
    echo ✗ Failed to verify file association
)

echo.
echo ========================================
echo Context menu fix completed!
echo ========================================
echo.
echo You should now see "Install as Administrator" when you:
echo 1. Right-click any MSI file
echo 2. Look for the new menu option
echo.
echo If the option doesn't appear immediately:
echo 1. Restart Windows Explorer (Ctrl+Shift+Esc → Restart explorer.exe)
echo 2. Or restart your computer
echo.
echo You can now install RoboBackup Tool MSI with proper elevation!
echo.
pause
