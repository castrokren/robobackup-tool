#!/usr/bin/env python3
"""
Update Checker for RoboBackup Tool
Checks for updates from GitHub releases and handles automatic updates
Notepad++-style update system for packaged executables
"""

import requests
import json
import os
import sys
import subprocess
import zipfile
import shutil
import tempfile
from pathlib import Path
import logging
import time

class UpdateChecker:
    def __init__(self, repo_owner="castrokren", repo_name="robobackup-tool"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        self.current_version = "1.0.0"  # Update this when you release new versions
        self.logger = logging.getLogger(__name__)
        
    def check_for_updates(self):
        """Check if a new version is available"""
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name']
                
                if self._compare_versions(latest_version, self.current_version) > 0:
                    return {
                        'available': True,
                        'version': latest_version,
                        'download_url': release_data['html_url'],
                        'release_notes': release_data.get('body', ''),
                        'assets': release_data.get('assets', [])
                    }
            
            return {'available': False}
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return {'available': False, 'error': str(e)}
    
    def _compare_versions(self, version1, version2):
        """Compare two version strings"""
        v1_parts = [int(x) for x in version1.lstrip('v').split('.')]
        v2_parts = [int(x) for x in version2.lstrip('v').split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1_part > v2_part:
                return 1
            elif v1_part < v2_part:
                return -1
        
        return 0
    
    def find_executable_asset(self, assets):
        """Find the executable asset in release assets"""
        for asset in assets:
            if asset['name'].endswith('.exe'):
                return asset
        return None
    
    def download_executable_update(self, assets, target_dir="updates"):
        """Download the executable update (Notepad++ style)"""
        try:
            # Find the executable asset
            exe_asset = self.find_executable_asset(assets)
            if not exe_asset:
                self.logger.error("No executable asset found in release")
                return None
            
            # Create updates directory
            os.makedirs(target_dir, exist_ok=True)
            
            # Download the executable
            download_url = exe_asset['browser_download_url']
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Save to file
            filename = exe_asset['name']
            filepath = os.path.join(target_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded update: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error downloading executable update: {e}")
            return None
    
    def create_restart_script(self, new_exe_path, current_exe_path):
        """Create a script to handle the executable replacement and restart"""
        script_content = f'''@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak >nul

echo Replacing executable...
copy "{new_exe_path}" "{current_exe_path}" /Y

echo Starting updated application...
start "" "{current_exe_path}"

echo Cleaning up...
del "{new_exe_path}"
del "%~f0"

echo Update completed!
'''
        
        # Create temporary batch file
        temp_script = os.path.join(os.path.dirname(current_exe_path), "update_restart.bat")
        with open(temp_script, 'w') as f:
            f.write(script_content)
        
        return temp_script
    
    def perform_notepad_style_update(self, update_info):
        """Perform Notepad++-style update by downloading new executable"""
        try:
            # Get current executable path
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            
            # Download new executable
            new_exe_path = self.download_executable_update(update_info['assets'])
            if not new_exe_path:
                return False
            
            # Create restart script
            restart_script = self.create_restart_script(new_exe_path, current_exe_path)
            
            # Execute restart script
            subprocess.Popen([restart_script], shell=True)
            
            # Exit current application
            self.logger.info("Update downloaded. Application will restart with new version.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing Notepad++-style update: {e}")
            return False
    
    def download_update(self, download_url, target_dir="updates"):
        """Download the latest release (legacy method)"""
        try:
            # Create updates directory
            os.makedirs(target_dir, exist_ok=True)
            
            # Download the release
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Save to file
            filename = f"robobackup-tool-{self.current_version}.zip"
            filepath = os.path.join(target_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None
    
    def install_update(self, update_file):
        """Install the downloaded update (legacy method)"""
        try:
            # Extract the update
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall("temp_update")
            
            # Backup current files
            backup_dir = f"backup_{self.current_version}"
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns('.git*', 'temp_update', backup_dir))
            
            # Copy new files
            temp_dir = "temp_update"
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(".", item)
                
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Clean up
            shutil.rmtree(temp_dir)
            os.remove(update_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing update: {e}")
            return False
    
    def create_update_script(self):
        """Create a script to handle updates"""
        script_content = '''#!/usr/bin/env python3
"""
Auto-update script for RoboBackup Tool
"""
import os
import sys
import subprocess
import time

def main():
    print("Checking for updates...")
    
    # Import the update checker
    from update_checker import UpdateChecker
    
    checker = UpdateChecker()
    update_info = checker.check_for_updates()
    
    if update_info.get('available'):
        print(f"New version available: {update_info['version']}")
        print(f"Current version: {checker.current_version}")
        
        response = input("Do you want to update? (y/n): ")
        if response.lower() == 'y':
            print("Downloading update...")
            update_file = checker.download_update(update_info['download_url'])
            
            if update_file:
                print("Installing update...")
                if checker.install_update(update_file):
                    print("Update installed successfully!")
                    print("Please restart the application.")
                else:
                    print("Error installing update.")
            else:
                print("Error downloading update.")
    else:
        print("No updates available.")

if __name__ == "__main__":
    main()
'''
        
        with open("update_app.py", "w") as f:
            f.write(script_content)
        
        return "update_app.py"

def main():
    """Main function for testing"""
    checker = UpdateChecker()
    
    print("Checking for updates...")
    update_info = checker.check_for_updates()
    
    if update_info.get('available'):
        print(f"New version available: {update_info['version']}")
        print(f"Release notes: {update_info.get('release_notes', 'No release notes')}")
        
        # Test Notepad++-style update
        if update_info.get('assets'):
            print("Testing Notepad++-style update...")
            success = checker.perform_notepad_style_update(update_info)
            if success:
                print("Update process initiated successfully!")
            else:
                print("Update process failed.")
    else:
        print("No updates available.")
        if update_info.get('error'):
            print(f"Error: {update_info['error']}")

if __name__ == "__main__":
    main() 