# RoboBackup Service - Running Backups When Not Logged In

This document explains how to set up the RoboBackup service to run scheduled backups even when you're not logged into Windows.

## Overview

The RoboBackup application includes a standalone service that can run in the background to execute scheduled backups. This service can be installed in two ways:

1. **Windows Service** - Runs as a system service
2. **Scheduled Task** - Runs as a scheduled task

## Prerequisites

- Python 3.7+ installed
- pywin32 library installed (`pip install pywin32`)
- Administrator privileges (required for installation)

## Installation Options

### Option 1: Windows Service (Recommended)

The Windows Service runs continuously and checks for scheduled backups every minute.

#### Installation Steps:

1. **Run as Administrator**: Right-click on `install_service.bat` and select "Run as administrator"

2. **Or use the service manager**:
   ```cmd
   service_manager.bat install
   service_manager.bat start
   ```

3. **Manual installation**:
   ```cmd
   python backup_service.py install
   python backup_service.py start
   ```

#### Service Management:

- **Start service**: `service_manager.bat start` or `python backup_service.py start`
- **Stop service**: `service_manager.bat stop` or `python backup_service.py stop`
- **Check status**: `service_manager.bat status` or `python backup_service.py status`
- **Remove service**: `service_manager.bat remove` or `python backup_service.py remove`

### Option 2: Scheduled Task

The Scheduled Task runs at system startup and continues running in the background.

#### Installation Steps:

1. **Run as Administrator**: Right-click on `create_scheduled_task.ps1` and select "Run as administrator"

2. **Or use PowerShell**:
   ```powershell
   .\create_scheduled_task.ps1 create
   ```

#### Task Management:

- **Create task**: `.\create_scheduled_task.ps1 create`
- **Remove task**: `.\create_scheduled_task.ps1 remove`
- **Check status**: `.\create_scheduled_task.ps1 status`
- **Start task**: `.\create_scheduled_task.ps1 start`
- **Stop task**: `.\create_scheduled_task.ps1 stop`

## How It Works

### Service Operation

1. **Settings Loading**: The service reads the encrypted settings file (`config/settings.encrypted`)
2. **Scheduled Backup Check**: Every minute, it checks for scheduled backups
3. **Backup Execution**: When a backup is due, it runs robocopy with the configured parameters
4. **Logging**: All activities are logged to `logs/backup_service.log`
5. **Settings Update**: After running backups, it updates the next run time and saves settings

### Security Features

- **Encrypted Settings**: All settings and credentials are encrypted
- **Secure Credentials**: Passwords are encrypted and decrypted as needed
- **Audit Logging**: All backup activities are logged securely
- **Error Handling**: Comprehensive error handling and recovery

## Configuration

### Service Configuration

The service uses the same settings as the main application:

- **Source/Destination paths**
- **Robocopy flags**
- **User credentials** (encrypted)
- **Scheduled backup times**

### Logging

Service logs are written to:
- `logs/backup_service.log` - Main service log
- `logs/app_YYYYMMDD.log` - Daily application logs

### Network Access

The service can access:
- Local file systems
- Network shares (UNC paths)
- Mapped network drives
- SMB/CIFS shares

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   - Check if running as administrator
   - Verify Python and pywin32 are installed
   - Check Windows Event Viewer for errors

2. **Backups Not Running**
   - Verify scheduled backups are configured in the main app
   - Check service logs in `logs/backup_service.log`
   - Ensure network paths are accessible

3. **Permission Errors**
   - Run installation as administrator
   - Check file permissions on config and logs directories
   - Verify network credentials are correct

4. **Network Access Issues**
   - Test network connectivity manually
   - Verify UNC paths are correct
   - Check if credentials are properly encrypted

### Debug Mode

To run the service in debug mode:

```cmd
python backup_service.py --standalone
```

This runs the service in the foreground with console output for debugging.

### Log Analysis

Check the service logs for issues:

```cmd
type logs\backup_service.log
```

Look for:
- Service start/stop messages
- Backup execution details
- Error messages
- Network connection issues

## Integration with Main Application

The main RoboBackup application can:

1. **Check Service Status**: Use the service status checking methods
2. **Install Service**: Automatically install the service when needed
3. **Share Settings**: Both applications use the same encrypted settings file
4. **Coordinate Logging**: Both use the same logging system

## Security Considerations

- **Encryption**: All sensitive data is encrypted
- **Credentials**: Passwords are encrypted and only decrypted when needed
- **File Permissions**: Config files have restricted permissions
- **Network Security**: Uses secure SMB connections when possible
- **Audit Trail**: All activities are logged for security auditing

## Performance

- **Low Resource Usage**: Service uses minimal CPU and memory
- **Efficient Scheduling**: Checks every minute, not continuously
- **Background Operation**: Runs without user interface
- **Error Recovery**: Automatically retries failed operations

## Best Practices

1. **Test First**: Always test backups manually before scheduling
2. **Monitor Logs**: Regularly check service logs for issues
3. **Network Stability**: Ensure stable network connections for remote backups
4. **Credential Security**: Use strong passwords and change them regularly
5. **Backup Verification**: Periodically verify backup integrity
6. **Service Updates**: Keep the service updated with application updates

## Support

For issues with the backup service:

1. Check the logs in `logs/backup_service.log`
2. Verify network connectivity and credentials
3. Test with manual backup execution
4. Check Windows Event Viewer for system errors
5. Ensure all prerequisites are installed correctly 