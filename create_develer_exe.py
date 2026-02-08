#!/usr/bin/env python3
"""
Create Develer Browser EXE from main.py directly
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("DEVELER BROWSER EXE BUILDER")
    print("=" * 50)
    
    # Clean previous attempts (skip if in use)
    for name in ["DevelerBrowser.exe", "DevelerBrowser_Fixed.exe", "DevelerBrowser_New.exe"]:
        if os.path.exists(name):
            try:
                os.remove(name)
                print(f"Removed old file: {name}")
            except PermissionError:
                print(f"Skipping {name} (file in use)")
    
    print("\nBuilding from main.py (correct version with Develer Browser branding)...")
    
    # Simple direct PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=DevelerBrowser",
        "--icon=browser-icon.png",
        "main.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, timeout=300, 
                             capture_output=True, text=True)
        print("Build completed successfully!")
        print("\nBuild output:")
        print(result.stdout)
        
        # Check result
        exe_path = os.path.join("dist", "DevelerBrowser.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024*1024)
            print(f"EXE created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            # Copy to root directory
            shutil.copy2(exe_path, "DevelerBrowser.exe")
            print("Copied to main directory as DevelerBrowser.exe")
            
            return True
        else:
            print("EXE not found after build")
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("Build timed out (5 minutes)")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Build failed with code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: DevelerBrowser.exe is ready!")
        print("The new EXE should show 'Develer Browser' in all windows.")
        print("Run it with: DevelerBrowser.exe")
    else:
        print("\nFAILED: Could not create DevelerBrowser.exe")
        sys.exit(1)