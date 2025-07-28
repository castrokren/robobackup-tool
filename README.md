# RoboBackup Tool

A Python-based backup tool that provides automated file backup functionality with logging and configuration management.

## 📋 About

**RoboBackup Tool** is a comprehensive Windows backup solution designed for automated file synchronization and backup operations. Built with Python and leveraging Windows Robocopy, this tool provides both GUI and service-based backup capabilities for enterprise and personal use.

### 🎯 Purpose
- **Automated Backup Operations**: Schedule and automate file backups without manual intervention
- **Network Path Support**: Native support for UNC paths and network drives without requiring drive mapping
- **Dual Mode Operation**: Run as a GUI application for configuration or as a Windows service for automated backups
- **Enterprise-Ready**: Designed for corporate environments with security features and audit logging

### 🔧 Core Features
- **Robocopy Integration**: Leverages Windows Robocopy for reliable file synchronization
- **UNC Path Support**: Direct support for network paths (\\server\share) without drive mapping
- **Windows Service**: Can run as a background service for automated, scheduled backups
- **GUI Interface**: User-friendly Tkinter interface for easy configuration and monitoring
- **Comprehensive Logging**: Detailed logs for troubleshooting and audit trails
- **Security Features**: Encrypted configuration storage and security audit logging
- **Network Drive Mapping**: Automatic mapping and cleanup of network drives
- **Configurable Schedules**: Flexible backup scheduling options

### 🏗️ Architecture
The application consists of three main components:
- **`backup_core.py`**: Core backup functionality with UNC path support
- **`backupapp.py`**: Tkinter GUI for user-friendly configuration
- **`backup_service.py`**: Windows service implementation for automated backups

### 🛡️ Security & Compliance
- **Encrypted Credentials**: Secure storage of network credentials
- **Audit Logging**: Comprehensive security event logging
- **Temporary Network Mappings**: Automatic cleanup of network drive mappings
- **Secure Configuration**: Encrypted configuration files

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows OS (primary target)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/robobackup-tool.git
   cd robobackup-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
Backup_APP_1/
├── .github/          # GitHub workflows and CI/CD
├── assets/           # Icons, images, and static resources
├── config/           # Configuration files and settings
├── installers/       # Installer scripts and NSIS files
├── logs/             # Application logs (with archive subfolder)
├── scripts/          # Build scripts and utilities
├── backupapp.py      # Main application GUI
├── backup_core.py    # Core backup functionality
├── backup_service.py # Windows service functionality
├── main.py          # Application entry point
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 Development

### Building the Application
```bash
# Run build script
python scripts/build_exe.py

# Or use PyInstaller directly
pyinstaller --onefile --windowed main.py
```

### Running Tests
```bash
python -m pytest test_backup_core.py
```

## 📋 Features

- Automated file backup with configurable schedules
- Comprehensive logging system
- Windows service integration
- GUI interface for easy configuration
- Security audit logging
- Configurable backup destinations

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔄 CI/CD

This project uses GitHub Actions for continuous integration:
- Automated testing on multiple Python versions
- Code linting with flake8
- Automated builds with PyInstaller
- Artifact uploads for releases

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.
