#!/usr/bin/env python3
"""
Simple backup service runner for NSSM
This replaces the complex Windows Service framework with a simple loop
"""

import os
import sys
import time
import logging
import signal
from pathlib import Path
from datetime import datetime, timedelta

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class SimpleBackupService:
    """Simple backup service that runs as a regular process"""
    
    def __init__(self):
        self.running = True
        self.setup_logging()
        
        # Handle shutdown signals gracefully
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def setup_logging(self):
        """Setup logging for the service"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "backup_service.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    def load_settings(self):
        """Load settings from the encrypted settings file"""
        try:
            # Import here to avoid circular imports
            from backup_service import BackupService
            
            # Use the existing settings loading logic
            temp_service = BackupService([])
            return temp_service.load_settings()
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            return {"scheduled_backups": []}
            
    def run_backup(self, backup_info):
        """Run a single backup"""
        try:
            # Import here to avoid circular imports
            from backup_service import BackupService
            
            # Use the existing backup logic
            temp_service = BackupService([])
            temp_service.logger = self.logger
            return temp_service.run_backup(backup_info)
            
        except Exception as e:
            self.logger.error(f"Error running backup: {str(e)}")
            return False
            
    def main_loop(self):
        """Main service loop"""
        self.logger.info("Simple Backup Service started (NSSM mode)")
        
        while self.running:
            try:
                # Load settings (in case they were updated)
                settings = self.load_settings()
                scheduled_backups = settings.get("scheduled_backups", [])
                
                now = datetime.now()
                
                for backup in scheduled_backups[:]:  # Create a copy to safely modify
                    backup_time = backup.get("datetime")
                    if backup_time and backup_time <= now:
                        self.logger.info(f"Running scheduled backup: {backup['source']} -> {backup['dest']}")
                        
                        if self.run_backup(backup):
                            # Handle recurring backups
                            if backup["frequency"] == "One-time":
                                scheduled_backups.remove(backup)
                                self.logger.info("Removed one-time backup from schedule")
                            else:
                                # Update next run time for recurring backups
                                if backup["frequency"] == "Daily":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=1)
                                elif backup["frequency"] == "Weekly":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=7)
                                elif backup["frequency"] == "Monthly":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=30)
                                    
                                self.logger.info(f"Updated next run time for {backup['frequency']} backup")
                                
                            # Save updated settings
                            try:
                                from backup_service import BackupService
                                temp_service = BackupService([])
                                temp_service.save_settings(settings)
                            except Exception as e:
                                self.logger.error(f"Error saving settings: {str(e)}")
                        else:
                            self.logger.error("Scheduled backup failed")
                            
                # Sleep for a minute before checking again
                for _ in range(60):  # Sleep in 1-second intervals to be responsive to shutdown
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait before retrying
                
        self.logger.info("Simple Backup Service stopped")


if __name__ == '__main__':
    service = SimpleBackupService()
    service.main_loop()