# RoboBackup Tool v1.0.0

A professional Windows backup solution powered by Robocopy with a modern GUI interface.

## ✨ Features

### 🎯 Core Functionality
- **Manual Backup Execution** - Point-and-click backup operations via GUI
- **Robocopy Integration** - Leverages Windows' robust file synchronization engine
- **Network Drive Mapping** - Automatic mapping and unmapping of network drives
- **UNC Path Support** - Direct backup to network paths without drive mapping
- **Hidden Command Execution** - Silent background operations without flashing windows

### 🔒 Security & Reliability
- **Encrypted Credential Storage** - Secure storage of network credentials using Fernet encryption
- **Comprehensive Logging** - Detailed audit trails and backup logs
- **Real-time Progress Tracking** - Visual feedback during backup operations
- **Proper Error Handling** - Robust error detection and reporting
- **Exit Code Validation** - Accurate success/failure detection based on Robocopy results

### 🖥️ User Experience
- **Modern GUI Interface** - Clean, intuitive Tkinter-based interface
- **System Tray Integration** - Minimize to tray for background operation
- **Validation Engine** - Input validation for paths, flags, and credentials
- **Flexible Robocopy Flags** - Support for custom Robocopy parameters
- **Cross-version Python Support** - Compatible with Python 3.8+

## 🚀 Quick Start

### Download & Run
1. Download `backupapp.exe` from the releases
2. Double-click to launch (no installation required)
3. Configure your source and destination paths
4. Click "Start Backup" to begin

### Basic Backup Setup
1. **Source Path**: Select the folder to backup
2. **Destination Path**: Choose backup destination (local or network)
3. **Robocopy Flags**: Use defaults or customize (e.g., `/MIR /FFT /R:3 /W:10`)
4. **Network Credentials**: Add if backing up to/from network locations

## 📋 System Requirements

- **OS**: Windows 10 1809+ / Windows Server 2019+
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB disk space
- **Python**: 3.8+ (for development only - executable is self-contained)
- **Dependencies**: All dependencies bundled in executable

## 🔧 Advanced Configuration

### Network Drive Configuration
```
Source: \\server\share\data
Destination: E:\Backups
Credentials: domain\username / password (encrypted)
```

### Custom Robocopy Flags
```
/MIR    - Mirror directory tree
/FFT    - Use fat file times
/R:3    - Retry 3 times on failure
/W:10   - Wait 10 seconds between retries
/XJD    - Exclude junction points (directories)
/XJF    - Exclude junction points (files)
```

## 📁 File Structure

```
backupapp.exe                 # Main executable
├── assets/                   # Application icons and images
├── config/                   # Configuration files (created on first run)
│   ├── app_settings.json     # Application settings
│   ├── passcode.dat          # Encrypted passcode
│   └── log_salt.bin          # Logging salt
├── logs/                     # Backup and application logs
└── utils/                    # Utility modules (bundled in exe)
```

## 🏗️ Development

### Building from Source
```bash
# Install dependencies
pip install -r requirements.txt

# Build executable
python setup.py

# Output: dist/backupapp.exe
```

### Dependencies
- **GUI**: tkinter, PIL (Pillow)
- **System Integration**: pystray, win32com, pywin32
- **Encryption**: cryptography (Fernet)
- **Network**: requests
- **Packaging**: PyInstaller

## 🔄 Version History

- **v1.0.0** (2024-12-26): Initial release with GUI backup functionality
- **v1.1.0** (Planned): Add Windows Service support for scheduled backups

## 📝 Known Limitations

- Service functionality not included in v1.0.0 (planned for v1.1.0)
- Requires manual execution via GUI
- Windows-only application
- Symbolic links may not be followed in some Robocopy scenarios

## 🛠️ Troubleshooting

### Common Issues

**Backup Creates Empty Directories But No Files**
- ✅ Fixed in v1.0.0 - robocopy command execution corrected

**Command Windows Flash During Backup**
- ✅ Fixed in v1.0.0 - hidden command window execution

**Network Path Access Denied**
- Verify network credentials are correct
- Ensure source/destination paths are accessible
- Check network connectivity

**Application Won't Start**
- Run as Administrator if accessing system directories
- Check antivirus isn't blocking the executable
- Verify Windows version compatibility

## 📞 Support

- **Documentation**: Check `/docs` folder for detailed guides
- **Logs**: Review log files in `/logs` directory for troubleshooting
- **GitHub**: [Issues and feature requests](https://github.com/castrokren/robobackup-tool/issues)

## 📄 License

Licensed under the terms specified in the LICENSE file.

---

**RoboBackup Tool v1.0.0** - Professional Windows Backup Solution  
*Built with ❤️ for reliable, secure file synchronization*
