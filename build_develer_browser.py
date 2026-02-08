#!/usr/bin/env python3
"""
Simple Develer Browser EXE Builder
Creates a standalone executable with correct branding
"""

import os
import sys
import shutil
import subprocess

def create_simple_exe():
    """Create simple standalone EXE"""
    print("=" * 50)
    print("Creating Develer Browser EXE")
    print("=" * 50)
    
    # Clean previous builds (skip if files are in use)
    if os.path.exists("build"):
        try:
            shutil.rmtree("build")
        except:
            print("Warning: Could not clean build directory")
    
    # Create new dist directory
    os.makedirs("dist", exist_ok=True)
    
    # Simple PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name=DevelerBrowser",
        "--icon=browser-icon.png",
        "--add-data=*.html;.",
        "--add-data=error_pages;error_pages",
        "--add-data=data;data",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui", 
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=PyQt5.QtWebEngineWidgets",
        "--hidden-import=browser",
        "--hidden-import=devtools",
        "--hidden-import=error_page_handler", 
        "--hidden-import=local_server",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=tkinter",
        "main.py"
    ]
    
    print("Running PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("✅ Build completed successfully!")
        
        # Check if EXE was created
        exe_path = os.path.join("dist", "DevelerBrowser.exe")
        if os.path.exists(exe_path):
            print(f"✅ EXE created: {exe_path}")
            print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
            return True
        else:
            print("❌ EXE not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    success = create_simple_exe()
    if success:
        print("\n🎉 Develer Browser EXE is ready!")
        print("Run: dist\\DevelerBrowser.exe")
    else:
        print("\n❌ Build failed")
        sys.exit(1)