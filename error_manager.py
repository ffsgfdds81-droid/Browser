#!/usr/bin/env python3
"""
Error Pages Manager - Manages all error pages for Python Browser Pro
Integrates with error_pages directory structure
"""

import os
import json
import random
from PyQt5.QtCore import QUrl, QTimer, QDateTime
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtWidgets import QMessageBox, QMenu, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView

class ErrorPagesManager:
    """Manages all error pages and provides intelligent error handling"""
    
    def __init__(self, browser_window):
        self.browser_window = browser_window
        self.error_pages_dir = "error_pages"
        self.setup_error_mappings()
        
    def setup_error_mappings(self):
        """Setup mappings for different error types"""
        # HTTP Errors (400-511)
        self.http_errors = {
            # 4xx Client Errors
            400: "google_errors/400.html",
            401: "google_errors/401.html", 
            402: "google_errors/402.html",
            403: "google_errors/403.html",
            404: "google_errors/404.html",
            405: "google_errors/405.html",
            406: "google_errors/406.html",
            407: "google_errors/407.html",
            408: "google_errors/408.html",
            409: "google_errors/409.html",
            410: "google_errors/410.html",
            411: "google_errors/411.html",
            412: "google_errors/412.html",
            413: "google_errors/413.html",
            414: "google_errors/414.html",
            415: "google_errors/415.html",
            416: "google_errors/416.html",
            417: "google_errors/417.html",
            418: "google_errors/418.html",
            421: "google_errors/421.html",
            422: "google_errors/422.html",
            423: "google_errors/423.html",
            424: "google_errors/424.html",
            425: "google_errors/425.html",
            426: "google_errors/426.html",
            428: "google_errors/428.html",
            429: "google_errors/429.html",
            431: "google_errors/431.html",
            451: "google_errors/451.html",
            
            # 5xx Server Errors
            500: "server_errors/500.html",
            501: "server_errors/501.html",
            502: "server_errors/502.html",
            503: "server_errors/503.html",
            504: "server_errors/504.html",
            505: "server_errors/505.html",
            506: "server_errors/506.html",
            507: "server_errors/507.html",
            508: "server_errors/508.html",
            510: "server_errors/510.html",
            511: "server_errors/511.html",
        }
        
        # Chrome Browser Errors
        self.chrome_errors = {
            "ERR_INTERNET_DISCONNECTED": "chrome_errors/ERR_INTERNET_DISCONNECTED.html",
            "ERR_CONNECTION_REFUSED": "chrome_errors/ERR_CONNECTION_REFUSED.html",
            "ERR_CONNECTION_TIMED_OUT": "chrome_errors/ERR_CONNECTION_TIMED_OUT.html",
            "ERR_NAME_NOT_RESOLVED": "chrome_errors/ERR_NAME_NOT_RESOLVED.html",
            "ERR_SSL_PROTOCOL_ERROR": "chrome_errors/ERR_SSL_PROTOCOL_ERROR.html",
            "ERR_SSL_VERSION_OR_CIPHER_MISMATCH": "chrome_errors/ERR_SSL_VERSION_OR_CIPHER_MISMATCH.html",
            "ERR_TOO_MANY_REDIRECTS": "chrome_errors/ERR_TOO_MANY_REDIRECTS.html",
            "ERR_EMPTY_RESPONSE": "chrome_errors/ERR_EMPTY_RESPONSE.html",
            "ERR_NETWORK_CHANGED": "chrome_errors/ERR_NETWORK_CHANGED.html",
            "ERR_CACHE_MISS": "chrome_errors/ERR_CACHE_MISS.html",
            "ERR_BLOCKED_BY_CLIENT": "chrome_errors/ERR_BLOCKED_BY_CLIENT.html",
            "ERR_CONTENT_DECODING_FAILED": "chrome_errors/ERR_CONTENT_DECODING_FAILED.html",
            "ERR_CACHE_READ_FAILURE": "chrome_errors/ERR_CACHE_READ_FAILURE.html",
        }
        
        # Google Service Errors
        self.google_service_errors = {
            "quota_exceeded": "google_specific/google_quota_exceeded.html",
            "unusual_traffic": "google_specific/google_unusual_traffic.html",
            "access_denied": "google_specific/google_access_denied.html",
            "captcha": "google_specific/google_captcha.html",
            "something_went_wrong": "google_specific/google_something_went_wrong.html",
        }
        
        # Chrome Feature Pages
        self.chrome_features = {
            "offline": "chrome_specific/chrome_offline_page.html",
            "dino_game": "chrome_specific/chrome_dino_game.html",
        }
        
        # Special pages
        self.special_pages = {
            "error_index": "index.html",
            "error_search": "search.html", 
            "troubleshooting": "troubleshooting.html",
        }
    
    def get_error_page_path(self, error_code_or_name, **kwargs):
        """Get the appropriate error page path based on error code or name"""
        
        # Try HTTP error codes first
        if isinstance(error_code_or_name, int) or error_code_or_name.isdigit():
            code = int(error_code_or_name)
            if code in self.http_errors:
                return self._build_file_path(self.http_errors[code], **kwargs)
        
        # Try Chrome error names
        if error_code_or_name in self.chrome_errors:
            return self._build_file_path(self.chrome_errors[error_code_or_name], **kwargs)
        
        # Try Google service errors
        if error_code_or_name in self.google_service_errors:
            return self._build_file_path(self.google_service_errors[error_code_or_name], **kwargs)
        
        # Try Chrome features
        if error_code_or_name in self.chrome_features:
            return self._build_file_path(self.chrome_features[error_code_or_name], **kwargs)
        
        # Try special pages
        if error_code_or_name in self.special_pages:
            return self._build_file_path(self.special_pages[error_code_or_name], **kwargs)
        
        # Fallback to 404 or generic error
        return self._build_file_path(self.http_errors.get(404, "google_errors/400.html"), **kwargs)
    
    def _build_file_path(self, relative_path, **kwargs):
        """Build full file path with query parameters"""
        base_path = os.path.abspath(os.path.join(self.error_pages_dir, relative_path))
        
        # Add query parameters if provided
        if kwargs:
            query_parts = [f"{key}={value}" for key, value in kwargs.items()]
            query_string = "&".join(query_parts)
            return f"{base_path}?{query_string}"
        
        return base_path
    
    def show_error_page(self, error_code_or_name, webview=None, **kwargs):
        """Show error page in specified webview or current tab"""
        if webview is None:
            webview = self.browser_window.tab_widget.currentWidget()
            if webview is None:
                return False
        
        error_page_path = self.get_error_page_path(error_code_or_name, **kwargs)
        file_url = QUrl.fromLocalFile(error_page_path)
        
        webview.setUrl(file_url)
        return True
    
    def simulate_http_error(self, error_code, original_url=None):
        """Simulate HTTP error for testing purposes"""
        kwargs = {}
        if original_url:
            kwargs['original_url'] = original_url
            kwargs['timestamp'] = QDateTime.currentDateTime().toString(Qt.ISODate)
        
        self.show_error_page(error_code, **kwargs)
    
    def simulate_chrome_error(self, error_name, original_url=None):
        """Simulate Chrome browser error"""
        kwargs = {}
        if original_url:
            kwargs['original_url'] = original_url
            kwargs['failed_url'] = original_url
        
        self.show_error_page(error_name, **kwargs)
    
    def show_google_service_error(self, service_error, service_name=None):
        """Show Google service specific error"""
        kwargs = {}
        if service_name:
            kwargs['service'] = service_name
        kwargs['timestamp'] = QDateTime.currentDateTime().toString(Qt.ISODate)
        
        self.show_error_page(service_error, **kwargs)
    
    def show_chrome_feature(self, feature_name):
        """Show Chrome specific feature page"""
        self.show_error_page(feature_name)
    
    def get_random_error_page(self):
        """Get a random error page for testing"""
        all_errors = {}
        all_errors.update(self.http_errors)
        all_errors.update(self.chrome_errors)
        all_errors.update(self.google_service_errors)
        
        error_key = random.choice(list(all_errors.keys()))
        return error_key, self.get_error_page_path(error_key)
    
    def create_error_test_menu(self, parent_menu):
        """Create a menu with all error pages for testing"""
        from PyQt5.QtWidgets import QMenu
        
        error_menu = QMenu("🚨 Test Error Pages", parent_menu)
        
        # HTTP Errors submenu
        http_menu = QMenu("📡 HTTP Errors", error_menu)
        for code in sorted(self.http_errors.keys()):
            action = http_menu.addAction(f"HTTP {code}")
            action.triggered.connect(lambda checked, c=code: self.simulate_http_error(c))
        error_menu.addMenu(http_menu)
        
        # Chrome Errors submenu  
        chrome_menu = QMenu("🌐 Chrome Errors", error_menu)
        for error_name in sorted(self.chrome_errors.keys()):
            action = chrome_menu.addAction(error_name)
            action.triggered.connect(lambda checked, e=error_name: self.simulate_chrome_error(e))
        error_menu.addMenu(chrome_menu)
        
        # Google Service Errors submenu
        google_menu = QMenu("🔍 Google Service Errors", error_menu)
        for error_name in sorted(self.google_service_errors.keys()):
            action = google_menu.addAction(error_name.replace('_', ' ').title())
            action.triggered.connect(lambda checked, e=error_name: self.show_google_service_error(e))
        error_menu.addMenu(google_menu)
        
        # Chrome Features submenu
        features_menu = QMenu("🎮 Chrome Features", error_menu)
        for feature_name in sorted(self.chrome_features.keys()):
            action = features_menu.addAction(feature_name.replace('_', ' ').title())
            action.triggered.connect(lambda checked, f=feature_name: self.show_chrome_feature(f))
        error_menu.addMenu(features_menu)
        
        # Special pages submenu
        special_menu = QMenu("📄 Special Pages", error_menu)
        for page_name in sorted(self.special_pages.keys()):
            action = special_menu.addAction(page_name.replace('_', ' ').title())
            action.triggered.connect(lambda checked, p=page_name: self.show_error_page(p))
        error_menu.addMenu(special_menu)
        
        # Random error
        random_action = error_menu.addAction("🎲 Random Error")
        random_action.triggered.connect(self.show_random_error)
        
        return error_menu
    
    def show_random_error(self):
        """Show a random error page"""
        error_key, _ = self.get_random_error_page()
        
        if isinstance(error_key, int):
            self.simulate_http_error(error_key)
        elif error_key in self.chrome_errors:
            self.simulate_chrome_error(error_key)
        elif error_key in self.google_service_errors:
            self.show_google_service_error(error_key)
        elif error_key in self.chrome_features:
            self.show_chrome_feature(error_key)
        else:
            self.show_error_page(error_key)
    
    def handle_network_error(self, error_reply):
        """Handle actual network errors from QtWebEngine"""
        error_code = error_reply.error()
        error_string = error_reply.errorString()
        url = error_reply.url().toString()
        
        # Map Qt error codes to our error pages
        if error_code == 1:  # Connection Refused Error
            self.simulate_chrome_error("ERR_CONNECTION_REFUSED", url)
        elif error_code == 2:  # Host Not Found Error
            self.simulate_chrome_error("ERR_NAME_NOT_RESOLVED", url)
        elif error_code == 3:  # Unknown Error
            self.simulate_http_error(500, url)
        elif error_code == 4:  # Protocol Failure
            self.simulate_chrome_error("ERR_SSL_PROTOCOL_ERROR", url)
        elif error_code == 5:  # Connection Reset
            self.simulate_chrome_error("ERR_CONNECTION_RESET", url)
        else:
            # Fallback to generic error
            self.simulate_http_error(400, url)
    
    def show_error_index(self):
        """Show the error pages index"""
        self.show_error_page("error_index")
    
    def show_troubleshooting(self):
        """Show troubleshooting page"""
        self.show_error_page("troubleshooting")
    
    def show_error_search(self):
        """Show error search page"""
        self.show_error_page("error_search")
    
    def get_available_errors_count(self):
        """Get total number of available error pages"""
        return len(self.http_errors) + len(self.chrome_errors) + len(self.google_service_errors) + len(self.chrome_features)
    
    def list_all_error_pages(self):
        """List all available error pages"""
        all_pages = {
            "HTTP Errors": self.http_errors,
            "Chrome Errors": self.chrome_errors, 
            "Google Service Errors": self.google_service_errors,
            "Chrome Features": self.chrome_features,
            "Special Pages": self.special_pages
        }
        return all_pages