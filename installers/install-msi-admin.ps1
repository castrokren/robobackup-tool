# RoboBackup Tool MSI Admin Installer
# This script ensures proper admin installation of the MSI package

param(
    [Parameter(Mandatory=$false)]
    [string]$MsiPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent = $false,
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = "install.log"
)

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Find-MsiFile {
    $scriptDir = Split-Path -Parent $MyInvocation.ScriptName
    $distDir = Join-Path (Split-Path -Parent $scriptDir) "dist"
    
    # Look for MSI files in common locations
    $searchPaths = @(
        $scriptDir,
        $distDir,
        (Get-Location).Path
    )
    
    foreach ($path in $searchPaths) {
        $msiFiles = Get-ChildItem -Path $path -Filter "RoboBackupTool*.msi" -ErrorAction SilentlyContinue
        if ($msiFiles) {
            return $msiFiles[0].FullName
        }
    }
    
    return $null
}

function Install-MsiAsAdmin {
    param(
        [string]$MsiFilePath,
        [bool]$SilentInstall,
        [string]$LogFilePath
    )
    
    Write-Host "Installing RoboBackup Tool MSI..." -ForegroundColor Green
    Write-Host "MSI File: $MsiFilePath" -ForegroundColor Gray
    
    # Build msiexec arguments
    $arguments = @("/i", "`"$MsiFilePath`"")
    
    if ($SilentInstall) {
        $arguments += "/quiet"
        $arguments += "/norestart"
        Write-Host "Silent installation mode" -ForegroundColor Gray
    }
    
    # Add logging
    $arguments += "/l*v"
    $arguments += "`"$LogFilePath`""
    
    try {
        Write-Host "Executing: msiexec.exe $($arguments -join ' ')" -ForegroundColor Gray
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru -Verb RunAs
        
        if ($process.ExitCode -eq 0) {
            Write-Host "Installation completed successfully!" -ForegroundColor Green
            Write-Host "The RoboBackup service has been installed and started." -ForegroundColor Green
            return $true
        } else {
            Write-Host "Installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
            
            # Common exit codes
            switch ($process.ExitCode) {
                1603 { Write-Host "Error 1603: Fatal error during installation" -ForegroundColor Red }
                1619 { Write-Host "Error 1619: This installation package could not be opened" -ForegroundColor Red }
                1620 { Write-Host "Error 1620: This installation package could not be opened" -ForegroundColor Red }
                1633 { Write-Host "Error 1633: This installation package is not supported on this platform" -ForegroundColor Red }
                default { Write-Host "See log file for details: $LogFilePath" -ForegroundColor Yellow }
            }
            return $false
        }
    } catch {
        Write-Host "Error executing installer: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "RoboBackup Tool MSI Admin Installer" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check admin privileges
if (-not (Test-AdminPrivileges)) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running with Administrator privileges ✓" -ForegroundColor Green

# Find MSI file if not specified
if (-not $MsiPath) {
    Write-Host "Searching for MSI file..." -ForegroundColor Gray
    $MsiPath = Find-MsiFile
    
    if (-not $MsiPath) {
        Write-Host "ERROR: Could not find RoboBackupTool MSI file!" -ForegroundColor Red
        Write-Host "Please specify the path using: -MsiPath 'path\to\RoboBackupTool.msi'" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "Found MSI: $MsiPath" -ForegroundColor Green
}

# Verify MSI file exists
if (-not (Test-Path $MsiPath)) {
    Write-Host "ERROR: MSI file not found: $MsiPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install MSI
$success = Install-MsiAsAdmin -MsiFilePath $MsiPath -SilentInstall $Silent -LogFilePath $LogFile

if ($success) {
    Write-Host "`nInstallation completed successfully!" -ForegroundColor Green
    Write-Host "You can now run RoboBackup Tool from the Start Menu." -ForegroundColor Green
} else {
    Write-Host "`nInstallation failed. Check the log file: $LogFile" -ForegroundColor Red
}

if (-not $Silent) {
    Read-Host "`nPress Enter to exit"
}