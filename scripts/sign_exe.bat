@echo off
echo Creating and applying digital signature to RoboBackups.exe...
echo.

REM Check if executable exists
if not exist "RoboBackups.exe" (
    echo Error: RoboBackups.exe not found. Please build it first.
    pause
    exit /b 1
)

REM Create a test certificate (for development only)
echo Creating test certificate...
makecert -r -pe -n "CN=RoboBackup Tool" -ss CA -sr CurrentUser -a sha256 -cy end -sky signature -sv CA.pvk CA.cer

REM Create a code signing certificate
echo Creating code signing certificate...
makecert -pe -n "CN=RoboBackup Tool" -ss MY -a sha256 -cy end -sky signature -ic CA.cer -iv CA.pvk -sv RoboBackup.pvk RoboBackup.cer

REM Convert to PFX format
echo Converting to PFX format...
pvk2pfx -pvk RoboBackup.pvk -spc RoboBackup.cer -pfx RoboBackup.pfx

REM Sign the executable
echo Signing RoboBackups.exe...
signtool sign /f RoboBackup.pfx /p "" /t http://timestamp.digicert.com /d "RoboBackup Tool" /du "https://your-website.com" RoboBackups.exe

REM Verify the signature
echo Verifying signature...
signtool verify /pa RoboBackups.exe

echo.
echo Digital signature applied successfully!
echo Note: This uses a test certificate. For production, use a trusted certificate.
pause 