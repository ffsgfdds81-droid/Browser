# -*- coding: utf-8 -*-
"""
Менеджер истории браузера
"""

import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, filename='data/history.json'):
        self.filename = filename
        self.history = []
        self.load_history()
    
    def load_history(self):
        """Загрузить историю"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []
    
    def save_history(self):
        """Сохранить историю"""
        # Сохраняем только последние 1000 записей
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_to_history(self, url, title):
        """Добавить в историю"""
        history_entry = {
            'url': url,
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'visit_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Удаляем старые записи с тем же URL
        self.history = [h for h in self.history if h['url'] != url]
        
        # Добавляем новую запись
        self.history.append(history_entry)
        self.save_history()
    
    def clear_history(self, days_old=None):
        """Очистить историю"""
        if days_old:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            self.history = [
                h for h in self.history 
                if datetime.fromisoformat(h['timestamp']).timestamp() > cutoff_date
            ]
        else:
            self.history = []
        
        self.save_history()
    
    def get_history(self):
        """Получить историю"""
        return sorted(self.history, 
                     key=lambda x: x['timestamp'], 
                     reverse=True)