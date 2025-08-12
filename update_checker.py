#!/usr/bin/env python3
"""
Update Checker for RoboBackup Tool
Handles checking for updates, downloading, and installing them
"""

import os
import sys
import json
import requests
import subprocess
import tempfile
import shutil
from datetime import datetime
import logging

class UpdateChecker:
    def __init__(self):
        self.current_version = self.get_current_version()
        # GitHub repository URLs for castrokren/robobackup-tool
        self.update_url = "https://api.github.com/repos/castrokren/robobackup-tool/releases/latest"
        self.download_base_url = "https://github.com/castrokren/robobackup-tool/releases/download"
        self.logger = logging.getLogger(__name__)
        
    def get_current_version(self):
        """Get current application version"""
        try:
            version_file = os.path.join(os.getcwd(), 'version_info.txt')
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    for line in f:
                        if line.startswith('version='):
                            return line.split('=')[1].strip()
            return "1.0.0.0"  # Default version
        except Exception as e:
            self.logger.error(f"Error reading version: {e}")
            return "1.0.0.0"
    
    def check_for_updates(self):
        """Check for available updates"""
        try:
            # Check GitHub releases for updates
            response = requests.get(self.update_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data['tag_name'].lstrip('v')
                
                if self.compare_versions(latest_version, self.current_version) > 0:
                    return {
                        'available': True,
                        'version': latest_version,
                        'download_url': f"{self.download_base_url}/{release_data['tag_name']}/RoboBackupTool-{latest_version}.msi",
                        'release_notes': release_data.get('body', ''),
                        'error': None
                    }
                
            return {
                'available': False,
                'version': self.current_version,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return {
                'available': False,
                'version': self.current_version,
                'error': str(e)
            }
    
    def compare_versions(self, version1, version2):
        """Compare two version strings"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_part = v1_parts[i] if i < len(v1_parts) else 0
                v2_part = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_part > v2_part:
                    return 1
                elif v1_part < v2_part:
                    return -1
            
            return 0
        except Exception as e:
            self.logger.error(f"Error comparing versions: {e}")
            return 0
    
    def download_update(self, download_url):
        """Download the update file"""
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.msi')
            
            # Download the file
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            
            temp_file.close()
            return temp_file.name
            
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None
    
    def install_update(self, update_file):
        """Install the downloaded update"""
        try:
            # For MSI files, use msiexec
            if update_file.endswith('.msi'):
                result = subprocess.run([
                    'msiexec', '/i', update_file, '/quiet', '/norestart'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True
                else:
                    self.logger.error(f"MSI installation failed: {result.stderr}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error installing update: {e}")
            return False
        finally:
            # Clean up temporary file
            try:
                os.unlink(update_file)
            except:
                pass
    
    def perform_notepad_style_update(self, update_info):
        """Perform Notepad++-style update (download and prepare for restart)"""
        try:
            if not update_info.get('available'):
                return False
            
            # Download the update
            update_file = self.download_update(update_info['download_url'])
            if not update_file:
                return False
            
            # Create restart script
            restart_script = self.create_restart_script(update_file)
            if not restart_script:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error performing update: {e}")
            return False
    
    def create_restart_script(self, update_file):
        """Create a script to restart the application after update"""
        try:
            script_content = f'''@echo off
echo Waiting for application to close...
timeout /t 2 /nobreak >nul

echo Installing update...
msiexec /i "{update_file}" /quiet /norestart

echo Starting application...
start "" "{sys.executable}" "{sys.argv[0]}"

del "%~f0"
'''
            
            script_file = tempfile.NamedTemporaryFile(delete=False, suffix='.bat', mode='w')
            script_file.write(script_content)
            script_file.close()
            
            # Execute the restart script
            subprocess.Popen([script_file.name], shell=True)
            
            return script_file.name
            
        except Exception as e:
            self.logger.error(f"Error creating restart script: {e}")
            return None
