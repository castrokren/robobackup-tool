#!/usr/bin/env python3
"""
RoboBackup Service - Standalone backup service for running scheduled backups
when the user is not logged in.

This service can be:
1. Installed as a Windows Service
2. Run as a Scheduled Task
3. Run manually from command line
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class BackupService(win32serviceutil.ServiceFramework):
    """Windows Service for running scheduled backups"""
    
    _svc_name_ = "RoboBackupService"
    _svc_display_name_ = "RoboBackup Backup Service"
    _svc_description_ = "Runs scheduled backups for RoboBackup Tool"
    
    def __init__(self, args):
        # Ensure args has at least one element for ServiceFramework
        if not args:
            args = ['backup_service.py']
        
        # Only initialize ServiceFramework if we're running as a service
        # When running as a service, sys.argv has only one element
        # When running installation commands, sys.argv has multiple elements
        if len(sys.argv) == 1:
            win32serviceutil.ServiceFramework.__init__(self, args)
        else:
            # For installation/removal commands, don't initialize the service framework
            # This prevents the "service name is not hosted by this process" error
            pass
            
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = False
        self.scheduler_thread = None
        
        # Setup logging
        self.setup_logging()
        
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
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Stopping RoboBackup Service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        
    def SvcDoRun(self):
        """Run the service"""
        self.logger.info("Starting RoboBackup Service...")
        self.running = True
        
        # Report that we're starting
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        
        try:
            self.main()
        except Exception as e:
            self.logger.error(f"Service failed to start: {str(e)}")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            raise
        
    def load_settings(self):
        """Load settings from the encrypted settings file"""
        try:
            settings_file = Path("config/settings.encrypted")
            if not settings_file.exists():
                self.logger.info("Settings file not found, using default settings")
                return {"scheduled_backups": []}
                
            # Load encryption key
            key_file = Path("config/credential_key.key")
            if not key_file.exists():
                self.logger.info("Encryption key not found, using default settings")
                return {"scheduled_backups": []}
                
            with open(key_file, 'rb') as f:
                key = f.read()
                
            f = Fernet(key)
            
            with open(settings_file, 'rb') as sf:
                encrypted_data = sf.read()
                
            decrypted_data = f.decrypt(encrypted_data)
            settings = json.loads(decrypted_data.decode(), object_hook=self.datetime_decoder)
            
            self.logger.info("Settings loaded successfully")
            return settings
            
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            return {}
            
    def datetime_decoder(self, obj):
        """Custom JSON decoder to handle datetime objects"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    try:
                        # Try to parse as ISO format datetime
                        obj[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
        return obj
        
    def run_backup(self, backup_info):
        """Run a single backup"""
        try:
            source = backup_info["source"]
            dest = backup_info["dest"]
            flags = backup_info["flags"]
            source_user = backup_info.get("source_user", "")
            source_pwd = backup_info.get("source_pwd", "")
            dest_user = backup_info.get("dest_user", "")
            dest_pwd = backup_info.get("dest_pwd", "")
            
            # Decrypt passwords if they're encrypted
            if isinstance(source_pwd, bytes):
                key_file = Path("config/credential_key.key")
                with open(key_file, 'rb') as f:
                    key = f.read()
                f = Fernet(key)
                source_pwd = f.decrypt(source_pwd).decode()
                
            if isinstance(dest_pwd, bytes):
                key_file = Path("config/credential_key.key")
                with open(key_file, 'rb') as f:
                    key = f.read()
                f = Fernet(key)
                dest_pwd = f.decrypt(dest_pwd).decode()
            
            # Build robocopy command
            cmd = ["robocopy", source, dest]
            cmd.extend(flags.split())
            
            # Add credentials if provided
            if source_user and source_pwd:
                cmd.extend(["/user:" + source_user, "/pass:" + source_pwd])
            if dest_user and dest_pwd:
                cmd.extend(["/user:" + dest_user, "/pass:" + dest_pwd])
                
            self.logger.info(f"Running backup: {' '.join(cmd[:3])}...")
            
            # Run robocopy
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode < 8:  # Robocopy success codes are 0-7
                self.logger.info(f"Backup completed successfully (exit code: {result.returncode})")
                return True
            else:
                self.logger.error(f"Backup failed (exit code: {result.returncode})")
                self.logger.error(f"Error output: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error running backup: {str(e)}")
            return False
            
    def scheduler_thread(self):
        """Main scheduler thread that checks for scheduled backups"""
        self.logger.info("Scheduler thread started")
        
        while self.running:
            try:
                # Load settings (in case they were updated)
                settings = self.load_settings()
                scheduled_backups = settings.get("scheduled_backups", [])
                
                now = datetime.now()
                
                for backup in scheduled_backups[:]:  # Create a copy to safely modify
                    if backup["datetime"] <= now:
                        self.logger.info(f"Running scheduled backup: {backup['source']} -> {backup['dest']}")
                        
                        if self.run_backup(backup):
                            # Remove one-time backups after running
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
                            self.save_settings(settings)
                        else:
                            self.logger.error("Scheduled backup failed")
                            
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler thread: {str(e)}")
                time.sleep(60)  # Wait before retrying
                
    def save_settings(self, settings):
        """Save settings to encrypted file"""
        try:
            # Load encryption key
            key_file = Path("config/credential_key.key")
            if not key_file.exists():
                self.logger.info("Encryption key not found, skipping save")
                return
                
            with open(key_file, 'rb') as f:
                key = f.read()
                
            f = Fernet(key)
            
            # Convert datetime objects to ISO format for JSON serialization
            def datetime_encoder(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
                
            # Serialize settings
            settings_json = json.dumps(settings, default=datetime_encoder)
            encrypted_data = f.encrypt(settings_json.encode())
            
            # Save encrypted settings
            settings_file = Path("config/settings.encrypted")
            settings_file.parent.mkdir(exist_ok=True)
            
            with open(settings_file, 'wb') as sf:
                sf.write(encrypted_data)
                
            self.logger.info("Settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            
    def main(self):
        """Main service loop"""
        try:
            # Report that we're running
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self.scheduler_thread, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.info("RoboBackup Service is running")
            
            # Wait for stop signal
            while self.running:
                # Check if we should stop
                if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
        except Exception as e:
            self.logger.error(f"Service error: {str(e)}")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
            raise
        finally:
            self.logger.info("RoboBackup Service stopped")
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def run_as_service():
    """Run the service using Windows Service Manager"""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BackupService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BackupService)


def run_standalone():
    """Run the service standalone (for testing or manual execution)"""
    print("Starting RoboBackup Service in standalone mode...")
    
    # Create a simple service-like object for standalone mode
    class StandaloneService:
        def __init__(self):
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)
            self.running = False
            self.scheduler_thread = None
            self.setup_logging()
            
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
            
        def main(self):
            """Main service loop"""
            try:
                # Start scheduler thread
                self.scheduler_thread = threading.Thread(target=self.scheduler_thread, daemon=True)
                self.scheduler_thread.start()
                
                self.logger.info("RoboBackup Service is running in standalone mode")
                
                # Wait for stop signal (Ctrl+C)
                while self.running:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.logger.info("Received stop signal")
            except Exception as e:
                self.logger.error(f"Service error: {str(e)}")
            finally:
                self.logger.info("RoboBackup Service stopped")
                
        def scheduler_thread(self):
            """Scheduler thread for standalone mode"""
            # Import the same methods from BackupService
            service = BackupService(['backup_service.py'])
            service.scheduler_thread()
    
    service = StandaloneService()
    service.running = True
    service.main()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--standalone':
        run_standalone()
    else:
        run_as_service()