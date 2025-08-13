# Group Policy Deployment Guide for RoboBackup Tool

This guide provides step-by-step instructions for deploying RoboBackup Tool across your organization using Group Policy.

## Overview

Group Policy Software Installation allows IT administrators to deploy MSI packages to computers or users automatically without requiring manual intervention from end users.

## Prerequisites

- Windows Server with Active Directory Domain Services
- Group Policy Management Console (GPMC)
- Domain administrator privileges
- RoboBackupTool MSI file

## Deployment Methods

### Method 1: Computer-Based Deployment (Recommended)

This method installs RoboBackup Tool on computers regardless of who logs in.

#### Step 1: Prepare the Distribution Point

1. **Create a network share** that all domain computers can access:
   ```
   \\server\software\RoboBackup\
   ```

2. **Set permissions** on the share:
   - `Domain Computers`: Read access
   - `Authenticated Users`: Read access
   - `Domain Admins`: Full Control

3. **Copy the MSI file** to the share:
   ```
   \\server\software\RoboBackup\RoboBackupTool-1.0.0.0.msi
   ```

#### Step 2: Create Group Policy Object (GPO)

1. **Open Group Policy Management Console**
2. **Right-click** your domain or desired OU
3. **Select** "Create a GPO in this domain, and Link it here"
4. **Name** the GPO: "Deploy RoboBackup Tool"

#### Step 3: Configure Software Installation

1. **Right-click** the new GPO → **Edit**
2. **Navigate to**: 
   ```
   Computer Configuration > Policies > Software Settings > Software Installation
   ```
3. **Right-click** Software Installation → **New** → **Package**
4. **Browse** to: `\\server\software\RoboBackup\RoboBackupTool-1.0.0.0.msi`
5. **Select** "Assigned" deployment method
6. **Click** OK

#### Step 4: Configure Deployment Options

1. **Right-click** the deployed package → **Properties**
2. **Deployment tab**:
   - ✅ Published
   - ✅ Auto-install this application by file extension activation
   - ✅ Uninstall this application when it falls out of the scope of management
3. **Advanced tab**:
   - ✅ Ignore language when deploying this package
   - ✅ Make this 32-bit X86 application available to Win64 machines
4. **Click** OK

### Method 2: User-Based Deployment

This method makes RoboBackup Tool available to specific users.

#### Configure User-Based Deployment

1. **Navigate to**:
   ```
   User Configuration > Policies > Software Settings > Software Installation
   ```
2. **Follow steps 3-4** from Computer-Based Deployment
3. **Select** "Published" instead of "Assigned"

## Advanced Configuration

### Silent Installation Parameters

For enterprise deployments, configure MSI properties:

1. **Right-click** the package → **Properties**
2. **Modifications tab** → **Add**
3. **Create transform file (.mst)** with custom properties:
   ```
   INSTALLDIR="C:\Program Files\RoboBackup Tool"
   ALLUSERS=1
   REBOOT=ReallySuppress
   MSIRESTARTMANAGERCONTROL=Disable
   ```

### Installation Logging

Enable logging for troubleshooting:

1. **Computer Configuration** → **Administrative Templates** → **Windows Components** → **Windows Installer**
2. **Enable** "Logging"
3. **Set** log location: `%TEMP%\MSI*.log`
4. **Set** logging options: `voicewarmupx`

### Targeting Specific Computers

Use security filtering to deploy to specific computers:

1. **Select** the GPO in GPMC
2. **Security Filtering** section
3. **Remove** "Authenticated Users"
4. **Add** specific computer groups or OUs

## Deployment Timeline

- **Computer-based**: Installs during computer startup (next reboot)
- **User-based**: Available during user login
- **Forced installation**: Use `gpupdate /force` on target computers

## Monitoring Deployment

### Check Installation Status

1. **Event Viewer** on target computers:
   - Windows Logs → Application
   - Filter by Source: MsiInstaller

2. **Group Policy Results**:
   ```
   gpresult /h GPReport.html
   ```

3. **WMI Query** for installed software:
   ```powershell
   Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*RoboBackup*"}
   ```

### Common Status Codes

- **1603**: Fatal error during installation
- **1618**: Another installation is in progress
- **1633**: Installation package not supported
- **Success**: Exit code 0

## Troubleshooting

### Installation Failures

1. **Check MSI file accessibility**:
   ```cmd
   \\server\software\RoboBackup\RoboBackupTool-1.0.0.0.msi
   ```

2. **Verify computer account permissions** on the share

3. **Check Group Policy application**:
   ```cmd
   gpresult /r
   ```

4. **Review Windows Installer logs** in Event Viewer

### Network Issues

- Ensure SMB file sharing is enabled
- Check firewall rules for SMB traffic
- Verify DNS resolution for the server

### Permission Issues

- Computer accounts need read access to MSI
- Service accounts may need additional privileges
- Check NTFS permissions on the share

## Removal/Uninstallation

### Automatic Removal

When the GPO is unlinked or the computer moves out of scope, RoboBackup Tool will be automatically uninstalled if configured.

### Manual Removal GPO

1. **Create new GPO**: "Remove RoboBackup Tool"
2. **Software Installation** → **Add package**
3. **Select** same MSI file
4. **Choose** "Advanced" → **Remove**

## Best Practices

### Planning

- Test deployment in a pilot OU first
- Schedule deployments during maintenance windows
- Communicate with users about new software

### Maintenance

- Keep MSI files in a secure, backed-up location
- Update GPO when new versions are available
- Monitor deployment success rates

### Security

- Use digital signatures on MSI files
- Restrict who can modify the software share
- Audit software installation events

## Enterprise Scenarios

### Large Organizations

For organizations with 1000+ computers:

1. **Use multiple distribution points** for performance
2. **Implement staged rollouts** by OU
3. **Monitor network bandwidth** during deployment
4. **Use WSUS integration** if available

### Branch Offices

For remote locations:

1. **Replicate MSI files** to local file servers
2. **Use site-aware Group Policy** linking
3. **Consider offline deployment** methods
4. **Test WAN connectivity** impact

### Mixed Environments

For organizations with different Windows versions:

1. **Test compatibility** on all target platforms
2. **Use WMI filtering** for OS-specific deployment
3. **Create separate GPOs** for different configurations
4. **Document version compatibility** matrix

## Support Commands

### Force Group Policy Update
```cmd
gpupdate /force
```

### Check Applied Policies
```cmd
gpresult /r /scope:computer
```

### Reinstall Software
```cmd
msiexec /i "\\server\share\RoboBackupTool.msi" /qn REINSTALL=ALL REINSTALLMODE=vomus
```

### Check Installation Status
```powershell
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -match "RoboBackup"}
```

This Group Policy deployment method ensures enterprise-wide deployment without requiring user interaction or manual admin privileges on each machine.
