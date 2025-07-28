import sys
import os

if len(sys.argv) > 1 and sys.argv[1] == "service":
    # Run as service
    import backup_service
    backup_service.main()  # Or: win32serviceutil.HandleCommandLine(backup_service.BackupService)
else:
    # Run GUI
    import backupapp
    backupapp.run_gui()  # <-- You need to define this in backupapp.py