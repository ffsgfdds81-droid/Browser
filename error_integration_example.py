#!/usr/bin/env python3
"""
Integration Example - How to use error pages in other Python files
Demonstrates integration with all error pages in various scenarios
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QTabWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Import error manager
from error_manager import ErrorPagesManager

class ErrorIntegrationExample(QMainWindow):
    """Example of integrating error pages in any Python application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error Pages Integration Example")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize error manager
        self.error_manager = ErrorPagesManager(self)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🔗 Error Pages Integration Examples")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976d2; padding: 10px;")
        layout.addWidget(title)
        
        # Create tabs for different scenarios
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tab 1: HTTP Error Handling
        self.create_http_error_tab()
        
        # Tab 2: Chrome Error Simulation
        self.create_chrome_error_tab()
        
        # Tab 3: Google Service Errors
        self.create_google_service_tab()
        
        # Tab 4: Network Error Handling
        self.create_network_error_tab()
        
        # Tab 5: Error Manager API
        self.create_api_demo_tab()
        
    def create_http_error_tab(self):
        """Create tab for HTTP error examples"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Webview
        webview = QWebEngineView()
        layout.addWidget(webview)
        
        # Button row
        button_layout = QHBoxLayout()
        
        buttons = [
            ("400 Bad Request", 400),
            ("401 Unauthorized", 401),
            ("403 Forbidden", 403),
            ("404 Not Found", 404),
            ("500 Server Error", 500),
            ("502 Bad Gateway", 502),
            ("503 Service Unavailable", 503),
            ("Random HTTP Error", "random_http")
        ]
        
        for text, error in buttons:
            btn = QPushButton(text)
            if error == "random_http":
                btn.clicked.connect(lambda: self.show_random_http_error(webview))
            else:
                btn.clicked.connect(lambda checked, e=error: self.error_manager.simulate_http_error(e, webview))
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(widget, "📡 HTTP Errors")
    
    def create_chrome_error_tab(self):
        """Create tab for Chrome error examples"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Webview
        webview = QWebEngineView()
        layout.addWidget(webview)
        
        # Button row
        button_layout = QHBoxLayout()
        
        chrome_errors = [
            ("No Internet", "ERR_INTERNET_DISCONNECTED"),
            ("Connection Refused", "ERR_CONNECTION_REFUSED"),
            ("DNS Resolution Failed", "ERR_NAME_NOT_RESOLVED"),
            ("SSL Error", "ERR_SSL_PROTOCOL_ERROR"),
            ("Too Many Redirects", "ERR_TOO_MANY_REDIRECTS"),
            ("Random Chrome Error", "random_chrome")
        ]
        
        for text, error in chrome_errors:
            btn = QPushButton(text)
            if error == "random_chrome":
                btn.clicked.connect(lambda: self.show_random_chrome_error(webview))
            else:
                btn.clicked.connect(lambda checked, e=error: self.error_manager.simulate_chrome_error(e, webview))
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(widget, "🌐 Chrome Errors")
    
    def create_google_service_tab(self):
        """Create tab for Google service error examples"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Webview
        webview = QWebEngineView()
        layout.addWidget(webview)
        
        # Button row
        button_layout = QHBoxLayout()
        
        google_errors = [
            ("Quota Exceeded", "quota_exceeded"),
            ("Unusual Traffic", "unusual_traffic"),
            ("Access Denied", "access_denied"),
            ("Captcha Required", "captcha"),
            ("Something Went Wrong", "something_went_wrong"),
            ("Random Google Error", "random_google")
        ]
        
        for text, error in google_errors:
            btn = QPushButton(text)
            if error == "random_google":
                btn.clicked.connect(lambda: self.show_random_google_error(webview))
            else:
                btn.clicked.connect(lambda checked, e=error, s="Google": self.error_manager.show_google_service_error(e, s, webview))
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(widget, "🔍 Google Services")
    
    def create_network_error_tab(self):
        """Create tab for network error handling examples"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Instructions
        instructions = QLabel("""
🌐 Network Error Handling Examples

This tab demonstrates how to handle network errors programmatically:

1. Try different connection scenarios
2. See how errors are mapped to appropriate pages
3. Test retry mechanisms
4. Simulate various network conditions
        """)
        instructions.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Webview
        webview = QWebEngineView()
        layout.addWidget(webview)
        
        # Control buttons
        button_layout = QVBoxLayout()
        
        # Simulate network issues
        network_scenarios = [
            ("Simulate Slow Connection", lambda: self.simulate_slow_connection(webview)),
            ("Simulate Connection Lost", lambda: self.simulate_connection_lost(webview)),
            ("Simulate DNS Failure", lambda: self.simulate_dns_failure(webview)),
            ("Simulate Server Timeout", lambda: self.simulate_server_timeout(webview)),
            ("Simulate Mixed Errors", lambda: self.simulate_mixed_errors(webview)),
            ("Start Error Monitor", lambda: self.start_error_monitor(webview)),
            ("Stop Error Monitor", lambda: self.stop_error_monitor())
        ]
        
        for text, callback in network_scenarios:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(widget, "🌐 Network Errors")
    
    def create_api_demo_tab(self):
        """Create tab demonstrating Error Manager API"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API documentation
        api_text = QTextEdit()
        api_text.setPlainText("""
🔧 Error Manager API Examples

1. Basic Usage:
   error_manager.show_error_page(404)
   error_manager.show_error_page("ERR_CONNECTION_REFUSED")

2. With Parameters:
   error_manager.show_error_page(404, original_url="https://example.com", user="john")

3. HTTP Errors:
   error_manager.simulate_http_error(500, "https://api.example.com")

4. Chrome Errors:
   error_manager.simulate_chrome_error("ERR_INTERNET_DISCONNECTED", "https://site.com")

5. Google Service Errors:
   error_manager.show_google_service_error("quota_exceeded", "Google Drive")

6. Chrome Features:
   error_manager.show_chrome_feature("dino_game")
   error_manager.show_chrome_feature("offline")

7. Random Errors:
   error_manager.show_random_error()

8. Get Statistics:
   total = error_manager.get_available_errors_count()
   all_pages = error_manager.list_all_error_pages()

9. Error Categories:
   - HTTP Errors (400-511)
   - Chrome Browser Errors
   - Google Service Errors  
   - Chrome Features
   - Special Pages

10. Integration in WebView:
    # Connect to load signals
    webview.page().loadFinished.connect(
        lambda success: handle_load_finish(webview, success)
    )
    
    def handle_load_finish(webview, success):
        if not success:
            error_manager.simulate_chrome_error(
                "ERR_CONNECTION_REFUSED", 
                webview.url().toString()
            )
        """)
        api_text.setReadOnly(True)
        layout.addWidget(api_text)
        
        # Interactive demo
        demo_label = QLabel("🎮 Interactive API Demo:")
        demo_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(demo_label)
        
        # Demo webview
        demo_webview = QWebEngineView()
        layout.addWidget(demo_webview)
        
        # Demo buttons
        demo_layout = QHBoxLayout()
        
        demo_buttons = [
            ("Show 404", lambda: self.error_manager.simulate_http_error(404, demo_webview, demo_url="https://missing.com")),
            ("Show Captcha", lambda: self.error_manager.show_google_service_error("captcha", "Google", demo_webview)),
            ("Show Offline", lambda: self.error_manager.show_chrome_feature("offline", demo_webview)),
            ("API Stats", lambda: self.show_api_stats())
        ]
        
        for text, callback in demo_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            demo_layout.addWidget(btn)
        
        layout.addLayout(demo_layout)
        
        self.tab_widget.addTab(widget, "🔧 API Demo")
    
    def show_random_http_error(self, webview):
        """Show random HTTP error"""
        import random
        http_codes = [400, 401, 403, 404, 408, 429, 500, 502, 503, 504]
        error_code = random.choice(http_codes)
        self.error_manager.simulate_http_error(error_code, webview)
    
    def show_random_chrome_error(self, webview):
        """Show random Chrome error"""
        import random
        chrome_errors = ["ERR_INTERNET_DISCONNECTED", "ERR_CONNECTION_REFUSED", "ERR_NAME_NOT_RESOLVED", 
                        "ERR_SSL_PROTOCOL_ERROR", "ERR_TOO_MANY_REDIRECTS"]
        error_name = random.choice(chrome_errors)
        self.error_manager.simulate_chrome_error(error_name, webview)
    
    def show_random_google_error(self, webview):
        """Show random Google service error"""
        import random
        google_errors = ["quota_exceeded", "unusual_traffic", "access_denied", "captcha", "something_went_wrong"]
        error_name = random.choice(google_errors)
        self.error_manager.show_google_service_error(error_name, "Google", webview)
    
    def simulate_slow_connection(self, webview):
        """Simulate slow connection error"""
        # Simulate loading then timeout
        webview.setHtml("""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>🐌 Simulating Slow Connection...</h2>
            <p>This will timeout and show an error page.</p>
        </body>
        </html>
        """)
        
        QTimer.singleShot(2000, lambda: self.error_manager.simulate_chrome_error("ERR_CONNECTION_TIMED_OUT", "https://slow-site.com", webview))
    
    def simulate_connection_lost(self, webview):
        """Simulate connection lost"""
        self.error_manager.simulate_chrome_error("ERR_INTERNET_DISCONNECTED", "https://connected-site.com", webview)
    
    def simulate_dns_failure(self, webview):
        """Simulate DNS resolution failure"""
        self.error_manager.simulate_chrome_error("ERR_NAME_NOT_RESOLVED", "https://nonexistent-domain-12345.com", webview)
    
    def simulate_server_timeout(self, webview):
        """Simulate server timeout"""
        self.error_manager.simulate_chrome_error("ERR_CONNECTION_TIMED_OUT", "https://slow-api.com", webview)
    
    def simulate_mixed_errors(self, webview):
        """Simulate sequence of different errors"""
        errors = [
            ("ERR_CONNECTION_REFUSED", "https://server-down.com"),
            (404, "https://missing-page.com"),
            ("quota_exceeded", "Google"),
            ("ERR_INTERNET_DISCONNECTED", "https://any-site.com")
        ]
        
        self.current_error_index = 0
        self.error_sequence = errors
        
        def show_next_error():
            if self.current_error_index < len(self.error_sequence):
                error, target = self.error_sequence[self.current_error_index]
                
                if isinstance(error, int):
                    self.error_manager.simulate_http_error(error, target, webview)
                elif error in self.error_manager.google_service_errors:
                    self.error_manager.show_google_service_error(error, target, webview)
                else:
                    self.error_manager.simulate_chrome_error(error, target, webview)
                
                self.current_error_index += 1
                
                if self.current_error_index < len(self.error_sequence):
                    QTimer.singleShot(3000, show_next_error)
        
        show_next_error()
    
    def start_error_monitor(self, webview):
        """Start error monitoring demonstration"""
        if not hasattr(self, 'monitor_timer'):
            self.monitor_timer = QTimer()
            self.monitor_timer.timeout.connect(lambda: self.random_error_test(webview))
        
        self.monitor_timer.start(5000)  # Every 5 seconds
        print("🔍 Error monitoring started")
    
    def stop_error_monitor(self):
        """Stop error monitoring"""
        if hasattr(self, 'monitor_timer'):
            self.monitor_timer.stop()
            print("⏹️ Error monitoring stopped")
    
    def random_error_test(self, webview):
        """Random error for monitoring demo"""
        import random
        all_errors = [
            (400, "https://test-site.com"),
            ("ERR_CONNECTION_REFUSED", "https://api.example.com"),
            ("quota_exceeded", "Google Drive"),
            (503, "https://service-down.com"),
            ("ERR_INTERNET_DISCONNECTED", "https://offline-site.com")
        ]
        
        error, target = random.choice(all_errors)
        
        if isinstance(error, int):
            self.error_manager.simulate_http_error(error, target, webview)
        elif error in self.error_manager.google_service_errors:
            self.error_manager.show_google_service_error(error, target, webview)
        else:
            self.error_manager.simulate_chrome_error(error, target, webview)
    
    def show_api_stats(self):
        """Show API statistics"""
        stats = f"""
📊 Error Manager API Statistics

🗂️ Categories: 5
📄 Total Pages: {self.error_manager.get_available_errors_count()}
🔧 API Version: 1.0

Available Methods:
• show_error_page(error_code, **kwargs)
• simulate_http_error(code, url=None)
• simulate_chrome_error(name, url=None)  
• show_google_service_error(error, service=None)
• show_chrome_feature(feature)
• show_random_error()
• get_available_errors_count()
• list_all_error_pages()
• create_error_test_menu(parent)

Integration Complete! ✅
"""
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "API Statistics", stats)

# Example of how to integrate in other applications
def integrate_error_pages_in_any_app():
    """
    Example function showing how to integrate error pages in any PyQt application
    """
    
    # 1. Import the error manager
    from error_manager import ErrorPagesManager
    
    # 2. Create error manager (pass main window or parent widget)
    # error_manager = ErrorPagesManager(main_window)
    
    # 3. Handle webview load failures
    """
    def on_load_finished(webview, success):
        if not success:
            url = webview.url().toString()
            # Show appropriate error page
            error_manager.simulate_chrome_error("ERR_CONNECTION_REFUSED", url, webview)
    
    webview.page().loadFinished.connect(lambda success: on_load_finished(webview, success))
    """
    
    # 4. Handle specific errors programmatically
    """
    # HTTP errors
    error_manager.simulate_http_error(404, "https://missing.com")
    
    # Chrome errors
    error_manager.simulate_chrome_error("ERR_INTERNET_DISCONNECTED")
    
    # Google service errors
    error_manager.show_google_service_error("quota_exceeded", "YouTube")
    
    # Chrome features
    error_manager.show_chrome_feature("dino_game")
    """
    
    # 5. Add error pages to menu
    """
    error_menu = error_manager.create_error_test_menu(menu_bar)
    menu_bar.addMenu(error_menu)
    """
    
    pass

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Error Pages Integration Example")
    
    # Create and show integration example
    example_window = ErrorIntegrationExample()
    example_window.show()
    
    print("🔗 Error Pages Integration Example Started")
    print("=" * 60)
    print("This demonstrates how to integrate error pages in any Python application:")
    print()
    print("✅ HTTP Error Handling")
    print("✅ Chrome Error Simulation") 
    print("✅ Google Service Errors")
    print("✅ Network Error Monitoring")
    print("✅ Complete API Demonstration")
    print()
    print("See the code in test_error_pages.py for detailed examples")
    print("=" * 60)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()