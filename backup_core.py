import os
import ntpath
import subprocess
import logging
import time
from datetime import datetime

# Optional: import win32wnet and win32netcon if available (for network drive mapping)
try:
    import win32wnet
    import win32netcon
    WIN32_AVAILABLE = True
except ImportError:
    win32wnet = None
    win32netcon = None
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Network drive mapping will be disabled.")


def is_unc_path(path: str) -> bool:
    """
    Return True if `path` is a UNC network path (\\server\share\...).
    Handles both slashes, normalizes, and uses ntpath.splitdrive for robust detection.
    """
    p = path.replace('/', '\\')
    drive, _ = ntpath.splitdrive(p)
    return drive.startswith('\\\\')


def normalize_unc_path(path):
    """
    Normalize a path to use backslashes and ensure UNC paths start with double backslashes.
    Only affects UNC paths, leaves local paths unchanged.
    """
    if not path:
        return path
    
    # Check if this is a UNC path before any conversion
    is_unc = path.startswith('\\\\') or path.startswith('//') or path.startswith('\\') or path.startswith('\\\\?\\UNC\\')
    
    if is_unc:
        # Convert forward slashes to backslashes for UNC paths
        path = path.replace('/', '\\')
        if path.startswith('\\\\'):
            return path
        elif path.startswith('\\'):
            return '\\\\' + path.lstrip('\\')
        elif path.startswith('\\\\?\\UNC\\'):
            return path
        else:
            return path
    else:
        # For local paths, leave unchanged
        return path


def map_network_drive(unc_path, username, password, temporary=False, logger=None):
    """
    Map a network drive and return the drive letter. Returns None if mapping fails or not on Windows.
    """
    if not WIN32_AVAILABLE:
        if logger:
            logger.warning("pywin32 not available; skipping drive mapping.")
        return None
    if not is_unc_path(unc_path):
        return None
    # Find an available drive letter
    used_drives = set()
    for drive in range(ord('A'), ord('Z')+1):
        if os.path.exists(f"{chr(drive)}:/"):
            used_drives.add(chr(drive))
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
                if logger:
                    logger.info(f"Mapped {unc_path} to {drive_letter}")
                return drive_letter
            except Exception as e:
                if logger:
                    logger.warning(f"Failed to map {unc_path} to {letter}: {e}")
                continue
    if logger:
        logger.error(f"No available drive letters to map {unc_path}")
    return None


def unmap_network_drive(drive_letter, logger=None):
    """
    Unmap a network drive by drive letter. Returns True if unmapped, False otherwise.
    """
    if not WIN32_AVAILABLE:
        if logger:
            logger.warning("pywin32 not available; skipping unmap.")
        return False
    try:
        win32wnet.WNetCancelConnection2(drive_letter, 0, True)
        if logger:
            logger.info(f"Unmapped network drive {drive_letter}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to unmap network drive {drive_letter}: {e}")
        return False


def run_backup(source, dest, flags, log_dir, source_user=None, source_pwd=None, dest_user=None, dest_pwd=None, logger=None):
    """
    Run a backup using robocopy. Logs to the specified log_dir. Credentials are used for network paths if provided.
    """
    if logger is None:
        logger = logging.getLogger("backup_core")
    logger.info(f"Starting backup from {source} to {dest}")
    mapped_source = None
    mapped_dest = None
    log_file = None
    try:
        # Handle source path
        effective_source = source
        if is_unc_path(source) and source_user:
            mapped_source = map_network_drive(source, source_user, source_pwd, temporary=True, logger=logger)
            if mapped_source:
                effective_source = mapped_source
        # Handle destination path
        effective_dest = dest
        if is_unc_path(dest) and dest_user:
            mapped_dest = map_network_drive(dest, dest_user, dest_pwd, temporary=True, logger=logger)
            if mapped_dest:
                effective_dest = mapped_dest
        # Prepare log file
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"robocopy_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        log_file = os.path.join(log_dir, log_filename)
        # Build robocopy command
        cmd = [
            "robocopy",
            f'"{effective_source}"',
            f'"{effective_dest}"',
            *flags.split(),
            f"/LOG:{log_file}",
            "/TEE"
        ]
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(" ".join(cmd), capture_output=True, text=True, shell=True)
        if result.stdout:
            logger.info("Robocopy output:\n" + result.stdout)
        if result.stderr:
            logger.error("Robocopy errors:\n" + result.stderr)
        logger.info("Backup completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return False
    finally:
        # Clean up mapped drives
        if mapped_source:
            unmap_network_drive(mapped_source, logger=logger)
        if mapped_dest:
            unmap_network_drive(mapped_dest, logger=logger)
