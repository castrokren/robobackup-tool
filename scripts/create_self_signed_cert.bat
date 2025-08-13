@echo off
echo ========================================
echo Creating Self-Signed Code Signing Certificate
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
set "CERT_NAME=RoboBackupTool_CodeSigning"
set "CERT_FILE=..\%CERT_NAME%.pfx"
set "CERT_PASSWORD=RoboBackup2024!"
set "CERT_SUBJECT=CN=RoboBackup Tool Code Signing Certificate, O=RoboBackup Development Team, C=US"

:: Check if certificate already exists
if exist "%CERT_FILE%" (
    echo WARNING: Certificate already exists: %CERT_FILE%
    echo.
    set /p "OVERWRITE=Do you want to overwrite it? (y/N): "
    if /i not "%OVERWRITE%"=="y" (
        echo Certificate creation cancelled.
        pause
        exit /b 0
    )
    echo.
)

echo Creating self-signed code signing certificate...
echo Certificate Name: %CERT_NAME%
echo Certificate File: %CERT_FILE%
echo Subject: %CERT_SUBJECT%
echo.

:: Create the certificate using PowerShell
powershell -Command "try { $cert = New-SelfSignedCertificate -Type Custom -Subject '%CERT_SUBJECT%' -KeyUsage DigitalSignature -KeyAlgorithm RSA -KeyLength 2048 -HashAlgorithm SHA256 -CertStoreLocation 'Cert:\LocalMachine\My' -KeyExportPolicy Exportable -KeyProtection None -NotAfter (Get-Date).AddYears(3) -FriendlyName 'RoboBackup Tool Code Signing Certificate'; if ($cert) { Write-Host 'Certificate created successfully!' -ForegroundColor Green; Write-Host ('Thumbprint: ' + $cert.Thumbprint) -ForegroundColor Cyan; $pfxPath = '%CERT_FILE%'; $pfxPassword = ConvertTo-SecureString -String '%CERT_PASSWORD%' -Force -AsPlainText; Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pfxPassword; if (Test-Path $pfxPath) { Write-Host ('PFX file exported to: ' + $pfxPath) -ForegroundColor Green } else { Write-Host 'ERROR: Failed to export PFX file!' -ForegroundColor Red; exit 1 } } else { Write-Host 'ERROR: Failed to create certificate!' -ForegroundColor Red; exit 1 } } catch { Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }"

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Certificate Creation Complete!
    echo ========================================
    echo.
    echo Certificate Details:
    echo - Name: %CERT_NAME%
    echo - File: %CERT_FILE%
    echo - Password: %CERT_PASSWORD%
    echo - Valid for: 3 years
    echo.
    echo The certificate is now ready for code signing.
    echo Run sign_executables.bat to sign your files.
    echo.
) else (
    echo.
    echo ERROR: Certificate creation failed!
    echo Please check the error messages above.
    echo.
)

pause
