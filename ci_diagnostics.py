#!/usr/bin/env python3
"""
CI Diagnostics Script
Simple diagnostic script for CI environment testing
"""

import sys
import os
import platform

def main():
    print("=== CI Environment Diagnostics ===")
    
    # Python version and platform
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")
    print(f"Machine: {platform.machine()}")
    
    # Working directory
    print(f"Working directory: {os.getcwd()}")
    
    # Environment variables
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")
    
    # Test basic imports
    print("\n=== Testing Basic Imports ===")
    basic_modules = ['os', 'sys', 'tempfile', 'shutil', 'json', 'logging']
    for module in basic_modules:
        try:
            __import__(module)
            print(f"OK: {module} imported successfully")
        except ImportError as e:
            print(f"FAIL: {module} import failed: {e}")
    
    # Test optional imports
    print("\n=== Testing Optional Imports ===")
    optional_modules = ['requests', 'cryptography', 'win32wnet', 'win32netcon']
    for module in optional_modules:
        try:
            __import__(module)
            print(f"OK: {module} imported successfully")
        except ImportError as e:
            print(f"FAIL: {module} import failed: {e}")
    
    # Test file operations
    print("\n=== Testing File Operations ===")
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        with open(temp_file, 'r') as f:
            content = f.read()
        
        os.unlink(temp_file)
        print("OK: File operations successful")
    except Exception as e:
        print(f"FAIL: File operations failed: {e}")
    
    # Test directory listing
    print("\n=== Testing Directory Operations ===")
    try:
        files = os.listdir('.')
        print(f"OK: Directory listing successful, found {len(files)} items")
        for file in files[:5]:  # Show first 5 files
            print(f"  - {file}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    except Exception as e:
        print(f"FAIL: Directory listing failed: {e}")
    
    print("\n=== Diagnostics Complete ===")

if __name__ == "__main__":
    main() 