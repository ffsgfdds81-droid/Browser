# -*- coding: utf-8 -*-
"""
Enhanced New Tab Page with quick access and customization
"""

import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
import webbrowser

class NewTabPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Новая вкладка")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Settings
        self.settings_file = 'data/newtab_settings.json'
        self.settings = self.load_settings()
        
        self.init_ui()
        self.setStyleSheet(self.get_style())
        
    def load_settings(self):
        """Load new tab settings"""
        default_settings = {
            'background_color': '#ffffff',
            'show_clock': True,
            'show_search': True,
            'show_quick_access': True,
            'quick_sites': [
                {'title': 'Google', 'url': 'https://www.google.com', 'icon': '🔍'},
                {'title': 'YouTube', 'url': 'https://www.youtube.com', 'icon': '📺'},
                {'title': 'GitHub', 'url': 'https://github.com', 'icon': '💻'},
                {'title': 'Stack Overflow', 'url': 'https://stackoverflow.com', 'icon': '📚'}
            ]
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_settings
        return default_settings
    
    def save_settings(self):
        """Save new tab settings"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)
        
        # Clock and Date
        if self.settings['show_clock']:
            content_layout.addWidget(self.create_clock_widget())
        
        # Search Bar
        if self.settings['show_search']:
            content_layout.addWidget(self.create_search_widget())
        
        # Quick Access Sites
        if self.settings['show_quick_access']:
            content_layout.addWidget(self.create_quick_access_widget())
        
        # Recent History
        content_layout.addWidget(self.create_recent_history_widget())
        
        # Bookmarks
        content_layout.addWidget(self.create_bookmarks_widget())
        
        # Settings Button
        content_layout.addWidget(self.create_settings_widget())
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
        # Update clock every second
        if self.settings['show_clock']:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_clock)
            self.timer.start(1000)
    
    def create_clock_widget(self):
        """Create clock and date widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: 300;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        
        self.date_label = QLabel()
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
        """)
        self.date_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        widget.setLayout(layout)
        
        self.update_clock()
        return widget
    
    def update_clock(self):
        """Update clock display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %d %B %Y")
        
        self.time_label.setText(time_str)
        self.date_label.setText(date_str)
    
    def create_search_widget(self):
        """Create search widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите поисковый запрос или URL...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                background-color: #f8f9fa;
                min-width: 500px;
            }
            QLineEdit:focus {
                border-color: #4285f4;
                background-color: white;
            }
        """)
        
        self.search_input.returnPressed.connect(self.handle_search)
        
        layout.addWidget(self.search_input)
        widget.setLayout(layout)
        return widget
    
    def handle_search(self):
        """Handle search or URL input"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        # Check if it's a URL
        if query.startswith(('http://', 'https://', 'www.')) or '.' in query:
            if not query.startswith(('http://', 'https://')):
                url = 'https://' + query
            else:
                url = query
        else:
            # Search query
            url = f'https://www.google.com/search?q={query}'
        
        # Open in parent browser
        if self.parent:
            self.parent.add_new_tab(url)
        else:
            webbrowser.open(url)
        
        self.close()
    
    def create_quick_access_widget(self):
        """Create quick access sites widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Быстрый доступ")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Sites grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        for i, site in enumerate(self.settings['quick_sites']):
            btn = self.create_site_button(site)
            row = i // 4
            col = i % 4
            grid_layout.addWidget(btn, row, col)
        
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        layout.addWidget(grid_widget)
        
        widget.setLayout(layout)
        return widget
    
    def create_site_button(self, site):
        """Create a site button for quick access"""
        btn = QPushButton()
        btn.setFixedSize(140, 140)
        btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #4285f4;
                transform: translateY(-2px);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel(site.get('icon', '🌐'))
        icon_label.setStyleSheet("font-size: 32px; margin-bottom: 8px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel(site['title'])
        title_label.setStyleSheet("color: #2c3e50; font-weight: 500;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        btn.setLayout(layout)
        
        btn.clicked.connect(lambda: self.open_site(site['url']))
        return btn
    
    def open_site(self, url):
        """Open site in browser"""
        if self.parent:
            self.parent.add_new_tab(url)
        else:
            webbrowser.open(url)
    
    def create_recent_history_widget(self):
        """Create recent history widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Недавние страницы")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Get recent history
        history_items = self.get_recent_history()
        
        if history_items:
            for item in history_items:
                item_widget = self.create_history_item(item)
                layout.addWidget(item_widget)
        else:
            no_history = QLabel("Нет недавних страниц")
            no_history.setStyleSheet("color: #7f8c8d; font-style: italic; margin: 20px;")
            layout.addWidget(no_history)
        
        widget.setLayout(layout)
        return widget
    
    def get_recent_history(self):
        """Get recent history items"""
        if os.path.exists('data/history.json'):
            try:
                with open('data/history.json', 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history[-5:] if history else []
            except:
                pass
        return []
    
    def create_history_item(self, item):
        """Create a history item widget"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Title
        title = QLabel(item.get('title', item['url']))
        title.setStyleSheet("color: #2c3e50; font-size: 14px;")
        title.setMaximumWidth(400)
        title.setWordWrap(True)
        
        # URL
        url = QLabel(item['url'])
        url.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        url.setMaximumWidth(300)
        
        # Time
        time_str = item.get('visit_time', '')
        if time_str:
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
            layout.addWidget(time_label)
        
        layout.addWidget(title)
        layout.addWidget(url)
        layout.addStretch()
        
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                padding: 10px;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #f8f9fa;
                cursor: pointer;
            }
        """)
        
        # Make clickable
        widget.mousePressEvent = lambda e: self.open_site(item['url'])
        
        return widget
    
    def create_bookmarks_widget(self):
        """Create bookmarks widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Закладки")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Get bookmarks
        bookmarks = self.get_bookmarks()
        
        if bookmarks:
            for bookmark in bookmarks[:8]:  # Show max 8 bookmarks
                item_widget = self.create_bookmark_item(bookmark)
                layout.addWidget(item_widget)
        else:
            no_bookmarks = QLabel("Нет закладок")
            no_bookmarks.setStyleSheet("color: #7f8c8d; font-style: italic; margin: 20px;")
            layout.addWidget(no_bookmarks)
        
        widget.setLayout(layout)
        return widget
    
    def get_bookmarks(self):
        """Get bookmarks"""
        if os.path.exists('data/bookmarks.json'):
            try:
                with open('data/bookmarks.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def create_bookmark_item(self, bookmark):
        """Create a bookmark item widget"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Title
        title = QLabel(bookmark.get('title', bookmark['url']))
        title.setStyleSheet("color: #2c3e50; font-size: 14px;")
        title.setMaximumWidth(400)
        title.setWordWrap(True)
        
        # URL
        url = QLabel(bookmark['url'])
        url.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        url.setMaximumWidth(300)
        
        layout.addWidget(title)
        layout.addWidget(url)
        layout.addStretch()
        
        widget.setLayout(layout)
        widget.setStyleSheet("""
            QWidget {
                padding: 8px;
                border-radius: 6px;
            }
            QWidget:hover {
                background-color: #f8f9fa;
                cursor: pointer;
            }
        """)
        
        # Make clickable
        widget.mousePressEvent = lambda e: self.open_site(bookmark['url'])
        
        return widget
    
    def create_settings_widget(self):
        """Create settings widget"""
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        settings_btn = QPushButton("⚙️ Настройки новой вкладки")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        widget.setLayout(layout)
        return widget
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = NewTabSettingsDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
            # Refresh UI
            self.init_ui()
    
    def get_style(self):
        """Get the stylesheet for the dialog"""
        return f"""
            QDialog {{
                background-color: {self.settings['background_color']};
            }}
        """


class NewTabSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings.copy()
        self.setWindowTitle("Настройки новой вкладки")
        self.setFixedSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Show clock checkbox
        self.show_clock_cb = QCheckBox("Показывать часы")
        self.show_clock_cb.setChecked(self.settings['show_clock'])
        layout.addWidget(self.show_clock_cb)
        
        # Show search checkbox
        self.show_search_cb = QCheckBox("Показывать поисковую строку")
        self.show_search_cb.setChecked(self.settings['show_search'])
        layout.addWidget(self.show_search_cb)
        
        # Show quick access checkbox
        self.show_quick_access_cb = QCheckBox("Показывать быстрый доступ")
        self.show_quick_access_cb.setChecked(self.settings['show_quick_access'])
        layout.addWidget(self.show_quick_access_cb)
        
        # Background color
        layout.addWidget(QLabel("Цвет фона:"))
        self.bg_color_combo = QComboBox()
        self.bg_color_combo.addItems(['#ffffff', '#f5f5f5', '#2c3e50', '#34495e', '#ecf0f1'])
        self.bg_color_combo.setCurrentText(self.settings['background_color'])
        layout.addWidget(self.bg_color_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_settings(self):
        """Get updated settings"""
        self.settings['show_clock'] = self.show_clock_cb.isChecked()
        self.settings['show_search'] = self.show_search_cb.isChecked()
        self.settings['show_quick_access'] = self.show_quick_access_cb.isChecked()
        self.settings['background_color'] = self.bg_color_combo.currentText()
        return self.settings