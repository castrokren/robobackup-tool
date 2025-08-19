# Code Signing Guide for RoboBackup Tool

This guide explains how to sign your RoboBackup Tool application to avoid "Unknown Publisher" warnings and establish trust with users.

## 🔐 Why Code Signing Matters

- **Eliminates "Unknown Publisher" warnings**
- **Builds user trust and confidence**
- **Required for Windows SmartScreen compatibility**
- **Essential for enterprise deployment**

## 📋 Prerequisites

### Required Tools:
- **Windows SDK** (for signtool.exe)
- **Visual Studio** (includes Windows SDK)
- **Administrator privileges**

### Installation:
1. Download and install [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/)
2. Or install [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/) with Windows development tools

## 🚀 Quick Start (Self-Signed Certificate)

### Step 1: Create Self-Signed Certificate
```bash
# Run as Administrator
cd scripts
.\create_self_signed_cert.bat
```

### Step 2: Build and Sign Everything
```bash
# Run as Administrator
cd scripts
.\build_and_sign.bat
```

This will:
- Create a self-signed certificate
- Build the MSI installer
- Sign all executables and the MSI
- Verify signatures

## 🔧 Manual Signing Process

### 1. Create Certificate
```bash
# Generate self-signed certificate
makecert.exe -r -pe -n "CN=RoboBackupTool_CodeSigning" -ss CA -sr CurrentUser -a sha256 -cy end -sky signature -sv "RoboBackupTool_CodeSigning.pvk" "RoboBackupTool_CodeSigning.cer"

# Create PFX file
pvk2pfx.exe -pvk "RoboBackupTool_CodeSigning.pvk" -spc "RoboBackupTool_CodeSigning.cer" -pfx "RoboBackupTool_CodeSigning.pfx" -pi "RoboBackup2024!"
```

### 2. Sign Individual Files
```bash
# Sign executables (v1.0.0)
signtool.exe sign /f "RoboBackupTool_CodeSigning.pfx" /p "RoboBackup2024!" /t "http://timestamp.digicert.com" /d "RoboBackup Tool" /du "https://github.com/castrokren/robobackup-tool" "dist\backupapp.exe"
signtool.exe sign /f "RoboBackupTool_CodeSigning.pfx" /p "RoboBackup2024!" /t "http://timestamp.digicert.com" /d "RoboBackup Tool" /du "https://github.com/castrokren/robobackup-tool" "dist\backup_core.exe"

# Sign MSI installer
signtool.exe sign /f "RoboBackupTool_CodeSigning.pfx" /p "RoboBackup2024!" /t "http://timestamp.digicert.com" /d "RoboBackup Tool" /du "https://github.com/castrokren/robobackup-tool" "dist\RoboBackupTool-1.0.0.0.msi"
```

### 3. Verify Signatures
```bash
# Verify each file (v1.0.0)
signtool.exe verify /pa "dist\backupapp.exe"
signtool.exe verify /pa "dist\backup_core.exe"
signtool.exe verify /pa "dist\RoboBackupTool-1.0.0.0.msi"
```

## 🏢 Production Code Signing (Recommended)

For production use, purchase a commercial code signing certificate from a trusted Certificate Authority:

### Popular CAs:
- **DigiCert** - https://www.digicert.com/code-signing/
- **Sectigo** - https://sectigo.com/code-signing-certificates
- **GlobalSign** - https://www.globalsign.com/en/code-signing-certificate
- **Comodo** - https://www.comodo.com/ssl-certificates/code-signing-certificates/

### Benefits of Commercial Certificates:
- **Widely trusted** by Windows and antivirus software
- **No "Unknown Publisher" warnings**
- **Better SmartScreen reputation**
- **Professional appearance**

### Using Commercial Certificate:
1. Purchase certificate from CA
2. Install certificate on your machine
3. Update the signing scripts with your certificate details
4. Sign your application

## 🔍 Troubleshooting

### Common Issues:

#### "signtool.exe not found"
- Install Windows SDK or Visual Studio
- Add SDK path to PATH environment variable
- Typical path: `C:\Program Files (x86)\Windows Kits\10\bin\10.0.xxxxx.0\x64`

#### "Certificate not found"
- Run `create_self_signed_cert.bat` first
- Check certificate file exists in scripts directory
- Verify certificate password is correct

#### "Access denied"
- Run scripts as Administrator
- Check file permissions
- Ensure no files are in use

#### "Timestamp server error"
- Check internet connection
- Try different timestamp server:
  - `http://timestamp.digicert.com`
  - `http://timestamp.sectigo.com`
  - `http://timestamp.globalsign.com`

## 📁 File Structure

```
scripts/
├── create_self_signed_cert.bat    # Create self-signed certificate
├── sign_executables.bat           # Sign all executables
├── build_and_sign.bat             # Complete build and sign process
└── RoboBackupTool_CodeSigning.pfx # Certificate file (created)

dist/
├── backupapp.exe                  # Signed main application
├── backup_core.exe                # Signed core module
└── RoboBackupTool-1.0.0.0.msi    # Signed MSI installer
```

## 🔒 Security Best Practices

1. **Keep certificate files secure**
2. **Use strong passwords**
3. **Backup certificates safely**
4. **Use timestamp servers** for long-term validity
5. **Verify signatures** after signing
6. **Test on clean machines** to ensure trust

## 📞 Support

For issues with code signing:
1. Check Windows SDK installation
2. Verify administrator privileges
3. Review error messages carefully
4. Test with simple files first

---

**Note**: Self-signed certificates are suitable for development and internal use. For public distribution, use a commercial code signing certificate for maximum trust and compatibility.
