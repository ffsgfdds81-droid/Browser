#!/usr/bin/env python3
"""
Develer Browser - Simple Standalone Version
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QTabWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("Warning: PyQtWebEngine not available")

class DevelerBrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Develer Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply modern styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                background-color: #f5f5f5;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Navigation bar
        nav_layout = QVBoxLayout()
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add first tab
        self.add_new_tab("https://www.google.com")
        
        nav_layout.addWidget(self.tab_widget)
        layout.addLayout(nav_layout)
        
    def add_new_tab(self, url=None):
        if WEBENGINE_AVAILABLE:
            browser_tab = QWebEngineView()
            if url:
                browser_tab.setUrl(QUrl(url))
            else:
                browser_tab.setUrl(QUrl("https://www.google.com"))
            browser_tab.urlChanged.connect(self.update_url_bar)
            browser_tab.titleChanged.connect(lambda title: self.update_tab_title(self.tab_widget.count()-1, title))
        else:
            browser_tab = QLabel("PyQt5 WebEngine not available.\nPlease install: pip install PyQtWebEngine")
            browser_tab.setStyleSheet("padding: 20px; font-size: 16px; text-align: center;")
            browser_tab.setAlignment(Qt.AlignCenter)
        
        index = self.tab_widget.addTab(browser_tab, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        
        if WEBENGINE_AVAILABLE:
            self.tab_widget.currentWidget().setFocus()
        
        return browser_tab
    
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
            
        if not url.startswith(('http://', 'https://')):
            # Check if it's a search query
            if '.' in url or ' ' in url:
                url = f"https://www.google.com/search?q={url}"
            else:
                url = f"https://{url}"
        
        current_tab = self.tab_widget.currentWidget()
        if WEBENGINE_AVAILABLE and hasattr(current_tab, 'setUrl'):
            current_tab.setUrl(QUrl(url))
    
    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
    
    def update_tab_title(self, index, title):
        if title:
            # Truncate long titles
            if len(title) > 30:
                title = title[:27] + "..."
            self.tab_widget.setTabText(index, title)
        else:
            self.tab_widget.setTabText(index, "New Tab")
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # Don't close the last tab, create a new one instead
            self.add_new_tab()

class DevelerBrowserApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Develer Browser")
        self.setApplicationVersion("1.0.0")
        
        # Set Qt attributes for WebEngine
        self.setAttribute(Qt.AA_ShareOpenGLContexts)
        self.setAttribute(Qt.AA_UseSoftwareOpenGL)
        
        self.window = DevelerBrowserWindow()
        self.window.show()

def main():
    print("Starting Develer Browser...")
    print("=" * 40)
    
    app = DevelerBrowserApplication(sys.argv)
    
    # Set WebEngine settings
    if WEBENGINE_AVAILABLE:
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())