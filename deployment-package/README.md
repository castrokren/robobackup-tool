# RoboBackup Tool - Enterprise Deployment Package

This package contains everything needed to deploy RoboBackup Tool in an enterprise environment.

## Package Contents

### Main Installer
- `RoboBackupTool.msi` - Main MSI installer package
- `RoboBackupInstaller.bat` - User-friendly installer with automatic elevation

### For IT Administrators
- `scripts/Deploy-RoboBackup-Enterprise.ps1` - PowerShell enterprise deployment script
- `scripts/fix-msi-context-menu.bat` - Adds "Run as administrator" context menu
- `scripts/add-run-as-admin.reg` - Registry file for context menu fix

### For End Users
- `installers/install-msi-elevated.bat` - Self-elevating installer
- `installers/install-msi-admin.ps1` - PowerShell installer with admin checks

### Documentation
- `documentation/Group-Policy-Deployment-Guide.md` - Complete Group Policy setup guide
- `documentation/MSI_PACKAGING_README.md` - Technical MSI information

## Quick Start

### For End Users
1. Double-click `RoboBackupInstaller.bat`
2. Click "Yes" when UAC prompt appears
3. Follow installation wizard

### For IT Administrators - Group Policy Deployment
1. Read `documentation/Group-Policy-Deployment-Guide.md`
2. Copy `RoboBackupTool.msi` to network share
3. Create Group Policy Object for software installation
4. Deploy to target computers/users

### For IT Administrators - Script Deployment
1. Run PowerShell as Administrator
2. Execute: `scripts/Deploy-RoboBackup-Enterprise.ps1`
3. Monitor deployment logs

## System Requirements
- Windows 10 1809 or later / Windows Server 2019 or later
- Administrator privileges for installation
- .NET Framework 4.7.2 or later
- 512 MB RAM minimum
- 100 MB disk space

## Enterprise Features
- Silent installation support
- Group Policy deployment ready
- Automatic privilege elevation
- Comprehensive logging
- SCCM/Intune compatible

## Note
- Service functionality will be available in v1.1.0
- This v1.0.0 release focuses on GUI backup operations

## Support
For technical support or questions:
1. Check the documentation folder
2. Review installation logs
3. Contact your IT administrator

Generated on: Wed 08/13/2025 12:12:51.60
Package Version: 1.0.0.0
