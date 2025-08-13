@echo off
echo ========================================
echo Code Signing RoboBackup Tool Executables
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
set "CERT_FILE=..\RoboBackupTool_CodeSigning.pfx"
set "CERT_PASSWORD=RoboBackup2024!"
set "TIMESTAMP_SERVER=http://timestamp.digicert.com"

:: Check if certificate exists
if not exist "%CERT_FILE%" (
    echo ERROR: Certificate file not found: %CERT_FILE%
    echo Please run create_self_signed_cert.bat first to create the certificate.
    pause
    exit /b 1
)

echo Certificate found: %CERT_FILE%

:: Try to find signtool.exe in common SDK locations
set "SIGNTOOL_FOUND="

:: Check common SDK paths
for %%p in (
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.20348.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.20348.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.17134.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.16299.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.16299.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.15063.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.15063.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.14393.0\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\10.0.14393.0\x86"
    "C:\Program Files (x86)\Windows Kits\10\bin\x64"
    "C:\Program Files (x86)\Windows Kits\10\bin\x86"
    "C:\Program Files\Windows Kits\10\bin\10.0.22621.0\x64"
    "C:\Program Files\Windows Kits\10\bin\10.0.22621.0\x86"
    "C:\Program Files\Windows Kits\10\bin\x64"
    "C:\Program Files\Windows Kits\10\bin\x86"
) do (
    if exist "%%~p\signtool.exe" (
        set "SIGNTOOL_PATH=%%~p"
        set "SIGNTOOL_FOUND=1"
        echo Found signtool.exe at: %%p
        goto :found_signtool
    )
)

:: If not found in common paths, try where command
where signtool.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "SIGNTOOL_FOUND=1"
    echo Found signtool.exe in PATH
    goto :found_signtool
)

echo ERROR: signtool.exe not found!
echo Please install Windows SDK or Visual Studio with Windows SDK.
echo Or add the SDK path to your PATH environment variable.
echo.
echo Common SDK installation paths:
echo - C:\Program Files (x86)\Windows Kits\10\bin\
echo - C:\Program Files\Windows Kits\10\bin\
pause
exit /b 1

:found_signtool
echo signtool found - OK

:: Function to sign a file
:sign_file
set "file_to_sign=%~1"
if not exist "%file_to_sign%" (
    echo WARNING: File not found: %file_to_sign%
    goto :eof
)

echo.
echo Signing: %file_to_sign%
if defined SIGNTOOL_PATH (
    "%SIGNTOOL_PATH%\signtool.exe" sign /f "%CERT_FILE%" /p "%CERT_PASSWORD%" /t "%TIMESTAMP_SERVER%" /fd SHA256 /d "RoboBackup Tool" /du "https://github.com/castrokren/robobackup-tool" "%file_to_sign%"
) else (
    signtool.exe sign /f "%CERT_FILE%" /p "%CERT_PASSWORD%" /t "%TIMESTAMP_SERVER%" /fd SHA256 /d "RoboBackup Tool" /du "https://github.com/castrokren/robobackup-tool" "%file_to_sign%"
)

if %errorlevel% equ 0 (
    echo ✓ Successfully signed: %file_to_sign%
) else (
    echo ✗ Failed to sign: %file_to_sign%
)
goto :eof

:: Sign PyInstaller executables
echo.
echo ========================================
echo Signing PyInstaller Executables
echo ========================================

call :sign_file "..\dist\RoboBackupApp.exe"

:: Sign MSI installer
echo.
echo ========================================
echo Signing MSI Installer
echo ========================================

call :sign_file "..\dist\RoboBackupTool-1.0.0.0.msi"

:: Verify signatures
echo.
echo ========================================
echo Verifying Signatures
echo ========================================

echo.
echo Verifying RoboBackupApp.exe...
if defined SIGNTOOL_PATH (
    "%SIGNTOOL_PATH%\signtool.exe" verify /pa "..\dist\RoboBackupApp.exe"
) else (
    signtool.exe verify /pa "..\dist\RoboBackupApp.exe"
)

echo.
echo Verifying MSI installer...
if defined SIGNTOOL_PATH (
    "%SIGNTOOL_PATH%\signtool.exe" verify /pa "..\dist\RoboBackupTool-1.0.0.0.msi"
) else (
    signtool.exe verify /pa "..\dist\RoboBackupTool-1.0.0.0.msi"
)

echo.
echo ========================================
echo Code Signing Complete!
echo ========================================
echo.
echo All executables and the MSI installer have been signed.
echo Users will no longer see "Unknown Publisher" warnings.
echo.
echo Note: For production use, consider purchasing a commercial
echo code signing certificate from a trusted Certificate Authority.
echo.

pause
