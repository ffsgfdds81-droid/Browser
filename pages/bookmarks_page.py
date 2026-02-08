# -*- coding: utf-8 -*-
"""
Enhanced Bookmarks Page with folder organization and search
"""

import json
import os
import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class BookmarksPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Управление закладками")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Data
        self.bookmarks_file = 'data/bookmarks.json'
        self.bookmarks = self.load_bookmarks()
        self.filtered_bookmarks = self.bookmarks.copy()
        
        # Folders
        self.folders = set()
        self.current_folder = "Все закладки"
        self.extract_folders()
        
        self.init_ui()
        self.setStyleSheet(self.get_style())
    
    def load_bookmarks(self):
        """Load bookmarks from file"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_bookmarks(self):
        """Save bookmarks to file"""
        os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
        with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, ensure_ascii=False, indent=2)
        
        # Notify parent to refresh
        if self.parent and hasattr(self.parent, 'bookmarks_manager'):
            self.parent.bookmarks_manager.load_bookmarks()
    
    def extract_folders(self):
        """Extract folders from bookmarks"""
        self.folders = set()
        for bookmark in self.bookmarks:
            if 'folder' in bookmark and bookmark['folder']:
                self.folders.add(bookmark['folder'])
        self.folders = sorted(list(self.folders))
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main content
        content_layout = QHBoxLayout()
        
        # Left panel - folders and tree view
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 1)
        
        # Right panel - bookmarks list
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 2)
        
        layout.addLayout(content_layout)
        
        # Status bar
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
        
        self.setLayout(layout)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        
        # Search box
        search_label = QLabel("Поиск:")
        toolbar.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или URL...")
        self.search_input.setMaximumWidth(300)
        self.search_input.textChanged.connect(self.filter_bookmarks)
        toolbar.addWidget(self.search_input)
        
        toolbar.addSeparator()
        
        # Add bookmark button
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self.add_bookmark)
        toolbar.addWidget(add_btn)
        
        # Delete selected button
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self.delete_selected)
        toolbar.addWidget(delete_btn)
        
        toolbar.addSeparator()
        
        # Sort options
        sort_label = QLabel("Сортировка:")
        toolbar.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['По дате', 'По названию', 'По URL'])
        self.sort_combo.currentTextChanged.connect(self.sort_bookmarks)
        toolbar.addWidget(self.sort_combo)
        
        return toolbar
    
    def create_left_panel(self):
        """Create left panel with folder tree"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Folder tree
        folder_label = QLabel("Папки:")
        folder_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(folder_label)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("Закладки")
        self.folder_tree.setMaximumWidth(200)
        
        # Add "All bookmarks" root
        all_item = QTreeWidgetItem(["Все закладки"])
        all_item.setData(0, Qt.UserRole, "all")
        all_item.setSelected(True)
        self.folder_tree.addTopLevelItem(all_item)
        
        # Add folders
        for folder in self.folders:
            folder_item = QTreeWidgetItem([folder])
            folder_item.setData(0, Qt.UserRole, folder)
            all_item.addChild(folder_item)
        
        # Add "Other" for bookmarks without folder
        other_item = QTreeWidgetItem(["Без папки"])
        other_item.setData(0, Qt.UserRole, None)
        all_item.addChild(other_item)
        
        self.folder_tree.expandAll()
        self.folder_tree.itemSelectionChanged.connect(self.on_folder_selected)
        layout.addWidget(self.folder_tree)
        
        widget.setLayout(layout)
        return widget
    
    def create_right_panel(self):
        """Create right panel with bookmarks list"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)
        
        # Add context menu
        self.bookmarks_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bookmarks_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.bookmarks_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.status_label = QLabel(f"Всего закладок: {len(self.bookmarks)}")
        status_bar.addWidget(self.status_label)
        return status_bar
    
    def filter_bookmarks(self):
        """Filter bookmarks based on search"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            self.filtered_bookmarks = self.get_folder_bookmarks(self.current_folder)
        else:
            folder_bookmarks = self.get_folder_bookmarks(self.current_folder)
            self.filtered_bookmarks = [
                b for b in folder_bookmarks
                if search_text in b.get('title', '').lower() or 
                   search_text in b.get('url', '').lower()
            ]
        
        self.update_bookmarks_display()
        self.update_status()
    
    def get_folder_bookmarks(self, folder):
        """Get bookmarks from specific folder"""
        if folder == "Все закладки":
            return self.bookmarks
        
        return [
            b for b in self.bookmarks
            if folder == "Без папки" and not b.get('folder') or
               b.get('folder') == folder
        ]
    
    def on_folder_selected(self):
        """Handle folder selection"""
        current_item = self.folder_tree.currentItem()
        if current_item:
            folder_data = current_item.data(0, Qt.UserRole)
            if folder_data == "all":
                self.current_folder = "Все закладки"
            else:
                self.current_folder = folder_data if folder_data else "Без папки"
            
            self.filtered_bookmarks = self.get_folder_bookmarks(self.current_folder)
            
            # Apply search filter if active
            if self.search_input.text():
                self.filter_bookmarks()
            else:
                self.update_bookmarks_display()
            
            self.update_status()
    
    def sort_bookmarks(self, sort_type):
        """Sort bookmarks"""
        if sort_type == 'По дате':
            self.filtered_bookmarks.sort(
                key=lambda x: x.get('date_added', ''), reverse=True
            )
        elif sort_type == 'По названию':
            self.filtered_bookmarks.sort(
                key=lambda x: x.get('title', '').lower()
            )
        elif sort_type == 'По URL':
            self.filtered_bookmarks.sort(
                key=lambda x: x.get('url', '').lower()
            )
        
        self.update_bookmarks_display()
    
    def update_bookmarks_display(self):
        """Update bookmarks list display"""
        self.bookmarks_list.clear()
        
        for bookmark in self.filtered_bookmarks:
            item = self.create_bookmark_item(bookmark)
            self.bookmarks_list.addItem(item)
    
    def create_bookmark_item(self, bookmark):
        """Create a bookmark list item"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, bookmark)
        
        # Create custom widget
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Title
        title = QLabel(bookmark.get('title', 'Без названия'))
        title.setStyleSheet("font-weight: bold; color: #2c3e50;")
        title.setMaximumWidth(300)
        title.setWordWrap(True)
        
        # URL
        url = QLabel(bookmark['url'])
        url.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        url.setMaximumWidth(400)
        
        # Folder
        if bookmark.get('folder'):
            folder = QLabel(f"📁 {bookmark['folder']}")
            folder.setStyleSheet("color: #3498db; font-size: 11px;")
            layout.addWidget(folder)
        
        # Date
        date_str = bookmark.get('date_added', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_label = QLabel(date_obj.strftime('%d.%m.%Y'))
                date_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
                layout.addWidget(date_label)
            except:
                pass
        
        layout.addWidget(title)
        layout.addWidget(url)
        layout.addStretch()
        
        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        
        return item
    
    def add_bookmark(self):
        """Add new bookmark"""
        dialog = AddBookmarkDialog(self.folders, self)
        if dialog.exec_() == QDialog.Accepted:
            bookmark_data = dialog.get_bookmark_data()
            bookmark = {
                'url': bookmark_data['url'],
                'title': bookmark_data['title'],
                'date_added': datetime.now().isoformat()
            }
            
            if bookmark_data.get('folder'):
                bookmark['folder'] = bookmark_data['folder']
            
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            self.extract_folders()
            self.refresh_all()
    
    def delete_selected(self):
        """Delete selected bookmarks"""
        selected_items = self.bookmarks_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите закладки для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить {len(selected_items)} выбранную закладку(и)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            urls_to_delete = []
            for item in selected_items:
                bookmark = item.data(Qt.UserRole)
                urls_to_delete.append(bookmark['url'])
            
            self.bookmarks = [b for b in self.bookmarks if b['url'] not in urls_to_delete]
            self.save_bookmarks()
            self.extract_folders()
            self.refresh_all()
    
    def open_bookmark(self, item):
        """Open bookmark in browser"""
        bookmark = item.data(Qt.UserRole)
        if self.parent:
            self.parent.add_new_tab(bookmark['url'])
        else:
            webbrowser.open(bookmark['url'])
    
    def show_context_menu(self, position):
        """Show context menu for bookmark"""
        item = self.bookmarks_list.itemAt(position)
        if not item:
            return
        
        bookmark = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        
        open_action = menu.addAction("🔗 Открыть")
        open_action.triggered.connect(lambda: self.open_bookmark(item))
        
        edit_action = menu.addAction("✏️ Изменить")
        edit_action.triggered.connect(lambda: self.edit_bookmark(bookmark))
        
        delete_action = menu.addAction("🗑️ Удалить")
        delete_action.triggered.connect(lambda: self.delete_bookmark(bookmark))
        
        menu.exec_(self.bookmarks_list.mapToGlobal(position))
    
    def edit_bookmark(self, bookmark):
        """Edit bookmark"""
        dialog = AddBookmarkDialog(self.folders, self, bookmark)
        if dialog.exec_() == QDialog.Accepted:
            bookmark_data = dialog.get_bookmark_data()
            
            # Update bookmark
            bookmark['url'] = bookmark_data['url']
            bookmark['title'] = bookmark_data['title']
            
            if bookmark_data.get('folder'):
                bookmark['folder'] = bookmark_data['folder']
            elif 'folder' in bookmark:
                del bookmark['folder']
            
            self.save_bookmarks()
            self.extract_folders()
            self.refresh_all()
    
    def delete_bookmark(self, bookmark):
        """Delete single bookmark"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить закладку \"{bookmark.get('title', bookmark['url'])}\"?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.bookmarks = [b for b in self.bookmarks if b['url'] != bookmark['url']]
            self.save_bookmarks()
            self.extract_folders()
            self.refresh_all()
    
    def refresh_all(self):
        """Refresh all displays"""
        self.filtered_bookmarks = self.get_folder_bookmarks(self.current_folder)
        if self.search_input.text():
            self.filter_bookmarks()
        else:
            self.update_bookmarks_display()
        self.update_status()
        self.refresh_folder_tree()
    
    def refresh_folder_tree(self):
        """Refresh folder tree"""
        self.folder_tree.clear()
        
        # Add "All bookmarks" root
        all_item = QTreeWidgetItem(["Все закладки"])
        all_item.setData(0, Qt.UserRole, "all")
        self.folder_tree.addTopLevelItem(all_item)
        
        # Add folders
        for folder in self.folders:
            folder_item = QTreeWidgetItem([folder])
            folder_item.setData(0, Qt.UserRole, folder)
            all_item.addChild(folder_item)
        
        # Add "Other" for bookmarks without folder
        other_item = QTreeWidgetItem(["Без папки"])
        other_item.setData(0, Qt.UserRole, None)
        all_item.addChild(other_item)
        
        self.folder_tree.expandAll()
    
    def update_status(self):
        """Update status bar"""
        self.status_label.setText(
            f"Показано: {len(self.filtered_bookmarks)} | Всего: {len(self.bookmarks)}"
        )
    
    def get_style(self):
        """Get stylesheet"""
        return """
            QDialog {
                background-color: #ffffff;
            }
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
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


class AddBookmarkDialog(QDialog):
    def __init__(self, folders, parent=None, bookmark=None):
        super().__init__(parent)
        self.folders = folders
        self.bookmark = bookmark
        
        self.setWindowTitle("Изменить закладку" if bookmark else "Добавить закладку")
        self.setFixedSize(400, 250)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # URL
        layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        if self.bookmark:
            self.url_input.setText(self.bookmark['url'])
        layout.addWidget(self.url_input)
        
        # Title
        layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        if self.bookmark:
            self.title_input.setText(self.bookmark.get('title', ''))
        layout.addWidget(self.title_input)
        
        # Folder
        layout.addWidget(QLabel("Папка:"))
        self.folder_combo = QComboBox()
        self.folder_combo.addItem("Без папки")
        self.folder_combo.addItems(self.folders)
        
        # Add current folder if editing
        if self.bookmark and self.bookmark.get('folder'):
            index = self.folder_combo.findText(self.bookmark['folder'])
            if index >= 0:
                self.folder_combo.setCurrentIndex(index)
        
        # Option to create new folder
        new_folder_btn = QPushButton("Создать новую папку")
        new_folder_btn.clicked.connect(self.create_new_folder)
        layout.addWidget(self.folder_combo)
        layout.addWidget(new_folder_btn)
        
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
    
    def create_new_folder(self):
        """Create new folder"""
        folder_name, ok = QInputDialog.getText(
            self, "Новая папка", "Введите название папки:"
        )
        
        if ok and folder_name.strip():
            folder_name = folder_name.strip()
            self.folder_combo.addItem(folder_name)
            self.folder_combo.setCurrentText(folder_name)
    
    def get_bookmark_data(self):
        """Get bookmark data from form"""
        folder = self.folder_combo.currentText()
        if folder == "Без папки":
            folder = None
        
        return {
            'url': self.url_input.text().strip(),
            'title': self.title_input.text().strip(),
            'folder': folder
        }