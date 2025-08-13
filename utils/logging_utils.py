"""
Logging utilities for RoboBackup Tool
Provides centralized logging configuration and utilities
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional


class ColorFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            record.levelname = colored_levelname
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_colors: bool = True
) -> logging.Logger:
    """
    Set up centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name (if None, uses timestamp)
        log_dir: Directory for log files
        enable_console: Whether to enable console logging
        enable_colors: Whether to use colors in console output
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # File handler
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"robobackup_{timestamp}.log"
    
    log_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        if enable_colors and sys.stdout.isatty():
            console_formatter = ColorFormatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_exception(logger: logging.Logger, message: str = "An error occurred"):
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        message: Custom message to include
    """
    logger.exception(message)


def log_system_info(logger: logging.Logger):
    """
    Log system information for debugging purposes.
    
    Args:
        logger: Logger instance
    """
    import platform
    import psutil
    
    logger.info("=== System Information ===")
    logger.info(f"OS: {platform.platform()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Architecture: {platform.architecture()}")
    logger.info(f"Processor: {platform.processor()}")
    logger.info(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    logger.info(f"Available Memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    logger.info("=========================")


class ContextLogger:
    """Context manager for logging with automatic timing"""
    
    def __init__(self, logger: logging.Logger, message: str, level: int = logging.INFO):
        self.logger = logger
        self.message = message
        self.level = level
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting: {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type is None:
            self.logger.log(self.level, f"Completed: {self.message} (took {duration.total_seconds():.2f}s)")
        else:
            self.logger.error(f"Failed: {self.message} (took {duration.total_seconds():.2f}s) - {exc_val}")
        return False  # Don't suppress exceptions
