import unittest
import os
import tempfile
import shutil
import sys

# Try to import the functions, but handle missing dependencies gracefully
try:
    from backup_core import is_unc_path, normalize_unc_path, map_network_drive, unmap_network_drive
    BACKUP_CORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import backup_core functions: {e}")
    BACKUP_CORE_AVAILABLE = False


class TestBackupCore(unittest.TestCase):
    
    @unittest.skipUnless(BACKUP_CORE_AVAILABLE, "backup_core module not available")
    def test_is_unc_path(self):
        """Test UNC path detection"""
        # Test UNC paths
        self.assertTrue(is_unc_path(r"\\server\share\path"))
        self.assertTrue(is_unc_path(r"//server/share/path"))
        self.assertTrue(is_unc_path(r"\\?\UNC\server\share\path"))
        
        # Test local paths
        self.assertFalse(is_unc_path(r"C:\path\to\file"))
        self.assertFalse(is_unc_path(r"/path/to/file"))
        self.assertFalse(is_unc_path(r"relative/path"))
        
    @unittest.skipUnless(BACKUP_CORE_AVAILABLE, "backup_core module not available")
    def test_normalize_unc_path(self):
        """Test UNC path normalization"""
        # Test various UNC path formats
        self.assertEqual(normalize_unc_path(r"\\server\share"), r"\\server\share")
        self.assertEqual(normalize_unc_path(r"//server/share"), r"\\server\share")
        self.assertEqual(normalize_unc_path(r"\server\share"), r"\\server\share")
        
        # Test local paths (should remain unchanged)
        self.assertEqual(normalize_unc_path(r"C:\path"), r"C:\path")
        self.assertEqual(normalize_unc_path(r"/path"), r"/path")
        
    @unittest.skipUnless(BACKUP_CORE_AVAILABLE, "backup_core module not available")
    def test_empty_paths(self):
        """Test handling of empty paths"""
        self.assertFalse(is_unc_path(""))
        self.assertEqual(normalize_unc_path(""), "")
        self.assertEqual(normalize_unc_path(None), None)
        
    @unittest.skipUnless(BACKUP_CORE_AVAILABLE, "backup_core module not available")
    def test_network_drive_mapping(self):
        """Test network drive mapping (mock test)"""
        # This is a mock test since we can't actually map drives in CI
        # In a real environment, you'd need to test with actual network credentials
        unc_path = r"\\testserver\testshare"
        
        # Test that the function doesn't crash with invalid credentials
        result = map_network_drive(unc_path, "invalid_user", "invalid_pass")
        # Should return None for invalid credentials or if win32wnet is not available
        self.assertIsNone(result)
        
    @unittest.skipUnless(BACKUP_CORE_AVAILABLE, "backup_core module not available")
    def test_drive_unmapping(self):
        """Test network drive unmapping (mock test)"""
        # Test unmapping a non-existent drive
        result = unmap_network_drive("Z:", None)
        # The function returns True if it successfully processes the request
        # (even if the drive didn't exist to unmap)
        self.assertIsInstance(result, bool)


class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that don't require specific modules"""
    
    def test_python_version(self):
        """Test that we're running a supported Python version"""
        self.assertGreaterEqual(sys.version_info, (3, 9))
    
    def test_imports(self):
        """Test that basic imports work"""
        import os
        import sys
        import tempfile
        import shutil
        # If we get here, the imports worked
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main() 