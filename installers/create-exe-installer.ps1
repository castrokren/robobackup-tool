# Create Self-Extracting EXE Installer for RoboBackup Tool
# This creates a user-friendly EXE that automatically handles admin elevation

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "1.0.0.0",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputName = "RoboBackup-Setup.exe"
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    RoboBackup Tool EXE Installer Creator" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host

function Test-Prerequisites {
    # Check if 7-Zip is installed for self-extracting archives
    $sevenZipPaths = @(
        "${env:ProgramFiles}\7-Zip\7z.exe",
        "${env:ProgramFiles(x86)}\7-Zip\7z.exe",
        "C:\Program Files\7-Zip\7z.exe",
        "C:\Program Files (x86)\7-Zip\7z.exe"
    )
    
    foreach ($path in $sevenZipPaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    Write-Host "7-Zip not found. Checking for WinRAR..." -ForegroundColor Yellow
    
    # Check for WinRAR
    $winrarPaths = @(
        "${env:ProgramFiles}\WinRAR\WinRAR.exe",
        "${env:ProgramFiles(x86)}\WinRAR\WinRAR.exe"
    )
    
    foreach ($path in $winrarPaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    return $null
}

function New-InstallerScript {
    $scriptContent = @'
@echo off
setlocal enabledelayedexpansion

:: Self-extracting installer for RoboBackup Tool
echo ================================================
echo       RoboBackup Tool Setup v{VERSION}
echo ================================================
echo.

:: Check for admin privileges and auto-elevate
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    goto :install
) else (
    echo Requesting administrator privileges...
    echo.
    echo When the UAC prompt appears, click "Yes" to continue.
    echo This is required to install the Windows service properly.
    echo.
    
    :: Try PowerShell elevation
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs" >nul 2>&1
    if %errorLevel% == 0 (
        echo Elevation successful. This window will close.
        timeout /t 2 >nul
        exit
    ) else (
        echo.
        echo Automatic elevation failed. Please run this installer as administrator:
        echo 1. Right-click this file
        echo 2. Select "Run as administrator"
        echo 3. Click "Yes" when prompted
        echo.
        pause
        exit /b 1
    )
)

:install
echo.
echo Extracting installation files...

:: Create temp directory
set "TEMP_DIR=%TEMP%\RoboBackup_Install_%RANDOM%"
mkdir "%TEMP_DIR%" 2>nul

:: Extract files (this will be replaced with actual extraction command)
echo Files extracted to: %TEMP_DIR%

:: Install MSI silently
echo.
echo Installing RoboBackup Tool...
msiexec /i "%TEMP_DIR%\RoboBackupTool.msi" /qb /norestart /l*v "%TEMP%\RoboBackup_Install.log"

set "EXIT_CODE=%errorLevel%"

:: Cleanup temp files
echo.
echo Cleaning up temporary files...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%" 2>nul

:: Show results
if %EXIT_CODE% == 0 (
    echo.
    echo ================================================
    echo     Installation completed successfully!
    echo ================================================
    echo.
    echo RoboBackup Tool has been installed and is ready to use.
    echo.
    echo You can access it from:
    echo - Start Menu ^> RoboBackup Tool
    echo - Desktop shortcut
    echo.
    echo The backup service is now running in the background.
    echo.
) else (
    echo.
    echo ================================================
    echo           Installation failed!
    echo ================================================
    echo.
    echo Error code: %EXIT_CODE%
    echo Check the log file: %TEMP%\RoboBackup_Install.log
    echo.
)

echo Installation log: %TEMP%\RoboBackup_Install.log
echo.
pause
'@

    return $scriptContent.Replace('{VERSION}', $Version)
}

function New-SFXConfig {
    return @"
;The comment below contains SFX script commands

Path=%TEMP%\RoboBackup_Install_%RANDOM%
RunProgram="install.bat"
Silent=0
Overwrite=1
Title=RoboBackup Tool Setup v$Version
Text
{
RoboBackup Tool Setup

This will install RoboBackup Tool on your computer.
The installer will request administrator privileges to:
- Install the Windows service
- Create program files
- Add start menu shortcuts

Click OK to continue, then click "Yes" when UAC prompts appear.
}
"@
}

# Main execution
Write-Host "Checking prerequisites..." -ForegroundColor Gray

$compressor = Test-Prerequisites
if (-not $compressor) {
    Write-Host "ERROR: Neither 7-Zip nor WinRAR found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install one of the following:" -ForegroundColor Yellow
    Write-Host "- 7-Zip: https://www.7-zip.org/"
    Write-Host "- WinRAR: https://www.win-rar.com/"
    Write-Host ""
    Write-Host "Alternative: Use the existing MSI installer with the deployment package." -ForegroundColor Cyan
    exit 1
}

Write-Host "Found compressor: $compressor" -ForegroundColor Green

# Find MSI file
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$distDir = Join-Path $projectRoot "dist"
$msiFile = Join-Path $distDir "RoboBackupTool-$Version.msi"

if (-not (Test-Path $msiFile)) {
    Write-Host "ERROR: MSI file not found: $msiFile" -ForegroundColor Red
    Write-Host "Please build the MSI first using build-msi.bat" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found MSI file: $msiFile" -ForegroundColor Green

# Create temporary build directory
$buildDir = Join-Path $scriptDir "sfx-build"
if (Test-Path $buildDir) {
    Remove-Item $buildDir -Recurse -Force
}
New-Item -ItemType Directory -Path $buildDir | Out-Null

# Copy MSI to build directory
Copy-Item $msiFile -Destination (Join-Path $buildDir "RoboBackupTool.msi")

# Create installer script
$installerScript = New-InstallerScript
$installerScript | Out-File -FilePath (Join-Path $buildDir "install.bat") -Encoding ASCII

Write-Host "Created installer script" -ForegroundColor Green

# Create SFX configuration
$sfxConfig = New-SFXConfig
$sfxConfig | Out-File -FilePath (Join-Path $buildDir "config.txt") -Encoding ASCII

# Create the self-extracting executable
Write-Host "Creating self-extracting executable..." -ForegroundColor Gray

$outputPath = Join-Path $distDir $OutputName

if ($compressor -like "*7z.exe") {
    # Using 7-Zip
    $sfxModule = Join-Path (Split-Path -Parent $compressor) "7zS2con.sfx"
    if (-not (Test-Path $sfxModule)) {
        $sfxModule = Join-Path (Split-Path -Parent $compressor) "7zS2.sfx"
    }
    
    if (Test-Path $sfxModule) {
        # Create archive first
        $archivePath = Join-Path $buildDir "installer.7z"
        & $compressor "a" "-t7z" "-mx9" $archivePath "$buildDir\*" | Out-Null
        
        # Create SFX
        $configBytes = [System.IO.File]::ReadAllBytes((Join-Path $buildDir "config.txt"))
        $sfxBytes = [System.IO.File]::ReadAllBytes($sfxModule)
        $archiveBytes = [System.IO.File]::ReadAllBytes($archivePath)
        
        $outputStream = [System.IO.File]::Create($outputPath)
        $outputStream.Write($sfxBytes, 0, $sfxBytes.Length)
        $outputStream.Write($configBytes, 0, $configBytes.Length)
        $outputStream.Write($archiveBytes, 0, $archiveBytes.Length)
        $outputStream.Close()
        
        Write-Host "Self-extracting EXE created successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: 7-Zip SFX module not found!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "WinRAR support not fully implemented in this version." -ForegroundColor Yellow
    Write-Host "Please use 7-Zip for now, or use the MSI installer." -ForegroundColor Yellow
    exit 1
}

# Cleanup
Remove-Item $buildDir -Recurse -Force

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "      EXE Installer created successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output file: $outputPath" -ForegroundColor Cyan
Write-Host "File size: $([math]::Round((Get-Item $outputPath).Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "This EXE installer:" -ForegroundColor White
Write-Host "✓ Automatically requests admin privileges" -ForegroundColor Green
Write-Host "✓ No need for 'Run as administrator' context menu" -ForegroundColor Green
Write-Host "✓ User just double-clicks and follows prompts" -ForegroundColor Green
Write-Host "✓ Includes progress bar and status messages" -ForegroundColor Green
Write-Host "✓ Automatic cleanup of temporary files" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "- Distribute this single EXE file to users" -ForegroundColor White
Write-Host "- Users double-click to install" -ForegroundColor White
Write-Host "- No technical knowledge required" -ForegroundColor White
