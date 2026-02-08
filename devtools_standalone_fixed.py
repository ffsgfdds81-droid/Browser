#!/usr/bin/env python3
"""
DevTools Standalone Launcher - Fixed QtWebEngine initialization
"""
import sys
import os

# CRITICAL: Set Qt attributes BEFORE any Qt imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Set required attributes for QtWebEngine
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

# Now import QtWebEngine modules
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                               QLabel, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

class DevToolsStandalone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevTools Standalone")
        self.setGeometry(200, 200, 1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create web view
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("https://www.google.com"))
        layout.addWidget(self.webview)
        
        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        test_btn = QPushButton("Test DevTools")
        test_btn.clicked.connect(self.test_devtools)
        control_layout.addWidget(test_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        control_layout.addWidget(close_btn)
        
        layout.addWidget(control_panel)
        
        # Status
        self.statusBar().showMessage("Ready - Click Test DevTools")
    
    def test_devtools(self):
        try:
            # Import DevTools AFTER Qt is properly initialized
            from devtools import DevToolsWindow, __version__
            
            # Create DevTools window
            devtools = DevToolsWindow(self.webview)
            devtools.show()
            
            self.statusBar().showMessage(f"DevTools v{__version__} opened successfully!")
            
        except Exception as e:
            error_msg = f"DevTools Error: {str(e)}"
            print(f"❌ {error_msg}")
            QMessageBox.critical(self, "DevTools Error", error_msg)
            self.statusBar().showMessage("DevTools failed!")

def main():
    # Create application with proper Qt setup
    app = QApplication(sys.argv)
    app.setApplicationName("DevTools Standalone")
    
    # Create and show window
    window = DevToolsStandalone()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    main()