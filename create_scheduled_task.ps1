# RoboBackup Scheduled Task Creator
# This script creates a Windows Scheduled Task that runs the backup service
# even when the user is not logged in.

param(
    [string]$Action = "create",
    [string]$TaskName = "RoboBackupService",
    [string]$Description = "Runs RoboBackup scheduled backups when user is not logged in"
)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as administrator" -ForegroundColor Red
    Write-Host "Please right-click and 'Run as administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupServicePath = Join-Path $scriptDir "backup_service.py"
$pythonPath = "python"

# Verify backup service exists
if (-not (Test-Path $backupServicePath)) {
    Write-Host "ERROR: backup_service.py not found in $scriptDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

function New-ScheduledTask {
    Write-Host "Creating RoboBackup Scheduled Task..." -ForegroundColor Green
    
    # Create the action
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$backupServicePath`" --standalone" -WorkingDirectory $scriptDir
    
    # Create the trigger (run at system startup)
    $trigger = New-ScheduledTaskTrigger -AtStartup
    
    # Create the principal (run as SYSTEM account)
    $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    # Create the settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Create the task
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $Description
    
    # Register the task
    Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force
    
    Write-Host "Scheduled Task created successfully!" -ForegroundColor Green
    Write-Host "Task Name: $TaskName" -ForegroundColor Yellow
    Write-Host "The task will run the backup service at system startup" -ForegroundColor Yellow
    Write-Host "and continue running even when no user is logged in." -ForegroundColor Yellow
}

function Remove-ScheduledTask {
    Write-Host "Removing RoboBackup Scheduled Task..." -ForegroundColor Green
    
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Scheduled Task removed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Failed to remove scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Get-ScheduledTaskStatus {
    Write-Host "Checking RoboBackup Scheduled Task status..." -ForegroundColor Green
    
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "Task Name: $($task.TaskName)" -ForegroundColor Yellow
            Write-Host "State: $($task.State)" -ForegroundColor Yellow
            Write-Host "Last Run: $($task.LastRunTime)" -ForegroundColor Yellow
            Write-Host "Next Run: $($task.NextRunTime)" -ForegroundColor Yellow
        }
        else {
            Write-Host "Scheduled Task '$TaskName' not found" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "ERROR: Failed to get task status: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-ScheduledTask {
    Write-Host "Starting RoboBackup Scheduled Task..." -ForegroundColor Green
    
    try {
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Scheduled Task started successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Failed to start scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-ScheduledTask {
    Write-Host "Stopping RoboBackup Scheduled Task..." -ForegroundColor Green
    
    try {
        Stop-ScheduledTask -TaskName $TaskName
        Write-Host "Scheduled Task stopped successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Failed to stop scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
switch ($Action.ToLower()) {
    "create" {
        New-ScheduledTask
    }
    "remove" {
        Remove-ScheduledTask
    }
    "status" {
        Get-ScheduledTaskStatus
    }
    "start" {
        Start-ScheduledTask
    }
    "stop" {
        Stop-ScheduledTask
    }
    default {
        Write-Host "Usage: $($MyInvocation.MyCommand.Name) [create|remove|status|start|stop]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Yellow
        Write-Host "  create  - Create the scheduled task" -ForegroundColor White
        Write-Host "  remove  - Remove the scheduled task" -ForegroundColor White
        Write-Host "  status  - Check task status" -ForegroundColor White
        Write-Host "  start   - Start the task" -ForegroundColor White
        Write-Host "  stop    - Stop the task" -ForegroundColor White
    }
}

Read-Host "Press Enter to exit" 