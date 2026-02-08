#!/usr/bin/env python3
"""
Открыть DevTools - Python Browser
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def open_devtools_standalone():
    """Открыть DevTools как отдельное приложение"""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QUrl
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        
        # Создаем приложение
        app = QApplication(sys.argv)
        app.setApplicationName("DevTools - Python Browser")
        
        # Проверяем существование файла
        devtools_path = os.path.abspath("devtools.html")
        if not os.path.exists(devtools_path):
            print(f"Ошибка: Файл не найден - {devtools_path}")
            return 1
        
        # Создаем окно DevTools
        webview = QWebEngineView()
        webview.setWindowTitle("DevTools - Python Browser")
        webview.setGeometry(100, 100, 1400, 900)
        webview.setUrl(QUrl.fromLocalFile(devtools_path))
        webview.show()
        
        print("DevTools открыт!")
        print("URL:", QUrl.fromLocalFile(devtools_path).toString())
        
        return app.exec_()
        
    except Exception as e:
        print(f"Ошибка открытия DevTools: {e}")
        return 1

def open_devtools_in_browser():
    """Открыть DevTools в браузере по умолчанию"""
    try:
        import webbrowser
        
        devtools_path = os.path.abspath("devtools.html")
        if os.path.exists(devtools_path):
            url = QUrl.fromLocalFile(devtools_path).toString()
            webbrowser.open(url)
            print(f"DevTools открыт в браузере: {url}")
            return 0
        else:
            print(f"Ошибка: Файл не найден - {devtools_path}")
            return 1
            
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1

def main():
    """Основная функция"""
    print("DevTools - Python Browser")
    print("=" * 30)
    
    # Проверяем существование файла
    devtools_path = os.path.abspath("devtools.html")
    if not os.path.exists(devtools_path):
        print(f"- Файл не найден: {devtools_path}")
        print("\nПроверьте:")
        print("1. Файл devtools.html существует в папке")
        print("2. Вы находитесь в правильной директории")
        return 1
    
    print(f"+ Файл найден: {devtools_path}")
    print()
    print("Способы открытия:")
    print("1. Встроенный DevTools - F12 в браузере")
    print("2. Кнопка 🔧 в браузере") 
    print("3. Автономный DevTools")
    print("4. В браузере по умолчанию")
    print()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == "--standalone":
            return open_devtools_standalone()
        elif sys.argv[1] == "--browser":
            return open_devtools_in_browser()
    
    # По умолчанию открываем в браузере
    return open_devtools_in_browser()

if __name__ == "__main__":
    sys.exit(main())