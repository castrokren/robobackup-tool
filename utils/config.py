"""
Configuration management utilities for RoboBackup Tool
Handles application settings, validation, and persistent storage
"""

import os
import json
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from .logging_utils import get_logger, log_exception
from .path_utils import validate_path, ensure_directory_exists
from .security import EncryptionManager

logger = get_logger(__name__)


@dataclass
class BackupJobConfig:
    """Configuration for a backup job"""
    name: str
    source_path: str
    destination_path: str
    robocopy_flags: str = "/MIR /FFT /R:3 /W:10 /XJD /XJF"
    enabled: bool = True
    schedule_enabled: bool = False
    schedule_type: str = "daily"  # daily, weekly, monthly
    schedule_time: str = "02:00"  # HH:MM format
    source_credentials_key: Optional[str] = None
    dest_credentials_key: Optional[str] = None
    exclude_folders: List[str] = field(default_factory=list)
    exclude_files: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run: Optional[str] = None
    last_success: Optional[str] = None
    
    def validate(self) -> tuple[bool, str]:
        """Validate backup job configuration"""
        # Validate required fields
        if not self.name or not self.name.strip():
            return False, "Job name cannot be empty"
        
        if not self.source_path or not self.source_path.strip():
            return False, "Source path cannot be empty"
        
        if not self.destination_path or not self.destination_path.strip():
            return False, "Destination path cannot be empty"
        
        # Validate paths
        is_valid, error = validate_path(self.source_path)
        if not is_valid:
            return False, f"Invalid source path: {error}"
        
        is_valid, error = validate_path(self.destination_path)
        if not is_valid:
            return False, f"Invalid destination path: {error}"
        
        # Validate schedule if enabled
        if self.schedule_enabled:
            if not self.schedule_time:
                return False, "Schedule time is required when scheduling is enabled"
            
            try:
                time_parts = self.schedule_time.split(":")
                if len(time_parts) != 2:
                    raise ValueError("Invalid format")
                hour, minute = int(time_parts[0]), int(time_parts[1])
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Invalid time range")
            except ValueError:
                return False, "Schedule time must be in HH:MM format (24-hour)"
        
        return True, ""


@dataclass 
class AppConfig:
    """Main application configuration"""
    # Logging settings
    log_level: str = "INFO"
    log_retention_days: int = 30
    max_log_files: int = 100
    
    # UI settings
    theme: str = "light"  # light, dark, auto
    check_updates_on_startup: bool = True
    minimize_to_tray: bool = True
    show_tray_notifications: bool = True
    
    # Security settings
    require_password: bool = True
    session_timeout_minutes: int = 30
    max_failed_attempts: int = 3
    lockout_duration_minutes: int = 5
    enable_2fa: bool = False
    
    # Backup settings
    default_robocopy_flags: str = "/MIR /FFT /R:3 /W:10 /XJD /XJF"
    backup_timeout_hours: int = 24
    concurrent_backups: int = 1
    
    # Network settings
    network_timeout_seconds: int = 30
    retry_attempts: int = 3
    
    # Paths
    config_dir: str = "config"
    log_dir: str = "logs"
    temp_dir: str = "temp"
    
    def validate(self) -> tuple[bool, str]:
        """Validate application configuration"""
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            return False, f"Invalid log level. Must be one of: {', '.join(valid_levels)}"
        
        # Validate numeric ranges
        if self.log_retention_days < 1:
            return False, "Log retention days must be at least 1"
        
        if self.max_log_files < 1:
            return False, "Max log files must be at least 1"
        
        if self.session_timeout_minutes < 1:
            return False, "Session timeout must be at least 1 minute"
        
        if self.backup_timeout_hours < 1:
            return False, "Backup timeout must be at least 1 hour"
        
        if self.concurrent_backups < 1:
            return False, "Concurrent backups must be at least 1"
        
        # Validate theme
        valid_themes = ["light", "dark", "auto"]
        if self.theme not in valid_themes:
            return False, f"Invalid theme. Must be one of: {', '.join(valid_themes)}"
        
        return True, ""


class ConfigManager:
    """Manages application configuration and backup jobs"""
    
    def __init__(
        self, 
        config_file: str = "config/app_settings.json",
        jobs_file: str = "config/backup_jobs.json",
        encrypted: bool = False,
        encryption_password: Optional[str] = None
    ):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to application config file
            jobs_file: Path to backup jobs config file
            encrypted: Whether to encrypt configuration files
            encryption_password: Password for encryption (required if encrypted=True)
        """
        self.config_file = config_file
        self.jobs_file = jobs_file
        self.encrypted = encrypted
        self.encryption_password = encryption_password
        
        if self.encrypted and not self.encryption_password:
            raise ValueError("Encryption password required when encrypted=True")
        
        self.encryption_manager = EncryptionManager() if encrypted else None
        
        # Ensure config directories exist
        for config_path in [self.config_file, self.jobs_file]:
            config_dir = os.path.dirname(config_path)
            if config_dir:
                ensure_directory_exists(config_dir)
        
        # Load configurations
        self.app_config = self.load_app_config()
        self.backup_jobs = self.load_backup_jobs()
    
    def load_app_config(self) -> AppConfig:
        """Load application configuration from file"""
        try:
            if not os.path.exists(self.config_file):
                logger.info(f"Config file not found, creating default: {self.config_file}")
                config = AppConfig()
                self.save_app_config(config)
                return config
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = f.read()
            
            if self.encrypted and self.encryption_manager:
                data = self.encryption_manager.decrypt_data(data, self.encryption_password)
            
            config_dict = json.loads(data)
            config = AppConfig(**config_dict)
            
            # Validate configuration
            is_valid, error = config.validate()
            if not is_valid:
                logger.error(f"Invalid configuration: {error}")
                logger.info("Using default configuration")
                return AppConfig()
            
            logger.info("Application configuration loaded successfully")
            return config
            
        except Exception as e:
            log_exception(logger, f"Failed to load app config from {self.config_file}")
            logger.info("Using default configuration")
            return AppConfig()
    
    def save_app_config(self, config: AppConfig) -> bool:
        """Save application configuration to file"""
        try:
            # Validate before saving
            is_valid, error = config.validate()
            if not is_valid:
                logger.error(f"Cannot save invalid configuration: {error}")
                return False
            
            config_dict = asdict(config)
            data = json.dumps(config_dict, indent=2)
            
            if self.encrypted and self.encryption_manager:
                data = self.encryption_manager.encrypt_data(data, self.encryption_password)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(data)
            
            self.app_config = config
            logger.info("Application configuration saved successfully")
            return True
            
        except Exception as e:
            log_exception(logger, f"Failed to save app config to {self.config_file}")
            return False
    
    def load_backup_jobs(self) -> List[BackupJobConfig]:
        """Load backup jobs from file"""
        try:
            if not os.path.exists(self.jobs_file):
                logger.info(f"Jobs file not found, creating empty: {self.jobs_file}")
                self.save_backup_jobs([])
                return []
            
            with open(self.jobs_file, 'r', encoding='utf-8') as f:
                data = f.read()
            
            if self.encrypted and self.encryption_manager:
                data = self.encryption_manager.decrypt_data(data, self.encryption_password)
            
            jobs_data = json.loads(data)
            jobs = []
            
            for job_dict in jobs_data:
                try:
                    job = BackupJobConfig(**job_dict)
                    is_valid, error = job.validate()
                    if is_valid:
                        jobs.append(job)
                    else:
                        logger.warning(f"Skipping invalid backup job '{job.name}': {error}")
                except Exception as e:
                    logger.warning(f"Skipping malformed backup job: {e}")
            
            logger.info(f"Loaded {len(jobs)} backup jobs")
            return jobs
            
        except Exception as e:
            log_exception(logger, f"Failed to load backup jobs from {self.jobs_file}")
            return []
    
    def save_backup_jobs(self, jobs: List[BackupJobConfig]) -> bool:
        """Save backup jobs to file"""
        try:
            # Validate all jobs before saving
            valid_jobs = []
            for job in jobs:
                is_valid, error = job.validate()
                if is_valid:
                    valid_jobs.append(job)
                else:
                    logger.error(f"Skipping invalid job '{job.name}': {error}")
            
            jobs_data = [asdict(job) for job in valid_jobs]
            data = json.dumps(jobs_data, indent=2)
            
            if self.encrypted and self.encryption_manager:
                data = self.encryption_manager.encrypt_data(data, self.encryption_password)
            
            with open(self.jobs_file, 'w', encoding='utf-8') as f:
                f.write(data)
            
            self.backup_jobs = valid_jobs
            logger.info(f"Saved {len(valid_jobs)} backup jobs")
            return True
            
        except Exception as e:
            log_exception(logger, f"Failed to save backup jobs to {self.jobs_file}")
            return False
    
    def add_backup_job(self, job: BackupJobConfig) -> bool:
        """Add a new backup job"""
        # Validate job
        is_valid, error = job.validate()
        if not is_valid:
            logger.error(f"Cannot add invalid backup job: {error}")
            return False
        
        # Check for duplicate names
        if any(existing_job.name == job.name for existing_job in self.backup_jobs):
            logger.error(f"Backup job with name '{job.name}' already exists")
            return False
        
        self.backup_jobs.append(job)
        return self.save_backup_jobs(self.backup_jobs)
    
    def update_backup_job(self, job_name: str, updated_job: BackupJobConfig) -> bool:
        """Update an existing backup job"""
        # Validate updated job
        is_valid, error = updated_job.validate()
        if not is_valid:
            logger.error(f"Cannot update with invalid backup job: {error}")
            return False
        
        # Find and update job
        for i, job in enumerate(self.backup_jobs):
            if job.name == job_name:
                self.backup_jobs[i] = updated_job
                return self.save_backup_jobs(self.backup_jobs)
        
        logger.error(f"Backup job '{job_name}' not found")
        return False
    
    def delete_backup_job(self, job_name: str) -> bool:
        """Delete a backup job"""
        original_count = len(self.backup_jobs)
        self.backup_jobs = [job for job in self.backup_jobs if job.name != job_name]
        
        if len(self.backup_jobs) < original_count:
            return self.save_backup_jobs(self.backup_jobs)
        else:
            logger.error(f"Backup job '{job_name}' not found")
            return False
    
    def get_backup_job(self, job_name: str) -> Optional[BackupJobConfig]:
        """Get a backup job by name"""
        for job in self.backup_jobs:
            if job.name == job_name:
                return job
        return None
    
    def get_enabled_jobs(self) -> List[BackupJobConfig]:
        """Get all enabled backup jobs"""
        return [job for job in self.backup_jobs if job.enabled]
    
    def get_scheduled_jobs(self) -> List[BackupJobConfig]:
        """Get all jobs that have scheduling enabled"""
        return [job for job in self.backup_jobs if job.enabled and job.schedule_enabled]
