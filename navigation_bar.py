# -*- coding: utf-8 -*-
"""
Панель навигации браузера
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QToolButton, QMenu, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QIcon

class NavigationBar(QWidget):
    url_changed = pyqtSignal(QUrl)
    search_requested = pyqtSignal(str)
    bookmark_toggled = pyqtSignal()
    
    def __init__(self, bookmarks_manager, history_manager):
        super().__init__()
        self.bookmarks_manager = bookmarks_manager
        self.history_manager = history_manager
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Кнопки навигации
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(30, 30)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(30, 30)
        
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setFixedSize(30, 30)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос")
        
        # Кнопка перехода
        self.go_btn = QPushButton("Перейти")
        self.go_btn.setFixedSize(80, 30)
        
        # Кнопка закладок
        self.bookmark_btn = QPushButton("☆")
        self.bookmark_btn.setFixedSize(30, 30)
        self.bookmark_btn.setCheckable(True)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(100)
        self.progress_bar.setVisible(False)
        
        # Добавляем в layout
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addWidget(self.reload_btn)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.go_btn)
        layout.addWidget(self.bookmark_btn)
        layout.addWidget(self.progress_bar)
        
        # Подключаем сигналы
        self.go_btn.clicked.connect(self.on_go_clicked)
        self.url_bar.returnPressed.connect(self.on_go_clicked)
        self.bookmark_btn.clicked.connect(self.bookmark_toggled.emit)
        self.back_btn.clicked.connect(self.on_back_clicked)
        self.forward_btn.clicked.connect(self.on_forward_clicked)
        self.reload_btn.clicked.connect(self.on_reload_clicked)
    
    def on_go_clicked(self):
        """Обработка нажатия кнопки Перейти"""
        text = self.url_bar.text().strip()
        if text:
            self.search_requested.emit(text)
    
    def on_back_clicked(self):
        """Назад"""
        self.url_changed.emit(QUrl())
    
    def on_forward_clicked(self):
        """Вперед"""
        pass
    
    def on_reload_clicked(self):
        """Обновить"""
        pass
    
    def update_url(self, url):
        """Обновить URL в адресной строке"""
        url_str = url.toString() if url.isValid() else ""
        self.url_bar.setText(url_str)
        
        # Обновляем состояние кнопки закладки
        is_bookmarked = self.bookmarks_manager.is_bookmarked(url_str)
        self.bookmark_btn.setChecked(is_bookmarked)
        self.bookmark_btn.setText("★" if is_bookmarked else "☆")
    
    def update_progress(self, value):
        """Обновить прогресс-бар"""
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_bar.setVisible(False)
        elif not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
    
    def update_loading_state(self, loading):
        """Обновить состояние загрузки"""
        if loading:
            self.reload_btn.setText("✕")
        else:
            self.reload_btn.setText("↻")
    
    def set_bookmark_state(self, bookmarked):
        """Установить состояние закладки"""
        self.bookmark_btn.setChecked(bookmarked)
        self.bookmark_btn.setText("★" if bookmarked else "☆")