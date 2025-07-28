!include "MUI2.nsh"

; General settings
Name "Backup Tool"
OutFile "BackupTool_Setup.exe"
InstallDir "$PROGRAMFILES\Backup Tool"
InstallDirRegKey HKCU "Software\Backup Tool" "Install_Dir"

; Request application privileges
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "backup_icon.ico"
!define MUI_UNICON "backup_icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Add files
    File "dist\BackupTool.exe"
    File "backup_icon.ico"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\Backup Tool"
    CreateShortcut "$SMPROGRAMS\Backup Tool\Backup Tool.lnk" "$INSTDIR\BackupTool.exe" "" "$INSTDIR\backup_icon.ico"
    CreateShortcut "$SMPROGRAMS\Backup Tool\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Create desktop shortcut
    CreateShortcut "$DESKTOP\Backup Tool.lnk" "$INSTDIR\BackupTool.exe" "" "$INSTDIR\backup_icon.ico"
    
    ; Write registry keys
    WriteRegStr HKCU "Software\Backup Tool" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool" "DisplayName" "Backup Tool"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool" "DisplayIcon" "$INSTDIR\backup_icon.ico"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool" "NoRepair" 1
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove files
    Delete "$INSTDIR\BackupTool.exe"
    Delete "$INSTDIR\backup_icon.ico"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\Backup Tool\Backup Tool.lnk"
    Delete "$SMPROGRAMS\Backup Tool\Uninstall.lnk"
    Delete "$DESKTOP\Backup Tool.lnk"
    RMDir "$SMPROGRAMS\Backup Tool"
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Backup Tool"
    DeleteRegKey HKCU "Software\Backup Tool"
    
    ; Remove install directory
    RMDir "$INSTDIR"
SectionEnd 