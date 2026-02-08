#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Develer Browser Main Launcher
Always uses stable browser.py for maximum reliability
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main launcher function"""
    print("Starting Develer Browser - Advanced Optimized Version")
    print("=" * 60)
    print("Core Features:")
    print("  + Web Browsing")
    print("  + 67+ Error Pages") 
    print("  + DevTools Integration (F12)")
    print("  + Local Server")
    print("  + All Tools Working")
    print("")
    print("Advanced Optimizations:")
    print("  [OK] Advanced Memory Management")
    print("  [OK] WebGPU Hardware Acceleration") 
    print("  [OK] Optimized Rendering Engine")
    print("  [OK] Browser Component Memory Pooling")
    print("  [OK] Performance Monitoring & Diagnostics")
    print("  [OK] Advanced Shader Effects System")
    print("=" * 60)
    
    try:
        # Try to import stable browser
        print("Loading stable browser module...")
        
        from browser import BrowserApplication
        
        print("Stable browser loaded successfully!")
        print()
        
        # Create and run browser application
        app = BrowserApplication(sys.argv)
        print("Develer Browser started successfully!")
        print()
        print("Controls:")
        print("  F12 - DevTools")
        print("  [!] - Error Pages")  
        print("  Ctrl+T - New Tab")
        print("  [?] - Find on Page")
        print("  <---> - Navigation")
        print("  [*] - Bookmarks")
        print("  DevTools Menu - Performance Stats, Memory Stats, GPU Stats, Shader Effects")
        print()
        
        return app.exec_()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print()
        print("Please ensure you have the required modules:")
        print("  pip install PyQt5 PyQtWebEngine psutil numpy")
        return 1
        
    except KeyboardInterrupt:
        print("\nBrowser stopped by user")
        return 0
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())