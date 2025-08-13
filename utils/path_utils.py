"""
Path utilities for RoboBackup Tool
Provides common path handling functions used across the application
"""
import os
import ntpath


def is_unc_path(path: str) -> bool:
    """
    Return True if `path` is a UNC network path (\\server\share\...).
    Handles both slashes, normalizes, and uses ntpath.splitdrive for robust detection.
    
    Args:
        path (str): The path to check
        
    Returns:
        bool: True if path is a UNC path, False otherwise
    """
    if not path:
        return False
    
    p = path.replace('/', '\\')
    drive, _ = ntpath.splitdrive(p)
    return drive.startswith('\\\\')


def normalize_unc_path(path: str) -> str:
    """
    Normalize a path to use backslashes and ensure UNC paths start with double backslashes.
    Only affects UNC paths, leaves local paths unchanged.
    
    Args:
        path (str): The path to normalize
        
    Returns:
        str: The normalized path
    """
    if not path:
        return path
    
    # Check if this is a UNC path before any conversion
    is_unc = (path.startswith('\\\\') or 
              path.startswith('//') or 
              path.startswith('\\') or 
              path.startswith('\\\\?\\UNC\\'))
    
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


def validate_path(path: str, must_exist: bool = False) -> tuple[bool, str]:
    """
    Validate a file or directory path.
    
    Args:
        path (str): The path to validate
        must_exist (bool): Whether the path must exist
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not path:
        return False, "Path cannot be empty"
    
    if not path.strip():
        return False, "Path cannot be just whitespace"
    
    # Check for invalid characters (Windows specific)
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in path:
            return False, f"Path contains invalid character: {char}"
    
    # Check path length (Windows has a 260 character limit for most APIs)
    if len(path) > 260 and not path.startswith('\\\\?\\'):
        return False, "Path is too long (>260 characters). Use UNC notation for long paths."
    
    if must_exist:
        if not os.path.exists(path):
            return False, "Path does not exist"
    
    return True, ""


def ensure_directory_exists(path: str) -> tuple[bool, str]:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path (str): The directory path
        
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True, ""
    except PermissionError:
        return False, f"Permission denied creating directory: {path}"
    except OSError as e:
        return False, f"Failed to create directory {path}: {str(e)}"


def get_safe_filename(filename: str) -> str:
    """
    Convert a string to a safe filename by removing invalid characters.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: A safe filename
    """
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name
