#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Develer Browser v1.1.1 - Navigation Manager
Enhanced navigation with history, bookmarks, and search features
"""

import sys
import os
import json
import datetime
import re
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class NavigationManagerV1_1_1:
    """Enhanced navigation manager with full v1.1.1 features"""
    
    def __init__(self, browser_core):
        self.browser_core = browser_core
        self.version = "1.1.1"
        
        # Navigation state
        self.navigation_history = []
        self.bookmarks = browser_core.bookmarks
        self.passwords = browser_core.passwords
        self.settings = browser_core.settings
        
        # Search functionality
        self.search_history = []
        self.current_search_query = ""
        
        print(f"[NAV] Navigation Manager v{self.version} initialized")
    
    def create_navigation_widget(self):
        """Create enhanced navigation widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search bar with history
        search_widget = self.create_search_widget()
        layout.addWidget(search_widget)
        
        # Quick access buttons
        quick_access_widget = self.create_quick_access_widget()
        layout.addWidget(quick_access_widget)
        
        # Navigation controls
        nav_widget = self.create_navigation_controls()
        layout.addWidget(nav_widget)
        
        return widget
    
    def create_search_widget(self):
        """Create enhanced search widget with history"""
        search_group = QGroupBox("🔍 Enhanced Search")
        search_layout = QVBoxLayout(search_group)
        
        # Search input with autocomplete
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search web, bookmarks, history...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Search options
        search_options = QHBoxLayout()
        
        self.search_web_btn = QPushButton("Web")
        self.search_web_btn.setCheckable(True)
        self.search_web_btn.setChecked(True)
        
        self.search_bookmarks_btn = QPushButton("Bookmarks")
        self.search_bookmarks_btn.setCheckable(True)
        
        self.search_history_btn = QPushButton("History")
        self.search_history_btn.setCheckable(True)
        
        self.search_case_sensitive = QCheckBox("Case Sensitive")
        
        self.search_regex = QCheckBox("Regex")
        
        search_options.addWidget(self.search_web_btn)
        search_options.addWidget(self.search_bookmarks_btn)
        search_options.addWidget(self.search_history_btn)
        search_options.addWidget(self.search_case_sensitive)
        search_options.addWidget(self.search_regex)
        
        # Search button
        self.search_button = QPushButton("🔍 Search")
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        
        # Clear button
        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_btn)
        
        search_layout.addLayout(search_options)
        
        search_layout.setStretch(0, 1)
        
        search_layout.addLayout(search_options)
        
        search_group_layout = QVBoxLayout(search_group)
        search_group_layout.addLayout(search_layout)
        
        # Search results
        self.search_results = QListWidget()
        self.search_results.setAlternatingRowColors(True)
        self.search_results.itemDoubleClicked.connect(self.open_search_result)
        self.search_results.setMaximumHeight(200)
        
        search_group_layout.addWidget(QLabel("Search Results:"))
        search_group_layout.addWidget(self.search_results)
        
        search_group.setLayout(search_group_layout)
        
        return search_group
    
    def create_quick_access_widget(self):
        """Create quick access widget with favorites"""
        quick_group = QGroupBox("⚡ Quick Access")
        quick_layout = QVBoxLayout(quick_group)
        
        # Favorite bookmarks
        favorites_layout = QHBoxLayout()
        
        # Get top 5 most recent history items
        recent_history = self.get_recent_history_items(5)
        
        for item in recent_history:
            btn = self.create_quick_access_button(item)
            favorites_layout.addWidget(btn)
        
        favorites_layout.addStretch()
        
        # Bookmarks folders
        bookmarks_widget = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_widget)
        
        self.bookmarks_folders = self.get_bookmarks_folders()
        
        for folder_name, bookmarks in self.bookmarks_folders.items():
            if bookmarks:  # Only show folders with bookmarks
                folder_btn = QPushButton(f"📁 {folder_name} ({len(bookmarks)})")
                folder_btn.clicked.connect(lambda checked, f=folder_name: self.show_bookmark_folder(f))
                folder_btn.setStyleSheet("text-align: left; padding: 5px;")
                
                bookmarks_layout.addWidget(folder_btn)
        
        bookmarks_layout.addStretch()
        
        quick_layout.addWidget(QLabel("Recent:"))
        quick_layout.addLayout(favorites_layout)
        quick_layout.addWidget(QLabel("Folders:"))
        quick_layout.addWidget(bookmarks_widget)
        
        quick_group.setLayout(quick_layout)
        
        return quick_group
    
    def create_navigation_controls(self):
        """Create enhanced navigation controls"""
        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        
        # Standard navigation
        self.back_btn = QPushButton("←")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setToolTip("Go back")
        self.back_btn.setMinimumWidth(40)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setToolTip("Go forward")
        self.forward_btn.setMinimumWidth(40)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.clicked.connect(self.refresh_page)
        self.refresh_btn.setToolTip("Refresh page")
        self.refresh_btn.setMinimumWidth(40)
        
        self.home_btn = QPushButton("🏠")
        self.home_btn.clicked.connect(self.go_home)
        self.home_btn.setToolTip("Go to home page")
        self.home_btn.setMinimumWidth(40)
        
        # Navigation history
        self.history_btn = QPushButton("🕐")
        self.history_btn.clicked.connect(self.show_navigation_history)
        self.history_btn.setToolTip("Show navigation history")
        
        self.nav_history_btn = QPushButton("📜")
        self.nav_history_btn.clicked.connect(self.show_tab_history)
        self.nav_history_btn.setToolTip("Show tab history")
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.refresh_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.history_btn)
        nav_layout.addWidget(self.nav_history_btn)
        
        return nav_widget
    
    def create_quick_access_button(self, history_item):
        """Create quick access button for history item"""
        btn = QPushButton()
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Truncate text
        title = history_item.get('title', 'Untitled')[:30]
        url = history_item.get('url', '')
        if len(url) > 30:
            url = url[:27] + "..."
        
        btn.setText(f"{title}\n{url}")
        btn.setToolTip(f"{title}\n{url}\nClicked: {history_item.get('timestamp', '')}")
        btn.clicked.connect(lambda checked: self.navigate_to_url(url, title))
        
        return btn
    
    def on_search_text_changed(self, text):
        """Handle search text change for autocomplete"""
        if len(text) >= 2:
            suggestions = self.get_search_suggestions(text)
            # In a real implementation, would update a popup
            # For now, store current query
            self.current_search_query = text
    
    def get_search_suggestions(self, query):
        """Get search suggestions based on query"""
        suggestions = []
        
        # Bookmark suggestions
        for bookmark in self.bookmarks:
            if query.lower() in bookmark.get('title', '').lower():
                suggestions.append({
                    'type': 'bookmark',
                    'title': bookmark['title'],
                    'url': bookmark['url'],
                    'icon': '📁'
                })
            elif query.lower() in bookmark.get('url', '').lower():
                suggestions.append({
                    'type': 'bookmark',
                    'title': bookmark['title'],
                    'url': bookmark['url'],
                    'icon': '📁'
                })
        
        # History suggestions
        for item in self.navigation_history[:20]:  # Last 20 items
            if query.lower() in item.get('title', '').lower():
                suggestions.append({
                    'type': 'history',
                    'title': item['title'],
                    'url': item['url'],
                    'icon': '🕐',
                    'timestamp': item.get('timestamp', '')
                })
            elif query.lower() in item.get('url', '').lower():
                suggestions.append({
                    'type': 'history',
                    'title': item['title'],
                    'url': item['url'],
                    'icon': '🕐',
                    'timestamp': item.get('timestamp', '')
                })
        
        return suggestions
    
    def perform_search(self):
        """Perform comprehensive search"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.current_search_query = query
        self.search_history.insert(0, query)
        
        # Keep only last 50 searches
        self.search_history = self.search_history[:50]
        
        # Clear previous results
        self.search_results.clear()
        
        # Search options
        search_web = self.search_web_btn.isChecked()
        search_bookmarks = self.search_bookmarks_btn.isChecked()
        search_history = self.search_history_btn.isChecked()
        case_sensitive = self.search_case_sensitive.isChecked()
        use_regex = self.search_regex.isChecked()
        
        results = []
        
        # Search web
        if search_web:
            # In a real implementation, would search the web
            web_results = self.search_web_query(query)
            results.extend(web_results)
        
        # Search bookmarks
        if search_bookmarks:
            bookmark_results = self.search_bookmarks_query(query, case_sensitive, use_regex)
            results.extend(bookmark_results)
        
        # Search history
        if search_history:
            history_results = self.search_history_query(query, case_sensitive, use_regex)
            results.extend(history_results)
        
        # Display results
        self.display_search_results(results)
        
        print(f"[NAV] Search performed for: '{query}' - {len(results)} results found")
    
    def search_web_query(self, query):
        """Search the web (placeholder implementation)"""
        # In a real implementation, would use a search API
        # For now, create placeholder web search results
        web_results = []
        
        search_engines = [
            {
                'name': 'Google',
                'url': f"https://www.google.com/search?q={query}",
                'icon': '🌐'
            },
            {
                'name': 'Bing',
                'url': f"https://www.bing.com/search?q={query}",
                'icon': '🔍'
            },
            {
                'name': 'DuckDuckGo',
                'url': f"https://duckduckgo.com/?q={query}",
                'icon': '🦆'
            }
        ]
        
        for engine in search_engines:
            web_results.append({
                'type': 'web_search',
                'title': f"Search '{query}' on {engine['name']}",
                'url': engine['url'],
                'icon': engine['icon'],
                'engine': engine['name']
            })
        
        return web_results
    
    def search_bookmarks_query(self, query, case_sensitive=False, use_regex=False):
        """Search bookmarks"""
        results = []
        
        for bookmark in self.bookmarks:
            title = bookmark.get('title', '')
            url = bookmark.get('url', '')
            tags = bookmark.get('tags', [])
            
            match = False
            
            if use_regex:
                try:
                    pattern = re.compile(query, 0 if case_sensitive else re.IGNORECASE)
                    match = bool(pattern.search(title) or pattern.search(url))
                except re.error:
                    match = False
            else:
                if case_sensitive:
                    match = query in title or query in url
                else:
                    match = query.lower() in title.lower() or query.lower() in url.lower()
            
            if match:
                results.append({
                    'type': 'bookmark',
                    'title': title,
                    'url': url,
                    'tags': tags,
                    'icon': '📁',
                    'folder': bookmark.get('folder', 'Default')
                })
        
        return results
    
    def search_history_query(self, query, case_sensitive=False, use_regex=False):
        """Search navigation history"""
        results = []
        
        for item in self.navigation_history:
            title = item.get('title', '')
            url = item.get('url', '')
            timestamp = item.get('timestamp', '')
            
            match = False
            
            if use_regex:
                try:
                    pattern = re.compile(query, 0 if case_sensitive else re.IGNORECASE)
                    match = bool(pattern.search(title) or pattern.search(url))
                except re.error:
                    match = False
            else:
                if case_sensitive:
                    match = query in title or query in url
                else:
                    match = query.lower() in title.lower() or query.lower() in url.lower()
            
            if match:
                results.append({
                    'type': 'history',
                    'title': title,
                    'url': url,
                    'timestamp': timestamp,
                    'icon': '🕐'
                })
        
        return results
    
    def display_search_results(self, results):
        """Display search results"""
        self.search_results.clear()
        
        for result in results:
            icon = result.get('icon', '🔍')
            title = result.get('title', 'No title')
            url = result.get('url', '')
            extra_info = ""
            
            if result.get('type') == 'web_search':
                extra_info = f" - {result.get('engine', 'Search Engine')}"
            elif result.get('tags'):
                extra_info = f" - {', '.join(result['tags'])}"
            elif result.get('folder'):
                extra_info = f" - {result['folder']}"
            elif result.get('timestamp'):
                extra_info = f" - {result['timestamp'][:10]}"
            
            display_text = f"{icon} {title}{extra_info}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, result)
            self.search_results.addItem(item)
        
        self.search_results.setMaximumHeight(min(300, self.search_results.count() * 30))
    
    def clear_search(self):
        """Clear search"""
        self.search_input.clear()
        self.search_results.clear()
        self.current_search_query = ""
        print("[NAV] Search cleared")
    
    def open_search_result(self, item):
        """Open search result"""
        result = item.data(Qt.UserRole)
        
        if result:
            url = result.get('url', '')
            title = result.get('title', '')
            
            if url:
                self.navigate_to_url(url, title)
                
                # Add to navigation history if not already there
                self.add_to_navigation_history(url, title)
                
                # Close search if from search results
                # In a real implementation, could close search panel
                print(f"[NAV] Navigated to: {title} ({result.get('type')})")
    
    def get_recent_history_items(self, count=10):
        """Get recent history items"""
        return self.navigation_history[:count] if self.navigation_history else []
    
    def get_bookmarks_folders(self):
        """Get bookmarks organized by folders"""
        folders = {}
        
        for bookmark in self.bookmarks:
            folder = bookmark.get('folder', 'Default')
            
            if folder not in folders:
                folders[folder] = []
            
            folders[folder].append(bookmark)
        
        return folders
    
    def show_bookmark_folder(self, folder_name):
        """Show bookmarks from specific folder"""
        bookmarks = self.bookmarks_folders.get(folder_name, [])
        
        if not bookmarks:
            QMessageBox.information(self.browser_core.browser_windows[0] if self.browser_core.browser_windows else self, 
                                     "Bookmarks", f"Folder '{folder_name}' is empty.")
            return
        
        # In a real implementation, would show folder contents
        print(f"[NAV] Opening folder: {folder_name} ({len(bookmarks)} bookmarks)")
    
    def go_back(self):
        """Navigate back"""
        current_window = self.get_current_browser_window()
        if current_window and hasattr(current_window, 'go_back'):
            current_window.go_back()
            print("[NAV] Navigated back")
    
    def go_forward(self):
        """Navigate forward"""
        current_window = self.get_current_browser_window()
        if current_window and hasattr(current_window, 'go_forward'):
            current_window.go_forward()
            print("[NAV] Navigated forward")
    
    def refresh_page(self):
        """Refresh current page"""
        current_window = self.get_current_browser_window()
        if current_window and hasattr(current_window, 'refresh_page'):
            current_window.refresh_page()
            print("[NAV] Page refreshed")
    
    def go_home(self):
        """Navigate to home page"""
        home_url = self.browser_core.settings.get('home_page', 'https://www.google.com')
        self.navigate_to_url(home_url, "Home Page")
    
    def show_navigation_history(self):
        """Show navigation history dialog"""
        dialog = QDialog(self.browser_core.browser_windows[0] if self.browser_core.browser_windows else self)
        dialog.setWindowTitle("🕐 Navigation History")
        dialog.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Search bar for history
        search_layout = QHBoxLayout()
        
        self.history_search_input = QLineEdit()
        self.history_search_input.setPlaceholderText("Search history...")
        self.history_search_input.textChanged.connect(self.filter_history)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.history_search_input)
        layout.addLayout(search_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setAlternatingRowColors(True)
        self.populate_history_list()
        
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_navigation_history)
        clear_history_btn.setStyleSheet("background-color: #f44336; color: white;")
        
        export_history_btn = QPushButton("Export History")
        export_history_btn.clicked.connect(self.export_navigation_history)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(clear_history_btn)
        button_layout.addWidget(export_history_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def show_tab_history(self):
        """Show tab history dialog"""
        current_window = self.get_current_browser_window()
        
        if current_window and hasattr(current_window, 'tab_widget'):
            tabs = current_window.tab_widget
            
            # Get all tabs info
            all_tabs = []
            for i in range(tabs.count()):
                widget = tabs.widget(i)
                if hasattr(widget, 'url'):
                    all_tabs.append({
                        'index': i,
                        'title': tabs.tabText(i),
                        'url': widget.url().toString(),
                        'widget': widget
                    })
            
            if all_tabs:
                self.show_tab_history_dialog(all_tabs, current_window)
    
    def show_tab_history_dialog(self, tabs, current_window):
        """Show tab history dialog"""
        dialog = QDialog(current_window)
        dialog.setWindowTitle("📜 Tab History")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Tab list
        tab_list = QListWidget()
        tab_list.setAlternatingRowColors(True)
        
        for tab in tabs:
            item_text = f"Tab {tab['index']+1}: {tab['title']}\n{tab['url']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, tab)
            tab_list.addItem(item)
        
        tab_list.itemDoubleClicked.connect(lambda item: self.switch_to_tab(item.data(Qt.UserRole), current_window))
        
        layout.addWidget(tab_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_current_btn = QPushButton("Close Current")
        close_current_btn.clicked.connect(lambda: current_window.tab_widget.removeTab(current_window.tab_widget.currentIndex()))
        
        close_others_btn = QPushButton("Close Others")
        close_others_btn.clicked.connect(lambda: self.close_other_tabs(current_window))
        
        restore_all_btn = QPushButton("Restore All")
        restore_all_btn.clicked.connect(lambda: self.restore_all_closed_tabs(current_window, tabs))
        
        button_layout.addWidget(close_current_btn)
        button_layout.addWidget(close_others_btn)
        button_layout.addWidget(restore_all_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def switch_to_tab(self, tab, current_window):
        """Switch to specific tab"""
        current_window.tab_widget.setCurrentWidget(tab['widget'])
        print(f"[NAV] Switched to tab {tab['index']+1}: {tab['title']}")
    
    def close_other_tabs(self, current_window):
        """Close all tabs except current"""
        current_index = current_window.tab_widget.currentIndex()
        
        while current_window.tab_widget.count() > current_index + 1:
            current_window.tab_widget.removeTab(current_index + 1)
    
    def restore_all_closed_tabs(self, current_window, tabs):
        """Restore all closed tabs"""
        # In a real implementation, would reopen closed tabs
        print(f"[NAV] Restoring {len(tabs)} closed tabs")
    
    def filter_history(self, text):
        """Filter history based on search text"""
        self.populate_history_list(text)
    
    def populate_history_list(self, filter_text=""):
        """Populate history list with optional filter"""
        self.history_list.clear()
        
        for item in reversed(self.navigation_history):
            title = item.get('title', 'No title')
            url = item.get('url', '')
            timestamp = item.get('timestamp', '')
            
            if filter_text and filter_text.lower() not in title.lower() and filter_text.lower() not in url.lower():
                continue
            
            # Format: Title - URL - Date
            date_str = timestamp[:10] if timestamp else "Unknown"
            item_text = f"{title}\n{url}\nVisited: {date_str}"
            
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, item)
            
            # Set color based on recency
            if self.is_recent_history_item(item):
                list_item.setBackground(QColor("#e8f5e8"))
            
            self.history_list.addItem(list_item)
    
    def is_recent_history_item(self, item):
        """Check if history item is recent (last 7 days)"""
        try:
            timestamp_str = item.get('timestamp', '')
            if timestamp_str:
                item_date = datetime.datetime.fromisoformat(timestamp_str)
                return (datetime.datetime.now() - item_date).days <= 7
        except:
            return False
        return False
    
    def clear_navigation_history(self):
        """Clear navigation history"""
        reply = QMessageBox.question(
            self.browser_core.browser_windows[0] if self.browser_core.browser_windows else self,
            "Clear History",
            "Are you sure you want to clear all browsing history? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.navigation_history = []
            self.browser_core.save_history()
            self.populate_history_list()
            QMessageBox.information(self, "History Cleared", "Navigation history has been cleared.")
            print("[NAV] Navigation history cleared")
    
    def export_navigation_history(self):
        """Export navigation history"""
        if not self.navigation_history:
            QMessageBox.information(self, "Export History", "No history to export.")
            return
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"navigation_history_v1.1.1_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.navigation_history, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "History Exported", f"History exported to:\n{filename}")
            print(f"[NAV] History exported to: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export history:\n{e}")
    
    def navigate_to_url(self, url, title=None):
        """Navigate to URL and add to history"""
        if not url or url == "about:blank":
            return
        
        # Add to history
        self.add_to_navigation_history(url, title)
        
        # Navigate
        current_window = self.get_current_browser_window()
        if current_window and hasattr(current_window, 'navigate_to_url'):
            current_window.navigate_to_url(url)
    
    def add_to_navigation_history(self, url, title=None):
        """Add URL to navigation history"""
        if url and url != "about:blank":
            history_item = {
                'url': url,
                'title': title or 'Untitled',
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            self.navigation_history.insert(0, history_item)
            
            # Keep only last 1000 items
            self.navigation_history = self.navigation_history[:1000]
            self.browser_core.save_history()
    
    def get_current_browser_window(self):
        """Get current browser window"""
        if self.browser_core.browser_windows:
            return self.browser_core.browser_windows[0]
        return None