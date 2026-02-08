#!/usr/bin/env python3
"""
Open DevTools - Python Browser
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_devtools_in_browser():
    """Open DevTools in default browser"""
    try:
        import webbrowser
        from PyQt5.QtCore import QUrl
        
        devtools_path = os.path.abspath("devtools.html")
        if os.path.exists(devtools_path):
            url = QUrl.fromLocalFile(devtools_path).toString()
            webbrowser.open(url)
            print(f"DevTools opened in browser: {url}")
            return 0
        else:
            print(f"Error: File not found - {devtools_path}")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

def main():
    """Main function"""
    print("DevTools - Python Browser")
    print("=" * 30)
    
    # Check if file exists
    devtools_path = os.path.abspath("devtools.html")
    if not os.path.exists(devtools_path):
        print(f"File not found: {devtools_path}")
        return 1
    
    print(f"File found: {devtools_path}")
    print(f"URL: file:///C:/Users/Sklad2/Downloads/python_browser/devtools.html")
    print()
    
    # Open in browser
    return open_devtools_in_browser()

if __name__ == "__main__":
    sys.exit(main())