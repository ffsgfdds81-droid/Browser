# -*- coding: utf-8 -*-
"""
Менеджер загрузок браузера
"""

import os
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWebEngineCore import QWebEngineDownloadItem

class DownloadManager(QObject):
    download_progress = pyqtSignal(str, int)
    download_finished = pyqtSignal(str, str)
    download_error = pyqtSignal(str, str)
    
    def __init__(self, download_folder=None):
        super().__init__()
        self.download_folder = download_folder or os.path.join(
            os.path.expanduser('~'), 'Downloads'
        )
        self.downloads = []
    
    def handle_download(self, download: QWebEngineDownloadItem):
        """Обработать загрузку"""
        # Получаем имя файла
        filename = download.suggestedFileName()
        if not filename:
            filename = "download"
        
        # Создаем путь для сохранения
        filepath = os.path.join(self.download_folder, filename)
        
        # Настраиваем загрузку
        download.setPath(filepath)
        download.accept()
        
        print(f"Начата загрузка: {filename}")