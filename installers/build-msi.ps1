# RoboBackup Tool MSI Installer Builder
param([string]$Version = "1.0.0.0", [switch]$Clean, [switch]$Help)

if ($Help) {
    Write-Host "RoboBackup Tool MSI Installer Builder"
    Write-Host "Usage: .\build-msi.ps1 [Options]"
    Write-Host "Options: -Version <version> -Clean -Help"
    exit 0
}

Write-Host "RoboBackup Tool MSI Installer Builder" -ForegroundColor Green

# Check if WiX Toolset is installed
try {
    $null = Get-Command candle.exe -ErrorAction Stop
    Write-Host "WiX Toolset found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: WiX Toolset not found!" -ForegroundColor Red
    Write-Host "Please install WiX Toolset from: https://wixtoolset.org/releases/" -ForegroundColor Yellow
    exit 1
}

# Check if PyInstaller is available
try {
    $null = Get-Command pyinstaller.exe -ErrorAction Stop
    Write-Host "PyInstaller found" -ForegroundColor Green
} catch {
    Write-Host "ERROR: PyInstaller not found!" -ForegroundColor Red
    Write-Host "Please install PyInstaller: pip install pyinstaller" -ForegroundColor Yellow
    exit 1
}

# Set variables
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $ProjectRoot "build"
$DistDir = Join-Path $ProjectRoot "dist"
$InstallerDir = Join-Path $ProjectRoot "installers"

Write-Host "Building executable files..." -ForegroundColor Cyan

# Clean build directories if requested
if ($Clean) {
    Write-Host "Cleaning build directories..." -ForegroundColor Yellow
    if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
    if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
}

# Create build directories
if (!(Test-Path $BuildDir)) { New-Item -ItemType Directory -Path $BuildDir | Out-Null }
if (!(Test-Path $DistDir)) { New-Item -ItemType Directory -Path $DistDir | Out-Null }

# Build main application
Write-Host "Building main application..." -ForegroundColor Yellow
$MainAppIcon = Join-Path $ProjectRoot "assets\robot_copier.ico"
$MainAppSource = Join-Path $ProjectRoot "backupapp.py"
$MainAppResult = & pyinstaller --onefile --windowed --icon="$MainAppIcon" --name="backupapp" "$MainAppSource" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build main application!" -ForegroundColor Red
    Write-Host $MainAppResult -ForegroundColor Red
    exit 1
}
Write-Host "Main application built successfully" -ForegroundColor Green

# Build service executable
Write-Host "Building service executable..." -ForegroundColor Yellow
$ServiceSource = Join-Path $ProjectRoot "backup_service.py"
$ServiceResult = & pyinstaller --onefile --console --icon="$MainAppIcon" --name="backup_service" "$ServiceSource" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build service executable!" -ForegroundColor Red
    Write-Host $ServiceResult -ForegroundColor Red
    exit 1
}
Write-Host "Service executable built successfully" -ForegroundColor Green

# Build core module
Write-Host "Building core module..." -ForegroundColor Yellow
$CoreSource = Join-Path $ProjectRoot "backup_core.py"
$CoreResult = & pyinstaller --onefile --console --icon="$MainAppIcon" --name="backup_core" "$CoreSource" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build core module!" -ForegroundColor Red
    Write-Host $CoreResult -ForegroundColor Red
    exit 1
}
Write-Host "Core module built successfully" -ForegroundColor Green

Write-Host "Building MSI installer..." -ForegroundColor Cyan

# Copy files to build directory for MSI
$MsiSourceDir = Join-Path $BuildDir "msi-source"
if (Test-Path $MsiSourceDir) { Remove-Item $MsiSourceDir -Recurse -Force }
New-Item -ItemType Directory -Path $MsiSourceDir | Out-Null

# Copy executables
Copy-Item (Join-Path $DistDir "backupapp.exe") $MsiSourceDir
Copy-Item (Join-Path $DistDir "backup_service.exe") $MsiSourceDir
Copy-Item (Join-Path $DistDir "backup_core.exe") $MsiSourceDir

# Copy assets
$AssetsDir = Join-Path $MsiSourceDir "assets"
New-Item -ItemType Directory -Path $AssetsDir | Out-Null
Copy-Item (Join-Path $ProjectRoot "assets\*.*") $AssetsDir

# Copy configuration files
$ConfigDir = Join-Path $MsiSourceDir "config"
New-Item -ItemType Directory -Path $ConfigDir | Out-Null
Copy-Item (Join-Path $ProjectRoot "config\*.json") $ConfigDir

# Copy documentation
Copy-Item (Join-Path $ProjectRoot "README.md") $MsiSourceDir
Copy-Item (Join-Path $ProjectRoot "ABOUT.md") $MsiSourceDir
Copy-Item (Join-Path $ProjectRoot "LICENSE") $MsiSourceDir

# Generate GUID for UpgradeCode
$UpgradeGuid = [System.Guid]::NewGuid().ToString()

# Update WiX file with generated GUID
$WixFile = Join-Path $InstallerDir "wix-setup.wxs"
$WixContent = Get-Content $WixFile -Raw
$WixContent = $WixContent -replace 'PUT-GUID-HERE-1234-5678-9ABC-DEF012345678', $UpgradeGuid
Set-Content $WixFile $WixContent -NoNewline

# Compile WiX source
Write-Host "Compiling WiX source..." -ForegroundColor Yellow
$WixObjFile = Join-Path $BuildDir "wix-setup.wixobj"
$CandleResult = & candle.exe -ext WixUtilExtension -ext WixNetFxExtension -dSourceDir="$MsiSourceDir" -dVersion="$Version" "$WixFile" -out "$WixObjFile" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to compile WiX source!" -ForegroundColor Red
    Write-Host $CandleResult -ForegroundColor Red
    exit 1
}
Write-Host "WiX source compiled successfully" -ForegroundColor Green

# Link MSI
Write-Host "Linking MSI installer..." -ForegroundColor Yellow
$MsiOutput = Join-Path $DistDir "RoboBackupTool-$Version.msi"
$LightResult = & light.exe -ext WixUtilExtension -ext WixNetFxExtension -ext WixUIExtension "$WixObjFile" -out "$MsiOutput" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to link MSI installer!" -ForegroundColor Red
    Write-Host $LightResult -ForegroundColor Red
    exit 1
}
Write-Host "MSI installer linked successfully" -ForegroundColor Green

Write-Host "MSI Installer created successfully!" -ForegroundColor Green
Write-Host "Installer location: $MsiOutput" -ForegroundColor Cyan

# Clean up temporary files
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
if (Test-Path $WixObjFile) { Remove-Item $WixObjFile }
if (Test-Path $MsiSourceDir) { Remove-Item $MsiSourceDir -Recurse -Force }

Write-Host "Build completed successfully!" -ForegroundColor Green
