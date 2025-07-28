#!/usr/bin/env python3
"""
Standalone Update Script for RoboBackup Tool
Run this script to check for and install updates
"""

import sys
import os
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update_checker import UpdateChecker

def main():
    """Main update function"""
    print("=" * 50)
    print("RoboBackup Tool - Update Checker")
    print("=" * 50)
    
    checker = UpdateChecker()
    
    print("Checking for updates...")
    update_info = checker.check_for_updates()
    
    if update_info.get('available'):
        print(f"\n✅ New version available: {update_info['version']}")
        print(f"Current version: {checker.current_version}")
        
        if update_info.get('release_notes'):
            print(f"\nRelease Notes:")
            print("-" * 30)
            print(update_info['release_notes'])
            print("-" * 30)
        
        response = input("\nDo you want to update? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print("\n📥 Downloading update...")
            update_file = checker.download_update(update_info['download_url'])
            
            if update_file:
                print("📦 Installing update...")
                if checker.install_update(update_file):
                    print("\n✅ Update installed successfully!")
                    print("🔄 Please restart the application.")
                else:
                    print("\n❌ Error installing update.")
            else:
                print("\n❌ Error downloading update.")
        else:
            print("\n⏭️ Update cancelled.")
    else:
        print("\n✅ No updates available.")
        if update_info.get('error'):
            print(f"⚠️ Error: {update_info['error']}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 