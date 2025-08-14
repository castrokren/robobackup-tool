#!/usr/bin/env python3
"""
RoboBackup Tool - Main Entry Point
Professional Windows Backup Solution
"""

import sys
import os
from utils.logging_utils import setup_logging, get_logger, log_exception, log_system_info


def check_for_updates(logger):
    """Check for updates on startup"""
    try:
        from update_gui import check_for_updates_gui
        result = check_for_updates_gui()
        
        if result:
            logger.info(f"Update dialog result: {result}")
            return result
        else:
            logger.info("No updates available")
            return None
            
    except Exception as e:
        log_exception(logger, f"Error checking for updates: {e}")
        return None


def validate_environment(logger):
    """Validate the runtime environment"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error(f"Python 3.8+ required, current version: {sys.version}")
            return False
        
        # Check if we're on Windows
        if sys.platform != "win32":
            logger.error("This application is designed for Windows only")
            return False
        
        # Check for critical dependencies
        critical_modules = ['tkinter', 'PIL', 'pystray']
        missing_modules = []
        
        for module in critical_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            logger.error(f"Missing critical dependencies: {', '.join(missing_modules)}")
            return False
        
        logger.info("Environment validation passed")
        return True
        
    except Exception as e:
        log_exception(logger, "Failed to validate environment")
        return False


def is_admin():
    """Check if the current process is running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def print_usage():
    """Print usage information for the GUI application"""
    print("\nRoboBackup Tool - Windows Backup Solution v1.0.0")
    print("================================================")
    print("\nUsage:")
    print("  RoboBackup.exe                    Start GUI application (default)")
    print("  RoboBackup.exe help               Show this help")
    print("\nFeatures:")
    print("  • Manual backup execution")
    print("  • Robocopy integration") 
    print("  • Network drive mapping")
    print("  • Encrypted credential storage")
    print("  • Comprehensive logging")
    print("\nNote: Service functionality will be available in v1.1.0")


def main():
    """Main application entry point"""
    # Initialize logging
    logger = setup_logging(
        log_level="INFO",
        log_dir="logs",
        enable_console=True,
        enable_colors=True
    )
    
    logger.info("=== RoboBackup Tool Starting ===")
    log_system_info(logger)
    
    try:
        # Validate environment
        if not validate_environment(logger):
            logger.critical("Environment validation failed. Exiting.")
            sys.exit(1)
        
        # Check for updates (GUI dialog will show if updates are available)
        update_result = check_for_updates(logger)
        
        # Determine run mode based on command line arguments  
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command in ["--help", "-h", "help"]:
                print_usage()
                sys.exit(0)
            else:
                logger.warning(f"Unknown command: {command}")
                print_usage()
                sys.exit(1)
        else:
            # No arguments - start GUI mode
            logger.info("Starting in GUI mode")
            try:
                import backupapp
                if hasattr(backupapp, 'run_gui'):
                    backupapp.run_gui()
                else:
                    logger.error("run_gui function not found in backupapp module")
                    sys.exit(1)
            except Exception as e:
                log_exception(logger, "Failed to start GUI")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        log_exception(logger, "Unexpected error in main application")
        sys.exit(1)
    finally:
        logger.info("=== RoboBackup Tool Shutting Down ===")


if __name__ == "__main__":
    main()