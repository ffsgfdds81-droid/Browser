#!/usr/bin/env python3
"""
Final Test - Quick verification that error pages integration works
"""

import sys
import os

def final_test():
    """Final comprehensive test"""
    print("Python Browser Pro - Final Integration Test")
    print("=" * 50)
    
    # Test 1: Check error pages exist
    print("1. Checking error pages...")
    html_files = []
    if os.path.exists("error_pages"):
        import glob
        html_files = glob.glob("error_pages/**/*.html", recursive=True)
        print(f"   Found {len(html_files)} error pages")
    else:
        print("   ERROR: error_pages directory not found")
        return False
    
    # Test 2: Check core files exist
    print("2. Checking core files...")
    core_files = [
        "error_manager.py",
        "browser_pro.py", 
        "test_error_pages.py",
        "main.py"
    ]
    
    for file in core_files:
        if os.path.exists(file):
            print(f"   Found: {file}")
        else:
            print(f"   MISSING: {file}")
            return False
    
    # Test 3: Test imports
    print("3. Testing imports...")
    try:
        from PyQt5.QtWidgets import QApplication
        from error_manager import ErrorPagesManager
        from browser_pro import SettingsManager
        print("   All imports successful")
    except Exception as e:
        print(f"   Import failed: {e}")
        return False
    
    # Test 4: Test error manager
    print("4. Testing error manager...")
    try:
        app = QApplication(sys.argv)
        from PyQt5.QtWidgets import QMainWindow
        dummy_window = QMainWindow()
        error_manager = ErrorPagesManager(dummy_window)
        
        total_pages = error_manager.get_available_errors_count()
        print(f"   Error pages available: {total_pages}")
        
        if total_pages >= 50:
            print("   Error manager working correctly")
        else:
            print(f"   Warning: Expected at least 50 pages, got {total_pages}")
    except Exception as e:
        print(f"   Error manager test failed: {e}")
        return False
    
    # Test 5: Test a specific error page
    print("5. Testing error page loading...")
    try:
        error_404_path = error_manager.get_error_page_path(404)
        if os.path.exists(error_404_path):
            print(f"   404 error page found: {os.path.basename(error_404_path)}")
        else:
            print(f"   404 error page not found: {error_404_path}")
            return False
    except Exception as e:
        print(f"   Error page test failed: {e}")
        return False
    
    return True

def show_usage():
    """Show usage instructions"""
    print("\n" + "=" * 50)
    print("USAGE INSTRUCTIONS")
    print("=" * 50)
    print()
    print("1. RUN MAIN BROWSER:")
    print("   python main.py")
    print()
    print("2. RUN BROWSER PRO DIRECTLY:")
    print("   python browser_pro.py")
    print()
    print("3. TEST ALL ERROR PAGES:")
    print("   python test_error_pages.py")
    print()
    print("4. VIEW INTEGRATION EXAMPLES:")
    print("   python error_integration_example.py")
    print()
    print("5. QUICK DEMO:")
    print("   python quick_error_demo.py")
    print()
    print("INTEGRATED FEATURES:")
    print("- 57+ error pages with Chrome-style design")
    print("- Automatic error detection and handling")
    print("- Error Pages button in navigation bar")
    print("- Complete Error Pages menu with categories")
    print("- Random error functionality for testing")
    print("- Comprehensive API for integration")
    print("- Russian language interface")
    print("- Responsive and mobile-friendly design")
    print()
    print("ERROR CATEGORIES:")
    print("- HTTP Errors (400-511)")
    print("- Chrome Browser Errors")
    print("- Google Service Errors") 
    print("- Chrome Features (dino game, offline)")
    print("- Special Pages (index, search, troubleshooting)")

def main():
    """Main test function"""
    if final_test():
        print("\nSUCCESS: All tests passed!")
        show_usage()
        return 0
    else:
        print("\nFAILED: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())