"""
Utilities package for RoboBackup Tool
"""

from .path_utils import (
    is_unc_path,
    normalize_unc_path,
    validate_path,
    ensure_directory_exists,
    get_safe_filename
)

from .logging_utils import (
    setup_logging,
    get_logger,
    log_exception,
    log_system_info,
    ContextLogger
)

from .security import (
    SecurityError,
    EncryptionManager,
    CredentialManager,
    TOTPManager,
    SecurityAuditor,
    generate_secure_token,
    secure_compare,
    hash_password,
    verify_password
)

from .config import (
    BackupJobConfig,
    AppConfig,
    ConfigManager
)

__all__ = [
    'is_unc_path',
    'normalize_unc_path', 
    'validate_path',
    'ensure_directory_exists',
    'get_safe_filename',
    'setup_logging',
    'get_logger',
    'log_exception',
    'log_system_info',
    'ContextLogger',
    'SecurityError',
    'EncryptionManager',
    'CredentialManager',
    'TOTPManager',
    'SecurityAuditor',
    'generate_secure_token',
    'secure_compare',
    'hash_password',
    'verify_password',
    'BackupJobConfig',
    'AppConfig',
    'ConfigManager'
]
