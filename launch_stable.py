#!/usr/bin/env python3
"""
Reliable Browser Launcher - Always uses stable browser.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def launch_stable_browser():
    """Launch the stable browser version"""
    try:
        print("Starting Python Browser - Stable Version...")
        print("Features:")
        print("  + DevTools (F12)")
        print("  + Error Pages (67+ pages)")
        print("  + Full Integration")
        print("  + All Tools Working")
        print()
        
        # Import and run stable browser
        from browser import BrowserApplication, sys
        
        app = BrowserApplication(sys.argv)
        return app.exec_()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nPlease ensure you have PyQt5 and PyQtWebEngine installed:")
        print("pip install PyQt5 PyQtWebEngine")
        return 1
        
    except KeyboardInterrupt:
        print("\nBrowser stopped by user")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main launcher function"""
    try:
        return launch_stable_browser()
    except Exception as e:
        print(f"Launcher error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())