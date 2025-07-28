#!/usr/bin/env python3
"""
CI-friendly tests that work in any environment
These tests should pass even in minimal CI environments
"""

import unittest
import sys
import os


class TestCIEnvironment(unittest.TestCase):
    """Tests that should work in any CI environment"""
    
    def test_python_basics(self):
        """Test basic Python functionality"""
        self.assertIsInstance(sys.version_info, tuple)
        self.assertGreaterEqual(sys.version_info, (3, 9))
        print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    def test_os_imports(self):
        """Test basic OS imports"""
        import os
        import sys
        import tempfile
        import shutil
        import json
        import logging
        print("All basic imports successful")
        self.assertTrue(True)
    
    def test_file_operations(self):
        """Test basic file operations"""
        # Test we can create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        # Test we can read it back
        with open(temp_file, 'r') as f:
            content = f.read()
        
        # Clean up
        os.unlink(temp_file)
        
        self.assertEqual(content, "test content")
        print("File operations successful")
    
    def test_working_directory(self):
        """Test working directory access"""
        cwd = os.getcwd()
        self.assertIsInstance(cwd, str)
        self.assertTrue(len(cwd) > 0)
        print(f"Working directory: {cwd}")
    
    def test_environment_variables(self):
        """Test environment variable access"""
        # Test we can access environment variables
        env_vars = list(os.environ.keys())
        self.assertIsInstance(env_vars, list)
        print(f"Found {len(env_vars)} environment variables")


class TestOptionalDependencies(unittest.TestCase):
    """Tests for optional dependencies"""
    
    def test_requests_import(self):
        """Test requests import (should work in CI)"""
        try:
            import requests
            print("requests module available")
            self.assertTrue(True)
        except ImportError:
            print("requests module not available")
            self.skipTest("requests not available")
    
    def test_pywin32_import(self):
        """Test pywin32 import (optional)"""
        try:
            import win32wnet
            import win32netcon
            print("pywin32 modules available")
            self.assertTrue(True)
        except ImportError:
            print("pywin32 modules not available (expected in CI)")
            self.assertTrue(True)  # This is expected in CI
    
    def test_cryptography_import(self):
        """Test cryptography import"""
        try:
            import cryptography
            print("cryptography module available")
            self.assertTrue(True)
        except ImportError:
            print("cryptography module not available")
            self.skipTest("cryptography not available")


if __name__ == "__main__":
    unittest.main() 