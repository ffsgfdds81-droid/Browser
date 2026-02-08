# -*- coding: utf-8 -*-
"""
Enhanced History Page with filtering and search capabilities
"""

import json
import os
import webbrowser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class HistoryPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("История браузера")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Data
        self.history_file = 'data/history.json'
        self.history = self.load_history()
        self.filtered_history = self.history.copy()
        
        # Filters
        self.search_text = ""
        self.date_filter = "Все время"
        self.domain_filter = "Все домены"
        
        self.init_ui()
        self.setStyleSheet(self.get_style())
    
    def load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left panel - filters
        left_panel = self.create_filters_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Right panel - history list
        right_panel = self.create_history_panel()
        content_layout.addWidget(right_panel, 3)
        
        layout.addLayout(content_layout)
        
        # Status bar
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
        
        self.setLayout(layout)
        
        # Load history data
        self.refresh_display()
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        
        # Search box
        search_label = QLabel("Поиск:")
        toolbar.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или URL...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.on_search_changed)
        toolbar.addWidget(self.search_input)
        
        toolbar.addSeparator()
        
        # Clear history button
        clear_btn = QPushButton("🗑️ Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        toolbar.addWidget(clear_btn)
        
        # Export button
        export_btn = QPushButton("📥 Экспорт")
        export_btn.clicked.connect(self.export_history)
        toolbar.addWidget(export_btn)
        
        toolbar.addSeparator()
        
        # View options
        self.view_combo = QComboBox()
        self.view_combo.addItems(['Список', 'Детально', 'По доменам'])
        self.view_combo.currentTextChanged.connect(self.change_view)
        toolbar.addWidget(self.view_combo)
        
        return toolbar
    
    def create_filters_panel(self):
        """Create left filters panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Date filter
        date_group = QGroupBox("Фильтр по дате")
        date_layout = QVBoxLayout()
        
        self.date_combo = QComboBox()
        self.date_combo.addItems([
            'Все время', 'Сегодня', 'Вчера', 'Последние 7 дней',
            'Последние 30 дней', 'Этот месяц', 'Прошлый месяц'
        ])
        self.date_combo.currentTextChanged.connect(self.on_date_filter_changed)
        date_layout.addWidget(self.date_combo)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Domain filter
        domain_group = QGroupBox("Фильтр по домену")
        domain_layout = QVBoxLayout()
        
        self.domain_combo = QComboBox()
        self.domain_combo.addItem("Все домены")
        
        # Extract domains from history
        domains = self.extract_domains()
        self.domain_combo.addItems(sorted(domains))
        
        self.domain_combo.currentTextChanged.connect(self.on_domain_filter_changed)
        domain_layout.addWidget(self.domain_combo)
        domain_group.setLayout(domain_layout)
        layout.addWidget(domain_group)
        
        # Statistics
        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel()
        self.update_statistics()
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Quick actions
        actions_group = QGroupBox("Быстрые действия")
        actions_layout = QVBoxLayout()
        
        today_btn = QPushButton("📅 Сегодня")
        today_btn.clicked.connect(lambda: self.set_date_filter("Сегодня"))
        actions_layout.addWidget(today_btn)
        
        week_btn = QPushButton("📆 Неделя")
        week_btn.clicked.connect(lambda: self.set_date_filter("Последние 7 дней"))
        actions_layout.addWidget(week_btn)
        
        most_visited_btn = QPushButton("🔥 Часто посещаемые")
        most_visited_btn.clicked.connect(self.show_most_visited)
        actions_layout.addWidget(most_visited_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_history_panel(self):
        """Create history display panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.history_list.itemDoubleClicked.connect(self.open_history_item)
        
        # Add context menu
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.history_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.status_label = QLabel(f"Всего записей: {len(self.history)}")
        status_bar.addWidget(self.status_label)
        return status_bar
    
    def extract_domains(self):
        """Extract unique domains from history"""
        domains = set()
        for item in self.history:
            try:
                url = item.get('url', '')
                if url.startswith(('http://', 'https://')):
                    domain = url.split('/')[2]
                    domains.add(domain)
            except:
                pass
        return sorted(list(domains))
    
    def update_statistics(self):
        """Update statistics display"""
        total = len(self.history)
        
        # Count today's visits
        today = datetime.now().date()
        today_visits = 0
        
        # Count unique domains
        domains = set()
        
        # Most visited domain
        domain_counts = {}
        
        for item in self.history:
            try:
                date_str = item.get('timestamp', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if date_obj.date() == today:
                        today_visits += 1
                
                url = item.get('url', '')
                if url.startswith(('http://', 'https://')):
                    domain = url.split('/')[2]
                    domains.add(domain)
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except:
                pass
        
        most_visited = max(domain_counts.items(), key=lambda x: x[1])[0] if domain_counts else "Нет данных"
        
        stats_text = f"""
Всего посещений: {total}
Сегодня: {today_visits}
Уникальных доменов: {len(domains)}
Популярный домен: {most_visited}
        """.strip()
        
        self.stats_label.setText(stats_text)
    
    def on_search_changed(self, text):
        """Handle search text change"""
        self.search_text = text.lower()
        self.apply_filters()
    
    def on_date_filter_changed(self, filter_type):
        """Handle date filter change"""
        self.date_filter = filter_type
        self.apply_filters()
    
    def on_domain_filter_changed(self, domain):
        """Handle domain filter change"""
        self.domain_filter = domain
        self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters"""
        filtered = self.history.copy()
        
        # Apply search filter
        if self.search_text:
            filtered = [
                item for item in filtered
                if self.search_text in item.get('title', '').lower() or 
                   self.search_text in item.get('url', '').lower()
            ]
        
        # Apply date filter
        if self.date_filter != "Все время":
            filtered = self.apply_date_filter(filtered)
        
        # Apply domain filter
        if self.domain_filter != "Все домены":
            filtered = [
                item for item in filtered
                if item.get('url', '').find(self.domain_filter) != -1
            ]
        
        self.filtered_history = filtered
        self.update_history_display()
        self.update_status()
    
    def apply_date_filter(self, items):
        """Apply date filter to items"""
        now = datetime.now()
        
        if self.date_filter == "Сегодня":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.date_filter == "Вчера":
            cutoff = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            max_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.date_filter == "Последние 7 дней":
            cutoff = now - timedelta(days=7)
        elif self.date_filter == "Последние 30 дней":
            cutoff = now - timedelta(days=30)
        elif self.date_filter == "Этот месяц":
            cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.date_filter == "Прошлый месяц":
            if now.month == 1:
                cutoff = now.replace(year=now.year-1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
                max_time = now.replace(year=now.year-1, month=12, day=31, hour=23, minute=59, second=59)
            else:
                cutoff = now.replace(month=now.month-1, day=1, hour=0, minute=0, second=0, microsecond=0)
                max_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return items
        
        filtered = []
        for item in items:
            try:
                date_str = item.get('timestamp', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    
                    if self.date_filter == "Вчера":
                        if cutoff <= date_obj < max_time:
                            filtered.append(item)
                    else:
                        if date_obj >= cutoff:
                            filtered.append(item)
            except:
                pass
        
        return filtered
    
    def update_history_display(self):
        """Update history list display"""
        self.history_list.clear()
        
        # Group by date if detailed view
        if self.view_combo.currentText() == "Детально":
            self.display_detailed_view()
        elif self.view_combo.currentText() == "По доменам":
            self.display_domain_view()
        else:
            self.display_list_view()
    
    def display_list_view(self):
        """Display simple list view"""
        for item in reversed(self.filtered_history):  # Most recent first
            list_item = self.create_history_list_item(item)
            self.history_list.addItem(list_item)
    
    def display_detailed_view(self):
        """Display detailed view grouped by date"""
        # Group items by date
        grouped = {}
        for item in self.filtered_history:
            try:
                date_str = item.get('timestamp', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    date_key = date_obj.strftime('%d.%m.%Y')
                    
                    if date_key not in grouped:
                        grouped[date_key] = []
                    grouped[date_key].append(item)
            except:
                continue
        
        # Display grouped items
        for date in sorted(grouped.keys(), reverse=True):
            # Add date header
            header_item = QListWidgetItem(f"📅 {date}")
            header_item.setBackground(QColor(240, 240, 240))
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            self.history_list.addItem(header_item)
            
            # Add items for this date
            for item in sorted(grouped[date], 
                             key=lambda x: x.get('timestamp', ''), reverse=True):
                list_item = self.create_history_list_item(item)
                list_item.setData(Qt.UserRole, item)
                self.history_list.addItem(list_item)
    
    def display_domain_view(self):
        """Display view grouped by domain"""
        # Group items by domain
        grouped = {}
        for item in self.filtered_history:
            try:
                url = item.get('url', '')
                if url.startswith(('http://', 'https://')):
                    domain = url.split('/')[2]
                    
                    if domain not in grouped:
                        grouped[domain] = []
                    grouped[domain].append(item)
            except:
                continue
        
        # Display grouped items
        for domain in sorted(grouped.keys(), 
                            key=lambda d: len(grouped[d]), reverse=True):
            # Add domain header with count
            header_item = QListWidgetItem(f"🌐 {domain} ({len(grouped[domain])})")
            header_item.setBackground(QColor(240, 240, 240))
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            self.history_list.addItem(header_item)
            
            # Add recent items for this domain
            recent_items = sorted(grouped[domain], 
                                key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            for item in recent_items:
                list_item = self.create_history_list_item(item)
                self.history_list.addItem(list_item)
    
    def create_history_list_item(self, history_item):
        """Create a history list item"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, history_item)
        
        # Create custom widget
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Title
        title = QLabel(history_item.get('title', 'Без названия'))
        title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        title.setMaximumWidth(400)
        title.setWordWrap(True)
        
        # URL
        url = QLabel(history_item['url'])
        url.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        url.setMaximumWidth(500)
        
        # Time
        time_str = history_item.get('visit_time', '')
        if time_str:
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
            layout.addWidget(time_label)
        
        layout.addWidget(title)
        layout.addWidget(url)
        layout.addStretch()
        
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        
        return item
    
    def open_history_item(self, item):
        """Open history item in browser"""
        history_item = item.data(Qt.UserRole)
        if history_item:
            if self.parent:
                self.parent.add_new_tab(history_item['url'])
            else:
                webbrowser.open(history_item['url'])
    
    def show_context_menu(self, position):
        """Show context menu for history item"""
        item = self.history_list.itemAt(position)
        if not item:
            return
        
        history_item = item.data(Qt.UserRole)
        if not history_item:
            return
        
        menu = QMenu(self)
        
        open_action = menu.addAction("🔗 Открыть")
        open_action.triggered.connect(lambda: self.open_history_item(item))
        
        open_new_tab = menu.addAction("📑 Открыть в новой вкладке")
        open_new_tab.triggered.connect(lambda: self.open_in_new_tab(history_item['url']))
        
        copy_url = menu.addAction("📋 Копировать URL")
        copy_url.triggered.connect(lambda: self.copy_url(history_item['url']))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("🗑️ Удалить")
        delete_action.triggered.connect(lambda: self.delete_history_item(history_item))
        
        menu.exec_(self.history_list.mapToGlobal(position))
    
    def open_in_new_tab(self, url):
        """Open URL in new tab"""
        if self.parent:
            self.parent.add_new_tab(url)
        else:
            webbrowser.open(url)
    
    def copy_url(self, url):
        """Copy URL to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        QMessageBox.information(self, "Скопировано", "URL скопирован в буфер обмена")
    
    def delete_history_item(self, history_item):
        """Delete single history item"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить запись \"{history_item.get('title', history_item['url'])}\" из истории?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history = [
                h for h in self.history 
                if h.get('timestamp') != history_item.get('timestamp') or 
                   h.get('url') != history_item.get('url')
            ]
            self.save_history()
            self.apply_filters()
            self.update_statistics()
    
    def clear_history(self):
        """Clear all history"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить всю историю? Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history = []
            self.save_history()
            self.apply_filters()
            self.update_statistics()
    
    def export_history(self):
        """Export history to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт истории", 
            f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON files (*.json);;CSV files (*.csv);;Text files (*.txt)"
        )
        
        if filename:
            if filename.endswith('.json'):
                self.export_json(filename)
            elif filename.endswith('.csv'):
                self.export_csv(filename)
            else:
                self.export_text(filename)
            
            QMessageBox.information(self, "Экспорт завершен", f"История экспортирована в {filename}")
    
    def export_json(self, filename):
        """Export history as JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def export_csv(self, filename):
        """Export history as CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Date', 'Time'])
            
            for item in self.history:
                writer.writerow([
                    item.get('url', ''),
                    item.get('title', ''),
                    item.get('visit_time', ''),
                    item.get('timestamp', '')
                ])
    
    def export_text(self, filename):
        """Export history as text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("История браузера\n")
            f.write("=" * 50 + "\n\n")
            
            for item in reversed(self.history):
                f.write(f"URL: {item.get('url', '')}\n")
                f.write(f"Название: {item.get('title', '')}\n")
                f.write(f"Дата: {item.get('visit_time', '')}\n")
                f.write("-" * 30 + "\n\n")
    
    def change_view(self, view_type):
        """Change view type"""
        self.update_history_display()
    
    def set_date_filter(self, filter_type):
        """Set date filter"""
        index = self.date_combo.findText(filter_type)
        if index >= 0:
            self.date_combo.setCurrentIndex(index)
    
    def show_most_visited(self):
        """Show most visited sites"""
        # Count visits by domain
        domain_counts = {}
        for item in self.history:
            try:
                url = item.get('url', '')
                if url.startswith(('http://', 'https://')):
                    domain = url.split('/')[2]
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
            except:
                pass
        
        # Sort by visit count
        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Часто посещаемые сайты")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        for domain, count in sorted_domains[:20]:  # Top 20
            list_widget.addItem(f"{domain} - {count} посещений")
        
        layout.addWidget(list_widget)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def save_history(self):
        """Save history to file"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
        
        # Notify parent
        if self.parent and hasattr(self.parent, 'history_manager'):
            self.parent.history_manager.load_history()
    
    def refresh_display(self):
        """Refresh the entire display"""
        self.apply_filters()
        self.update_statistics()
    
    def update_status(self):
        """Update status bar"""
        self.status_label.setText(
            f"Показано: {len(self.filtered_history)} | Всего: {len(self.history)}"
        )
    
    def get_style(self):
        """Get stylesheet"""
        return """
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """