# MSI Packaging Guide for RoboBackup Tool

This guide explains how to create a professional MSI installer for the RoboBackup Tool that properly handles Windows service installation.

## Overview

The MSI installer provides:
- **Professional Installation**: Standard Windows installer experience
- **Service Integration**: Automatic Windows service installation and configuration
- **Proper Uninstallation**: Clean removal of all components including services
- **Enterprise Deployment**: Support for silent installation and group policy deployment
- **Digital Signing**: Support for code signing and certificate validation

## Prerequisites

### Required Software

1. **WiX Toolset v3.11 or later**
   - Download from: https://wixtoolset.org/releases/
   - Install and add to PATH environment variable
   - Verify installation: `candle.exe --version`

2. **PyInstaller**
   - Install via pip: `pip install pyinstaller`
   - Verify installation: `pyinstaller --version`

3. **Python 3.8+**
   - Required for building executables
   - All dependencies from `requirements.txt`

### Optional Software

- **Visual Studio Build Tools** (for advanced customization)
- **Code Signing Certificate** (for production releases)
- **WiX Extensions** (for additional features)

## File Structure

```
installers/
├── wix-setup.wxs          # Main WiX installer configuration
├── build-msi.bat          # Batch script for building MSI
├── build-msi.ps1          # PowerShell script for building MSI
├── installer.nsi          # Legacy NSIS installer (not recommended)
└── MSI_PACKAGING_README.md # This file
```

## Building the MSI Installer

### Method 1: Using PowerShell Script (Recommended)

```powershell
# Navigate to installers directory
cd installers

# Build with default version
.\build-msi.ps1

# Build with custom version
.\build-msi.ps1 -Version "1.1.0.0"

# Clean build with custom version
.\build-msi.ps1 -Version "1.1.0.0" -Clean

# Show help
.\build-msi.ps1 -Help
```

### Method 2: Using Batch Script

```cmd
# Navigate to installers directory
cd installers

# Run the build script
build-msi.bat
```

### Method 3: Manual Build Process

1. **Build Executables**:
   ```cmd
   pyinstaller --onefile --windowed --icon="assets\robot_copier.ico" --name="backupapp" backupapp.py
   pyinstaller --onefile --console --icon="assets\robot_copier.ico" --name="backup_service" backup_service.py
   pyinstaller --onefile --console --icon="assets\robot_copier.ico" --name="backup_core" backup_core.py
   ```

2. **Prepare Source Directory**:
   ```cmd
   mkdir build\msi-source
   copy dist\*.exe build\msi-source\
   xcopy assets build\msi-source\assets\ /E /I
   xcopy config build\msi-source\config\ /E /I
   copy *.md build\msi-source\
   copy LICENSE build\msi-source\
   ```

3. **Compile WiX Source**:
   ```cmd
   candle.exe -ext WixUtilExtension -ext WixNetFxExtension -dSourceDir="build\msi-source" -dVersion="1.0.0.0" installers\wix-setup.wxs -out build\wix-setup.wixobj
   ```

4. **Link MSI**:
   ```cmd
   light.exe -ext WixUtilExtension -ext WixNetFxExtension -ext WixUIExtension build\wix-setup.wixobj -out dist\RoboBackupTool-1.0.0.0.msi
   ```

## MSI Installer Features

### Windows Service Integration

The MSI installer automatically:
- Installs the RoboBackup service as a Windows service
- Configures the service to start automatically
- Sets proper service dependencies
- Handles service removal during uninstallation

### Installation Components

1. **Main Application** (`backupapp.exe`)
   - GUI application for configuration and monitoring
   - Installed to `%ProgramFiles%\RoboBackup Tool\`

2. **Windows Service** (`backup_service.exe`)
   - Background service for automated backups
   - Installed and configured as Windows service
   - Runs under LocalSystem account

3. **Core Engine** (`backup_core.exe`)
   - Core backup functionality
   - Used by both GUI and service

4. **Configuration Files**
   - Default configuration templates
   - Installed to application directory

5. **Documentation**
   - README, ABOUT, and LICENSE files
   - Available in application directory

6. **Shortcuts**
   - Start menu shortcuts
   - Desktop shortcut
   - Uninstall shortcut

### Installation Properties

- **Install Location**: `%ProgramFiles%\RoboBackup Tool\`
- **Install Scope**: Per-machine (requires admin rights)
- **Upgrade Support**: Automatic upgrade detection
- **Rollback Support**: Automatic rollback on failure

## Deployment Options

### Silent Installation

```cmd
# Basic silent installation
msiexec /i RoboBackupTool-1.0.0.0.msi /quiet

# Silent installation with logging
msiexec /i RoboBackupTool-1.0.0.0.msi /quiet /l*v install.log

# Silent installation with custom properties
msiexec /i RoboBackupTool-1.0.0.0.msi /quiet INSTALLDIR="C:\Custom\Path"
```

### Enterprise Deployment

1. **Group Policy Deployment**:
   - Use Group Policy Software Installation
   - Target computers or users
   - Configure automatic installation

2. **SCCM/Intune Deployment**:
   - Import MSI to System Center Configuration Manager
   - Deploy to target collections
   - Monitor installation status

3. **Scripted Deployment**:
   ```powershell
   # PowerShell deployment script
   $InstallerPath = "\\server\share\RoboBackupTool-1.0.0.0.msi"
   Start-Process msiexec.exe -ArgumentList "/i `"$InstallerPath`"", "/quiet", "/norestart" -Wait
   ```

### Uninstallation

```cmd
# Silent uninstallation
msiexec /x RoboBackupTool-1.0.0.0.msi /quiet

# Uninstallation with logging
msiexec /x RoboBackupTool-1.0.0.0.msi /quiet /l*v uninstall.log
```

## Customization

### Modifying the WiX Configuration

The `wix-setup.wxs` file can be customized for:

1. **Product Information**:
   - Product name, version, manufacturer
   - Upgrade codes and GUIDs
   - Installation properties

2. **Service Configuration**:
   - Service account (LocalSystem, NetworkService, custom)
   - Service dependencies
   - Startup type (auto, manual, disabled)

3. **Installation Options**:
   - Custom installation directory
   - Feature selection
   - Custom actions

4. **UI Customization**:
   - Custom installation UI
   - License agreement
   - Installation progress

### Adding Custom Actions

```xml
<!-- Example: Custom action to configure service -->
<CustomAction Id="ConfigureService" 
              FileKey="BackupServiceExe"
              ExeCommand="configure"
              Execute="deferred"
              Return="check" />

<InstallExecuteSequence>
    <Custom Action="ConfigureService" After="InstallService">NOT Installed</Custom>
</InstallExecuteSequence>
```

## Troubleshooting

### Common Issues

1. **Admin Error During Installation (MOST COMMON)**:
   - **Symptoms**: "Administrator privileges required" error even when logged in as admin
   - **Cause**: UAC (User Account Control) blocking MSI installation or missing InstallPrivileges
   - **Solutions**:
     - Use the provided PowerShell installer: `installers\install-msi-admin.ps1`
     - Right-click MSI file → "Run as administrator"
     - Command line: `msiexec /i RoboBackupTool-1.0.0.0.msi /quiet /l*v install.log`
     - Ensure UAC is enabled (counter-intuitive but required for proper elevation)

2. **"Run as Administrator" Option Missing**:
   - Add registry entry to enable context menu option:
   ```cmd
   reg add "HKEY_CLASSES_ROOT\Msi.Package\shell\runas" /ve /d "Install as &Administrator" /f
   reg add "HKEY_CLASSES_ROOT\Msi.Package\shell\runas\command" /ve /d "msiexec /i \"%%1\"" /f
   ```

3. **UAC Completely Blocking Installation**:
   - Temporarily lower UAC settings in Control Panel → User Accounts
   - Use PowerShell with `-ExecutionPolicy Bypass`
   - Contact IT administrator for group policy exceptions

4. **WiX Toolset Not Found**:
   - Ensure WiX is installed and in PATH
   - Verify installation: `candle.exe --version`

2. **PyInstaller Errors**:
   - Check Python environment
   - Verify all dependencies are installed
   - Check for antivirus interference

3. **Service Installation Failures**:
   - Ensure running as Administrator
   - Check Windows service permissions
   - Verify service executable compatibility

4. **MSI Build Failures**:
   - Check file paths and permissions
   - Verify GUID format and uniqueness
   - Review WiX compilation errors

### Debugging

1. **Enable Verbose Logging**:
   ```cmd
   candle.exe -v -ext WixUtilExtension -ext WixNetFxExtension wix-setup.wxs
   light.exe -v -ext WixUtilExtension -ext WixNetFxExtension wix-setup.wixobj
   ```

2. **Installation Logging**:
   ```cmd
   msiexec /i RoboBackupTool-1.0.0.0.msi /l*v install.log
   ```

3. **Service Verification**:
   ```cmd
   sc query RoboBackupService
   sc qc RoboBackupService
   ```

## Best Practices

### Security
- Always run MSI installation as Administrator
- Use appropriate service accounts
- Implement proper access controls
- Consider code signing for production

### Reliability
- Test installation on clean systems
- Verify uninstallation removes all components
- Test upgrade scenarios
- Validate service functionality

### Maintenance
- Keep WiX Toolset updated
- Maintain consistent version numbering
- Document customizations
- Archive installer versions

## Support

For issues with MSI packaging:
1. Check the troubleshooting section above
2. Review WiX Toolset documentation
3. Verify all prerequisites are met
4. Test on a clean Windows system

## References

- [WiX Toolset Documentation](https://wixtoolset.org/documentation/)
- [Windows Installer Documentation](https://docs.microsoft.com/en-us/windows/win32/msi/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Windows Service Documentation](https://docs.microsoft.com/en-us/windows/win32/services/)
