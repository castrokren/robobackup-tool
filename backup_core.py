import os
import subprocess
import time
from datetime import datetime
from typing import Optional, Tuple
from utils.path_utils import is_unc_path, normalize_unc_path, validate_path, ensure_directory_exists
from utils.logging_utils import get_logger, log_exception, ContextLogger

# Optional: import win32wnet and win32netcon if available (for network drive mapping)
try:
    import win32wnet
    import win32netcon
    WIN32_AVAILABLE = True
except ImportError:
    win32wnet = None
    win32netcon = None
    WIN32_AVAILABLE = False

# Module logger
logger = get_logger(__name__)


def map_network_drive(unc_path: str, username: str, password: str, temporary: bool = False) -> Optional[str]:
    """
    Map a network drive and return the drive letter. Returns None if mapping fails or not on Windows.
    
    Args:
        unc_path: UNC path to map (e.g., \\\\server\\share)
        username: Username for authentication
        password: Password for authentication
        temporary: If True, mapping will not persist after reboot
        
    Returns:
        Drive letter (e.g., 'Z:') if successful, None otherwise
    """
    if not WIN32_AVAILABLE:
        logger.warning("pywin32 not available; network drive mapping disabled")
        return None
        
    if not is_unc_path(unc_path):
        logger.warning(f"Path is not a UNC path: {unc_path}")
        return None
    
    # Validate inputs
    if not username or not password:
        logger.error("Username and password are required for network mapping")
        return None
    
    # Find an available drive letter
    used_drives = set()
    for drive in range(ord('A'), ord('Z')+1):
        if os.path.exists(f"{chr(drive)}:\\"):
            used_drives.add(chr(drive))
    
    # Try letters from Z to A (reverse order to avoid conflicts)
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
                
                logger.info(f"Successfully mapped {unc_path} to {drive_letter}")
                return drive_letter
                
            except Exception as e:
                logger.debug(f"Failed to map {unc_path} to {letter}: {e}")
                continue
    
    logger.error(f"No available drive letters to map {unc_path}")
    return None


def unmap_network_drive(drive_letter: str) -> bool:
    """
    Unmap a network drive by drive letter. Returns True if unmapped, False otherwise.
    
    Args:
        drive_letter: Drive letter to unmap (e.g., 'Z:')
        
    Returns:
        True if unmapped successfully, False otherwise
    """
    if not WIN32_AVAILABLE:
        logger.warning("pywin32 not available; cannot unmap network drive")
        return False
    
    if not drive_letter:
        logger.error("Drive letter cannot be empty")
        return False
    
    try:
        win32wnet.WNetCancelConnection2(drive_letter, 0, True)
        logger.info(f"Successfully unmapped network drive {drive_letter}")
        return True
    except Exception as e:
        log_exception(logger, f"Failed to unmap network drive {drive_letter}")
        return False


def run_backup(
    source: str, 
    dest: str, 
    flags: str, 
    log_dir: str, 
    source_user: Optional[str] = None, 
    source_pwd: Optional[str] = None, 
    dest_user: Optional[str] = None, 
    dest_pwd: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Run a backup using robocopy. Logs to the specified log_dir. 
    Credentials are used for network paths if provided.
    
    Args:
        source: Source directory path
        dest: Destination directory path  
        flags: Robocopy flags (e.g., "/MIR /FFT /R:3 /W:10")
        log_dir: Directory to store log files
        source_user: Username for source network path
        source_pwd: Password for source network path
        dest_user: Username for destination network path
        dest_pwd: Password for destination network path
        
    Returns:
        Tuple of (success: bool, log_file_path: str)
    """
    with ContextLogger(logger, f"Backup from {source} to {dest}"):
        # Validate inputs
        is_valid, error = validate_path(source, must_exist=True)
        if not is_valid:
            logger.error(f"Invalid source path: {error}")
            return False, ""
        
        is_valid, error = validate_path(dest)
        if not is_valid:
            logger.error(f"Invalid destination path: {error}")
            return False, ""
        
        # Ensure log directory exists
        success, error = ensure_directory_exists(log_dir)
        if not success:
            logger.error(f"Failed to create log directory: {error}")
            return False, ""
        
        mapped_source = None
        mapped_dest = None
        log_file = None
        
        try:
            # Handle source path
            effective_source = source
            if is_unc_path(source) and source_user and source_pwd:
                mapped_source = map_network_drive(source, source_user, source_pwd, temporary=True)
                if mapped_source:
                    effective_source = mapped_source
                    logger.info(f"Using mapped drive for source: {mapped_source}")
                else:
                    logger.warning("Failed to map source drive, using UNC path directly")
            
            # Handle destination path
            effective_dest = dest
            if is_unc_path(dest) and dest_user and dest_pwd:
                mapped_dest = map_network_drive(dest, dest_user, dest_pwd, temporary=True)
                if mapped_dest:
                    effective_dest = mapped_dest
                    logger.info(f"Using mapped drive for destination: {mapped_dest}")
                else:
                    logger.warning("Failed to map destination drive, using UNC path directly")
            
            # Prepare log file
            log_filename = f"robocopy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            log_file = os.path.join(log_dir, log_filename)
            
            # Build robocopy command properly
            cmd = [
                "robocopy",
                effective_source,
                effective_dest,
                *flags.split(),
                f"/LOG:{log_file}",
                "/TEE"
            ]
            
            logger.info(f"Executing robocopy command")
            logger.debug(f"Full command: {' '.join(cmd)}")
            
            # Run robocopy without shell=True to avoid quote issues, hide command window
            start_time = datetime.now()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=3600,  # 1 hour timeout
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            duration = datetime.now() - start_time
            
            # Robocopy exit codes (0-8 are success, >8 are errors)
            exit_code = result.returncode
            if exit_code <= 8:
                logger.info(f"Backup completed successfully (exit code: {exit_code}, duration: {duration.total_seconds():.2f}s)")
                success = True
            else:
                logger.error(f"Backup failed with exit code: {exit_code}")
                success = False
            
            # Log output
            if result.stdout:
                logger.debug("Robocopy stdout:\n" + result.stdout)
            if result.stderr:
                logger.warning("Robocopy stderr:\n" + result.stderr)
            
            return success, log_file or ""
            
        except subprocess.TimeoutExpired:
            logger.error("Backup operation timed out after 1 hour")
            return False, log_file or ""
        except Exception as e:
            log_exception(logger, "Backup operation failed")
            return False, log_file or ""
        finally:
            # Clean up mapped drives
            if mapped_source:
                unmap_network_drive(mapped_source)
            if mapped_dest:
                unmap_network_drive(mapped_dest)
