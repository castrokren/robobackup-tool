@echo off
echo Verifying RoboBackup Tool installation...
echo.

REM Check if MSI is installed
for /f "tokens=*" %%a in ('wmic product where "Name like '%RoboBackup%'" get Name /value 2>nul') do (
)

REM Check service status
if %errorlevel% == 0 (
    echo ✓ RoboBackup Service is installed
    for /f "tokens=3" %%a in ('sc query RoboBackupService | findstr STATE') do (
        echo   Service Status: %%a
    )
) else (
    echo ✗ RoboBackup Service not found
)

REM Check installation directory
if exist "C:\Program Files\RoboBackup Tool\backupapp.exe" (
    echo ✓ Application files found in Program Files
) else (
    echo ✗ Application files not found
)

echo Installation verification completed.
pause
