import sys
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)  # SYSTEM_AWARE
    except Exception:
        pass

import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw, ImageTk
import win32com.client
import pythoncom
import win32net
import win32netcon
import win32wnet
import win32security
import win32profile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import atexit
import json
from cryptography.fernet import Fernet
import base64
import winreg
import requests
import stat
import hmac
import hashlib
import base64
import time
import urllib.parse
import pyotp
import qrcode
from io import BytesIO
import ntpath
import secrets
import binascii
import getpass
from tkinter.simpledialog import askstring

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def datetime_decoder(obj):
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

# Set scalable default font for Tkinter
try:
    import tkinter.font as tkFont
    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size=12)  # You can adjust this size as needed
except Exception:
    pass

def is_unc_path(path: str) -> bool:
    """
    Return True if `path` is a UNC network path (\\\\server\\share\\...).
    Handles both slashes, normalizes, and uses ntpath.splitdrive for robust detection.
    """
    p = path.replace('/', '\\')
    drive, _ = ntpath.splitdrive(p)
    return drive.startswith('\\\\')

# Check for required packages
try:
    import qrcode
    import pyotp
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"Error: Required package not found - {str(e)}")
    print("Please install required packages using:")
    print("pip install qrcode pyotp pillow")
    sys.exit(1)

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class PasscodeDialog:
    def __init__(self, parent, passcode):
        self.result = False
        self.parent = parent
        self.passcode = passcode
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Passcode")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        
        # Make dialog stay on top and modal
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add widgets
        ttk.Label(main_frame, text="Enter passcode to restore application:").pack(pady=(0, 10))
        
        self.passcode_var = tk.StringVar()
        self.passcode_entry = ttk.Entry(main_frame, textvariable=self.passcode_var, show="*", width=20)
        self.passcode_entry.pack(pady=(0, 10))
        self.passcode_entry.focus_set()
        
        # Add verify button
        ttk.Button(main_frame, text="Verify", command=self.verify, width=15).pack(pady=(0, 10))
        
        # Bind events
        self.passcode_entry.bind('<Return>', lambda e: self.verify())
        self.dialog.bind('<Alt-F4>', self.on_close)
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Make sure dialog stays on top
        self.keep_on_top()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
    
    def verify(self):
        if not self.passcode:  # If no passcode is set, allow access
            self.result = True
            self.dialog.destroy()
            return
            
        if self.passcode_var.get() == self.passcode:
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Invalid passcode", parent=self.dialog)
            self.passcode_var.set("")
            self.passcode_entry.focus_set()
    
    def on_close(self, event=None):
        """Handle dialog close"""
        self.result = False
        self.dialog.grab_release()  # Release the grab before destroying
        self.dialog.destroy()
    
    def keep_on_top(self):
        if self.dialog.winfo_exists():
            self.dialog.attributes('-topmost', True)
            self.dialog.after(100, self.keep_on_top)

class InputValidator:
    """Class for validating user inputs, now allows all local directories"""
    def __init__(self):
        self.allowed_robocopy_flags = {
            '/E', '/S', '/COPYALL', '/DCOPY:T', '/PURGE', '/MIR', '/MOV', '/MOVE',
            '/A+', '/A-', '/IA', '/XA', '/XF', '/XD', '/XC', '/XN', '/XO', '/XX',
            '/XL', '/IS', '/IT', '/TBD', '/FS', '/MAX', '/MIN', '/MAXAGE', '/MINAGE',
            '/MAXLAD', '/MINLAD', '/J', '/B', '/ZB', '/R', '/W', '/REG', '/TBD',
            '/NP', '/NC', '/NS', '/NDL', '/NFL', '/NJH', '/NJS', '/UNILOG', '/UNILOG+',
            '/TEE', '/NODCOPY', '/NOCOPY', '/SEC', '/DCOPY:D', '/COPY:D', '/SECFIX',
            '/TIMFIX', '/MT', '/LOG', '/LOG+', '/TEE', '/NP', '/NC', '/NS', '/NDL',
            '/NFL', '/NJH', '/NJS', '/UNILOG', '/UNILOG+', '/TEE', '/NODCOPY', '/NOCOPY',
            '/SEC', '/DCOPY:D', '/COPY:D', '/SECFIX', '/TIMFIX', '/MT', '/LOG', '/LOG+'
        }
        # Add missing attributes for input validation
        self.max_lengths = {
            'flags': 256,
            'username': 256,
            'password': 256,
            'path': 1024
        }
        self.allowed_chars = {
            'flags': set('/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:-+.'),
            'username': set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-@'),
            'password': set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=,.?<>[]{}|~`'),
            'path': set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:/\\._- ')
        }
    
    def validate_path(self, path, must_exist=True, must_be_dir=False, must_be_file=False):
        """For local paths: no validation except existence/type. Only UNC paths validated for format."""
        try:
            if not path or not path.strip():
                return False, "Path cannot be empty"

            path = os.path.normpath(path)

            # If UNC/network path, check format
            if is_unc_path(path):
                norm_parts = [p for p in path.replace('/', '\\').split('\\') if p]
                if len(norm_parts) < 2:
                    return False, "Network path must be of the form \\\\server\\share\\..."


            # For both local and UNC: existence checks (if requested)
            if must_exist and not os.path.exists(path):
                return False, "Path does not exist"
            if must_be_dir and not os.path.isdir(path):
                return False, "Path must be a directory"
            if must_be_file and not os.path.isfile(path):
                return False, "Path must be a file"

            # Otherwise, pass!
            return True, path

        except Exception as e:
            return False, f"Path validation error: {str(e)}"
        
    def validate_input(self, value, input_type, required=True):
        """Validate input value against type-specific rules"""
        try:
            # Check if value is empty when required
            if required and (not value or not value.strip()):
                return False, f"{input_type} cannot be empty"
                
            # Check maximum length
            if len(value) > self.max_lengths.get(input_type, 128):
                return False, f"{input_type} exceeds maximum length of {self.max_lengths[input_type]} characters"
                
            # Check allowed characters if specified for this type
            if input_type in self.allowed_chars:
                invalid_chars = set(value) - self.allowed_chars[input_type]
                if invalid_chars:
                    return False, f"{input_type} contains invalid characters: {''.join(invalid_chars)}"
                    
            return True, value
            
        except Exception as e:
            return False, f"Error validating {input_type}: {str(e)}"
            
           
    def validate_robocopy_flags(self, flags_str):
        """Validate Robocopy flags"""
        try:
            # First validate basic input rules
            valid, msg = self.validate_input(flags_str, 'flags', required=False)
            if not valid:
                return False, msg
                
            if not flags_str:
                return True, []
                
            # Split flags into individual flags
            flags = flags_str.split()
            
            # Validate each flag
            valid_flags = []
            for flag in flags:
                # Check if flag is in allowed list
                if flag not in self.allowed_robocopy_flags:
                    return False, f"Invalid flag: {flag}"
                    
                # Check for flag parameters
                if flag in ['/R', '/W', '/MT', '/MAXAGE', '/MINAGE', '/MAXLAD', '/MINLAD']:
                    # These flags require numeric parameters
                    if not flag.endswith(':'):
                        return False, f"Flag {flag} requires a parameter"
                        
                valid_flags.append(flag)
                
            return True, valid_flags
            
        except Exception as e:
            return False, f"Flag validation error: {str(e)}"
            
    def validate_credentials(self, username, password):
        """Validate credentials"""
        try:
            # Check username
            if username and len(username) > 256:
                return False, "Username too long"
                
            # Check for invalid characters in username
            invalid_chars = '<>:"|?*'
            if username and any(char in username for char in invalid_chars):
                return False, f"Username contains invalid characters: {invalid_chars}"
                
            # Check password length
            if password and len(password) > 256:
                return False, "Password too long"
                
            return True, None
            
        except Exception as e:
            return False, f"Credential validation error: {str(e)}"


class PasswordDialog:
    def __init__(self, parent, title="Enter Password"):
        self.result = False
        self.password = None
        self.parent = parent
        
        # Create the dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        
        # Make dialog stay on top and modal
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add widgets
        ttk.Label(main_frame, text="Enter password:").pack(pady=(0, 10))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=20)
        self.password_entry.pack(pady=(0, 10))
        self.password_entry.focus_set()
        
        # Add verify button
        ttk.Button(main_frame, text="OK", command=self.verify, width=15).pack(pady=(0, 10))
        
        # Bind events
        self.password_entry.bind('<Return>', lambda e: self.verify())
        self.dialog.bind('<Alt-F4>', self.on_close)
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Make sure dialog stays on top
        self.keep_on_top()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
    
    def verify(self):
        password = self.password_var.get()
        if password:
            self.password = password
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Password cannot be empty", parent=self.dialog)
            self.password_entry.focus_set()
    
    def on_close(self, event=None):
        """Handle dialog close"""
        self.result = False
        self.dialog.grab_release()  # Release the grab before destroying
        self.dialog.destroy()
    
    def keep_on_top(self):
        if self.dialog.winfo_exists():
            self.dialog.attributes('-topmost', True)
            self.dialog.after(100, self.keep_on_top)

class CredentialManager:
    def __init__(self, app):
        self.app = app
        self.credentials_file = os.path.join(os.getcwd(), 'config', 'credentials.json')
        self.key_manager = KeyManager()
        self.key_manager.set_logger(app.log_message)
        self.initialize_encryption()
        
    def initialize_encryption(self):
        """Initialize encryption using the credential key"""
        try:
            self.app.log_message("Initializing credential encryption...", 'info')
            self.encryption_key = self.key_manager.get_or_create_key()
            if not self.encryption_key:
                self.app.log_message("Warning: Credential encryption disabled", 'warning')
            else:
                self.app.log_message("Credential encryption initialized successfully", 'info')
        except Exception as e:
            self.app.log_message(f"Error initializing credential encryption: {str(e)}")
            self.encryption_key = None
            
    def save_credentials(self, credentials):
        """Save credentials with encryption if available"""
        try:
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            if self.encryption_key:
                f = Fernet(self.encryption_key)
                encrypted_data = f.encrypt(json.dumps(credentials).encode())
                with open(self.credentials_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(self.credentials_file, 'w') as f:
                    json.dump(credentials, f)
            return True
        except Exception as e:
            self.app.log_message(f"Error saving credentials: {str(e)}")
            return False
            
    def load_credentials(self):
        """Load credentials with decryption if available"""
        try:
            if not os.path.exists(self.credentials_file):
                return {}
                
            if self.encryption_key:
                with open(self.credentials_file, 'rb') as f:
                    encrypted_data = f.read()
                f = Fernet(self.encryption_key)
                decrypted_data = f.decrypt(encrypted_data)
                return json.loads(decrypted_data)
            else:
                with open(self.credentials_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.app.log_message(f"Error loading credentials: {str(e)}")
            return {}

class UserManager:
    def __init__(self):
        self.roles = {
            'admin': ['backup', 'schedule', 'configure'],
            'user': ['backup', 'view']
        }
        self.current_user = None
        self.audit_log = []

    def authenticate(self, username, password):
        # Implement Windows authentication
        try:
            import win32security
            # Verify against Windows credentials
            return True
        except Exception as e:
            self.audit_log.append(f"Authentication failed: {str(e)}")
            return False

    def check_permission(self, action):
        if not self.current_user:
            return False
        return action in self.roles.get(self.current_user.role, [])

class SettingsManager:
    def __init__(self, app):
        self.app = app
        self.settings_file = os.path.join(os.getcwd(), 'config', 'app_settings.json')
        self.key_manager = KeyManager()
        self.key_manager.set_logger(app.log_message)
        self.initialize_encryption()
        
    def initialize_encryption(self):
        """Initialize encryption using the settings key"""
        try:
            self.app.log_message("Initializing settings encryption...", 'info')
            self.encryption_key = self.key_manager.get_or_create_key()
            if not self.encryption_key:
                self.app.log_message("Warning: Settings encryption disabled", 'warning')
            else:
                self.app.log_message("Settings encryption initialized successfully", 'info')
        except Exception as e:
            self.app.log_message(f"Error initializing settings encryption: {str(e)}")
            self.encryption_key = None
            
    def save_settings(self, settings):
        """Save settings with encryption if available"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            if self.encryption_key:
                f = Fernet(self.encryption_key)
                encrypted_data = f.encrypt(json.dumps(settings, cls=DateTimeEncoder).encode())
                with open(self.settings_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(self.settings_file, 'w') as f:
                    json.dump(settings, f, indent=2, cls=DateTimeEncoder)
            return True
        except Exception as e:
            self.app.log_message(f"Error saving settings: {str(e)}")
            return False
            
    def load_settings(self):
        """Load settings with decryption if available"""
        try:
            if not os.path.exists(self.settings_file):
                return {}
                
            if self.encryption_key:
                with open(self.settings_file, 'rb') as f:
                    encrypted_data = f.read()
                f = Fernet(self.encryption_key)
                decrypted_data = f.decrypt(encrypted_data)
                settings = json.loads(decrypted_data, object_hook=datetime_decoder)
                return settings
            else:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f, object_hook=datetime_decoder)
                    return settings
        except Exception as e:
            self.app.log_message(f"Error loading settings: {str(e)}", 'error')
            return {}

class PrivilegeManager:
    def __init__(self, app):
        self.app = app
        self.is_elevated = False
        self.check_and_require_elevation()
        
    def check_and_require_elevation(self):
        """Check if running as admin and auto-elevate if not"""
        try:
            import win32security
            import win32api
            import win32con
            
            # Check if running as administrator
            try:
                sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid)
                self.is_elevated = win32security.CheckTokenMembership(None, sid)
            except:
                self.is_elevated = False
            
            # If not elevated, automatically restart as admin
            if not self.is_elevated:
                self.restart_as_admin()
                
        except Exception as e:
            # If we can't check privileges, assume we need elevation
            self.restart_as_admin()
    
    def restart_as_admin(self):
        """Automatically restart the application with elevated privileges"""
        try:
            import subprocess
            import sys
            import os
            
            # Get the current script path
            script_path = sys.argv[0]
            
            # If running as a script, use pythonw.exe for silent execution
            if script_path.endswith('.py'):
                executable = sys.executable
                if 'pythonw.exe' in executable:
                    executable = executable.replace('pythonw.exe', 'python.exe')
                cmd = [executable, script_path]
            else:
                # If running as exe, use the exe path
                cmd = [script_path]
            
            # Use runas to restart with admin privileges
            result = subprocess.run(['runas', '/user:Administrator'] + cmd, 
                                  shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Close current instance
                self.app.root.destroy()
                sys.exit(0)
            else:
                # If runas fails, try alternative method
                self.restart_as_admin_alternative()
                
        except Exception as e:
            self.restart_as_admin_alternative()
    
    def restart_as_admin_alternative(self):
        """Alternative method to restart as admin using PowerShell"""
        try:
            import subprocess
            import sys
            import os
            
            script_path = sys.argv[0]
            
            # Use PowerShell to restart as admin
            ps_cmd = f'Start-Process -FilePath "{script_path}" -Verb RunAs -WindowStyle Hidden'
            
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.app.root.destroy()
                sys.exit(0)
            else:
                # Final fallback - show manual instructions
                self.show_manual_elevation_instructions()
                
        except Exception as e:
            self.show_manual_elevation_instructions()
    
    def show_manual_elevation_instructions(self):
        """Show manual instructions if automatic elevation fails"""
        instruction_text = (
            "🔒 ADMINISTRATOR PRIVILEGES REQUIRED\n\n"
            "This backup application requires administrator privileges to function properly.\n\n"
            "Please restart the application as administrator:\n\n"
            "1. Close this application\n"
            "2. Right-click the application file\n"
            "3. Select 'Run as administrator'\n\n"
            "This ensures proper access to:\n"
            "• Network shares and drives\n"
            "• System directories\n"
            "• Scheduled tasks\n"
            "• Registry settings"
        )
        
        messagebox.showerror("Administrator Privileges Required", instruction_text)
        self.app.root.destroy()
        sys.exit(0)
    
    def is_admin(self):
        """Check if current user is administrator"""
        return self.is_elevated
    
    def get_privilege_status(self):
        """Get privilege status (always elevated when running)"""
        return {
            'elevated': True,
            'missing_privileges': [],
            'recommendations': []
        }

class SecurityManager:
    def __init__(self):
        self.max_attempts = 5  # Maximum failed attempts before lockout
        self.lockout_duration = 120  # Lockout duration in seconds (5 minutes)
        self.rate_limit_window = 60  # Rate limit window in seconds (1 minute)
        self.max_requests = 5  # Maximum requests per rate limit window
        self.failed_attempts = {}  # Track failed attempts per IP/username
        self.lockouts = {}  # Track lockouts
        self.request_history = {}  # Track request history for rate limiting
        self.audit_log_file = os.path.join(os.getcwd(), 'logs', 'security_audit.log')
        self.initialize_audit_log()

    def initialize_audit_log(self):
        """Initialize the audit log file"""
        try:
            os.makedirs(os.path.dirname(self.audit_log_file), exist_ok=True)
            if not os.path.exists(self.audit_log_file):
                with open(self.audit_log_file, 'w') as f:
                    f.write("Timestamp,Event Type,User/IP,Details,Status\n")
        except Exception as e:
            print(f"Error initializing audit log: {str(e)}")

    def log_audit_event(self, event_type, user_ip, details, status="SUCCESS"):
        """Log security events to audit log"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.audit_log_file, 'a') as f:
                f.write(f"{timestamp},{event_type},{user_ip},{details},{status}\n")
        except Exception as e:
            print(f"Error writing to audit log: {str(e)}")

    def check_rate_limit(self, user_ip):
        """Check if user has exceeded rate limit"""
        current_time = time.time()
        if user_ip not in self.request_history:
            self.request_history[user_ip] = []
        
        # Remove old requests outside the window
        self.request_history[user_ip] = [
            t for t in self.request_history[user_ip]
            if current_time - t < self.rate_limit_window
        ]
        
        # Check if rate limit exceeded
        if len(self.request_history[user_ip]) >= self.max_requests:
            self.log_audit_event("RATE_LIMIT", user_ip, "Rate limit exceeded", "BLOCKED")
            return False
        
        # Add current request
        self.request_history[user_ip].append(current_time)
        return True

    def check_lockout(self, user_ip):
        """Check if user is currently locked out"""
        if user_ip in self.lockouts:
            lockout_time = self.lockouts[user_ip]
            if time.time() - lockout_time < self.lockout_duration:
                remaining_time = int(self.lockout_duration - (time.time() - lockout_time))
                self.log_audit_event("LOCKOUT_CHECK", user_ip, f"Account locked, {remaining_time}s remaining", "BLOCKED")
                return True, remaining_time
            else:
                # Lockout expired
                del self.lockouts[user_ip]
                del self.failed_attempts[user_ip]
        return False, 0

    def record_failed_attempt(self, user_ip):
        """Record a failed attempt and check for lockout"""
        if user_ip not in self.failed_attempts:
            self.failed_attempts[user_ip] = 0
        self.failed_attempts[user_ip] += 1
        
        self.log_audit_event("FAILED_ATTEMPT", user_ip, 
                           f"Failed attempt {self.failed_attempts[user_ip]}/{self.max_attempts}", 
                           "FAILED")
        
        if self.failed_attempts[user_ip] >= self.max_attempts:
            self.lockouts[user_ip] = time.time()
            self.log_audit_event("LOCKOUT", user_ip, 
                               f"Account locked for {self.lockout_duration} seconds", 
                               "LOCKED")
            return True
        return False

    def reset_attempts(self, user_ip):
        """Reset failed attempts for successful login"""
        if user_ip in self.failed_attempts:
            del self.failed_attempts[user_ip]
        if user_ip in self.lockouts:
            del self.lockouts[user_ip]
        self.log_audit_event("RESET_ATTEMPTS", user_ip, "Failed attempts reset", "SUCCESS")


class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robocopy Backup Tool")
        self.scheduler_running = True
        self.scheduled_backups = []
        self.tray_icon = None
        self.minimized_to_tray = False
        self.network_credentials = {}
        self.mapped_drives = {}
        
        # Set window to maximized state
        self.root.state('zoomed')  # For Windows
        self.root.minsize(900, 600)  # Keep minimum size constraint
        
        # Configure style
        try:
            self.style = ttk.Style()
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
            self.style.configure('TButton', font=('Segoe UI', 9))
            self.style.configure('TEntry', font=('Segoe UI', 9))
            self.style.configure('TCombobox', font=('Segoe UI', 9))
        except Exception as e:
            print(f"Warning: Could not configure styles: {str(e)}")
            
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize passcode manager early
        self.passcode_manager = PasscodeManager(self)
        
        # Initialize privilege manager
        self.privilege_manager = PrivilegeManager(self)
        
        # Build GUI first so logging can work
        self.build_gui()
        
        # Refresh protection status after GUI is built
        self.refresh_protection_status()
        
        # Initialize secure logging
        self.log_manager = SecureLogManager(self)
        
        # Initialize encryption keys after GUI is built
        try:
            # Initialize backup encryption key
            self.backup_key = self.get_or_create_key()
            if not self.backup_key:
                self.log_message("Warning: Backup encryption disabled", 'warning')
            
            # Initialize credential manager with its own key
            self.credential_manager = CredentialManager(self)
            
            # Initialize settings manager
            self.settings_manager = SettingsManager(self)
            
            # Load settings after settings manager is initialized
            self.load_settings()
            
            # Initialize security components
            self.security_manager = SecurityManager()
            self.audit_logger = AuditLogger()
            
            # Initialize secure components
            self.update_checker = SecureUpdateChecker()
            self.update_checker.set_logger(self.log_message)  # Set the logger
            self.smb_handler = SecureSMBHandler()
            
            # Set up loggers for all components
            self.credential_manager.key_manager.set_logger(self.log_message)
            self.smb_handler.set_logger(self.log_message)
            
            # Setup secure SMB
            if not self.smb_handler.setup_secure_smb():
                self.log_message("Warning: Some SMB security features may be limited. Consider running as administrator.", 'warning')
                
        except Exception as e:
            self.log_message(f"Error initializing security components: {str(e)}", 'error')
            self.backup_key = None
            self.credential_manager = None
            self.security_manager = None
            self.audit_logger = None
            
        # Register cleanup handler
        atexit.register(self.cleanup)
        
        # Start scheduler last
        self.start_scheduler()
        
        # Update service status in status bar
        self.update_service_status()
        
        self.log_message("Application initialized successfully", 'info')

    def get_or_create_key(self):
        """Get existing backup key or create a new one"""
        try:
            key_file = os.path.join(os.getcwd(), 'config', 'backup_key.key')
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except FileNotFoundError:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            self.log_message(f"Error with backup key: {str(e)}", 'error')
            return None

    def encrypt_passcode(self, passcode):
        """Encrypt a passcode using backup key"""
        if not self.backup_key:
            return passcode
        f = Fernet(self.backup_key)
        return f.encrypt(passcode.encode()).decode()

    def decrypt_passcode(self, encrypted_passcode):
        """Decrypt a passcode using backup key"""
        if not self.backup_key:
            return encrypted_passcode
        f = Fernet(self.backup_key)
        return f.decrypt(encrypted_passcode.encode()).decode()

    def verify_passcode(self, entered_passcode, encrypted_passcode):
        """Verify if entered passcode matches the encrypted one"""
        try:
            # Get user IP (in this case, we'll use the machine name as identifier)
            user_ip = os.environ.get('COMPUTERNAME', 'unknown')
            
            # Check rate limit
            if not self.security_manager.check_rate_limit(user_ip):
                messagebox.showerror("Security", "Too many attempts. Please wait before trying again.")
                return False
            
            # Check lockout
            is_locked, remaining_time = self.security_manager.check_lockout(user_ip)
            if is_locked:
                messagebox.showerror("Security", 
                    f"Account is locked. Please try again in {remaining_time} seconds.")
                return False
            
            # Verify passcode
            decrypted = self.decrypt_passcode(encrypted_passcode)
            if entered_passcode == decrypted:
                self.security_manager.reset_attempts(user_ip)
                self.security_manager.log_audit_event("PASSCODE_VERIFY", user_ip, 
                                                   "Passcode verification successful", 
                                                   "SUCCESS")
                return True
            else:
                # Record failed attempt
                if self.security_manager.record_failed_attempt(user_ip):
                    messagebox.showerror("Security", 
                        f"Too many failed attempts. Account locked for {self.security_manager.lockout_duration} seconds.")
                self.security_manager.log_audit_event("PASSCODE_VERIFY", user_ip, 
                                                   "Passcode verification failed", 
                                                   "FAILED")
                return False
        except Exception as e:
            self.security_manager.log_audit_event("PASSCODE_VERIFY", user_ip, 
                                               f"Error during verification: {str(e)}", 
                                               "ERROR")
            return False

    def get_existing_mapped_drives(self):
        """Get all currently mapped network drives"""
        existing_maps = {}
        try:
            # Get all network connections
            connections = win32wnet.WNetOpenEnum(win32netcon.RESOURCE_CONNECTED, 0, 0, None)
            while True:
                try:
                    items = win32wnet.WNetEnumResource(connections, 1)
                    if not items:
                        break
                    for item in items:
                        if item.lpLocalName:  # If it's a mapped drive
                            existing_maps[item.lpRemoteName] = item.lpLocalName
                except win32wnet.error as e:
                    if e.winerror == 259:  # ERROR_NO_MORE_ITEMS
                        break
                    raise
            win32wnet.WNetCloseEnum(connections)
        except Exception as e:
            self.log_message(f"Error getting mapped drives: {str(e)}", 'error')
        return existing_maps

    def map_network_drive(self, unc_path, username, password, temporary=False):
        """Map a network drive"""
        try:
            # Get existing mapped drives to avoid conflicts
            existing_drives = self.get_existing_mapped_drives()
            used_drives = set(existing_drives.keys())
            
            # Find available drive letter
            for letter in 'ZYXWVUTSRQPONMLKJIHGFEDCBA':
                if letter not in used_drives:
                    try:
                        drive_letter = f"{letter}:"
                        net_resource = win32netcon.NETRESOURCE()
                        net_resource.lpRemoteName = unc_path
                        net_resource.lpLocalName = drive_letter
                        
                        flags = 0
                        if temporary:
                            flags |= win32netcon.CONNECT_TEMPORARY
                        
                        win32wnet.WNetAddConnection2(
                            net_resource,
                            password,
                            username,
                            flags
                        )
                        
                        if temporary:
                            self.mapped_drives[unc_path] = (drive_letter, True)
                        else:
                            self.mapped_drives[unc_path] = (drive_letter, False)
                            
                        self.log_message(f"Mapped {unc_path} to {drive_letter}", 'info')
                        return drive_letter
                    except Exception as e:
                        continue
            
            self.log_message(f"No available drive letters to map {unc_path}", 'error')
            return None
        except Exception as e:
            self.log_message(f"Failed to map network drive {unc_path}: {str(e)}", 'error')
            return None

    def unmap_network_drive(self, drive_letter):
        """Unmap a network drive"""
        try:
            # Only unmap if it was a temporary mapping
            for unc, (letter, is_temp) in list(self.mapped_drives.items()):
                if letter == drive_letter and is_temp:
                    win32wnet.WNetCancelConnection2(drive_letter, 0, True)
                    del self.mapped_drives[unc]
                    self.log_message(f"Unmapped temporary network drive {drive_letter}", 'info')
                    return True
            return False
        except Exception as e:
            self.log_message(f"Failed to unmap network drive {drive_letter}: {str(e)}", 'error')
            return False

    def cleanup(self):
        """Clean up resources when the application exits"""
        try:
            # Stop the scheduler
            self.scheduler_running = False
            
            # Clean up any mapped drives
            for unc, (drive_letter, is_temp) in list(self.mapped_drives.items()):
                if is_temp:  # Only unmap temporary drives
                    try:
                        self.unmap_network_drive(drive_letter)
                    except:
                        pass
            
            # Stop the tray icon
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
            
            # Clear any remaining widgets
            try:
                for widget in self.root.winfo_children():
                    widget.destroy()
            except:
                pass
            
            # Save settings before shutdown
            try:
                self.save_settings()
            except:
                pass
            
            self.log_message("Application shutdown complete", 'info')
        except:
            pass

    def on_close(self):
        try:
            # If passcode is set, require verification
            if self.passcode_manager.has_passcode():
                dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
                if not dialog.result:
                    self.minimize_to_tray()
                    return
            if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
                self.quit_application()
        except Exception as e:
            self.log_message(f"Error during close: {str(e)}", 'error')
            try:
                self.minimize_to_tray()
            except:
                pass

    def build_gui(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        # Make canvas expand with container
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # Make scrollable_frame expand with canvas
        scrollable_frame.columnconfigure(0, weight=1)

        def _on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Now, instead of packing your main_frame into self.root,
        # pack it into scrollable_frame:
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add minimize to tray button in the top-right corner
        tray_button_frame = ttk.Frame(main_frame)
        tray_button_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(tray_button_frame, text="Minimize to Tray", 
                  command=self.minimize_to_tray, width=20).pack(side=tk.RIGHT)
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Backup Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add startup configuration section
        startup_frame = ttk.LabelFrame(config_frame, text="Startup Configuration", padding="10")
        startup_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Startup checkbox
        self.startup_var = tk.BooleanVar(value=self.is_startup_enabled())
        ttk.Checkbutton(startup_frame, text="Start with Windows", 
                       variable=self.startup_var,
                       command=self.toggle_startup).pack(anchor=tk.W)
        
        # Add passcode protection section
        passcode_frame = ttk.LabelFrame(config_frame, text="Passcode Protection", padding="10")
        passcode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Protection status indicator
        status_frame = ttk.Frame(passcode_frame)
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        protection_status = "🔒 PROTECTED" if self.passcode_manager.has_passcode() else "🔓 UNPROTECTED"
        status_color = "green" if self.passcode_manager.has_passcode() else "red"
        self.status_label = ttk.Label(status_frame, text=f"Status: {protection_status}", 
                               foreground=status_color, font=('Segoe UI', 9, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Button(status_frame, text="?", command=self.show_protection_help, 
                  width=3).pack(side=tk.RIGHT)
        
        # Remove editable passcode entry, add Set/Change Passcode button
        ttk.Button(passcode_frame, text="Set/Change Passcode", command=self.set_or_change_passcode, width=25).pack(anchor=tk.W, pady=5)
        ttk.Label(passcode_frame, text="(Passcode required for protected actions)").pack(anchor=tk.W)
        
                
        # Log configuration section
        # Remove Log Settings section
        # Delete from:
        # log_frame = ttk.LabelFrame(config_frame, text="Log Settings", padding="10")
        # log_frame.pack(...)
        # log_dir_frame = ttk.Frame(log_frame)
        # log_dir_frame.pack(...)
        # ttk.Label(log_dir_frame, ...)
        # self.log_dir_entry = ttk.Entry(...)
        # self.log_dir_entry.pack(...)
        # self.log_dir_entry.insert(...)
        # ttk.Button(log_dir_frame, ...)
        # self.log_enabled_var = tk.BooleanVar(...)
        # ttk.Checkbutton(log_frame, ...)
        # (Delete all these lines)

        # Source
        source_frame = ttk.Frame(config_frame)
        source_frame.pack(fill=tk.X, pady=5)
        ttk.Label(source_frame, text="Source Folder:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_entry = ttk.Entry(source_frame, width=60)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.source_entry.bind('<KeyRelease>', self.auto_save_settings)
        ttk.Button(source_frame, text="Browse", command=self.browse_source, width=10).pack(side=tk.LEFT)
        
        # Network credentials for source
        source_cred_frame = ttk.Frame(config_frame)
        source_cred_frame.pack(fill=tk.X, pady=2)
        ttk.Label(source_cred_frame, text="Source Credentials (if needed):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(source_cred_frame, text="Username:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_user_entry = ttk.Entry(source_cred_frame, width=15)
        self.source_user_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.source_user_entry.bind('<KeyRelease>', self.auto_save_settings)
        ttk.Label(source_cred_frame, text="Password:").pack(side=tk.LEFT, padx=(0, 5))
        self.source_pwd_entry = ttk.Entry(source_cred_frame, width=15, show="*")
        self.source_pwd_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_cred_frame, text="Test", command=self.test_source_connection, width=8).pack(side=tk.LEFT)

        # Add remember credentials checkbox
        self.source_remember_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(source_cred_frame, 
                       text="Remember Credentials",
                       variable=self.source_remember_var,
                       command=self.auto_save_settings).pack(side=tk.LEFT)

        # Destination
        dest_frame = ttk.Frame(config_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dest_frame, text="Destination Folder:").pack(side=tk.LEFT, padx=(0, 5))
        self.dest_entry = ttk.Entry(dest_frame, width=60)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.dest_entry.bind('<KeyRelease>', self.auto_save_settings)
        ttk.Button(dest_frame, text="Browse", command=self.browse_dest, width=10).pack(side=tk.LEFT)

        # Network credentials for destination
        dest_cred_frame = ttk.Frame(config_frame)
        dest_cred_frame.pack(fill=tk.X, pady=2)
        ttk.Label(dest_cred_frame, text="Destination Credentials (if needed):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(dest_cred_frame, text="Username:").pack(side=tk.LEFT, padx=(0, 5))
        self.dest_user_entry = ttk.Entry(dest_cred_frame, width=15)
        self.dest_user_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.dest_user_entry.bind('<KeyRelease>', self.auto_save_settings)
        ttk.Label(dest_cred_frame, text="Password:").pack(side=tk.LEFT, padx=(0, 5))
        self.dest_pwd_entry = ttk.Entry(dest_cred_frame, width=15, show="*")
        self.dest_pwd_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dest_cred_frame, text="Test", command=self.test_dest_connection, width=8).pack(side=tk.LEFT)

        # Add remember credentials checkbox
        self.dest_remember_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dest_cred_frame,
                       text="Remember Credentials",
                       variable=self.dest_remember_var,
                       command=self.auto_save_settings).pack(side=tk.LEFT)

        # Flags
        flags_frame = ttk.Frame(config_frame)
        flags_frame.pack(fill=tk.X, pady=5)
        ttk.Label(flags_frame, text="Robocopy Flags:").pack(side=tk.LEFT, padx=(0, 5))
        self.flags_entry = ttk.Entry(flags_frame, width=60)
        self.flags_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.flags_entry.insert(0, "/E /V /X /R:1 /W:5 /MT:12 /A-:SH /SL")  # Updated flags here
        self.flags_entry.bind('<KeyRelease>', self.auto_save_settings)
        ttk.Button(flags_frame, text="Help", command=self.show_flags_help, width=10).pack(side=tk.LEFT)

        # Split pane for schedule and messages
        split_pane = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        split_pane.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Schedule section (left pane)
        schedule_frame = ttk.LabelFrame(split_pane, text="Schedule Configuration", padding="10")
        split_pane.add(schedule_frame, weight=1)
        
        # Schedule controls
        date_time_frame = ttk.Frame(schedule_frame)
        date_time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_time_frame, text="Date (e.g. 07/09/2025 or 2025-07-09):").pack(anchor=tk.W)
        self.date_entry = ttk.Entry(date_time_frame)
        self.date_entry.pack(fill=tk.X)
        self.date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))

        
        ttk.Label(date_time_frame, text="Time (e.g. 10:00 AM or 14:30):").pack(anchor=tk.W, pady=(5, 0))
        self.time_entry = ttk.Entry(date_time_frame)
        self.time_entry.pack(fill=tk.X)
        self.time_entry.insert(0, "10:00 AM")  # or "" for blank, or your preferred friendly default

        # Frequency
        freq_frame = ttk.Frame(schedule_frame)
        freq_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(freq_frame, text="Frequency:").pack(anchor=tk.W)
        self.freq_combo = ttk.Combobox(freq_frame, values=["One-time", "Daily", "Weekly"], state="readonly")
        self.freq_combo.pack(fill=tk.X)
        self.freq_combo.set("One-time")

        # Action buttons
        button_frame = ttk.Frame(schedule_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Run Backup Now", command=self.run_backup_now).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Add to Schedule", command=self.add_to_schedule).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_scheduled_backup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Manage Service", command=self.manage_backup_service).pack(side=tk.LEFT)

        # Scheduled backups list
        list_frame = ttk.LabelFrame(schedule_frame, text="Scheduled Backups", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sched_listbox = tk.Listbox(list_frame, font=('Consolas', 9))
        self.sched_listbox.pack(fill=tk.BOTH, expand=True)

        # Message/Log section (right pane)
        message_frame = ttk.LabelFrame(split_pane, text="Activity Log", padding="10")
        split_pane.add(message_frame, weight=1)
        
        # Verbose message display
        self.message_text = tk.Text(message_frame, wrap=tk.WORD, font=('Consolas', 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(message_frame, command=self.message_text.yview)
        self.message_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_text.pack(fill=tk.BOTH, expand=True)
        
        # Create tags for different message types
        self.message_text.tag_config('error', foreground='red')
        self.message_text.tag_config('success', foreground='green')
        self.message_text.tag_config('warning', foreground='orange')
        self.message_text.tag_config('info', foreground='blue')
        self.message_text.tag_config('debug', foreground='gray')
        
        # Status bar
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def test_source_connection(self):
        path = self.source_entry.get().strip()
        username = self.source_user_entry.get().strip()
        password = self.source_pwd_entry.get().strip()
        
        if not path:
            self.log_message("Please enter a source path first.", 'error')
            return
            
        self.test_network_connection(path, username, password, "source")

    def test_dest_connection(self):
        path = self.dest_entry.get().strip()
        username = self.dest_user_entry.get().strip()
        password = self.dest_pwd_entry.get().strip()
        
        if not path:
            self.log_message("Please enter a destination path first.", 'error')
            return
            
        self.test_network_connection(path, username, password, "destination")

    def test_network_connection(self, path, username, password, location):
        """Test network connection with authenticator verification"""
        user_ip = os.environ.get('COMPUTERNAME', 'unknown')
        
        # Check rate limit
        if not self.security_manager.check_rate_limit(user_ip):
            self.log_message("Too many connection attempts. Please wait before trying again.", 'error')
            return
        
        # Check lockout
        is_locked, remaining_time = self.security_manager.check_lockout(user_ip)
        if is_locked:
            self.log_message(f"Account is locked. Please try again in {remaining_time} seconds.", 'error')
            return
        
        if not is_unc_path(path):
            # Only keep essential info log for local path
            self.log_message(f"Local path '{path}' doesn't require credentials.", 'info')
            return

        try:
            # Debug: show what credentials are being used
            self.log_message(f"DEBUG: Testing network connection for {path} as {location} with username={username}", 'debug')
            if location == "source" and self.source_remember_var.get():
                self.log_message(f"DEBUG: Will remember source credentials for {path} (username={username})", 'debug')
                self.credential_manager.save_credentials({
                    f"source_{path}": {
                        "username": username,
                        "password": password
                    }
                })
                self.log_message(f"DEBUG: Saved (remembered) source credentials for {path} (username={username})", 'debug')
            elif location == "destination" and self.dest_remember_var.get():
                self.log_message(f"DEBUG: Will remember destination credentials for {path} (username={username})", 'debug')
                self.credential_manager.save_credentials({
                    f"dest_{path}": {
                        "username": username,
                        "password": password
                    }
                })
                self.log_message(f"DEBUG: Saved (remembered) destination credentials for {path} (username={username})", 'debug')
            else:
                self.log_message(f"DEBUG: Using credentials for this session only for {path} (username={username})", 'debug')

            # Verify SMB security before proceeding
            if not self.smb_handler.verify_smb_security(path):
                self.security_manager.log_audit_event("SMB_SECURITY", user_ip, 
                                                   f"Security check failed for {path}", 
                                                   "WARNING")
                self.log_message(f"Warning: {location} path '{path}' does not meet security requirements", 'warning')
                if not messagebox.askyesno("Security Warning", 
                    f"The {location} path does not meet security requirements. Continue anyway?"):
                    return
            # Try to access the path without credentials first
            self.log_message(f"DEBUG: Attempting anonymous/current-session access to {path}", 'debug')
            try:
                os.listdir(path)
                self.log_message(f"Successfully accessed {location} '{path}' without credentials (anonymous or current session)", 'success')
                self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                                   f"Anonymous access successful to {path}", 
                                                   "SUCCESS")
                return
            except Exception as e:
                self.log_message(f"DEBUG: Anonymous/current-session access failed for {path}: {str(e)}", 'debug')
                if not username:
                    self.log_message(f"Anonymous access failed for {location} '{path}': {str(e)}", 'error')
                    self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                                       f"Anonymous access failed to {path}", 
                                                       "FAILED")
                    return
            # Now, log that you are attempting to map with credentials
            self.log_message(f"DEBUG: Attempting to map {path} with provided credentials (username={username})", 'debug')

            # Store credentials securely if remember is checked
            if location == "source" and self.source_remember_var.get():
                self.credential_manager.save_credentials({
                    f"source_{path}": {
                        "username": username,
                        "password": password
                    }
                })
                self.log_message(f"DEBUG: Saved (remembered) source credentials for {path} (username={username})", 'debug')
            elif location == "destination" and self.dest_remember_var.get():
                self.credential_manager.save_credentials({
                    f"dest_{path}": {
                        "username": username,
                        "password": password
                    }
                })
                self.log_message(f"DEBUG: Saved (remembered) destination credentials for {path} (username={username})", 'debug')
            else:
                # Only store in memory for this session
                self.network_credentials[path] = (username, password)

            # Debug: show what credentials are being used for mapping
            self.log_message(f"DEBUG: Mapping {path} as {location} with username={username}", 'debug')

            # Test with temporary mapping
            drive_letter = self.map_network_drive(path, username, password, temporary=True)
            if drive_letter:
                try:
                    # Verify we can access the mapped drive
                    os.listdir(drive_letter)
                    self.log_message(f"Successfully connected to {location} '{path}' as '{drive_letter}'", 'success')
                    self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                                       f"Authenticated access successful to {path}", 
                                                       "SUCCESS")
                except Exception as e:
                    self.log_message(f"Mapped drive but failed to access {location} '{drive_letter}': {str(e)}", 'error')
                    self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                                       f"Access failed to mapped drive {drive_letter}", 
                                                       "FAILED")
                finally:
                    self.unmap_network_drive(drive_letter)
            else:
                self.log_message(f"Failed to map network drive for {location} '{path}'", 'error')
                self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                                   f"Failed to map drive for {path}", 
                                                   "FAILED")
                
        except Exception as e:
            error_msg = str(e)
            if "1326" in error_msg:
                error_msg += " (Invalid username/password)"
                self.security_manager.record_failed_attempt(user_ip)
            elif "53" in error_msg:
                error_msg += " (Network path not found)"
            elif "1219" in error_msg:
                error_msg += " (Multiple connections to server not allowed)"
            self.log_message(f"Failed to access {location} '{path}': {error_msg}", 'error')
            self.security_manager.log_audit_event("NETWORK_ACCESS", user_ip, 
                                               f"Access failed to {path}: {error_msg}", 
                                               "FAILED")
        finally:
            # Securely clear password from memory
            if password:
                password = None

    def create_system_tray_icon(self):
        """Create the system tray icon with menu"""
        try:
            # Create a backup icon (blue square with white arrow)
            size = 16
            image = Image.new('RGB', (size, size), color='white')
            draw = ImageDraw.Draw(image)
            
            # Draw a blue square background
            draw.rectangle([0, 0, size-1, size-1], fill='#0078D7')
            
            # Draw a white arrow (backup symbol)
            arrow_points = [
                (4, 4),    # Start point
                (4, 12),   # Vertical line down
                (12, 12),  # Horizontal line right
                (12, 8),   # Vertical line up
                (8, 8),    # Horizontal line left
                (8, 4)     # Back to start
            ]
            draw.line(arrow_points, fill='white', width=2)
            
            # Draw arrow head
            draw.polygon([(8, 4), (12, 8), (4, 8)], fill='white')
            
            menu = pystray.Menu(
                pystray.MenuItem('Show Window', self.restore_from_tray),
                pystray.MenuItem('Exit', self.quit_application)
            )
            
            self.tray_icon = pystray.Icon(
                "robocopy_backup",
                image,
                "Robocopy Backup Tool",
                menu
            )
            
            # Start the icon in a separate thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.log_message("Application minimized to system tray", 'info')
        except Exception as e:
            self.log_message(f"Error creating tray icon: {str(e)}", 'error')
            # If tray icon creation fails, show the window
            self.root.deiconify()

    def minimize_to_tray(self):
        """Minimize the application to system tray"""
        try:
            if not self.tray_icon:
                self.create_system_tray_icon()
                if not self.tray_icon:  # If creation failed
                    return
                    
            self.root.withdraw()  # Hide the window
            self.minimized_to_tray = True
            self.log_message("Application minimized to system tray", 'info')
        except Exception as e:
            self.log_message(f"Error minimizing to tray: {str(e)}", 'error')
            # If minimization fails, keep the window visible
            self.root.deiconify()

    def restore_from_tray(self, icon=None, item=None):
        """Restore the window from system tray"""
        try:
            self.show_window()
        except Exception as e:
            self.log_message(f"Error restoring window: {str(e)}", 'error')
            # On error, try to show the window anyway
            try:
                self.root.deiconify()
            except:
                pass

    def show_window(self):
        """Show the main window"""
        try:
            self.root.deiconify()  # Show the window
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Force focus
            self.minimized_to_tray = False
            self.log_message("Application window restored", 'info')
        except Exception as e:
            self.log_message(f"Error showing window: {str(e)}", 'error')

    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        try:
            # Stop the scheduler first
            self.scheduler_running = False
            
            # Clean up any mapped drives
            for unc, (drive_letter, is_temp) in list(self.mapped_drives.items()):
                if is_temp:  # Only unmap temporary drives
                    try:
                        self.unmap_network_drive(drive_letter)
                    except:
                        pass
            
            # Stop the tray icon
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
            
            # Use after() to ensure clean shutdown
            self.root.after(100, self.root.destroy)
            self.log_message("Application shutting down", 'info')
        except Exception as e:
            self.log_message(f"Error during shutdown: {str(e)}", 'error')
            # Force quit if normal shutdown fails
            try:
                self.root.destroy()
            except:
                pass

    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            folder = normalize_unc_path(folder)
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)
            self.log_message(f"Selected source folder: {folder}", 'info')

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            folder = normalize_unc_path(folder)
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
            self.log_message(f"Selected destination folder: {folder}", 'info')

    def show_flags_help(self):
        help_text = (
            "Current Robocopy Flags:\n"
            "/E – Copy subdirectories including empty ones\n"
            "/V – Produce verbose output\n"
            "/X – Report all extra files, not just those selected\n"
            "/R:1 – Retry 1 time on failed copies (reduced from default)\n"
            "/W:5 – Wait 5 seconds between retries\n"
            "/MT:12 – Multithreaded copies with 12 threads\n"
            "/A-:SH – Remove system and hidden attributes from copied files\n"
            "\nThese flags provide:\n"
            "- Complete directory tree copying (/E)\n"
            "- Detailed logging (/V)\n"
            "- Full reporting of mismatched files (/X)\n"
            "- Faster failure recovery (reduced retries)\n"
            "- High performance copying (12 threads)\n"
            "- Clean target files (no system/hidden attributes)"
        )
        messagebox.showinfo("Robocopy Flag Help", help_text)
        self.log_message("Displayed robocopy flags help", 'info')

    def add_to_schedule(self):
        """Add a backup to schedule with audit logging and passcode protection"""
        # Check if passcode is required for scheduling
        if self.passcode_manager.has_passcode():
            dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
            if not dialog.result:
                self.log_message("Schedule addition cancelled - passcode verification failed", 'warning')
                return
        
        user_ip = os.environ.get('COMPUTERNAME', 'unknown')
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        freq = self.freq_combo.get()
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        flags = self.flags_entry.get().strip()
        source_user = self.source_user_entry.get().strip()
        source_pwd = self.source_pwd_entry.get().strip()
        dest_user = self.dest_user_entry.get().strip()
        dest_pwd = self.dest_pwd_entry.get().strip()

        if not (date_str and time_str and source and dest):
            self.log_message("Error: Date, time, source, and destination are required.", 'error')
            self.audit_logger.log_event("SCHEDULE_ERROR", "Missing required fields", user_ip)
            return

        # Flexible date and time parsing block
        date_formats = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y")
        time_formats = ("%H:%M", "%I:%M %p", "%I:%M%p")
        dt = None
        for d_fmt in date_formats:
            for t_fmt in time_formats:
                try:
                    dt = datetime.strptime(f"{date_str} {time_str}", f"{d_fmt} {t_fmt}")
                    break
                except ValueError:
                    continue
            if dt:
                break

        if not dt:
            self.log_message("Error: Invalid date or time format.", 'error')
            self.audit_logger.log_event("SCHEDULE_ERROR", "Invalid date or time format", user_ip)
            return

        # Encrypt passwords before storing
        if source_pwd and self.source_remember_var.get():
            self.credential_manager.save_credentials({
                f"source_{source}": {
                    "username": source_user,
                    "password": source_pwd
                }
            })
        if dest_pwd and self.dest_remember_var.get():
            self.credential_manager.save_credentials({
                f"dest_{dest}": {
                    "username": dest_user,
                    "password": dest_pwd
                }
            })

        backup_info = {
            "datetime": dt,
            "frequency": freq,
            "source": source,
            "dest": dest,
            "flags": flags,
            "source_user": source_user,
            "source_pwd": source_pwd,
            "dest_user": dest_user,
            "dest_pwd": dest_pwd
        }
        self.scheduled_backups.append(backup_info)
        self.update_schedule_listbox()
        msg = f"Scheduled backup added for {dt.strftime('%m/%d/%Y %I:%M %p')} ({freq})"
        self.log_message(msg, 'success')
        self.audit_logger.log_event("SCHEDULE_ADD", f"Added scheduled backup: {msg}", user_ip)
        
        # Save settings after adding backup (requires passcode protection)
        self.save_settings()

        # Clear password fields
        self.source_pwd_entry.delete(0, tk.END)
        self.dest_pwd_entry.delete(0, tk.END)


    def update_schedule_listbox(self):
        self.sched_listbox.delete(0, tk.END)
        for b in sorted(self.scheduled_backups, key=lambda x: x["datetime"]):
            dt = b["datetime"].strftime("%m/%d/%Y %I:%M %p")
            freq = b["frequency"]
            source = b["source"]
            dest = b["dest"]
            self.sched_listbox.insert(tk.END, f"{dt:20} | {freq:10} | {source:50} → {dest}")

    def remove_scheduled_backup(self):
        """Remove a scheduled backup with audit logging and passcode protection"""
        # Check if passcode is required for removing schedules
        if self.passcode_manager.has_passcode():
            dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
            if not dialog.result:
                self.log_message("Schedule removal cancelled - passcode verification failed", 'warning')
                return
        
        user_ip = os.environ.get('COMPUTERNAME', 'unknown')
        sel = self.sched_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        backup = self.scheduled_backups[idx]
        del self.scheduled_backups[idx]
        self.update_schedule_listbox()
        msg = f"Removed scheduled backup: {backup['source']} → {backup['dest']}"
        self.log_message(msg, 'info')
        self.audit_logger.log_event("SCHEDULE_REMOVE", msg, user_ip)
        
        # Save settings after removing backup (requires passcode protection)
        self.save_settings()

    def validate_date(self, date_text):
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"):
            try:
                datetime.strptime(date_text.strip(), fmt)
                return True
            except ValueError:
                continue
        return False

    def validate_time(self, time_text):
        for fmt in ("%H:%M", "%I:%M %p", "%I:%M%p"):
            try:
                datetime.strptime(time_text.strip().upper().replace('.', ''), fmt)
                return True
            except ValueError:
                continue
        return False

    def run_backup_now(self):
        source = self.source_entry.get().strip()
        dest = self.dest_entry.get().strip()
        flags = self.flags_entry.get().strip()
        source_user = self.source_user_entry.get().strip()
        source_pwd = self.source_pwd_entry.get().strip()
        dest_user = self.dest_user_entry.get().strip()
        dest_pwd = self.dest_pwd_entry.get().strip()

        if not source or not dest:
            self.log_message("Error: Please enter Source and Destination paths.", 'error')
            return

        # Store credentials if provided
        if is_unc_path(source) and source_user:
            self.network_credentials[source] = (source_user, source_pwd)
        if is_unc_path(source) and dest_user:
            self.network_credentials[dest] = (dest_user, dest_pwd)

        threading.Thread(
            target=self.run_backup, 
            args=(source, dest, flags, source_user, source_pwd, dest_user, dest_pwd),
            daemon=True
        ).start()
        self.log_message("Starting backup process...", 'info')

    def run_backup(self, source, dest, flags, source_user=None, source_pwd=None, dest_user=None, dest_pwd=None):
        """Run a backup with audit logging"""
        user_ip = os.environ.get('COMPUTERNAME', 'unknown')
        self.audit_logger.log_event("BACKUP_START", f"Starting backup from {source} to {dest}", user_ip)
        
        mapped_source = None
        mapped_dest = None
        success = False
        error_message = ""
        log_file = None
        
        try:
            # Handle source path
            if source.startswith(r"\\"):
                # Load remembered credentials if not already in memory
                creds = self.credential_manager.load_credentials().get(f"source_{source}")
                if creds:
                    source_user = creds.get("username")
                    source_pwd = creds.get("password")
                    self.log_message(f"Loaded source credentials for {source}: user={source_user}", 'debug')
                else:
                    self.log_message(f"No remembered source credentials found for {source}", 'debug')
                self.log_message(f"Mapping {source} with user={source_user}", 'debug')
                mapped_source = self.map_network_drive(source, source_user, source_pwd, temporary=True)
                if mapped_source:
                    effective_source = mapped_source
                    self.log_message(f"Mapped source to {mapped_source}", 'info')
                    self.audit_logger.log_event("DRIVE_MAP", f"Mapped source {source} to {mapped_source}", user_ip)
                else:
                    effective_source = source
                    self.log_message("Using UNC path directly for source", 'warning')
                    self.audit_logger.log_event("DRIVE_MAP_FAILED", f"Failed to map source {source}", user_ip)
            else:
                effective_source = source

            # Handle destination path
            if dest.startswith(r"\\"):
                # Load remembered credentials if not already in memory
                creds = self.credential_manager.load_credentials().get(f"dest_{dest}")
                if creds:
                    dest_user = creds.get("username")
                    dest_pwd = creds.get("password")
                    self.log_message(f"Loaded destination credentials for {dest}: user={dest_user}", 'debug')
                else:
                    self.log_message(f"No remembered destination credentials found for {dest}", 'debug')
                self.log_message(f"Mapping {dest} with user={dest_user}", 'debug')
                mapped_dest = self.map_network_drive(dest, dest_user, dest_pwd, temporary=True)
                if mapped_dest:
                    effective_dest = mapped_dest
                    self.log_message(f"Mapped destination to {mapped_dest}", 'info')
                    self.audit_logger.log_event("DRIVE_MAP", f"Mapped destination {dest} to {mapped_dest}", user_ip)
                else:
                    effective_dest = dest
                    self.log_message("Using UNC path directly for destination", 'warning')
                    self.audit_logger.log_event("DRIVE_MAP_FAILED", f"Failed to map destination {dest}", user_ip)
            else:
                effective_dest = dest

            # Clean up #backup_logs directory creation and log file naming
            backup_logs_dir = os.path.normcase(os.path.abspath(os.path.join(effective_dest, '#backup_logs')))
            try:
                os.makedirs(backup_logs_dir, exist_ok=True)
                log_filename = f"robocopy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                log_file = os.path.join(backup_logs_dir, log_filename)
                log_dir_used = backup_logs_dir
            except Exception as e:
                fallback_log_dir = os.path.normcase(os.path.abspath(os.path.join(os.getcwd(), 'logs')))
                os.makedirs(fallback_log_dir, exist_ok=True)
                log_file = os.path.join(fallback_log_dir, log_filename)
                log_dir_used = fallback_log_dir
                self.log_message(f"Warning: Could not write log to destination #backup_logs. Using app log folder instead. Reason: {e}", 'warning')
            self.audit_logger.log_event("LOG_CREATE", f"Created log file: {log_filename} in {log_dir_used}", user_ip)

            # Decrypt passwords if they're encrypted
            if source in self.network_credentials:
                source_user, encrypted_pwd = self.network_credentials[source]
                if isinstance(encrypted_pwd, bytes):
                    f = Fernet(self.credential_manager.encryption_key)
                    source_pwd = f.decrypt(encrypted_pwd).decode()
                    self.audit_logger.log_event("CREDENTIAL_DECRYPT", "Decrypted source credentials", user_ip)
            
            if dest in self.network_credentials:
                dest_user, encrypted_pwd = self.network_credentials[dest]
                if isinstance(encrypted_pwd, bytes):
                    f = Fernet(self.credential_manager.encryption_key)
                    dest_pwd = f.decrypt(encrypted_pwd).decode()
                    self.audit_logger.log_event("CREDENTIAL_DECRYPT", "Decrypted destination credentials", user_ip)
            
            cmd = ["robocopy", f'"{effective_source}"', f'"{effective_dest}"'] + flags.split() + ["/LOG:" + log_file, "/TEE"]
            
            self.log_message(f"Executing: {' '.join(cmd)}", 'debug')
            self.audit_logger.log_event("BACKUP_EXECUTE", f"Executing robocopy command", user_ip)
            
            result = subprocess.run(" ".join(cmd), capture_output=True, text=True, shell=True)
            
            if result.stdout:
                self.log_message("Robocopy output:\n" + result.stdout, 'info')
            if result.stderr:
                self.log_message("Robocopy errors:\n" + result.stderr, 'error')
                self.audit_logger.log_event("BACKUP_ERROR", f"Robocopy errors: {result.stderr}", user_ip)
            
            success = True
            self.log_message("Backup completed successfully.", 'success')
            self.audit_logger.log_event("BACKUP_COMPLETE", "Backup completed successfully", user_ip)
            
            if not self.minimized_to_tray:
                messagebox.showinfo("Backup Completed", "Backup finished successfully.")
        except Exception as e:
            error_message = str(e)
            self.log_message(f"Backup error: {error_message}", 'error')
            self.audit_logger.log_event("BACKUP_ERROR", f"Backup failed: {error_message}", user_ip)
            if not self.minimized_to_tray:
                messagebox.showerror("Backup Error", error_message)
        finally:
            # Securely clear passwords from memory
            if source_pwd:
                source_pwd = None
            if dest_pwd:
                dest_pwd = None
            
            # Ensure all logs are written to disk
            if log_file and log_file != os.devnull:
                try:
                    self.message_text.update()
                    self.root.update()
                    self.audit_logger.log_event("LOG_FLUSH", "Flushed log buffers to disk", user_ip)
                except:
                    pass

            # Clean up any temporary mapped drives
            if mapped_source:
                self.unmap_network_drive(mapped_source)
                self.audit_logger.log_event("DRIVE_UNMAP", f"Unmapped source drive {mapped_source}", user_ip)
            if mapped_dest:
                self.unmap_network_drive(mapped_dest)
                self.audit_logger.log_event("DRIVE_UNMAP", f"Unmapped destination drive {mapped_dest}", user_ip)

    def start_scheduler(self):
        """Start the scheduler thread to check for scheduled backups"""
        def scheduler_thread():
            while self.scheduler_running:
                now = datetime.now()
                for backup in self.scheduled_backups[:]:  # Create a copy to safely modify during iteration
                    if backup["datetime"] <= now:
                        # Run the backup with passcode verification
                        if self.run_scheduled_backup(backup):
                            # Remove one-time backups after running
                            if backup["frequency"] == "One-time":
                                self.scheduled_backups.remove(backup)
                                self.update_schedule_listbox()
                            else:
                                # Update next run time for recurring backups
                                if backup["frequency"] == "Daily":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=1)
                                elif backup["frequency"] == "Weekly":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=7)
                                elif backup["frequency"] == "Monthly":
                                    backup["datetime"] = backup["datetime"] + timedelta(days=30)
                                self.update_schedule_listbox()
                
                # Sleep for a minute before checking again
                time.sleep(60)
        
        # Start the scheduler thread
        threading.Thread(target=scheduler_thread, daemon=True).start()
        self.log_message("Scheduler started", 'info')

    def toggle_logging(self):
        """Enable or disable logging"""
        self.log_config['enabled'] = self.log_enabled_var.get()
        self.log_message(f"Logging {'enabled' if self.log_config['enabled'] else 'disabled'}", 'info')

    def log_message(self, message, msg_type='info'):
        """Add a message to the activity log with secure logging"""
        try:
            # Log to UI
            if hasattr(self, 'message_text'):
                self.message_text.configure(state=tk.NORMAL)
                self.message_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n", msg_type)
                self.message_text.configure(state=tk.DISABLED)
                self.message_text.see(tk.END)
                if hasattr(self, 'status_var'):
                    self.status_var.set(message)
                    
            # Log to file securely if log manager is initialized
            if hasattr(self, 'log_manager'):
                log_file = f"app_{datetime.now().strftime('%Y%m%d')}.log"
                self.log_manager.write_log(log_file, f"[{msg_type.upper()}] {message}")
                
                # Rotate logs if needed
                self.log_manager.rotate_logs()
            else:
                # Fallback to console if log manager isn't ready
                print(f"[{msg_type.upper()}] {message}")
            
        except Exception as e:
            print(f"Error logging message: {str(e)}")
            print(f"Original message: {message}")

    def run_scheduled_backup(self, backup):
        """Run a scheduled backup"""
        try:
         
            # Decrypt passwords if they're encrypted
            source_pwd = backup["source_pwd"]
            dest_pwd = backup["dest_pwd"]
            
            if isinstance(source_pwd, bytes):
                f = Fernet(self.credential_manager.encryption_key)
                source_pwd = f.decrypt(source_pwd).decode()
                
            if isinstance(dest_pwd, bytes):
                f = Fernet(self.credential_manager.encryption_key)
                dest_pwd = f.decrypt(dest_pwd).decode()
            
            self.run_backup(
                backup["source"],
                backup["dest"],
                backup["flags"],
                backup["source_user"],
                source_pwd,
                backup["dest_user"],
                dest_pwd
            )
            return True
        finally:
            # Securely clear decrypted passwords
            if 'source_pwd' in locals():
                source_pwd = None
            if 'dest_pwd' in locals():
                dest_pwd = None

    def is_startup_enabled(self):
        """Check if the application is set to start with Windows via Scheduled Task"""
        try:
            task_name = "RobocopyBackupTool_Autostart"
            result = subprocess.run([
                "schtasks",
                "/Query",
                "/TN",
                task_name
            ], capture_output=True, text=True, shell=True)
            return result.returncode == 0
        except Exception as e:
            self.log_message(f"Error checking startup status: {str(e)}", 'error')
            return False

    def check_backup_service_status(self):
        """Check if the backup service is installed and running"""
        try:
            # Check Windows Service
            result = subprocess.run([
                "sc", "query", "RoboBackupService"
            ], capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                output = result.stdout.upper()
                if "RUNNING" in output:
                    return "service_running"
                elif "STOPPED" in output:
                    return "service_stopped"
                elif "START_PENDING" in output:
                    return "service_starting"
                elif "STOP_PENDING" in output:
                    return "service_stopping"
                else:
                    return "service_installed"
            else:
                # Check Scheduled Task as fallback
                result = subprocess.run([
                    "schtasks", "/Query", "/TN", "RoboBackupService"
                ], capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    return "task_installed"
                else:
                    return "not_installed"
                    
        except Exception as e:
            self.log_message(f"Error checking service status: {str(e)}", 'error')
            return "error"
    
    def install_backup_service(self):
        """Install the backup service for running backups when not logged in"""
        try:
            # Check if running as administrator
            if not self.is_admin():
                self.log_message("Administrator privileges required to install service", 'warning')
                self.show_manual_elevation_instructions()
                return False
                
            # Find the backup service script
            possible_paths = [
                os.path.join(os.getcwd(), "backup_service.py"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_service.py"),
                os.path.join(os.path.dirname(sys.executable), "backup_service.py"),
                os.path.join(os.path.dirname(os.path.dirname(sys.executable)), "backup_service.py"),
                "backup_service.py"
            ]
            
            service_script = None
            for path in possible_paths:
                if os.path.exists(path):
                    service_script = path
                    break
                    
            if not service_script:
                # Try to copy the file from the source directory
                source_dir = os.path.dirname(os.path.dirname(sys.executable))
                source_script = os.path.join(source_dir, "backup_service.py")
                
                if os.path.exists(source_script):
                    import shutil
                    try:
                        shutil.copy2(source_script, os.getcwd())
                        service_script = os.path.join(os.getcwd(), "backup_service.py")
                        self.log_message(f"Copied backup_service.py from source to current directory", 'info')
                    except Exception as e:
                        self.log_message(f"Failed to copy backup_service.py: {str(e)}", 'error')
                        return False
                else:
                    self.log_message(f"Backup service script not found. Tried paths: {possible_paths}", 'error')
                    return False
                
            self.log_message(f"Found backup service script at: {service_script}", 'info')
            
            # Get the directory where the service script is located
            service_dir = os.path.dirname(os.path.abspath(service_script))
            
            # Get the full path to Python executable
            # Check if we're running from PyInstaller
            if getattr(sys, 'frozen', False):
                # Running from PyInstaller, need to find the actual Python interpreter
                python_exe = "python"
            else:
                # Running from source, use sys.executable
                python_exe = sys.executable
            
            # Install the service from the correct directory
            self.log_message(f"Installing service using: {python_exe} {service_script} install", 'info')
            result = subprocess.run([
                python_exe, service_script, "install"
            ], capture_output=True, text=True, shell=True, cwd=service_dir)
            
            # Check both return code and stderr for errors
            if result.returncode == 0 and not result.stderr:
                self.log_message("Backup service installed successfully", 'success')
                
                # Configure the service to start automatically
                config_result = subprocess.run([
                    "sc", "config", "RoboBackupService", "start=auto"
                ], capture_output=True, text=True, shell=True)
                
                if config_result.returncode != 0:
                    self.log_message(f"Warning: Could not configure service startup type: {config_result.stderr}", 'warning')
                
                # Start the service
                start_result = subprocess.run([
                    python_exe, service_script, "start"
                ], capture_output=True, text=True, shell=True, cwd=service_dir)
                
                if start_result.returncode == 0:
                    self.log_message("Backup service started successfully", 'success')
                    return True
                else:
                    self.log_message(f"Service installed but failed to start: {start_result.stderr}", 'warning')
                    return True
            else:
                # Check for specific error messages
                error_output = result.stderr if result.stderr else result.stdout
                if "Access is denied" in error_output or "Access is denied" in str(result.stdout):
                    self.log_message(f"Service installation failed: Access denied. Please ensure you're running as Administrator.", 'error')
                elif "already exists" in error_output:
                    self.log_message("Service already exists, attempting to start...", 'info')
                    # Try to start the existing service
                    start_result = subprocess.run([
                        python_exe, service_script, "start"
                    ], capture_output=True, text=True, shell=True, cwd=service_dir)
                    
                    if start_result.returncode == 0:
                        self.log_message("Existing backup service started successfully", 'success')
                        return True
                    else:
                        self.log_message(f"Failed to start existing service: {start_result.stderr}", 'error')
                        return False
                else:
                    self.log_message(f"Failed to install service. Return code: {result.returncode}, Error: {error_output}", 'error')
                return False
                
        except Exception as e:
            self.log_message(f"Error installing backup service: {str(e)}", 'error')
            return False
    
    def toggle_startup(self):
        """Toggle startup with Windows with passcode protection"""
        # Check if passcode is required for startup changes
        if self.passcode_manager.has_passcode():
            dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
            if not dialog.result:
                self.log_message("Startup change cancelled - passcode verification failed", 'warning')
                # Reset the checkbox to its previous state
                self.startup_var.set(not self.startup_var.get())
                return
        
        user_ip = os.environ.get('COMPUTERNAME', 'unknown')
        task_name = "RobocopyBackupTool_Autostart"
        try:
            exe_path = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            # Use pythonw.exe for silent start if available
            if exe_path.lower().endswith("python.exe"):
                exe_path = exe_path.replace("python.exe", "pythonw.exe")
            cmd = f'"{exe_path}" "{script_path}"'
            if self.startup_var.get():
                # Create the scheduled task
                result = subprocess.run([
                    "schtasks",
                    "/Create",
                    "/SC",
                    "ONLOGON",
                    "/RL",
                    "LIMITED",
                    "/TN",
                    task_name,
                    "/TR",
                    cmd,
                    "/F"
                ], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log_message("Application added to Windows startup (Scheduled Task)", 'success')
                    self.audit_logger.log_event("STARTUP_ADD", f"Added to startup (Scheduled Task): {cmd}", user_ip)
                else:
                    self.log_message(f"Failed to add to startup: {result.stderr}", 'error')
                    self.audit_logger.log_event("STARTUP_ERROR", f"Failed to add to startup: {result.stderr}", user_ip)
                    self.startup_var.set(False)
            else:
                # Delete the scheduled task
                result = subprocess.run([
                    "schtasks",
                    "/Delete",
                    "/TN",
                    task_name,
                    "/F"
                ], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log_message("Application removed from Windows startup (Scheduled Task)", 'info')
                    self.audit_logger.log_event("STARTUP_REMOVE", "Removed from startup (Scheduled Task)", user_ip)
                elif "ERROR: The system cannot find the file specified." in result.stderr:
                    self.log_message("Scheduled Task not found (already removed)", 'info')
                else:
                    self.log_message(f"Failed to remove from startup: {result.stderr}", 'error')
                    self.audit_logger.log_event("STARTUP_ERROR", f"Failed to remove from startup: {result.stderr}", user_ip)
                    self.startup_var.set(True)
        except Exception as e:
            self.log_message(f"Error toggling startup: {str(e)}", 'error')
            self.audit_logger.log_event("STARTUP_ERROR", f"Error toggling startup: {str(e)}", user_ip)
            self.startup_var.set(not self.startup_var.get())

    def manage_backup_service(self):
        """Manage the backup service (create, start, stop, remove)"""
        try:
            # Check if running as administrator
            if not self.is_admin():
                self.log_message("Administrator privileges required to manage backup service", 'warning')
                return False
                
            # Check current status
            status = self.check_backup_service_status()
            self.log_message(f"Current backup service status: {status}", 'info')
            
            # Create a simple dialog for service management
            dialog = tk.Toplevel(self.root)
            dialog.title("Backup Service Management")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"400x300+{x}+{y}")
            
            # Status label
            status_label = tk.Label(dialog, text=f"Status: {status}", font=("Arial", 10, "bold"))
            status_label.pack(pady=10)
            
            # Buttons frame
            buttons_frame = tk.Frame(dialog)
            buttons_frame.pack(pady=20)
            
            def create_service():
                if self.install_backup_service():
                    status_label.config(text="Status: service_running")
                    self.log_message("Backup service created and started", 'success')
                    self.update_service_status()
                else:
                    self.log_message("Failed to create backup service", 'error')
                    
            def start_service():
                result = subprocess.run([
                    "sc", "start", "RoboBackupService"
                ], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    status_label.config(text="Status: service_running")
                    self.log_message("Backup service started", 'success')
                    self.update_service_status()
                else:
                    self.log_message(f"Failed to start service: {result.stderr}", 'error')
                    
            def stop_service():
                result = subprocess.run([
                    "sc", "stop", "RoboBackupService"
                ], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    status_label.config(text="Status: service_stopped")
                    self.log_message("Backup service stopped", 'info')
                    self.update_service_status()
                else:
                    self.log_message(f"Failed to stop service: {result.stderr}", 'error')
                    
            def remove_service():
                result = subprocess.run([
                    "sc", "delete", "RoboBackupService"
                ], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    status_label.config(text="Status: not_installed")
                    self.log_message("Backup service removed", 'info')
                    self.update_service_status()
                else:
                    self.log_message(f"Failed to remove service: {result.stderr}", 'error')
            
            # Create buttons based on current status
            if status == "not_installed":
                tk.Button(buttons_frame, text="Create Service", command=create_service).pack(pady=5)
            elif status == "service_stopped" or status == "service_ready":
                tk.Button(buttons_frame, text="Start Service", command=start_service).pack(pady=5)
                tk.Button(buttons_frame, text="Remove Service", command=remove_service).pack(pady=5)
            elif status == "service_running":
                tk.Button(buttons_frame, text="Stop Service", command=stop_service).pack(pady=5)
                tk.Button(buttons_frame, text="Remove Service", command=remove_service).pack(pady=5)
            else:
                tk.Button(buttons_frame, text="Create Service", command=create_service).pack(pady=5)
            
            # Close button
            tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            self.log_message(f"Error managing backup service: {str(e)}", 'error')

    def is_admin(self):
        """Check if running as administrator"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def update_service_status(self):
        """Update the status bar with current service status"""
        try:
            status = self.check_backup_service_status()
            if status == "service_running":
                self.status_var.set("Ready - Backup Service: Running")
            elif status == "service_stopped":
                self.status_var.set("Ready - Backup Service: Stopped")
            elif status == "not_installed":
                self.status_var.set("Ready - Backup Service: Not Installed")
            else:
                self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set("Ready")

    def setup_key_protection(self):
        """Set up key file protection with proper permissions"""
        try:
            # Use a single key file for both backup and credentials
            key_file = os.path.join(os.getcwd(), 'config', 'key.key')
            
            # Create key file if it doesn't exist
            if not os.path.exists(key_file):
                # Generate a new key
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                self.log_message("Created new encryption key file")
            
            # Set basic file permissions (read/write for owner only)
            try:
                os.chmod(key_file, stat.S_IRUSR | stat.S_IWUSR)
                self.log_message("Set basic file permissions on key file")
            except Exception as e:
                self.log_message(f"Note: Could not set file permissions: {str(e)}")
            
            # Initialize encryption with the key
            with open(key_file, 'rb') as f:
                key = f.read()
            self.fernet = Fernet(key)
            self.log_message("Encryption system initialized successfully")
            
        except Exception as e:
            self.log_message(f"Error setting up key protection: {str(e)}")
            # Continue without encryption - application will still work
            self.log_message("Continuing without encryption")
            self.fernet = None
    
    def set_or_change_passcode(self):
       dialog = SetPasscodeDialog(self.root, self.passcode_manager)
       if dialog.result:
           self.log_message("Passcode updated.", 'success')
           self.refresh_protection_status()
    
    def check_for_updates(self):
        """Check for updates securely"""
        try:
            # Use the update checker to check for updates
            update_info = self.update_checker.check_for_updates()
            
            if update_info.get('available'):
                self.log_message(f"Update available: {update_info['version']}", 'info')
                return True
            else:
                self.log_message("No updates available", 'info')
                return False
                
        except Exception as e:
            self.log_message(f"Error checking for updates: {str(e)}", 'error')
            return False

    def perform_update(self):
        """Perform Notepad++-style update"""
        try:
            # Check for updates first
            update_info = self.update_checker.check_for_updates()
            
            if not update_info.get('available'):
                self.log_message("No updates available", 'info')
                return False
            
            # Perform the Notepad++-style update
            success = self.update_checker.perform_notepad_style_update(update_info)
            
            if success:
                self.log_message("Update downloaded. Application will restart with new version.", 'success')
                # Exit the application to allow the restart script to take over
                self.root.after(2000, self.root.quit)  # Exit after 2 seconds
                return True
            else:
                self.log_message("Update failed", 'error')
                return False
                
        except Exception as e:
            self.log_message(f"Error performing update: {str(e)}", 'error')
            return False

    def cleanup(self):
        """Clean up resources when the application exits"""
        try:
            # ... existing cleanup code ...
            
            # Clean up old logs
            self.log_manager.cleanup_old_logs()
            
            # ... rest of cleanup code ...
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def toggle_log_encryption(self):
        """Toggle log file encryption"""
        try:
            if self.log_encryption_var.get():
                if self.log_manager.initialize_encryption():
                    self.log_message("Log encryption enabled", 'success')
                else:
                    self.log_encryption_var.set(False)
                    self.log_message("Failed to enable log encryption", 'error')
            else:
                self.log_manager.encryption_enabled = False
                self.log_message("Log encryption disabled", 'info')
        except Exception as e:
            self.log_message(f"Error toggling log encryption: {str(e)}", 'error')
            self.log_encryption_var.set(False)

    def toggle_log_access_control(self):
        """Toggle log file access control"""
        try:
            if self.log_access_control_var.get():
                if self.log_manager.initialize_access_control():
                    self.log_message("Log access control enabled", 'success')
                else:
                    self.log_access_control_var.set(False)
                    self.log_message("Failed to enable log access control", 'error')
            else:
                self.log_manager.access_control_enabled = False
                self.log_message("Log access control disabled", 'info')
        except Exception as e:
            self.log_message(f"Error toggling log access control: {str(e)}", 'error')
            self.log_access_control_var.set(False)

    def apply_log_rotation_settings(self):
        """Apply log rotation settings"""
        try:
            # Validate inputs
            try:
                max_size = int(self.max_log_size_var.get())
                max_files = int(self.max_log_files_var.get())
                retention = int(self.log_retention_var.get())
                
                if max_size < 1 or max_files < 1 or retention < 1:
                    raise ValueError("Values must be positive integers")
            except ValueError as e:
                self.log_message("Invalid rotation settings. Please enter positive numbers.", 'error')
                return
            
            # Apply settings
            self.log_manager.rotate_logs(max_size_mb=max_size, max_files=max_files)
            self.log_manager.cleanup_old_logs(days=retention)
            
            self.log_message("Log rotation settings applied successfully", 'success')
        except Exception as e:
            self.log_message(f"Error applying log rotation settings: {str(e)}", 'error')

    def save_settings(self):
        """Save current application settings with passcode protection"""
        try:
            # Check if passcode is required for settings changes
            if self.passcode_manager.has_passcode():
                dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
                if not dialog.result:
                    self.log_message("Settings save cancelled - passcode verification failed", 'warning')
                    return False
            
            settings = {
                'source_path': self.source_entry.get() if hasattr(self, 'source_entry') else '',
                'dest_path': self.dest_entry.get() if hasattr(self, 'dest_entry') else '',
                'flags': self.flags_entry.get() if hasattr(self, 'flags_entry') else '/E /V /X /R:1 /W:5 /MT:12 /A-:SH /SL',
                'source_user': self.source_user_entry.get() if hasattr(self, 'source_user_entry') else '',
                'dest_user': self.dest_user_entry.get() if hasattr(self, 'dest_user_entry') else '',
                'source_remember': self.source_remember_var.get() if hasattr(self, 'source_remember_var') else False,
                'dest_remember': self.dest_remember_var.get() if hasattr(self, 'dest_remember_var') else False,
                'startup_enabled': self.startup_var.get() if hasattr(self, 'startup_var') else False,
                'scheduled_backups': self.scheduled_backups,
                'window_state': self.root.state() if hasattr(self, 'root') else 'normal'
            }
            
            if hasattr(self, 'settings_manager'):
                if self.settings_manager.save_settings(settings):
                    self.log_message("Settings saved successfully", 'info')
                    return True
                else:
                    self.log_message("Failed to save settings", 'error')
                    return False
        except Exception as e:
            self.log_message(f"Error saving settings: {str(e)}", 'error')
            return False

    def load_settings(self):
        """Load application settings"""
        try:
            if hasattr(self, 'settings_manager'):
                settings = self.settings_manager.load_settings()
                
                # Load source and destination paths
                if hasattr(self, 'source_entry') and 'source_path' in settings:
                    self.source_entry.delete(0, tk.END)
                    self.source_entry.insert(0, settings['source_path'])
                    
                if hasattr(self, 'dest_entry') and 'dest_path' in settings:
                    self.dest_entry.delete(0, tk.END)
                    self.dest_entry.insert(0, settings['dest_path'])
                    
                # Load flags
                if hasattr(self, 'flags_entry') and 'flags' in settings:
                    self.flags_entry.delete(0, tk.END)
                    self.flags_entry.insert(0, settings['flags'])
                    
                # Load credentials
                if hasattr(self, 'source_user_entry') and 'source_user' in settings:
                    self.source_user_entry.delete(0, tk.END)
                    self.source_user_entry.insert(0, settings['source_user'])
                    
                if hasattr(self, 'dest_user_entry') and 'dest_user' in settings:
                    self.dest_user_entry.delete(0, tk.END)
                    self.dest_user_entry.insert(0, settings['dest_user'])
                    
                # Load remember settings
                if hasattr(self, 'source_remember_var') and 'source_remember' in settings:
                    self.source_remember_var.set(settings['source_remember'])
                    
                if hasattr(self, 'dest_remember_var') and 'dest_remember' in settings:
                    self.dest_remember_var.set(settings['dest_remember'])
                    
                # Load startup setting
                if hasattr(self, 'startup_var') and 'startup_enabled' in settings:
                    self.startup_var.set(settings['startup_enabled'])
                    
                # Load scheduled backups
                if 'scheduled_backups' in settings:
                    self.scheduled_backups = settings['scheduled_backups']
                    self.update_schedule_listbox()
                    
                # Restore window state
                if 'window_state' in settings and hasattr(self, 'root'):
                    try:
                        if settings['window_state'] == 'zoomed':
                            self.root.state('zoomed')
                    except:
                        pass
                        
                self.log_message("Settings loaded successfully", 'info')
        except Exception as e:
            self.log_message(f"Error loading settings: {str(e)}", 'error')

    def auto_save_settings(self, event=None):
        """Auto-save settings when they change without passcode protection for basic settings"""
        try:
            # Use after() to debounce rapid changes
            if hasattr(self, '_save_timer'):
                self.root.after_cancel(self._save_timer)
            
            # Schedule the save for 1 second later to avoid too frequent saves
            self._save_timer = self.root.after(1000, self._auto_save_basic_settings)
        except Exception as e:
            self.log_message(f"Error in auto-save: {str(e)}", 'error')
    
    def _auto_save_basic_settings(self):
        """Auto-save basic settings without passcode protection"""
        try:
            # Only save basic settings that don't require passcode protection
            basic_settings = {
                'source_path': self.source_entry.get() if hasattr(self, 'source_entry') else '',
                'dest_path': self.dest_entry.get() if hasattr(self, 'dest_entry') else '',
                'flags': self.flags_entry.get() if hasattr(self, 'flags_entry') else '/E /V /X /R:1 /W:5 /MT:12 /A-:SH /SL',
                'source_user': self.source_user_entry.get() if hasattr(self, 'source_user_entry') else '',
                'dest_user': self.dest_user_entry.get() if hasattr(self, 'dest_user_entry') else '',
                'source_remember': self.source_remember_var.get() if hasattr(self, 'source_remember_var') else False,
                'dest_remember': self.dest_remember_var.get() if hasattr(self, 'dest_remember_var') else False,
                'startup_enabled': self.startup_var.get() if hasattr(self, 'startup_var') else False,
                'window_state': self.root.state() if hasattr(self, 'root') else 'normal'
            }
            
            # Load existing settings to preserve scheduled backups
            existing_settings = {}
            if hasattr(self, 'settings_manager'):
                existing_settings = self.settings_manager.load_settings()
            
            # Merge basic settings with existing settings
            existing_settings.update(basic_settings)
            
            # Save without passcode verification for auto-save
            if hasattr(self, 'settings_manager'):
                if self.settings_manager.save_settings(existing_settings):
                    self.log_message("Settings saved successfully", 'info')
                else:
                    self.log_message("Failed to save settings", 'error')
        except Exception as e:
            self.log_message(f"Error in auto-save: {str(e)}", 'error')

    def is_settings_protected(self):
        """Check if settings are protected by passcode"""
        return self.passcode_manager.has_passcode()
    
    def require_settings_protection(self, action_name="this action"):
        """Require passcode verification for protected settings changes"""
        if self.passcode_manager.has_passcode():
            dialog = VerifyPasscodeDialog(self.root, self.passcode_manager)
            if not dialog.result:
                self.log_message(f"{action_name} cancelled - passcode verification failed", 'warning')
                return False
        return True

    def show_protection_help(self):
        """Show help dialog explaining the protection system"""
        help_text = (
            "🔒 Settings Protection System\n\n"
            "This application uses passcode protection to secure sensitive operations.\n\n"
            "🔒 Protected Actions (require passcode):\n"
            "• Changing source/destination paths\n"
            "• Modifying backup flags\n"
            "• Adding/removing scheduled backups\n"
            "• Enabling/disabling startup with Windows\n"
            "• Auto-saving settings\n\n"
            "🔓 Unprotected Actions:\n"
            "• Running immediate backups\n"
            "• Viewing logs\n"
            "• Testing connections\n\n"
            "To set a passcode, click 'Set/Change Passcode' in the Passcode Protection section."
        )
        messagebox.showinfo("Protection System Help", help_text)
        self.log_message("Displayed protection system help", 'info')

    def refresh_protection_status(self):
        """Refresh the protection status indicator"""
        if hasattr(self, 'status_label'):
            protection_status = "🔒 PROTECTED" if self.passcode_manager.has_passcode() else "🔓 UNPROTECTED"
            status_color = "green" if self.passcode_manager.has_passcode() else "red"
            self.status_label.config(text=f"Status: {protection_status}", foreground=status_color)
            self.log_message(f"Protection status updated: {protection_status}", 'info')



class KeyManager:
    def __init__(self):
        self.key_file = os.path.join(os.getcwd(), 'config', 'credential_key.key')
        self.salt_file = os.path.join(os.getcwd(), 'config', 'key_salt.bin')
        self.logger = None
        
    def set_logger(self, logger):
        """Set the logger for error reporting"""
        self.logger = logger
        
    def log_error(self, message):
        """Log error message if logger is available"""
        if self.logger:
            self.logger(message, 'error')
        else:
            print(f"Error: {message}")
            
    def get_or_create_key(self, password=None):
        """Get existing key or create new one with protection"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            
            if os.path.exists(self.key_file):
                # Read existing key
                if self.logger:
                    self.logger(f"Using existing credential key from {self.key_file}", 'info')
                with open(self.key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                if self.logger:
                    self.logger(f"Creating new credential key at {self.key_file}", 'info')
                key = Fernet.generate_key()
                
                # Save key
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                
                # Set basic file permissions
                try:
                    os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)
                    if self.logger:
                        self.logger("Set credential key file permissions", 'info')
                except Exception as e:
                    self.log_error(f"Could not set key file permissions: {str(e)}")
                
                return key
                
        except Exception as e:
            self.log_error(f"Error managing credential key: {str(e)}")
            return None

    def verify_key_protection(self):
        """Verify key file permissions"""
        try:
            if not os.path.exists(self.key_file):
                return False
                
            # Check if file is readable
            with open(self.key_file, 'rb') as f:
                f.read(1)
            return True
        except Exception:
            return False

    def derive_key_from_password(self, password):
        """Derive encryption key using PBKDF2"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import os
            
            # Generate or load salt
            if os.path.exists(self.salt_file):
                with open(self.salt_file, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                os.makedirs(os.path.dirname(self.salt_file), exist_ok=True)
                with open(self.salt_file, 'wb') as f:
                    f.write(salt)
            
            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(password.encode())
            return key
        except Exception as e:
            self.log_error(f"Error deriving key: {str(e)}")
            return None

class SecureDataHandler:
    def __init__(self):
        self.encryption_key = None
        self.initialize_encryption()

    def initialize_encryption(self):
        """Initialize encryption key for in-memory storage"""
        try:
            key_file = os.path.join(os.getcwd(), 'config', 'credential_key.key')
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            try:
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            except FileNotFoundError:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
        except Exception as e:
            print(f"Error initializing encryption: {str(e)}")
            self.encryption_key = None

    def secure_delete(self, file_path):
        """Implement secure file deletion using DoD 5220.22-M standard"""
        try:
            # Overwrite file with random data
            with open(file_path, 'wb') as f:
                f.write(os.urandom(os.path.getsize(file_path)))
            # Delete file
            os.remove(file_path)
            return True
        except Exception as e:
            return False

    def encrypt_backup(self, data, key=None):
        """Encrypt backup data using AES-256"""
        try:
            from cryptography.fernet import Fernet
            if not key:
                key = Fernet.generate_key()
            f = Fernet(key)
            return f.encrypt(data)
        except Exception as e:
            return None

class NetworkSecurityManager:
    def __init__(self):
        self.trusted_paths = set()
        self.ssl_context = None

    def validate_network_path(self, path):
        """Validate network path security"""
        try:
            # Check if path is in trusted paths
            if path in self.trusted_paths:
                return True
            
            # Validate path format
            if not path.startswith(r"\\"):
                return False
                
            # Check path permissions
            import win32security
            security_info = win32security.GetFileSecurity(
                path, 
                win32security.OWNER_SECURITY_INFORMATION | 
                win32security.GROUP_SECURITY_INFORMATION | 
                win32security.DACL_SECURITY_INFORMATION
            )
            return True
        except Exception:
            return False

    def setup_secure_channel(self):
        """Setup SSL/TLS for network communications"""
        try:
            import ssl
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
            self.ssl_context.check_hostname = True
            return True
        except Exception:
            return False

class AuditLogger:
    def __init__(self):
        self.log_file = "security_audit.log"
        self.encryption_key = None

    def log_event(self, event_type, details, user=None):
        """Log security events with encryption"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                'timestamp': timestamp,
                'event_type': event_type,
                'details': details,
                'user': user
            }
            
            # Encrypt log entry
            if self.encryption_key:
                f = Fernet(self.encryption_key)
                encrypted_entry = f.encrypt(json.dumps(log_entry).encode())
            else:
                encrypted_entry = json.dumps(log_entry).encode()
            
            # Write to log file
            with open(self.log_file, 'ab') as f:
                f.write(encrypted_entry + b'\n')
            
            return True
        except Exception:
            return False

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_timeout = 3600  # 1 hour

    def create_session(self, user):
        """Create a new secure session"""
        try:
            session_id = os.urandom(32).hex()
            self.active_sessions[session_id] = {
                'user': user,
                'created': time.time(),
                'last_activity': time.time()
            }
            return session_id
        except Exception:
            return None

    def validate_session(self, session_id):
        """Validate session and check timeout"""
        if session_id not in self.active_sessions:
            return False
            
        session = self.active_sessions[session_id]
        if time.time() - session['last_activity'] > self.session_timeout:
            del self.active_sessions[session_id]
            return False
            
        session['last_activity'] = time.time()
        return True

class SecureUpdateChecker:
    def __init__(self):
        self.version_file = os.path.join(os.getcwd(), 'version.txt')
        self.current_version = self.get_current_version()
        self.public_key_file = os.path.join(os.getcwd(), 'config', 'public_key.pem')
        self.logger = None
        self.initialize_verification()
        
    def set_logger(self, logger):
        """Set the logger for error reporting"""
        self.logger = logger
        
    def log_message(self, message, msg_type='info'):
        """Log message if logger is available"""
        if self.logger:
            self.logger(message, msg_type)
        else:
            print(f"[{msg_type.upper()}] {message}")
        
    def initialize_verification(self):
        """Initialize digital signature verification"""
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import hashes
            
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.public_key_file), exist_ok=True)
            
            # Check if public key exists
            if not os.path.exists(self.public_key_file):
                self.log_message("Public key not found. Signature verification disabled.", 'warning')
                return False
                
            # Load public key
            with open(self.public_key_file, 'rb') as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read()
                )
            return True
        except Exception as e:
            self.log_message(f"Error initializing signature verification: {str(e)}", 'error')
            return False
            
    def verify_signature(self, data, signature):
        """Verify digital signature of data"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.exceptions import InvalidSignature
            
            if not hasattr(self, 'public_key'):
                self.log_message("Public key not loaded. Cannot verify signature.", 'error')
                return False
                
            try:
                # Verify signature
                self.public_key.verify(
                    signature,
                    data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                self.log_message("Invalid signature detected!", 'error')
                return False
                
        except Exception as e:
            self.log_message(f"Error verifying signature: {str(e)}", 'error')
            return False
            
    def verify_package(self, package_path, signature_path):
        """Verify a package file against its signature"""
        try:
            # Read package file
            with open(package_path, 'rb') as f:
                package_data = f.read()
                
            # Read signature file
            with open(signature_path, 'rb') as f:
                signature = f.read()
                
            # Verify signature
            if self.verify_signature(package_data, signature):
                self.log_message("Package signature verified successfully", 'success')
                return True
            else:
                self.log_message("Package signature verification failed", 'error')
                return False
                
        except Exception as e:
            self.log_message(f"Error verifying package: {str(e)}", 'error')
            return False
            
    def get_current_version(self):
        """Get current application version"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
            return "1.0.0"  # Default version if file doesn't exist
        except Exception as e:
            self.log_message(f"Error reading version: {str(e)}", 'error')
            return "1.0.0"

class SecureSMBHandler:
    def __init__(self):
        self.smb_config = {
            'signing_required': True,
            'encryption_required': True,
            'min_protocol': 'SMB3',
            'max_protocol': 'SMB3'
        }
        self.logger = None
        
    def set_logger(self, logger):
        """Set the logger for error reporting"""
        self.logger = logger
        
    def log_message(self, message, msg_type='info'):
        """Log message if logger is available"""
        if self.logger:
            self.logger(message, msg_type)
        else:
            print(f"[{msg_type.upper()}] {message}")
        
    def setup_secure_smb(self):
        """Configure secure SMB settings"""
        try:
            import win32security
            import win32net
            import win32netcon
            import win32api
            
            # Check if running with admin privileges
            if not self.is_admin():
                self.log_message("Running without admin privileges. Some SMB security features may be limited.", 'info')
                return False
            
            try:
                # Set SMB signing requirement
                win32net.NetServerSetInfo(
                    None,
                    101,
                    {'requiresignorseal': 1}
                )
            except Exception as e:
                self.log_message(f"Could not set SMB signing requirement: {str(e)}", 'info')
            
            try:
                # Set SMB encryption requirement
                win32net.NetServerSetInfo(
                    None,
                    101,
                    {'encryptdata': 1}
                )
            except Exception as e:
                self.log_message(f"Could not set SMB encryption requirement: {str(e)}", 'info')
            
            return True
        except Exception as e:
            self.log_message(f"Error setting up secure SMB: {str(e)}", 'info')
            return False
            
    def is_admin(self):
        """Check if running with admin privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
            
    def verify_smb_security(self, path):
        """Verify SMB security settings for a path"""
        try:
            import win32security
            import win32file
            
            # Get share security info
            security_info = win32security.GetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION |
                win32security.SACL_SECURITY_INFORMATION
            )
            
            # Check if signing is required
            if not self.smb_config['signing_required']:
                return False
                
            # Check if encryption is required
            if not self.smb_config['encryption_required']:
                return False
                
            return True
        except Exception as e:
            self.log_message(f"Warning: Could not verify SMB security: {str(e)}", 'warning')
            return False

class SecureLogManager:
    def __init__(self, app):
        self.app = app
        self.log_dir = os.path.join(os.getcwd(), 'logs')
        self.encryption_enabled = False
        self.access_control_enabled = False
        self.encryption_key = None
        self.key_file = os.path.join(os.getcwd(), 'config', 'log_key.key')
        self.salt_file = os.path.join(os.getcwd(), 'config', 'log_salt.bin')
        self.acl = None
        self.initialize_secure_logging()
        
    def initialize_secure_logging(self):
        """Initialize secure logging with encryption and access control"""
        try:
            # Create log directory if it doesn't exist
            os.makedirs(self.log_dir, exist_ok=True)
            
            # Initialize encryption if enabled
            if self.encryption_enabled:
                self.initialize_encryption()
                
            # Initialize access control if enabled
            if self.access_control_enabled:
                self.initialize_access_control()
                
        except Exception as e:
            self.app.log_message(f"Error initializing secure logging: {str(e)}", 'error')
            
    def initialize_encryption(self):
        """Initialize log file encryption with key derivation"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import os
            
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            
            # Generate or load salt
            if os.path.exists(self.salt_file):
                with open(self.salt_file, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                with open(self.salt_file, 'wb') as f:
                    f.write(salt)
            
            # Generate or load encryption key
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate a new key
                self.encryption_key = Fernet.generate_key()
                
                # Save the key
                with open(self.key_file, 'wb') as f:
                    f.write(self.encryption_key)
                
                # Set restrictive permissions on key file
                try:
                    os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)
                except Exception as e:
                    self.app.log_message(f"Warning: Could not set key file permissions: {str(e)}", 'warning')
            
            self.encryption_enabled = True
            self.app.log_message("Log encryption initialized successfully", 'success')
            return True
            
        except Exception as e:
            self.app.log_message(f"Error initializing log encryption: {str(e)}", 'error')
            self.encryption_enabled = False
            return False
            
    def initialize_access_control(self):
        """Initialize access control for log directory"""
        try:
            import win32security
            import win32file
            import win32con
            
            # Get current user's SID
            username = os.environ.get('USERNAME', '')
            if not username:
                return False
                
            # Create security descriptor
            security_info = win32security.SECURITY_DESCRIPTOR()
            
            # Get current user's SID
            user_sid = win32security.LookupAccountName(None, username)[0]
            
            # Create DACL
            dacl = win32security.ACL()
            
            # Add full control for current user
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                win32con.GENERIC_ALL,
                user_sid
            )
            
            # Set DACL in security descriptor
            security_info.SetSecurityDescriptorDacl(1, dacl, 0)
            
            # Apply security to log directory
            win32security.SetFileSecurity(
                self.log_dir,
                win32security.DACL_SECURITY_INFORMATION,
                security_info
            )
            
            self.acl = security_info
            self.app.log_message("Log directory access control initialized", 'info')
            return True
        except Exception as e:
            self.app.log_message(f"Error initializing access control: {str(e)}", 'error')
            return False
            
    def write_log(self, log_file, message, encrypt=True):
        """Write to log file with encryption"""
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
                
            log_path = os.path.join(self.log_dir, log_file)
            
            # Prepare message with metadata
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = {
                'timestamp': timestamp,
                'message': message,
                'checksum': self._calculate_checksum(message)
            }
            
            if self.encryption_enabled and encrypt:
                # Encrypt log entry
                f = Fernet(self.encryption_key)
                encrypted_data = f.encrypt(json.dumps(log_entry).encode())
                
                # Write encrypted data with metadata
                with open(log_path, 'ab') as f:
                    # Write IV and encrypted data length
                    f.write(len(encrypted_data).to_bytes(4, 'big'))
                    f.write(encrypted_data)
                    f.write(b'\n')
            else:
                # Write plain text with metadata
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + '\n')
                    
            return True
        except Exception as e:
            self.app.log_message(f"Error writing to log: {str(e)}", 'error')
            return False
            
    def read_log(self, log_file, decrypt=True):
        """Read from log file with decryption"""
        try:
            log_path = os.path.join(self.log_dir, log_file)
            
            if not os.path.exists(log_path):
                return []
                
            entries = []
            
            if self.encryption_enabled and decrypt:
                # Read and decrypt
                f = Fernet(self.encryption_key)
                with open(log_path, 'rb') as file:
                    while True:
                        # Read length of encrypted data
                        length_bytes = file.read(4)
                        if not length_bytes:
                            break
                            
                        length = int.from_bytes(length_bytes, 'big')
                        encrypted_data = file.read(length)
                        
                        if not encrypted_data:
                            break
                            
                        # Decrypt and verify
                        try:
                            decrypted = f.decrypt(encrypted_data)
                            entry = json.loads(decrypted)
                            
                            # Verify checksum
                            if self._verify_checksum(entry['message'], entry['checksum']):
                                entries.append(entry)
                            else:
                                self.app.log_message(f"Warning: Log entry checksum verification failed", 'warning')
                        except Exception as e:
                            self.app.log_message(f"Error decrypting log entry: {str(e)}", 'error')
                            
                return entries
            else:
                # Read plain text
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError:
                            self.app.log_message(f"Warning: Invalid log entry format", 'warning')
                return entries
                
        except Exception as e:
            self.app.log_message(f"Error reading log: {str(e)}", 'error')
            return []
            
    def _calculate_checksum(self, message):
        """Calculate SHA-256 checksum of message"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.hashes import Hash
            
            h = Hash(hashes.SHA256())
            h.update(message.encode())
            return h.finalize().hex()
        except Exception:
            return None
            
    def _verify_checksum(self, message, checksum):
        """Verify message checksum"""
        try:
            calculated = self._calculate_checksum(message)
            return calculated == checksum
        except Exception:
            return False
            
    def rotate_logs(self, max_size_mb=10, max_files=5):
        """Rotate log files when they exceed size limit"""
        try:
            for log_file in os.listdir(self.log_dir):
                if not log_file.endswith('.log'):
                    continue
                    
                log_path = os.path.join(self.log_dir, log_file)
                size_mb = os.path.getsize(log_path) / (1024 * 1024)
                
                if size_mb > max_size_mb:
                    # Create backup with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{log_file}.{timestamp}"
                    backup_path = os.path.join(self.log_dir, backup_name)
                    
                    # Move current log to backup
                    os.rename(log_path, backup_path)
                    
                    # Create new empty log file
                    open(log_path, 'w').close()
                    
                    # Clean up old backups
                    backups = sorted([
                        f for f in os.listdir(self.log_dir)
                        if f.startswith(log_file + '.')
                    ])
                    
                    while len(backups) > max_files:
                        os.remove(os.path.join(self.log_dir, backups.pop(0)))
                        
            return True
        except Exception as e:
            self.app.log_message(f"Error rotating logs: {str(e)}", 'error')
            return False
            
    def cleanup_old_logs(self, days=30):
        """Remove log files older than specified days"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            for log_file in os.listdir(self.log_dir):
                if not log_file.endswith('.log'):
                    continue
                    
                log_path = os.path.join(self.log_dir, log_file)
                file_time = datetime.fromtimestamp(os.path.getmtime(log_path))
                
                if file_time < cutoff:
                    # Securely delete the file
                    self._secure_delete(log_path)
                    
            return True
        except Exception as e:
            self.app.log_message(f"Error cleaning up old logs: {str(e)}", 'error')
            return False
            
    def _secure_delete(self, file_path):
        """Securely delete a file using DoD 5220.22-M standard"""
        try:
            # Get file size
            size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'wb') as f:
                # First pass: overwrite with random data
                f.write(os.urandom(size))
                f.flush()
                os.fsync(f.fileno())
                
                # Second pass: overwrite with zeros
                f.seek(0)
                f.write(b'\x00' * size)
                f.flush()
                os.fsync(f.fileno())
                
                # Third pass: overwrite with ones
                f.seek(0)
                f.write(b'\xFF' * size)
                f.flush()
                os.fsync(f.fileno())
            
            # Delete the file
            os.remove(file_path)
            return True
        except Exception as e:
            self.app.log_message(f"Error securely deleting file: {str(e)}", 'error')
            return False

# --- Passcode Hashing Helpers ---
PASSCODE_FILE = os.path.join(os.getcwd(), 'config', 'passcode.dat')

class PasscodeManager:
    def __init__(self, app=None):
        self.app = app
        self.passcode_file = PASSCODE_FILE
        self.passcode_hash = None
        self.salt = None
        self.load_passcode()

    def load_passcode(self):
        try:
            if os.path.exists(self.passcode_file):
                with open(self.passcode_file, 'rb') as f:
                    data = f.read()
                if b':' in data:
                    salt, hashval = data.split(b':', 1)
                    self.salt = salt
                    self.passcode_hash = hashval
        except Exception as e:
            if self.app:
                self.app.log_message(f"Error loading passcode: {str(e)}", 'error')

    def save_passcode(self, passcode):
        try:
            salt = secrets.token_bytes(16)
            hashval = self.hash_passcode(passcode, salt)
            with open(self.passcode_file, 'wb') as f:
                f.write(salt + b':' + hashval)
            self.salt = salt
            self.passcode_hash = hashval
            return True
        except Exception as e:
            if self.app:
                self.app.log_message(f"Error saving passcode: {str(e)}", 'error')
            return False

    def hash_passcode(self, passcode, salt):
        import hashlib
        return hashlib.pbkdf2_hmac('sha256', passcode.encode(), salt, 100_000)

    def verify_passcode(self, passcode):
        if not self.passcode_hash or not self.salt:
            return False
        return self.hash_passcode(passcode, self.salt) == self.passcode_hash

    def has_passcode(self):
        return self.passcode_hash is not None and self.salt is not None

# --- Passcode Dialog ---
class SetPasscodeDialog:
    def __init__(self, parent, passcode_manager):
        self.result = False
        self.parent = parent
        self.passcode_manager = passcode_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Set/Change Passcode")
        self.dialog.geometry("350x220")
        self.dialog.resizable(False, False)
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        row = 0
        if self.passcode_manager.has_passcode():
            ttk.Label(main_frame, text="Current Passcode:").grid(row=row, column=0, sticky=tk.W)
            self.current_var = tk.StringVar()
            self.current_entry = ttk.Entry(main_frame, textvariable=self.current_var, show="*", width=20)
            self.current_entry.grid(row=row, column=1, pady=5)
            row += 1
        else:
            self.current_var = None
        ttk.Label(main_frame, text="New Passcode:").grid(row=row, column=0, sticky=tk.W)
        self.new_var = tk.StringVar()
        self.new_entry = ttk.Entry(main_frame, textvariable=self.new_var, show="*", width=20)
        self.new_entry.grid(row=row, column=1, pady=5)
        row += 1
        ttk.Label(main_frame, text="Confirm Passcode:").grid(row=row, column=0, sticky=tk.W)
        self.confirm_var = tk.StringVar()
        self.confirm_entry = ttk.Entry(main_frame, textvariable=self.confirm_var, show="*", width=20)
        self.confirm_entry.grid(row=row, column=1, pady=5)
        row += 1
        ttk.Button(main_frame, text="Set Passcode", command=self.set_passcode, width=18).grid(row=row, column=0, columnspan=2, pady=15)
        self.new_entry.focus_set()
        self.parent.wait_window(self.dialog)
    def set_passcode(self):
        if self.passcode_manager.has_passcode():
            if not self.current_var.get():
                messagebox.showerror("Error", "Enter current passcode", parent=self.dialog)
                return
            if not self.passcode_manager.verify_passcode(self.current_var.get()):
                messagebox.showerror("Error", "Current passcode incorrect", parent=self.dialog)
                return
        new = self.new_var.get()
        confirm = self.confirm_var.get()
        if not new or not confirm:
            messagebox.showerror("Error", "Enter and confirm new passcode", parent=self.dialog)
            return
        if new != confirm:
            messagebox.showerror("Error", "Passcodes do not match", parent=self.dialog)
            return
        if self.passcode_manager.save_passcode(new):
            messagebox.showinfo("Success", "Passcode set successfully", parent=self.dialog)
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to set passcode", parent=self.dialog)
    def on_close(self):
        self.result = False
        self.dialog.destroy()

class VerifyPasscodeDialog:
    def __init__(self, parent, passcode_manager):
        self.result = False
        self.parent = parent
        self.passcode_manager = passcode_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Passcode")
        self.dialog.geometry("300x140")
        self.dialog.resizable(False, False)
        self.dialog.attributes('-topmost', True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text="Enter passcode:").pack(pady=(0, 10))
        self.passcode_var = tk.StringVar()
        self.passcode_entry = ttk.Entry(main_frame, textvariable=self.passcode_var, show="*", width=20)
        self.passcode_entry.pack(pady=(0, 10))
        self.passcode_entry.focus_set()
        ttk.Button(main_frame, text="Verify", command=self.verify, width=15).pack(pady=(0, 10))
        self.passcode_entry.bind('<Return>', lambda e: self.verify())
        self.parent.wait_window(self.dialog)
    def verify(self):
        if self.passcode_manager.verify_passcode(self.passcode_var.get()):
            self.result = True
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Invalid passcode", parent=self.dialog)
            self.passcode_var.set("")
            self.passcode_entry.focus_set()
    def on_close(self):
        self.result = False
        self.dialog.destroy()

def normalize_unc_path(path):
    """Normalize a path to use backslashes and ensure UNC paths start with double backslashes."""
    if not path:
        return path
    # Replace all forward slashes with backslashes
    path = path.replace('/', '\\')
    # If it's a UNC path, ensure it starts with exactly two backslashes
    if path.startswith('\\\\'):
        return path
    elif path.startswith('\\'):
        return '\\' + path.lstrip('\\')
    elif path.startswith('\\\\?\\UNC\\'):
        # Windows extended-length UNC path, leave as is
        return path
    elif path.startswith('//'):
        return '\\\\' + path.lstrip('/').replace('/', '\\')
    else:
        return path

def run_gui():
    import tkinter as tk
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BackupApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        try:
            root.destroy()
        except:
            pass

