import sys
print("Testing imports...")

try:
    from PyQt5.QtWidgets import QApplication
    print("PyQt5 OK")
except Exception as e:
    print(f"PyQt5 error: {e}")
    sys.exit(1)

try:
    from browser_pro import BrowserApplication
    print("browser_pro OK")
except Exception as e:
    print(f"browser_pro error: {e}")
    sys.exit(1)

try:
    app = QApplication([])
    browser = BrowserApplication([])
    print("Browser created successfully")
except Exception as e:
    print(f"Browser creation error: {e}")
    sys.exit(1)

if hasattr(browser.window, 'new_tab_btn'):
    print("+ button in nav: YES")
else:
    print("+ button in nav: NO")

if hasattr(browser.window, 'corner_new_tab_btn'):
    print("+ button in corner: YES")
else:
    print("+ button in corner: NO")

print("Test completed")