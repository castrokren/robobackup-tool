@echo off
echo Building and Signing RoboBackup Tool...
echo.

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build using the spec file
echo Building executable...
pyinstaller RoboBackups.spec

REM Copy executable to current directory
echo Copying executable...
copy "dist\RoboBackups.exe" "RoboBackups.exe"

REM Check if we should sign the executable
set /p SIGN="Do you want to sign the executable? (y/n): "
if /i "%SIGN%"=="y" (
    echo.
    echo Signing executable...
    call sign_exe.bat
) else (
    echo Skipping signature...
)

echo.
echo Build complete! 
echo.
echo To eliminate publisher warnings completely:
echo 1. Use a trusted code signing certificate from a CA
echo 2. Or add the certificate to Windows trusted publishers
echo 3. Or run: certmgr.msc and add the certificate manually
echo.
pause 