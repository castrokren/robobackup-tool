#!/usr/bin/env python3
"""
Test script for the update dialog
Run this to see the update dialog in action
"""

import tkinter as tk
from update_gui import check_for_updates_gui

def main():
    """Test the update dialog"""
    print("Testing Update Dialog...")
    print("This will show the update dialog if updates are available.")
    print("If no updates are available, it will show a message.")
    
    # Create a root window for the dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Check for updates
    result = check_for_updates_gui(root)
    
    if result:
        print(f"Update dialog result: {result}")
    else:
        print("No updates available or dialog was closed.")
    
    root.destroy()

if __name__ == "__main__":
    main() 