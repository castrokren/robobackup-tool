import unittest
import os
import tempfile
import shutil
from backup_core import is_unc_path, normalize_unc_path, map_network_drive, unmap_network_drive


class TestBackupCore(unittest.TestCase):
    
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
        
    def test_normalize_unc_path(self):
        """Test UNC path normalization"""
        # Test various UNC path formats
        self.assertEqual(normalize_unc_path(r"\\server\share"), r"\\server\share")
        self.assertEqual(normalize_unc_path(r"//server/share"), r"\\server\share")
        self.assertEqual(normalize_unc_path(r"\server\share"), r"\\server\share")
        
        # Test local paths (should remain unchanged)
        self.assertEqual(normalize_unc_path(r"C:\path"), r"C:\path")
        self.assertEqual(normalize_unc_path(r"/path"), r"/path")
        
    def test_empty_paths(self):
        """Test handling of empty paths"""
        self.assertFalse(is_unc_path(""))
        self.assertEqual(normalize_unc_path(""), "")
        self.assertEqual(normalize_unc_path(None), None)
        
    def test_network_drive_mapping(self):
        """Test network drive mapping (mock test)"""
        # This is a mock test since we can't actually map drives in CI
        # In a real environment, you'd need to test with actual network credentials
        unc_path = r"\\testserver\testshare"
        
        # Test that the function doesn't crash with invalid credentials
        result = map_network_drive(unc_path, "invalid_user", "invalid_pass")
        # Should return None for invalid credentials
        self.assertIsNone(result)
        
    def test_drive_unmapping(self):
        """Test network drive unmapping (mock test)"""
        # Test unmapping a non-existent drive
        result = unmap_network_drive("Z:", None)
        # Should return False for non-existent drive
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 