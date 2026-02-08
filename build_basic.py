#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ultra Simple Build Script
Minimal executable without advanced features
"""

import subprocess
import sys
import os

def build_basic():
    """Build basic executable"""
    print("Building basic executable (no advanced features)...")
    
    # Create simple main
    simple_main = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Develer Browser - Basic")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("https://www.google.com"))
        
        # Set central widget
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

def main():
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open('simple_main.py', 'w', encoding='utf-8') as f:
        f.write(simple_main)
    
    # Build with PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=DevelerBrowser_Basic',
        '--clean',
        '--noconfirm',
        '--log-level=ERROR',
        'simple_main.py'
    ]
    
    subprocess.run(cmd, check=True)
    
    # Check result
    if os.path.exists('dist/DevelerBrowser_Basic.exe'):
        size_mb = os.path.getsize('dist/DevelerBrowser_Basic.exe') / 1024 / 1024
        print(f"✅ Basic build successful!")
        print(f"📁 Executable: dist/DevelerBrowser_Basic.exe")
        print(f"📊 Size: {size_mb:.1f} MB")
        return True
    else:
        print("❌ Basic build failed!")
        return False

if __name__ == '__main__':
    success = build_basic()
    sys.exit(0 if success else 1)