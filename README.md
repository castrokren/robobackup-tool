# RoboBackup Tool

A comprehensive Windows backup application with GUI interface, scheduled backups, and Windows service integration.

## Features

- **GUI Interface**: User-friendly Tkinter-based interface
- **Scheduled Backups**: Create and manage scheduled backup tasks
- **Windows Service**: Run backups as a Windows service (runs when not logged in)
- **Network Drives**: Support for UNC paths and network drive mapping
- **Encryption**: Secure credential and settings storage
- **Logging**: Comprehensive logging with rotation
- **System Tray**: Minimize to system tray functionality
- **Passcode Protection**: Optional passcode protection for sensitive operations

## Requirements

- **Python**: 3.13.2 or higher
- **Windows**: Windows 10/11 (Windows-specific features)
- **Administrator Rights**: Required for service installation and some features

## Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Backup_APP_1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python backupapp.py
```

## Building the Executable

To create a standalone executable:

```bash
pyinstaller RoboBackups.spec
```

The executable will be created in the `dist/` folder.

## Project Structure

```
Backup_APP_1/
├── backupapp.py              # Main application
├── backup_service.py         # Windows service implementation
├── create_scheduled_task.ps1 # PowerShell script for scheduled tasks
├── requirements.txt          # Python dependencies
├── RoboBackups.spec         # PyInstaller specification
├── app.manifest             # Windows manifest file
├── config/                  # Configuration directory
├── logs/                    # Log files directory
├── assets/                  # Application assets
└── dist/                    # Built executable (generated)
```

## Configuration

### Initial Setup
1. Run the application for the first time
2. The application will create necessary directories and files
3. Configure your backup settings through the GUI

### Service Installation
1. Run the application as Administrator
2. Click "Manage Service" button
3. Click "Create Service" to install the Windows service
4. The service will run backups even when not logged in

## Usage

### Basic Backup
1. Enter source and destination paths
2. Configure robocopy flags if needed
3. Click "Run Backup Now" for immediate backup
4. Or add to schedule for automated backups

### Scheduled Backups
1. Configure backup settings
2. Click "Add to Schedule"
3. Set date and time
4. The backup will run automatically

### Service Management
- **Create Service**: Installs Windows service for background operation
- **Start Service**: Starts the backup service
- **Stop Service**: Stops the backup service
- **Remove Service**: Uninstalls the Windows service

## Troubleshooting

### Common Issues

1. **"Access is denied" errors**
   - Run the application as Administrator
   - Ensure you have proper permissions

2. **Service installation fails**
   - Make sure you're running as Administrator
   - Check that Python is in your PATH
   - Verify all dependencies are installed

3. **Network drive mapping issues**
   - Ensure network credentials are correct
   - Check network connectivity
   - Verify UNC path format

### Logs
- Application logs: `logs/app_YYYYMMDD.log`
- Service logs: `logs/backup_service.log`
- Security audit logs: `logs/security_audit.log`

## Development

### Running from Source
```bash
python backupapp.py
```

### Testing the Service
```bash
python backup_service.py --standalone
```

### Building
```bash
pyinstaller RoboBackups.spec
```

## Security Notes

- Credentials are encrypted and stored locally
- Passcode protection is available for sensitive operations
- Log files may contain sensitive information
- The `.gitignore` file excludes sensitive configuration files

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
