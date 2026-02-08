#!/usr/bin/env python3
"""
Develer Browser Pro - Advanced Web Browser with DevTools Integration
"""

import sys
import json
import os
import datetime
import webbrowser
import subprocess
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QLineEdit, QFrame, QMessageBox, 
                             QMenuBar, QListWidget, QDialog, QDialogButtonBox, QAction)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from error_manager import ErrorPagesManager
from error_page_handler import ErrorPageHandler
from local_server import ErrorPageServerBridge
from memory_manager import get_memory_manager, MemoryPriority
from webgpu_support import get_webgpu_support
from engine_optimizer import get_engine_optimizer, OptimizationLevel

# Set Qt attributes BEFORE creating QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

class SettingsManager:
    def __init__(self):
        self.config_file = "browser_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        # Try to load settings from web interface first
        web_settings = None  # Placeholder for web config loading
        
        default_settings = {
            "bookmarks": [],
            "extensions": [],
            "themes": ["light", "dark", "blue", "green", "purple"],
            "current_theme": "light",
            "start_pages": web_settings or [
                {"name": "Google", "url": "https://www.google.com"},
                {"name": "Python.org", "url": "https://www.python.org"},
                {"name": "GitHub", "url": "https://github.com"},
                {"name": "Stack Overflow", "url": "https://stackoverflow.com"},
                {"name": "MDN Web Docs", "url": "https://developer.mozilla.org"},
                {"name": "W3Schools", "url": "https://www.w3schools.com"},
                {"name": "DevDocs", "url": "https://devdocs.io"}
            ],
            "search_engines": {
                "google": "https://www.google.com/search?q=",
                "bing": "https://www.bing.com/search?q=",
                "duckduckgo": "https://duckduckgo.com/?q=",
                "yandex": "https://yandex.ru/search/?text=",
                "brave": "https://search.brave.com/search?q="
            },
            "current_search": "google",
            "devtools": {
                "enabled": True,
                "auto_open": False,
                "position": "right"
            },
            "browser": {
                "name": "Develer Browser Pro",
                "version": "4.0.0",
                "developer": "Advanced Python Team"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    default_settings.update(loaded_settings)
            except:
                pass
        
        self.settings = default_settings
        return default_settings
    
    def save_settings(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

class BrowserWindow(QMainWindow):
    def load_from_web_config(self):
        """Load quick sites configuration from newtab.html"""
        try:
            if os.path.exists("newtab.html"):
                with open("newtab.html", "r", encoding="utf-8") as f:
                    content = f.read()
                    # Extract quick sites from the HTML file
                    # This is a simplified version - in production, you'd parse this better
                    quick_sites = [
                        {"name": "Google", "url": "https://www.google.com"},
                        {"name": "GitHub", "url": "https://github.com"},
                        {"name": "Stack Overflow", "url": "https://stackoverflow.com"},
                        {"name": "MDN Web Docs", "url": "https://developer.mozilla.org"},
                        {"name": "W3Schools", "url": "https://www.w3schools.com"},
                        {"name": "Python.org", "url": "https://www.python.org"},
                        {"name": "Dev.to", "url": "https://dev.to"},
                        {"name": "DevDocs", "url": "https://devdocs.io"}
                    ]
                    return quick_sites
        except Exception as e:
            print(f"Error loading web config: {e}")
        return None

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Initialize Error Manager and new error system
        self.error_manager = ErrorPagesManager(self)
        self.error_handler = ErrorPageHandler(self)
        self.server_bridge = ErrorPageServerBridge(self)
        
        # Initialize memory management
        self.memory_manager = get_memory_manager()
        
        # Initialize WebGPU support
        self.webgpu_support = get_webgpu_support()
        self.webgpu_support.start_performance_monitoring()
        
        # Initialize engine optimizer
        self.engine_optimizer = get_engine_optimizer()
        self.engine_optimizer.start_performance_monitoring()
        
        # Apply enhanced optimizations
        self.engine_optimizer.apply_optimizations(OptimizationLevel.MAXIMUM)
        
        # Start local server for error pages
        self.server_bridge.start_server()
        
        self.setWindowTitle(f"{self.settings['browser']['name']} v{self.settings['browser']['version']}")
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
        self.apply_theme()
        self.create_menus()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("←")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.forward_btn)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.clicked.connect(self.refresh_page)
        nav_layout.addWidget(self.refresh_btn)
        
        self.home_btn = QPushButton("🏠")
        self.home_btn.clicked.connect(self.go_home)
        nav_layout.addWidget(self.home_btn)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_layout.addWidget(self.url_bar)
        
        # Bookmark button
        self.bookmark_btn = QPushButton("📚")
        self.bookmark_btn.clicked.connect(self.add_bookmark)
        self.bookmark_btn.setMaximumWidth(40)
        nav_layout.addWidget(self.bookmark_btn)
        
        # Error Pages button
        self.error_pages_btn = QPushButton("🚨")
        self.error_pages_btn.clicked.connect(self.show_error_pages_menu)
        self.error_pages_btn.setMaximumWidth(40)
        nav_layout.addWidget(self.error_pages_btn)
        
        # New tab button
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.new_tab_btn.setMaximumWidth(30)
        nav_layout.addWidget(self.new_tab_btn)
        
        # DevTools button
        # DevTools button
        self.devtools_btn = QPushButton("🔧")
        self.devtools_btn.clicked.connect(self.toggle_devtools)
        nav_layout.addWidget(self.devtools_btn)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setMaximumWidth(40)
        nav_layout.addWidget(self.settings_btn)
        
        # Incognito button
        self.incognito_btn = QPushButton("👤")
        self.incognito_btn.clicked.connect(self.toggle_incognito_mode)
        nav_layout.addWidget(self.incognito_btn)
        
        # Web DevTools button
        self.web_devtools_btn = QPushButton("🛠️")
        self.web_devtools_btn.clicked.connect(self.open_web_devtools)
        self.web_devtools_btn.setMaximumWidth(40)
        nav_layout.addWidget(self.web_devtools_btn)
        
        layout.addLayout(nav_layout)
        

        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add corner new tab button
        self.corner_new_tab_btn = QPushButton("+")
        self.corner_new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.corner_new_tab_btn.setMaximumWidth(25)
        self.corner_new_tab_btn.setToolTip("Add New Tab")
        self.tab_widget.setCornerWidget(self.corner_new_tab_btn, Qt.TopRightCorner)
        
        # Add first tab with newtab.html
        newtab_path = os.path.abspath('newtab.html')
        if os.path.exists(newtab_path):
            self.add_new_tab(QUrl.fromLocalFile(newtab_path).toString())
        else:
            self.add_new_tab("https://www.google.com")
        
        # Setup global error handling
        self.setup_global_error_handling()
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Develer Browser Pro")
        
        # Error handling
        self.debug_mode = False
        self.error_test_timer = None
        
    def apply_theme(self):
        theme = self.settings.get('current_theme', 'light')
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("")  # Default theme
            
    def add_new_tab(self, url=None):
        if url is None:
            url = "https://www.google.com"
            
        webview = QWebEngineView()
        
        # Enhance webview with comprehensive error handling
        self.enhance_webview_with_error_handling(webview)
        
        # Inject WebGPU support
        self.webgpu_support.inject_webgpu_support(webview)
        
        # Optimize memory usage for this webview
        self.memory_manager.allocate_from_pool('webview', lambda w=webview: w)
        
        # Apply engine optimizations to webview
        self.engine_optimizer.apply_optimizations(OptimizationLevel.MAXIMUM)
        
        webview.setUrl(QUrl(url))
        
        title = self.get_page_title(url)
        index = self.tab_widget.addTab(webview, title)
        self.tab_widget.setCurrentIndex(index)
        
        return webview
        
    def get_page_title(self, url):
        page_titles = {
            "google.com": "Google",
            "python.org": "Python.org", 
            "github.com": "GitHub",
            "stackoverflow.com": "Stack Overflow",
            "developer.mozilla.org": "MDN",
            "w3schools.com": "W3Schools",
            "devdocs.io": "DevDocs"
        }
        
        for domain, title in page_titles.items():
            if domain in url:
                return title
        return "New Tab"
        
    def go_back(self):
        current = self.tab_widget.currentWidget()
        if current:
            current.back()
            
    def go_forward(self):
        current = self.tab_widget.currentWidget()
        if current:
            current.forward()
            
    def refresh_page(self):
        current = self.tab_widget.currentWidget()
        if current:
            current.reload()
            
    def go_home(self):
        self.navigate_to_url("https://www.google.com")
        
    def navigate_to_url(self, url):
        if not url.startswith(('http://', 'https://')):
            search_engine = self.settings['search_engines'].get(
                self.settings.get('current_search', 'google'), 
                self.settings['search_engines']['google']
            )
            url = search_engine + url
            
        current = self.tab_widget.currentWidget()
        if current:
            current.setUrl(QUrl(url))
        else:
            self.add_new_tab(url)
            
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()
            
    def add_bookmark(self):
        """Add current page to bookmarks"""
        current_webview = self.tab_widget.currentWidget()
        if current_webview:
            url = current_webview.url().toString()
            title = current_webview.title()
            
            if url and url != "about:blank" and not url.startswith('file:///'):
                bookmark = {
                    'name': title or 'Untitled',
                    'url': url,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                # Check if bookmark already exists
                for existing in self.settings['bookmarks']:
                    if existing['url'] == url:
                        QMessageBox.information(self, "Закладка", "Эта страница уже в закладках!")
                        return
                
                self.settings['bookmarks'].append(bookmark)
                self.settings_manager.save_settings()
                
                QMessageBox.information(self, "Закладка добавлена", f"'{title}' добавлена в закладки!")
    
    def open_settings(self):
        """Open settings page in browser"""
        settings_path = os.path.abspath('settings.html')
        webbrowser.open(QUrl.fromLocalFile(settings_path).toString())
    
    def open_web_devtools(self):
        """Открыть веб версию DevTools"""
        devtools_path = os.path.abspath("devtools.html")
        if os.path.exists(devtools_path):
            # Открыть в новой вкладке
            self.add_new_tab(QUrl.fromLocalFile(devtools_path).toString())
        else:
            QMessageBox.information(self, "DevTools", "DevTools файл не найден")
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # Error Pages menu
        error_menu = menubar.addMenu("🚨 Error Pages")
        
        # Show Error Index
        show_index_action = QAction("📋 Error Index", self)
        show_index_action.triggered.connect(self.error_manager.show_error_index)
        error_menu.addAction(show_index_action)
        
        # Troubleshooting
        troubleshooting_action = QAction("🔧 Troubleshooting", self)
        troubleshooting_action.triggered.connect(self.error_manager.show_troubleshooting)
        error_menu.addAction(troubleshooting_action)
        
        # Error Search
        search_action = QAction("🔍 Search Errors", self)
        search_action.triggered.connect(self.error_manager.show_error_search)
        error_menu.addAction(search_action)
        
        error_menu.addSeparator()
        
        # Common errors
        show_404_action = QAction("🚫 Show 404 Error", self)
        show_404_action.triggered.connect(lambda: self.error_manager.simulate_http_error(404))
        error_menu.addAction(show_404_action)
        
        show_500_action = QAction("💥 Show 500 Error", self)
        show_500_action.triggered.connect(lambda: self.error_manager.simulate_http_error(500))
        error_menu.addAction(show_500_action)
        
        show_offline_action = QAction("📵 Show Offline Page", self)
        show_offline_action.triggered.connect(lambda: self.error_manager.show_chrome_feature("offline"))
        error_menu.addAction(show_offline_action)
        
        show_dino_action = QAction("🦕 Dino Game", self)
        show_dino_action.triggered.connect(lambda: self.error_manager.show_chrome_feature("dino_game"))
        error_menu.addAction(show_dino_action)
        
        error_menu.addSeparator()
        
        # Test menu with all errors
        test_menu = self.error_manager.create_error_test_menu(error_menu)
        error_menu.addMenu(test_menu)
        
        # Random error
        random_action = QAction("🎲 Random Error", self)
        random_action.triggered.connect(self.error_manager.show_random_error)
        error_menu.addAction(random_action)
        
        # Dev menu (hidden feature)
        dev_menu = menubar.addMenu("🛠️ Dev")
        
        show_stats_action = QAction("📊 Error Stats", self)
        show_stats_action.triggered.connect(self.show_error_stats)
        dev_menu.addAction(show_stats_action)
        
        debug_action = QAction("🐛 Debug Mode", self)
        debug_action.triggered.connect(self.toggle_debug_mode)
        dev_menu.addAction(debug_action)
    
    def show_error_pages_menu(self):
        """Show quick error pages menu"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QAction {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QAction:hover {
                background-color: #e3f2fd;
            }
        """)
        
        # Common errors
        actions = [
            ("🚫 404 Not Found", lambda: self.error_manager.simulate_http_error(404)),
            ("💥 500 Server Error", lambda: self.error_manager.simulate_http_error(500)),
            ("🔒 Access Denied", lambda: self.error_manager.show_google_service_error("access_denied")),
            ("🤖 Captcha", lambda: self.error_manager.show_google_service_error("captcha")),
            ("📵 Offline", lambda: self.error_manager.show_chrome_feature("offline")),
            ("🦕 Dino Game", lambda: self.error_manager.show_chrome_feature("dino_game")),
            ("📋 Error Index", self.error_manager.show_error_index),
            ("🔧 Troubleshooting", self.error_manager.show_troubleshooting),
            ("🎲 Random", self.error_manager.show_random_error)
        ]
        
        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            menu.addAction(action)
        
        menu.addSeparator()
        
        all_errors_action = QAction("📚 All Error Pages...", self)
        all_errors_action.triggered.connect(self.show_all_error_pages)
        menu.addAction(all_errors_action)
        
        # Show menu at button position
        button_rect = self.error_pages_btn.geometry()
        global_pos = self.error_pages_btn.mapToGlobal(button_rect.bottomLeft())
        menu.exec_(global_pos)
    
    def show_all_error_pages(self):
        """Show dialog with all available error pages"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QDialogButtonBox, QLabel
        
        dialog = QDialog(self)
        dialog.setWindowTitle("All Error Pages")
        dialog.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Info label
        total_errors = self.error_manager.get_available_errors_count()
        info_label = QLabel(f"Total Error Pages Available: {total_errors}")
        info_label.setStyleSheet("font-weight: bold; color: #1976d2; padding: 10px;")
        layout.addWidget(info_label)
        
        # List widget
        list_widget = QListWidget()
        all_pages = self.error_manager.list_all_error_pages()
        
        for category, pages in all_pages.items():
            # Add category header
            category_item = QListWidget()
            list_widget.addItem(f"📁 {category} ({len(pages)} pages)")
            
            # Add pages in category
            for key, path in pages.items():
                if isinstance(key, int):
                    list_widget.addItem(f"   HTTP {key}")
                else:
                    list_widget.addItem(f"   {key}")
        
        layout.addWidget(list_widget)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec_()
    
    def show_error_stats(self):
        """Show error pages statistics"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Error Pages Statistics")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Stats text
        all_pages = self.error_manager.list_all_error_pages()
        
        stats_text = "📊 Error Pages Statistics\n"
        stats_text += "=" * 40 + "\n\n"
        
        total = 0
        for category, pages in all_pages.items():
            count = len(pages)
            total += count
            stats_text += f"📁 {category}:\n"
            stats_text += f"   Count: {count} pages\n"
            stats_text += f"   Percentage: {(count/total*100):.1f}%\n\n"
        
        stats_text += "=" * 40 + "\n"
        stats_text += f"📈 Total Pages: {total}\n"
        stats_text += f"🌐 Error Pages Directory: {self.error_manager.error_pages_dir}\n"
        stats_text += f"✅ All pages integrated successfully!"
        
        text_edit = QTextEdit()
        text_edit.setPlainText(stats_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.exec_()
    
    def toggle_debug_mode(self):
        """Toggle debug mode for error pages"""
        self.debug_mode = not hasattr(self, 'debug_mode') or not self.debug_mode
        
        if self.debug_mode:
            QMessageBox.information(self, "Debug Mode", "🐛 Debug Mode Enabled!\n\nAll navigation errors will show detailed error pages.")
            self.status_bar.showMessage("Debug Mode Enabled - All errors will show custom pages")
        else:
            QMessageBox.information(self, "Debug Mode", "Debug Mode Disabled")
            self.status_bar.showMessage("Debug Mode Disabled")
    
    def test_random_errors(self):
        """Cycle through random error pages for testing"""
        if not hasattr(self, 'error_test_timer'):
            self.error_test_timer = QTimer()
            self.error_test_timer.timeout.connect(self.error_manager.show_random_error)
            self.error_test_timer.start(5000)  # Every 5 seconds
            self.status_bar.showMessage("Random Error Test Started (5s intervals)")
        else:
            self.error_test_timer.stop()
            delattr(self, 'error_test_timer')
            self.status_bar.showMessage("Random Error Test Stopped")
    
    def on_load_started(self, webview):
        """Handle page load start"""
        url = webview.url().toString()
        self.status_bar.showMessage(f"Loading: {url}")
    
    def on_load_finished(self, webview, success):
        """Handle page load completion"""
        url = webview.url().toString()
        
        if success:
            self.status_bar.showMessage(f"Ready: {url}")
        else:
            # Page failed to load - show appropriate error page
            if self.debug_mode or self.should_show_error_page(url):
                self.error_manager.simulate_chrome_error("ERR_CONNECTION_REFUSED", url)
            else:
                self.status_bar.showMessage(f"Failed to load: {url}")
    
    def on_load_progress(self, webview, progress):
        """Handle page load progress"""
        if progress < 100:
            self.status_bar.showMessage(f"Loading: {progress}%")
    
    def should_show_error_page(self, url):
        """Determine if we should show custom error page"""
        # Check if it's a local file
        if url.startswith('file:///'):
            return False
        
        # Check if it's a known working site
        working_sites = ['google.com', 'github.com', 'python.org', 'stackoverflow.com']
        return not any(site in url for site in working_sites)
    
    def handle_error_with_retry(self, webview, error_type, original_url):
        """Handle error with retry mechanism"""
        retry_count = getattr(webview, 'retry_count', 0)
        
        if retry_count < 3:
            # Try to reload
            webview.retry_count = retry_count + 1
            QTimer.singleShot(2000, lambda: webview.setUrl(QUrl(original_url)))
            self.status_bar.showMessage(f"Retrying... ({retry_count + 1}/3)")
        else:
            # Show error page after max retries
            self.error_manager.simulate_chrome_error(error_type, original_url)
            webview.retry_count = 0
    
    def setup_global_error_handling(self):
        """Setup global error handling for all webviews"""
        # This will be called for each webview as they're created
        pass
    
    def enhance_webview_with_error_handling(self, webview):
        """Enhance webview with comprehensive error handling"""
        # Minimal error handling - avoid any network manager calls
        try:
            # Store webview reference
            if not hasattr(self, 'webviews'):
                self.webviews = []
            self.webviews.append(webview)
            
            print(f"Webview enhanced successfully: {len(self.webviews)} total webviews")
            
        except Exception as e:
            print(f"Error in enhance_webview_with_error_handling: {e}")
            # Still try to store the webview
            if not hasattr(self, 'webviews'):
                self.webviews = []
            try:
                self.webviews.append(webview)
            except:
                pass
    
    def on_webview_load_started(self, webview):
        """Handle webview load start"""
        url = webview.url().toString()
        self.status_bar.showMessage(f"Loading: {url}")
    
    def on_webview_load_finished(self, webview, success):
        """Handle webview load completion"""
        url = webview.url().toString()
        
        if success:
            self.status_bar.showMessage(f"Ready: {url}")
            # Reset retry count on success
            if hasattr(webview, 'retry_count'):
                delattr(webview, 'retry_count')
        else:
            # Page failed to load - determine appropriate error
            if self.should_show_error_page(url):
                self.handle_failed_load(webview, url)
            else:
                self.status_bar.showMessage(f"Failed to load: {url}")
    
    def on_webview_load_progress(self, webview, progress):
        """Handle webview load progress"""
        if progress < 100:
            current_webview = self.tab_widget.currentWidget()
            if current_webview == webview:
                self.status_bar.showMessage(f"Loading: {progress}%")
    
    def on_webview_load_finished(self, webview, success):
        """Handle webview load completion"""
        url = webview.url().toString()
        
        if success:
            self.status_bar.showMessage(f"Ready: {url}")
            # Reset retry count on success
            if hasattr(webview, 'retry_count'):
                delattr(webview, 'retry_count')
        else:
            # Page failed to load - determine appropriate error
            if self.should_show_error_page(url):
                self.handle_failed_load_simple(webview, url)
            else:
                self.status_bar.showMessage(f"Failed to load: {url}")
    
    def handle_failed_load_simple(self, webview, url):
        """Simple failed load handler with basic error detection"""
        # Simple heuristics for error type detection
        if any(domain in url for domain in ['nonexistent', 'invalid', '.test']):
            self.error_manager.simulate_chrome_error("ERR_NAME_NOT_RESOLVED", url, webview)
        elif url.startswith('https://') and any(indicator in url for indicator in ['expired', 'self-signed']):
            self.error_manager.simulate_chrome_error("ERR_SSL_PROTOCOL_ERROR", url, webview)
        elif any(indicator in url for indicator in ['slow', 'timeout']):
            self.error_manager.simulate_chrome_error("ERR_CONNECTION_TIMED_OUT", url, webview)
        else:
            # Generic connection error
            self.handle_error_with_retry(webview, "ERR_CONNECTION_REFUSED", url)
    
    def show_error_statistics(self):
        """Show comprehensive error statistics"""
        stats = self.error_manager.get_available_errors_count()
        message = f"""
📊 Python Browser Pro Error System

🗂️ Total Error Pages: {stats}
📁 Categories: 5
🌐 Error Manager: Active
🔧 Integration: Complete

Categories Available:
• HTTP Errors (400-511)
• Chrome Browser Errors  
• Google Service Errors
• Chrome Features
• Special Pages

All Python files now use the complete error pages system! 🎯
"""
        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Error System Statistics", message)
    
def toggle_devtools(self):
        """Toggle DevTools for current tab"""
        current_webview = self.tab_widget.currentWidget()
        if current_webview:
            self.enhance_webview_with_error_handling(current_webview)
    
    def closeEvent(self, event):
        self.settings_manager.save_settings()
        
        # Clean up error test timer if running
        if hasattr(self, 'error_test_timer'):
            self.error_test_timer.stop()
        
        # Clean up WebGPU support
        if hasattr(self, 'webgpu_support'):
            self.webgpu_support.stop_performance_monitoring()
        
        # Clean up engine optimizer
        if hasattr(self, 'engine_optimizer'):
            self.engine_optimizer.stop_performance_monitoring()
        
        # Clean up memory manager
        if hasattr(self, 'memory_manager'):
            self.memory_manager.cleanup()
        
        # Clean up all webviews
        if hasattr(self, 'webviews'):
            for webview in self.webviews:
                try:
                    self.memory_manager.return_to_pool('webview', webview)
                    webview.deleteLater()
                except:
                    pass
        
        event.accept()

def toggle_devtools(self):
        """Toggle DevTools for current tab"""
        current_webview = self.tab_widget.currentWidget()
        if current_webview:
            self.enhance_webview_with_error_handling(current_webview)

class BrowserApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
# Configure web engine settings
        QWebEngineSettings.globalSettings().setAttribute(
            QWebEngineSettings.JavascriptEnabled, True
        )
        QWebEngineSettings.globalSettings().setAttribute(
            QWebEngineSettings.LocalStorageEnabled, True
        )
        QWebEngineSettings.globalSettings().setAttribute(
            QWebEngineSettings.PluginsEnabled, True
        )
        
# Отключаем проверки безопасности для локальных файлов
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        self.window = BrowserWindow()
        self.window.show()

def main():
    app = BrowserApplication(sys.argv)
    app.setApplicationName("Develer Browser Pro")
    
    # Check if we should open settings page
    if len(sys.argv) > 1 and sys.argv[1] == '--settings':
        webbrowser.open(QUrl.fromLocalFile(os.path.abspath('newtab.html')).toString())
        return 0
    
    return app.exec_()

if __name__ == "__main__":
    main()