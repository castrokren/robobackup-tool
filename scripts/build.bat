@echo off
echo Building RoboBackup Tool Executable...
echo.

REM Install required packages
echo Installing build requirements...
pip install cx_Freeze pywin32 cryptography

REM Build the executable
echo Building executable...
python setup.py build

REM Copy executable to current directory
echo Copying executable...
for /d %%i in (build\exe.*) do (
    copy "%%i\RoboBackupApp.exe" "RoboBackupApp.exe"
    echo Executable copied to current directory
)

echo.
echo Build complete! You can now run RoboBackupApp.exe
echo Right-click and select "Run as administrator" for full functionality.
pause 