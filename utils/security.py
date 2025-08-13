"""
Security utilities for RoboBackup Tool
Consolidated security functionality including encryption, credential management, and authentication
"""

import os
import base64
import secrets
import hmac
import hashlib
import time
from typing import Optional, Tuple, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pyotp
import qrcode
from io import BytesIO
from .logging_utils import get_logger, log_exception

logger = get_logger(__name__)


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class EncryptionManager:
    """Handles encryption and decryption operations"""
    
    def __init__(self, salt_file: str = "config/log_salt.bin"):
        """
        Initialize encryption manager
        
        Args:
            salt_file: Path to salt file for key derivation
        """
        self.salt_file = salt_file
        self._ensure_salt_file()
    
    def _ensure_salt_file(self):
        """Ensure salt file exists, create if it doesn't"""
        try:
            os.makedirs(os.path.dirname(self.salt_file), exist_ok=True)
            if not os.path.exists(self.salt_file):
                salt = secrets.token_bytes(32)
                with open(self.salt_file, 'wb') as f:
                    f.write(salt)
                logger.info(f"Created new salt file: {self.salt_file}")
        except Exception as e:
            raise SecurityError(f"Failed to create salt file: {e}")
    
    def _get_salt(self) -> bytes:
        """Get salt from file"""
        try:
            with open(self.salt_file, 'rb') as f:
                return f.read()
        except Exception as e:
            raise SecurityError(f"Failed to read salt file: {e}")
    
    def derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Password to derive key from
            
        Returns:
            Derived key bytes
        """
        try:
            salt = self._get_salt()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,  # OWASP recommended minimum
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
        except Exception as e:
            raise SecurityError(f"Key derivation failed: {e}")
    
    def encrypt_data(self, data: str, password: str) -> str:
        """
        Encrypt data using password-derived key
        
        Args:
            data: Data to encrypt
            password: Password for encryption
            
        Returns:
            Base64-encoded encrypted data
        """
        try:
            key = self.derive_key(password)
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise SecurityError(f"Encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str, password: str) -> str:
        """
        Decrypt data using password-derived key
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            password: Password for decryption
            
        Returns:
            Decrypted data
        """
        try:
            key = self.derive_key(password)
            fernet = Fernet(key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise SecurityError(f"Decryption failed: {e}")


class CredentialManager:
    """Manages secure storage of credentials"""
    
    def __init__(self, credentials_file: str = "config/credentials.dat"):
        """
        Initialize credential manager
        
        Args:
            credentials_file: Path to encrypted credentials file
        """
        self.credentials_file = credentials_file
        self.encryption_manager = EncryptionManager()
        self._credentials_cache = {}
    
    def store_credential(self, key: str, value: str, master_password: str) -> bool:
        """
        Store encrypted credential
        
        Args:
            key: Credential identifier
            value: Credential value to encrypt
            master_password: Master password for encryption
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing credentials
            credentials = self._load_credentials(master_password)
            
            # Add/update credential
            credentials[key] = value
            
            # Save back
            return self._save_credentials(credentials, master_password)
        except Exception as e:
            log_exception(logger, f"Failed to store credential {key}")
            return False
    
    def retrieve_credential(self, key: str, master_password: str) -> Optional[str]:
        """
        Retrieve decrypted credential
        
        Args:
            key: Credential identifier
            master_password: Master password for decryption
            
        Returns:
            Decrypted credential value or None if not found
        """
        try:
            credentials = self._load_credentials(master_password)
            return credentials.get(key)
        except Exception as e:
            log_exception(logger, f"Failed to retrieve credential {key}")
            return None
    
    def _load_credentials(self, master_password: str) -> Dict[str, str]:
        """Load and decrypt credentials from file"""
        if not os.path.exists(self.credentials_file):
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                encrypted_data = f.read()
            
            if not encrypted_data.strip():
                return {}
            
            decrypted_json = self.encryption_manager.decrypt_data(encrypted_data, master_password)
            import json
            return json.loads(decrypted_json)
        except Exception as e:
            raise SecurityError(f"Failed to load credentials: {e}")
    
    def _save_credentials(self, credentials: Dict[str, str], master_password: str) -> bool:
        """Encrypt and save credentials to file"""
        try:
            import json
            json_data = json.dumps(credentials)
            encrypted_data = self.encryption_manager.encrypt_data(json_data, master_password)
            
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            with open(self.credentials_file, 'w') as f:
                f.write(encrypted_data)
            
            logger.info("Credentials saved successfully")
            return True
        except Exception as e:
            log_exception(logger, "Failed to save credentials")
            return False


class TOTPManager:
    """Handles Time-based One-Time Password (TOTP) operations"""
    
    def __init__(self):
        """Initialize TOTP manager"""
        self.issuer_name = "RoboBackup Tool"
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret
        
        Returns:
            Base32-encoded secret
        """
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, account_name: str) -> bytes:
        """
        Generate QR code for TOTP setup
        
        Args:
            secret: TOTP secret
            account_name: Account identifier
            
        Returns:
            PNG image data
        """
        try:
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=account_name,
                issuer_name=self.issuer_name
            )
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            return img_buffer.getvalue()
        except Exception as e:
            raise SecurityError(f"Failed to generate QR code: {e}")
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: TOTP secret
            token: Token to verify
            window: Time window tolerance (default 1 = ±30 seconds)
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.warning(f"TOTP verification failed: {e}")
            return False
    
    def generate_token(self, secret: str) -> str:
        """
        Generate current TOTP token
        
        Args:
            secret: TOTP secret
            
        Returns:
            Current 6-digit token
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            raise SecurityError(f"Failed to generate token: {e}")


class SecurityAuditor:
    """Handles security auditing and validation"""
    
    def __init__(self):
        """Initialize security auditor"""
        self.failed_attempts = {}
        self.max_attempts = 3
        self.lockout_duration = 300  # 5 minutes
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'admin']
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                return False, f"Password contains common pattern: {pattern}"
        
        return True, "Password strength is acceptable"
    
    def record_failed_attempt(self, identifier: str):
        """
        Record a failed authentication attempt
        
        Args:
            identifier: Identifier for the attempt (e.g., username, IP)
        """
        current_time = time.time()
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        self.failed_attempts[identifier].append(current_time)
        
        # Clean old attempts
        cutoff_time = current_time - self.lockout_duration
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier] 
            if attempt > cutoff_time
        ]
        
        logger.warning(f"Failed authentication attempt recorded for {identifier}")
    
    def is_locked_out(self, identifier: str) -> bool:
        """
        Check if identifier is locked out due to failed attempts
        
        Args:
            identifier: Identifier to check
            
        Returns:
            True if locked out, False otherwise
        """
        if identifier not in self.failed_attempts:
            return False
        
        current_time = time.time()
        cutoff_time = current_time - self.lockout_duration
        
        # Clean old attempts
        self.failed_attempts[identifier] = [
            attempt for attempt in self.failed_attempts[identifier] 
            if attempt > cutoff_time
        ]
        
        return len(self.failed_attempts[identifier]) >= self.max_attempts
    
    def clear_failed_attempts(self, identifier: str):
        """
        Clear failed attempts for identifier (after successful auth)
        
        Args:
            identifier: Identifier to clear
        """
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
            logger.info(f"Cleared failed attempts for {identifier}")


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: Token length in bytes
        
    Returns:
        Base64-encoded token
    """
    token_bytes = secrets.token_bytes(length)
    return base64.urlsafe_b64encode(token_bytes).decode()


def secure_compare(a: str, b: str) -> bool:
    """
    Securely compare two strings to prevent timing attacks
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal, False otherwise
    """
    return hmac.compare_digest(a.encode(), b.encode())


def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """
    Hash password with salt using PBKDF2
    
    Args:
        password: Password to hash
        salt: Optional salt (generated if None)
        
    Returns:
        Tuple of (hash, salt) both base64-encoded
    """
    if salt is None:
        salt = secrets.token_bytes(32)
    
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 480000)
    
    return (
        base64.urlsafe_b64encode(pwdhash).decode(),
        base64.urlsafe_b64encode(salt).decode()
    )


def verify_password(password: str, hash_b64: str, salt_b64: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Password to verify
        hash_b64: Base64-encoded hash
        salt_b64: Base64-encoded salt
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        stored_hash = base64.urlsafe_b64decode(hash_b64.encode())
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 480000)
        return hmac.compare_digest(stored_hash, computed_hash)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False
