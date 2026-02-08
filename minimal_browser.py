#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon, QFont

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Develer Browser v1.1.1")
        self.setGeometry(100, 100, 800, 200)
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("🌐 Develer Browser v1.1.1")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # URL input
        url_layout = QHBoxLayout()
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL (e.g., google.com)")
        self.url_bar.returnPressed.connect(self.navigate)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        
        open_btn = QPushButton("🌍 Open")
        open_btn.clicked.connect(self.navigate)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        url_layout.addWidget(self.url_bar)
        url_layout.addWidget(open_btn)
        layout.addLayout(url_layout)
        
        # Quick links
        quick_layout = QHBoxLayout()
        
        google_btn = QPushButton("🔍 Google")
        google_btn.clicked.connect(lambda: self.open_url("https://www.google.com"))
        google_btn.setStyleSheet("QPushButton { background-color: #4285f4; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
        
        youtube_btn = QPushButton("📺 YouTube")
        youtube_btn.clicked.connect(lambda: self.open_url("https://www.youtube.com"))
        youtube_btn.setStyleSheet("QPushButton { background-color: #ff0000; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
        
        github_btn = QPushButton("💻 GitHub")
        github_btn.clicked.connect(lambda: self.open_url("https://www.github.com"))
        github_btn.setStyleSheet("QPushButton { background-color: #333; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
        
        quick_layout.addWidget(google_btn)
        quick_layout.addWidget(youtube_btn)
        quick_layout.addWidget(github_btn)
        layout.addLayout(quick_layout)
        
        # Status
        self.status_label = QLabel("Ready to browse!")
        self.status_label.setStyleSheet("color: #27ae60; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Set default URL
        self.url_bar.setText("google.com")
        
    def navigate(self):
        url = self.url_bar.text().strip()
        if not url:
            self.status_label.setText("Please enter a URL")
            return
            
        self.open_url(url)
        
    def open_url(self, url):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        try:
            webbrowser.open(url)
            self.status_label.setText(f"Opened: {url}")
            self.status_label.setStyleSheet("color: #27ae60; font-style: italic;")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c; font-style: italic;")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Develer Browser")
    app.setApplicationVersion("1.1.1")
    browser = SimpleBrowser()
    browser.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())