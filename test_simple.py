#!/usr/bin/env python3
"""
Simple test to verify basic functionality
This should always pass and help diagnose CI issues
"""

import unittest
import sys
import os


class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that should always pass"""
    
    def test_python_version(self):
        """Test that we're running a supported Python version"""
        self.assertGreaterEqual(sys.version_info, (3, 9))
        print(f"Python version: {sys.version}")
    
    def test_imports(self):
        """Test that basic imports work"""
        import os
        import sys
        import tempfile
        import shutil
        print("Basic imports successful")
        self.assertTrue(True)
    
    def test_working_directory(self):
        """Test that we can access the working directory"""
        cwd = os.getcwd()
        print(f"Working directory: {cwd}")
        self.assertIsInstance(cwd, str)
        self.assertTrue(len(cwd) > 0)
    
    def test_file_access(self):
        """Test that we can read files"""
        # Try to read this file
        try:
            with open(__file__, 'r') as f:
                content = f.read()
            print(f"Successfully read {__file__}")
            self.assertTrue(len(content) > 0)
        except Exception as e:
            print(f"Error reading file: {e}")
            self.fail(f"Could not read file: {e}")


if __name__ == "__main__":
    unittest.main() 