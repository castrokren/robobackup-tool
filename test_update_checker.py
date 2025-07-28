#!/usr/bin/env python3
"""
Test script for the update checker
Tests that don't require network access
"""

import unittest
import sys
import os

# Try to import the update checker
try:
    from update_checker import UpdateChecker
    UPDATE_CHECKER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import update_checker: {e}")
    UPDATE_CHECKER_AVAILABLE = False


class TestUpdateChecker(unittest.TestCase):
    """Test the update checker functionality"""
    
    @unittest.skipUnless(UPDATE_CHECKER_AVAILABLE, "update_checker module not available")
    def test_version_comparison(self):
        """Test version comparison logic"""
        checker = UpdateChecker()
        
        # Test version comparisons
        self.assertEqual(checker._compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(checker._compare_versions("1.0.1", "1.0.0"), 1)
        self.assertEqual(checker._compare_versions("1.0.0", "1.0.1"), -1)
        self.assertEqual(checker._compare_versions("2.0.0", "1.9.9"), 1)
        self.assertEqual(checker._compare_versions("1.9.9", "2.0.0"), -1)
        
        # Test with 'v' prefix
        self.assertEqual(checker._compare_versions("v1.0.1", "v1.0.0"), 1)
        self.assertEqual(checker._compare_versions("v1.0.0", "v1.0.1"), -1)
    
    @unittest.skipUnless(UPDATE_CHECKER_AVAILABLE, "update_checker module not available")
    def test_initialization(self):
        """Test UpdateChecker initialization"""
        checker = UpdateChecker()
        self.assertEqual(checker.current_version, "1.0.0")
        self.assertEqual(checker.repo_owner, "castrokren")
        self.assertEqual(checker.repo_name, "robobackup-tool")
    
    @unittest.skipUnless(UPDATE_CHECKER_AVAILABLE, "update_checker module not available")
    def test_offline_check(self):
        """Test update check when offline (should handle gracefully)"""
        checker = UpdateChecker()
        result = checker.check_for_updates()
        
        # Should return a dict with 'available' key
        self.assertIsInstance(result, dict)
        self.assertIn('available', result)
        
        # If there's an error, it should be in the result
        if 'error' in result:
            self.assertIsInstance(result['error'], str)


class TestBasicImports(unittest.TestCase):
    """Test that basic imports work"""
    
    def test_standard_library_imports(self):
        """Test standard library imports"""
        import os
        import sys
        import json
        import zipfile
        import shutil
        import logging
        import requests
        # If we get here, the imports worked
        self.assertTrue(True)
    
    def test_python_version(self):
        """Test that we're running a supported Python version"""
        self.assertGreaterEqual(sys.version_info, (3, 9))


if __name__ == "__main__":
    unittest.main() 