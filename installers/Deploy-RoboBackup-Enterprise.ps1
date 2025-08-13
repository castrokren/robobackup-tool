# Enterprise Deployment Script for RoboBackup Tool
# This script is designed for IT administrators to deploy RoboBackup Tool across multiple computers
# Supports SCCM, Group Policy, Intune, and manual deployment scenarios

param(
    [Parameter(Mandatory=$false)]
    [string]$MsiPath,
    
    [Parameter(Mandatory=$false)]
    [string]$TargetComputers = "localhost",
    
    [Parameter(Mandatory=$false)]
    [bool]$Silent = $true,
    
    [Parameter(Mandatory=$false)]
    [string]$InstallDir = "",
    
    [Parameter(Mandatory=$false)]
    [string]$LogPath = "C:\Windows\Temp\RoboBackup_Deploy.log",
    
    [Parameter(Mandatory=$false)]
    [switch]$Uninstall = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckOnly = $false
)

# Enterprise deployment configuration
$script:Config = @{
    ProductName = "RoboBackup Tool"
    ServiceName = "RoboBackupService"
    InstallDir = if($InstallDir) { $InstallDir } else { "${env:ProgramFiles}\RoboBackup Tool" }
    MinWindowsVersion = "10.0.17763"  # Windows 10 1809 / Server 2019
    RequiredMemoryMB = 512
    RequiredDiskSpaceMB = 100
}

function Write-Log {
    param([string]$Message, [string]$Level = "Info")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage
    if ($LogPath) {
        $logMessage | Out-File -FilePath $LogPath -Append -ErrorAction SilentlyContinue
    }
}

function Test-Prerequisites {
    Write-Log "Checking system prerequisites..."
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    $minVersion = [Version]$script:Config.MinWindowsVersion
    
    if ($osVersion -lt $minVersion) {
        Write-Log "Unsupported Windows version: $osVersion (minimum: $minVersion)" "Error"
        return $false
    }
    
    # Check available memory
    $memory = Get-CimInstance -ClassName Win32_ComputerSystem
    $memoryMB = [math]::Round($memory.TotalPhysicalMemory / 1MB)
    
    if ($memoryMB -lt $script:Config.RequiredMemoryMB) {
        Write-Log "Insufficient memory: ${memoryMB}MB (minimum: $($script:Config.RequiredMemoryMB)MB)" "Error"
        return $false
    }
    
    # Check disk space
    $systemDrive = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $env:SystemDrive }
    $freeSpaceMB = [math]::Round($systemDrive.FreeSpace / 1MB)
    
    if ($freeSpaceMB -lt $script:Config.RequiredDiskSpaceMB) {
        Write-Log "Insufficient disk space: ${freeSpaceMB}MB free (minimum: $($script:Config.RequiredDiskSpaceMB)MB)" "Error"
        return $false
    }
    
    Write-Log "Prerequisites check passed"
    return $true
}

function Test-ExistingInstallation {
    # Check if already installed via registry
    $uninstallKeys = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    
    foreach ($key in $uninstallKeys) {
        $installed = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue | 
                     Where-Object { $_.DisplayName -like "*RoboBackup*" }
        if ($installed) {
            return @{
                Installed = $true
                Version = $installed.DisplayVersion
                InstallDate = $installed.InstallDate
                UninstallString = $installed.UninstallString
            }
        }
    }
    
    # Check service
    $service = Get-Service -Name $script:Config.ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        return @{
            Installed = $true
            ServiceStatus = $service.Status
            ServiceStartType = $service.StartType
        }
    }
    
    return @{ Installed = $false }
}

function Install-RoboBackup {
    param([string]$MsiFilePath)
    
    Write-Log "Starting RoboBackup Tool installation..."
    Write-Log "MSI Path: $MsiFilePath"
    
    # Build msiexec arguments
    $arguments = @("/i", "`"$MsiFilePath`"")
    
    if ($Silent) {
        $arguments += "/quiet"
        $arguments += "/norestart"
    } else {
        $arguments += "/qb"  # Basic UI for progress
    }
    
    # Add custom install directory if specified
    if ($script:Config.InstallDir -ne "${env:ProgramFiles}\RoboBackup Tool") {
        $arguments += "INSTALLDIR=`"$($script:Config.InstallDir)`""
    }
    
    # Add logging
    $installLog = Join-Path $env:TEMP "RoboBackup_Install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $arguments += "/l*v"
    $arguments += "`"$installLog`""
    
    try {
        Write-Log "Executing: msiexec.exe $($arguments -join ' ')"
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        
        Write-Log "Installation completed with exit code: $($process.ExitCode)"
        Write-Log "Installation log: $installLog"
        
        if ($process.ExitCode -eq 0) {
            Write-Log "Installation successful" "Success"
            
            # Verify service installation
            Start-Sleep -Seconds 5
            $service = Get-Service -Name $script:Config.ServiceName -ErrorAction SilentlyContinue
            if ($service) {
                Write-Log "Service installed successfully: $($service.Status)" "Success"
            } else {
                Write-Log "Warning: Service not found after installation" "Warning"
            }
            
            return $true
        } else {
            Write-Log "Installation failed with exit code: $($process.ExitCode)" "Error"
            
            # Common error codes
            switch ($process.ExitCode) {
                1603 { Write-Log "Error 1603: Fatal error during installation" "Error" }
                1619 { Write-Log "Error 1619: Installation package could not be opened" "Error" }
                1633 { Write-Log "Error 1633: Installation package not supported on this platform" "Error" }
                1638 { Write-Log "Error 1638: Another version is already installed" "Error" }
            }
            
            return $false
        }
    } catch {
        Write-Log "Installation exception: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Uninstall-RoboBackup {
    Write-Log "Starting RoboBackup Tool uninstallation..."
    
    $existing = Test-ExistingInstallation
    if (-not $existing.Installed) {
        Write-Log "RoboBackup Tool is not installed" "Warning"
        return $true
    }
    
    # Stop service first
    $service = Get-Service -Name $script:Config.ServiceName -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq 'Running') {
        Write-Log "Stopping RoboBackup service..."
        Stop-Service -Name $script:Config.ServiceName -Force -ErrorAction SilentlyContinue
    }
    
    # Uninstall via MSI
    $arguments = @("/x", "{dddb19d1-da76-4e5b-9b63-a92b2204c4a4}")  # Product GUID from WiX
    
    if ($Silent) {
        $arguments += "/quiet"
        $arguments += "/norestart"
    }
    
    # Add logging
    $uninstallLog = Join-Path $env:TEMP "RoboBackup_Uninstall_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    $arguments += "/l*v"
    $arguments += "`"$uninstallLog`""
    
    try {
        Write-Log "Executing: msiexec.exe $($arguments -join ' ')"
        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Log "Uninstallation successful" "Success"
            return $true
        } else {
            Write-Log "Uninstallation failed with exit code: $($process.ExitCode)" "Error"
            return $false
        }
    } catch {
        Write-Log "Uninstallation exception: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Invoke-ComputerDeployment {
    param([string]$ComputerName, [string]$MsiPath)
    
    Write-Log "Deploying to computer: $ComputerName"
    
    if ($ComputerName -eq "localhost" -or $ComputerName -eq $env:COMPUTERNAME) {
        # Local deployment
        if ($CheckOnly) {
            $existing = Test-ExistingInstallation
            Write-Log "Installation status on ${ComputerName}: $($existing.Installed)"
            return $existing
        }
        
        if (-not (Test-Prerequisites)) {
            Write-Log "Prerequisites check failed on $ComputerName" "Error"
            return $false
        }
        
        if ($Uninstall) {
            return Uninstall-RoboBackup
        } else {
            return Install-RoboBackup -MsiFilePath $MsiPath
        }
    } else {
        # Remote deployment
        Write-Log "Remote deployment to $ComputerName not implemented in this version" "Warning"
        Write-Log "For remote deployment, use Group Policy or SCCM" "Info"
        return $false
    }
}

# Main execution
Write-Log "RoboBackup Tool Enterprise Deployment Script"
Write-Log "============================================="

# Validate admin privileges
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Log "ERROR: This script must be run as Administrator!" "Error"
    exit 1
}

# Find MSI file if not specified
if (-not $MsiPath -and -not $Uninstall -and -not $CheckOnly) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $msiFiles = Get-ChildItem -Path $scriptDir -Filter "RoboBackupTool*.msi" -ErrorAction SilentlyContinue
    
    if ($msiFiles) {
        $MsiPath = $msiFiles[0].FullName
        Write-Log "Found MSI file: $MsiPath"
    } else {
        Write-Log "ERROR: No MSI file found. Please specify -MsiPath parameter." "Error"
        exit 1
    }
}

# Verify MSI file exists
if ($MsiPath -and -not (Test-Path $MsiPath)) {
    Write-Log "ERROR: MSI file not found: $MsiPath" "Error"
    exit 1
}

# Process target computers
$computers = $TargetComputers.Split(',') | ForEach-Object { $_.Trim() }
$results = @()

foreach ($computer in $computers) {
    $result = Invoke-ComputerDeployment -ComputerName $computer -MsiPath $MsiPath
    $results += @{
        Computer = $computer
        Success = $result
        Timestamp = Get-Date
    }
}

# Summary
Write-Log "Deployment Summary"
Write-Log "=================="
foreach ($result in $results) {
    $status = if ($result.Success) { "SUCCESS" } else { "FAILED" }
    Write-Log "$($result.Computer): $status"
}

Write-Log "Deployment script completed"
Write-Log "Log file: $LogPath"
