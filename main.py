import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_for_updates():
    """Check for updates on startup"""
    try:
        from update_gui import check_for_updates_gui
        result = check_for_updates_gui()
        
        if result:
            logger.info(f"Update dialog result: {result}")
            return result
        else:
            logger.info("No updates available")
            return None
            
    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return None

def main():
    """Main application entry point"""
    # Check for updates (GUI dialog will show if updates are available)
    update_result = check_for_updates()
    
    if len(sys.argv) > 1 and sys.argv[1] == "service":
        # Run as service
        import backup_service
        backup_service.main()  # Or: win32serviceutil.HandleCommandLine(backup_service.BackupService)
    else:
        # Run GUI
        import backupapp
        backupapp.run_gui()  # <-- You need to define this in backupapp.py

if __name__ == "__main__":
    main()