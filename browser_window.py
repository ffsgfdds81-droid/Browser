from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMenuBar, 
    QAction, QMessageBox, QToolBar, QStatusBar, 
    QInputDialog, QFileDialog, QTabWidget, QDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QGroupBox, QGridLayout, QCheckBox, QComboBox,
    QSpinBox, QSplitter, QScrollArea, QFrame,
    QProgressBar, QToolButton, QMenu
)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QKeySequence, QIcon, QFont, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineSettings

from tab_widget import TabWidget
from navigation_bar import NavigationBar
from bookmarks import BookmarksManager
from history import HistoryManager
from settings import SettingsManager
from download_manager import DownloadManager
from devtools import DevToolsWindow
import os
import json
from datetime import datetime

class BrowserWindow(QMainWindow):
    """Главное окно браузера"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация менеджеров
        self.bookmarks_manager = BookmarksManager()
        self.history_manager = HistoryManager()
        self.settings_manager = SettingsManager()
        self.download_manager = DownloadManager()
        
        # DevTools windows
        self.devtools_windows = {}
        
        # Текущий масштаб
        self.current_zoom = 1.0
        
        # Настройка окна
        self.setWindowTitle("Python Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Установка иконки
        icon_paths = ["browser.ico", "icon.png", "icon.ico"]
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        
        # Инициализация UI
        self.init_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.setup_connections()
        
        # Загрузка настроек
        self.load_settings()
        
        # Обновление динамических меню
        self.update_bookmarks_menu()
        self.update_history_menu()
        
        # Таймер для обновления UI
        self.ui_update_timer = QTimer()
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(1000)
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Панель навигации
        self.nav_bar = NavigationBar(self.bookmarks_manager, self.history_manager)
        main_layout.addWidget(self.nav_bar)
        
        # Виджет вкладок
        self.tab_widget = TabWidget(self.bookmarks_manager, self.history_manager, self.download_manager)
        main_layout.addWidget(self.tab_widget)
    
    def create_menu(self):
        """Создание меню браузера"""
        menubar = self.menuBar()
        
        # ==================== Меню Файл ====================
        file_menu = menubar.addMenu("Файл")
        
        # Новая вкладка
        new_tab_action = QAction("Новая вкладка", self)
        new_tab_action.setShortcut(QKeySequence.AddTab)
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        # Новое окно
        new_window_action = QAction("Новое окно", self)
        new_window_action.setShortcut(QKeySequence("Ctrl+N"))
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        # Открыть файл
        open_file_action = QAction("Открыть файл...", self)
        open_file_action.setShortcut(QKeySequence.Open)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        # Сохранить страницу
        save_page_action = QAction("Сохранить страницу...", self)
        save_page_action.setShortcut(QKeySequence.Save)
        save_page_action.triggered.connect(self.save_page)
        file_menu.addAction(save_page_action)
        
        # Сохранить как PDF
        save_pdf_action = QAction("Сохранить как PDF...", self)
        save_pdf_action.triggered.connect(self.save_as_pdf)
        file_menu.addAction(save_pdf_action)
        
        file_menu.addSeparator()
        
        # Печать
        print_action = QAction("Печать...", self)
        print_action.setShortcut(QKeySequence.Print)
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)
        
        # Предварительный просмотр
        print_preview_action = QAction("Предварительный просмотр", self)
        print_preview_action.triggered.connect(self.print_preview)
        file_menu.addAction(print_preview_action)
        
        file_menu.addSeparator()
        
        # Импорт/Экспорт
        import_menu = file_menu.addMenu("Импорт")
        
        import_bookmarks_action = QAction("Импорт закладок...", self)
        import_bookmarks_action.triggered.connect(self.import_bookmarks)
        import_menu.addAction(import_bookmarks_action)
        
        import_history_action = QAction("Импорт истории...", self)
        import_history_action.triggered.connect(self.import_history)
        import_menu.addAction(import_history_action)
        
        export_menu = file_menu.addMenu("Экспорт")
        
        export_bookmarks_action = QAction("Экспорт закладок...", self)
        export_bookmarks_action.triggered.connect(self.export_bookmarks)
        export_menu.addAction(export_bookmarks_action)
        
        export_history_action = QAction("Экспорт истории...", self)
        export_history_action.triggered.connect(self.export_history)
        export_menu.addAction(export_history_action)
        
        file_menu.addSeparator()
        
        # Закрыть
        close_tab_action = QAction("Закрыть вкладку", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_tab_action)
        
        close_window_action = QAction("Закрыть окно", self)
        close_window_action.setShortcut(QKeySequence("Ctrl+Shift+W"))
        close_window_action.triggered.connect(self.close)
        file_menu.addAction(close_window_action)
        
        file_menu.addSeparator()
        
        # Выход
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ==================== Меню Правка ====================
        edit_menu = menubar.addMenu("Правка")
        
        # Отменить
        undo_action = QAction("Отменить", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        # Вернуть
        redo_action = QAction("Вернуть", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # Вырезать
        cut_action = QAction("Вырезать", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        # Копировать
        copy_action = QAction("Копировать", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        # Вставить
        paste_action = QAction("Вставить", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        # Удалить
        delete_action = QAction("Удалить", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        # Найти
        find_action = QAction("Найти на странице...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        # Найти далее
        find_next_action = QAction("Найти далее", self)
        find_next_action.setShortcut(QKeySequence.FindNext)
        find_next_action.triggered.connect(self.find_next)
        edit_menu.addAction(find_next_action)
        
        # Найти предыдущее
        find_previous_action = QAction("Найти предыдущее", self)
        find_previous_action.setShortcut(QKeySequence.FindPrevious)
        find_previous_action.triggered.connect(self.find_previous)
        edit_menu.addAction(find_previous_action)
        
        edit_menu.addSeparator()
        
        # Выделить всё
        select_all_action = QAction("Выделить всё", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # ==================== Меню Вид ====================
        view_menu = menubar.addMenu("Вид")
        
        # Панель инструментов
        self.toolbar_action = QAction("Панель инструментов", self)
        self.toolbar_action.setCheckable(True)
        self.toolbar_action.setChecked(True)
        self.toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(self.toolbar_action)
        
        # Строка состояния
        self.statusbar_action = QAction("Строка состояния", self)
        self.statusbar_action.setCheckable(True)
        self.statusbar_action.setChecked(True)
        self.statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(self.statusbar_action)
        
        view_menu.addSeparator()
        
        # Масштаб
        zoom_in_action = QAction("Увеличить", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Уменьшить", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Сбросить масштаб", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        # Полноэкранный режим
        fullscreen_action = QAction("Полноэкранный режим", self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Режим чтения
        reading_mode_action = QAction("Режим чтения", self)
        reading_mode_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        reading_mode_action.triggered.connect(self.toggle_reading_mode)
        view_menu.addAction(reading_mode_action)
        
        view_menu.addSeparator()
        
        # Стиль страницы
        page_style_menu = view_menu.addMenu("Стиль страницы")
        
        no_style_action = QAction("Без стилей", self)
        no_style_action.triggered.connect(lambda: self.set_page_style("no_style"))
        page_style_menu.addAction(no_style_action)
        
        default_style_action = QAction("Стиль по умолчанию", self)
        default_style_action.triggered.connect(lambda: self.set_page_style("default"))
        page_style_menu.addAction(default_style_action)
        
        dark_mode_action = QAction("Темный режим", self)
        dark_mode_action.triggered.connect(lambda: self.set_page_style("dark"))
        page_style_menu.addAction(dark_mode_action)
        
        high_contrast_action = QAction("Высокая контрастность", self)
        high_contrast_action.triggered.connect(lambda: self.set_page_style("high_contrast"))
        page_style_menu.addAction(high_contrast_action)
        
        view_menu.addSeparator()
        
        # Инструменты разработчика
        devtools_action = QAction("Инструменты разработчика", self)
        devtools_action.setShortcut(QKeySequence("F12"))
        devtools_action.triggered.connect(self.open_devtools)
        view_menu.addAction(devtools_action)
        
        inspect_action = QAction("Инспектировать элемент", self)
        inspect_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        inspect_action.triggered.connect(self.inspect_element)
        view_menu.addAction(inspect_action)
        
        view_source_action = QAction("Просмотр кода страницы", self)
        view_source_action.setShortcut(QKeySequence("Ctrl+U"))
        view_source_action.triggered.connect(self.view_source)
        view_menu.addAction(view_source_action)
        
        # ==================== Меню Переход ====================
        navigate_menu = menubar.addMenu("Переход")
        
        # Назад
        back_action = QAction("Назад", self)
        back_action.setShortcut(QKeySequence("Alt+Left"))
        back_action.triggered.connect(self.go_back)
        navigate_menu.addAction(back_action)
        
        # Вперёд
        forward_action = QAction("Вперёд", self)
        forward_action.setShortcut(QKeySequence("Alt+Right"))
        forward_action.triggered.connect(self.go_forward)
        navigate_menu.addAction(forward_action)
        
        navigate_menu.addSeparator()
        
        # Обновить
        reload_action = QAction("Обновить", self)
        reload_action.setShortcut(QKeySequence("F5"))
        reload_action.triggered.connect(self.reload_page)
        navigate_menu.addAction(reload_action)
        
        # Обновить без кэша
        force_reload_action = QAction("Обновить без кэша", self)
        force_reload_action.setShortcut(QKeySequence("Ctrl+F5"))
        force_reload_action.triggered.connect(self.force_reload)
        navigate_menu.addAction(force_reload_action)
        
        navigate_menu.addSeparator()
        
        # Остановить
        stop_action = QAction("Остановить", self)
        stop_action.setShortcut(QKeySequence("Esc"))
        stop_action.triggered.connect(self.stop_loading)
        navigate_menu.addAction(stop_action)
        
        navigate_menu.addSeparator()
        
        # Домашняя страница
        home_action = QAction("Домашняя страница", self)
        home_action.setShortcut(QKeySequence("Alt+Home"))
        home_action.triggered.connect(self.go_home)
        navigate_menu.addAction(home_action)
        
        # ==================== Меню Закладки ====================
        self.bookmarks_menu = menubar.addMenu("Закладки")
        
        # Добавить в закладки
        add_bookmark_action = QAction("Добавить страницу в закладки", self)
        add_bookmark_action.setShortcut(QKeySequence("Ctrl+D"))
        add_bookmark_action.triggered.connect(self.add_current_to_bookmarks)
        self.bookmarks_menu.addAction(add_bookmark_action)
        
        # Диспетчер закладок
        bookmarks_manager_action = QAction("Диспетчер закладок", self)
        bookmarks_manager_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        bookmarks_manager_action.triggered.connect(self.show_bookmarks_manager)
        self.bookmarks_menu.addAction(bookmarks_manager_action)
        
        self.bookmarks_menu.addSeparator()
        
        # Панель закладок
        bookmarks_bar_action = QAction("Панель закладок", self)
        bookmarks_bar_action.setCheckable(True)
        bookmarks_bar_action.setChecked(False)
        bookmarks_bar_action.triggered.connect(self.toggle_bookmarks_bar)
        self.bookmarks_menu.addAction(bookmarks_bar_action)
        
        self.bookmarks_menu.addSeparator()
        
        # Динамические закладки будут добавлены позже
        self.dynamic_bookmarks_menu = self.bookmarks_menu
        
        # ==================== Меню История ====================
        self.history_menu = menubar.addMenu("История")
        
        # Назад
        history_back_action = QAction("Назад", self)
        history_back_action.setShortcut(QKeySequence("Ctrl+H"))
        history_back_action.triggered.connect(self.show_history)
        self.history_menu.addAction(history_back_action)
        
        # Недавно закрытые
        recently_closed_action = QAction("Недавно закрытые вкладки", self)
        recently_closed_action.triggered.connect(self.show_recently_closed)
        self.history_menu.addAction(recently_closed_action)
        
        self.history_menu.addSeparator()
        
        # Очистить историю
        clear_history_action = QAction("Очистить историю...", self)
        clear_history_action.triggered.connect(self.clear_history_dialog)
        self.history_menu.addAction(clear_history_action)
        
        self.history_menu.addSeparator()
        
        # Динамическая история будет добавлена позже
        self.dynamic_history_menu = self.history_menu
        
        # ==================== Меню Инструменты ====================
        tools_menu = menubar.addMenu("Инструменты")
        
        # Загрузки
        downloads_action = QAction("Загрузки", self)
        downloads_action.setShortcut(QKeySequence("Ctrl+J"))
        downloads_action.triggered.connect(self.show_downloads_manager)
        tools_menu.addAction(downloads_action)
        
        tools_menu.addSeparator()
        
        # Расширения
        extensions_action = QAction("Расширения", self)
        extensions_action.triggered.connect(self.show_extensions_manager)
        tools_menu.addAction(extensions_action)
        
        # Менеджер паролей
        passwords_action = QAction("Менеджер паролей", self)
        passwords_action.triggered.connect(self.show_password_manager)
        tools_menu.addAction(passwords_action)
        
        tools_menu.addSeparator()
        
        # Настройки
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        tools_menu.addAction(settings_action)
        
        # Дополнительные инструменты
        more_tools_menu = tools_menu.addMenu("Дополнительные инструменты")
        
        # Инструменты разработчика (дублируем для удобства)
        devtools_tools_action = QAction("Инструменты разработчика", self)
        devtools_tools_action.triggered.connect(self.open_devtools)
        more_tools_menu.addAction(devtools_tools_action)
        
        # JavaScript консоль
        js_console_action = QAction("JavaScript консоль", self)
        js_console_action.triggered.connect(self.open_js_console)
        more_tools_menu.addAction(js_console_action)
        
        # Информация о странице
        page_info_action = QAction("Информация о странице", self)
        page_info_action.triggered.connect(self.show_page_info)
        more_tools_menu.addAction(page_info_action)
        
        # ==================== Меню Справка ====================
        help_menu = menubar.addMenu("Справка")
        
        # Справка
        help_action = QAction("Справка", self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        # Проверить обновления
        check_updates_action = QAction("Проверить обновления", self)
        check_updates_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(check_updates_action)
        
        # Отчет об ошибке
        report_bug_action = QAction("Сообщить об ошибке", self)
        report_bug_action.triggered.connect(self.report_bug)
        help_menu.addAction(report_bug_action)
        
        # Предложения
        feedback_action = QAction("Отправить отзыв", self)
        feedback_action.triggered.connect(self.send_feedback)
        help_menu.addAction(feedback_action)
        
        help_menu.addSeparator()
        
        # О программе
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        self.toolbar = QToolBar("Панель инструментов")
        self.toolbar.setMovable(True)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Назад
        back_action = QAction(QIcon.fromTheme("go-previous"), "Назад", self)
        back_action.setShortcut(QKeySequence("Alt+Left"))
        back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(back_action)
        
        # Вперёд
        forward_action = QAction(QIcon.fromTheme("go-next"), "Вперёд", self)
        forward_action.setShortcut(QKeySequence("Alt+Right"))
        forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(forward_action)
        
        # Обновить
        reload_action = QAction(QIcon.fromTheme("view-refresh"), "Обновить", self)
        reload_action.setShortcut(QKeySequence("F5"))
        reload_action.triggered.connect(self.reload_page)
        self.toolbar.addAction(reload_action)
        
        # Остановить
        stop_action = QAction(QIcon.fromTheme("process-stop"), "Остановить", self)
        stop_action.setShortcut(QKeySequence("Esc"))
        stop_action.triggered.connect(self.stop_loading)
        self.toolbar.addAction(stop_action)
        
        self.toolbar.addSeparator()
        
        # Домашняя страница
        home_action = QAction(QIcon.fromTheme("go-home"), "Домашняя страница", self)
        home_action.setShortcut(QKeySequence("Alt+Home"))
        home_action.triggered.connect(self.go_home)
        self.toolbar.addAction(home_action)
        
        self.toolbar.addSeparator()
        
        # Закладка (динамическая кнопка)
        self.bookmark_action = QAction(QIcon.fromTheme("bookmark-new"), "Добавить в закладки", self)
        self.bookmark_action.setShortcut(QKeySequence("Ctrl+D"))
        self.bookmark_action.triggered.connect(self.add_current_to_bookmarks)
        self.bookmark_action.setCheckable(True)
        self.toolbar.addAction(self.bookmark_action)
        
        self.toolbar.addSeparator()
        
        # Панель закладок
        bookmarks_bar_action = QAction(QIcon.fromTheme("bookmarks"), "Панель закладок", self)
        bookmarks_bar_action.triggered.connect(self.toggle_bookmarks_bar)
        bookmarks_bar_action.setCheckable(True)
        self.toolbar.addAction(bookmarks_bar_action)
        
        self.toolbar.addSeparator()
        
        # Печать
        print_action = QAction(QIcon.fromTheme("document-print"), "Печать", self)
        print_action.setShortcut(QKeySequence.Print)
        print_action.triggered.connect(self.print_page)
        self.toolbar.addAction(print_action)
        
        # Сохранить
        save_action = QAction(QIcon.fromTheme("document-save"), "Сохранить", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_page)
        self.toolbar.addAction(save_action)
        
        self.toolbar.addSeparator()
        
        # Инструменты разработчика
        devtools_action = QAction(QIcon.fromTheme("applications-development"), "Инструменты разработчика", self)
        devtools_action.setShortcut(QKeySequence("F12"))
        devtools_action.triggered.connect(self.open_devtools)
        self.toolbar.addAction(devtools_action)
        
        # Поиск
        find_action = QAction(QIcon.fromTheme("edit-find"), "Найти", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find_text)
        self.toolbar.addAction(find_action)
        
        self.toolbar.addSeparator()
        
        # Меню
        menu_button = QToolButton()
        menu_button.setText("☰")
        menu_button.setPopupMode(QToolButton.InstantPopup)
        
        # Создаем контекстное меню
        context_menu = QMenu()
        
        # Новая вкладка
        new_tab_context = QAction("Новая вкладка", self)
        new_tab_context.setShortcut(QKeySequence.AddTab)
        new_tab_context.triggered.connect(self.new_tab)
        context_menu.addAction(new_tab_context)
        
        # Новое окно
        new_window_context = QAction("Новое окно", self)
        new_window_context.setShortcut(QKeySequence("Ctrl+N"))
        new_window_context.triggered.connect(self.new_window)
        context_menu.addAction(new_window_context)
        
        context_menu.addSeparator()
        
        # Загрузки
        downloads_context = QAction("Загрузки", self)
        downloads_context.setShortcut(QKeySequence("Ctrl+J"))
        downloads_context.triggered.connect(self.show_downloads_manager)
        context_menu.addAction(downloads_context)
        
        # История
        history_context = QAction("История", self)
        history_context.setShortcut(QKeySequence("Ctrl+H"))
        history_context.triggered.connect(self.show_history)
        context_menu.addAction(history_context)
        
        # Закладки
        bookmarks_context = QAction("Закладки", self)
        bookmarks_context.setShortcut(QKeySequence("Ctrl+Shift+O"))
        bookmarks_context.triggered.connect(self.show_bookmarks_manager)
        context_menu.addAction(bookmarks_context)
        
        context_menu.addSeparator()
        
        # Настройки
        settings_context = QAction("Настройки", self)
        settings_context.triggered.connect(self.show_settings_dialog)
        context_menu.addAction(settings_context)
        
        # Печать
        print_context = QAction("Печать...", self)
        print_context.setShortcut(QKeySequence.Print)
        print_context.triggered.connect(self.print_page)
        context_menu.addAction(print_context)
        
        context_menu.addSeparator()
        
        # Справка
        help_context = QAction("Справка", self)
        help_context.setShortcut(QKeySequence.HelpContents)
        help_context.triggered.connect(self.show_help)
        context_menu.addAction(help_context)
        
        # О программе
        about_context = QAction("О программе", self)
        about_context.triggered.connect(self.show_about)
        context_menu.addAction(about_context)
        
        menu_button.setMenu(context_menu)
        self.toolbar.addWidget(menu_button)
    
    def create_statusbar(self):
        """Создание строки состояния"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Прогресс загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setVisible(False)
        self.statusbar.addPermanentWidget(self.progress_bar)
        
        # Индикатор безопасности
        self.security_indicator = QLabel()
        self.security_indicator.setMaximumWidth(20)
        self.statusbar.addPermanentWidget(self.security_indicator)
        
        # Информация о загрузке
        self.loading_label = QLabel()
        self.statusbar.addWidget(self.loading_label)
    
    def setup_connections(self):
        """Настройка соединений между компонентами"""
        # Панель навигации
        self.nav_bar.url_changed.connect(self.on_nav_url_changed)
        self.nav_bar.search_requested.connect(self.on_search_requested)
        self.nav_bar.bookmark_toggled.connect(self.on_bookmark_toggled)
        self.nav_bar.back_requested.connect(self.go_back)
        self.nav_bar.forward_requested.connect(self.go_forward)
        self.nav_bar.reload_requested.connect(self.reload_page)
        self.nav_bar.stop_requested.connect(self.stop_loading)
        self.nav_bar.home_requested.connect(self.go_home)
        
        # Виджет вкладок
        self.tab_widget.url_changed.connect(self.on_url_changed)
        self.tab_widget.title_changed.connect(self.on_title_changed)
        self.tab_widget.loading_progress.connect(self.on_loading_progress)
        self.tab_widget.loading_state.connect(self.on_loading_state)
        self.tab_widget.icon_changed.connect(self.on_icon_changed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Менеджер загрузок
        self.download_manager.download_progress.connect(self.on_download_progress)
        self.download_manager.download_finished.connect(self.on_download_finished)
        self.download_manager.download_error.connect(self.on_download_error)
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        settings = self.settings_manager.get_settings()
        
        # Размер и положение окна
        if settings.get('window_maximized'):
            self.showMaximized()
        else:
            if 'window_size' in settings:
                self.resize(settings['window_size'][0], settings['window_size'][1])
            if 'window_position' in settings:
                self.move(settings['window_position'][0], settings['window_position'][1])
        
        # Масштаб
        self.current_zoom = settings.get('zoom_level', 1.0)
        
        # Домашняя страница
        home_page = settings.get('home_page', 'https://www.google.com')
        
        # Загружаем домашнюю страницу в текущую вкладку
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.load(QUrl(home_page))
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        self.settings_manager.save_window_state(
            self.isMaximized(),
            self.size(),
            self.pos()
        )
        self.settings_manager.set_setting('zoom_level', self.current_zoom)
        self.settings_manager.save_settings()
    
    # ==================== Методы меню Файл ====================
    def new_tab(self):
        """Создание новой вкладки"""
        self.tab_widget.add_new_tab()
    
    def new_window(self):
        """Создание нового окна браузера"""
        new_window = BrowserWindow()
        new_window.show()
    
    def open_file(self):
        """Открытие локального файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "",
            "Все файлы (*.*);;HTML файлы (*.html *.htm);;"
            "Текстовые файлы (*.txt);;Изображения (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        if file_path:
            url = QUrl.fromLocalFile(file_path)
            self.load_url(url)
    
    def save_page(self):
        """Сохранение текущей страницы"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().toHtml(self.save_page_html)
    
    def save_page_html(self, html):
        """Обработчик сохранения HTML"""
        if html:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить страницу", "",
                "HTML файлы (*.html *.htm);;Текстовые файлы (*.txt);;Все файлы (*.*)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    self.statusbar.showMessage(f"Страница сохранена: {file_path}", 3000)
                except Exception as e:
                    self.statusbar.showMessage(f"Ошибка сохранения: {str(e)}", 3000)
    
    def save_as_pdf(self):
        """Сохранение страницы как PDF"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как PDF", "",
                "PDF файлы (*.pdf);;Все файлы (*.*)"
            )
            if file_path:
                web_view.page().printToPdf(file_path)
                self.statusbar.showMessage(f"PDF сохранен: {file_path}", 3000)
    
    def print_page(self):
        """Печать текущей страницы"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            # В PyQt5 используется системный диалог печати
            web_view.page().print(self.print_finished)
    
    def print_finished(self, success):
        """Обработчик завершения печати"""
        if success:
            self.statusbar.showMessage("Печать завершена", 3000)
        else:
            self.statusbar.showMessage("Ошибка печати", 3000)
    
    def print_preview(self):
        """Предварительный просмотр печати"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            # Здесь должна быть реализация предварительного просмотра
            QMessageBox.information(self, "Предварительный просмотр", 
                                  "Функция предварительного просмотра будет реализована в следующей версии")
    
    def import_bookmarks(self):
        """Импорт закладок из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт закладок", "",
            "JSON файлы (*.json);;HTML файлы (*.html);;Все файлы (*.*)"
        )
        if file_path:
            if self.bookmarks_manager.import_bookmarks(file_path):
                self.update_bookmarks_menu()
                QMessageBox.information(self, "Импорт", "Закладки успешно импортированы")
            else:
                QMessageBox.warning(self, "Импорт", "Ошибка при импорте закладок")
    
    def export_bookmarks(self):
        """Экспорт закладок в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт закладок", "",
            "JSON файлы (*.json);;HTML файлы (*.html);;Все файлы (*.*)"
        )
        if file_path:
            if self.bookmarks_manager.export_bookmarks(file_path):
                QMessageBox.information(self, "Экспорт", "Закладки успешно экспортированы")
            else:
                QMessageBox.warning(self, "Экспорт", "Ошибка при экспорте закладок")
    
    def import_history(self):
        """Импорт истории из файла"""
        QMessageBox.information(self, "Импорт истории", 
                              "Функция импорта истории будет реализована в следующей версии")
    
    def export_history(self):
        """Экспорт истории в файл"""
        QMessageBox.information(self, "Экспорт истории", 
                              "Функция экспорта истории будет реализована в следующей версии")
    
    def close_current_tab(self):
        """Закрытие текущей вкладки"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            # Закрываем DevTools для этой вкладки, если открыты
            if current_index in self.devtools_windows:
                self.devtools_windows[current_index].close()
                del self.devtools_windows[current_index]
            
            self.tab_widget.close_tab(current_index)
    
    # ==================== Методы меню Правка ====================
    def undo(self):
        """Отмена действия"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.Undo)
    
    def redo(self):
        """Повтор действия"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.Redo)
    
    def cut(self):
        """Вырезание"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.Cut)
    
    def copy(self):
        """Копирование"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggered.connect(QWebEnginePage.Copy)
    
    def paste(self):
        """Вставка"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.Paste)
    
    def delete(self):
        """Удаление"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.Delete)
    
    def find_text(self):
        """Поиск текста на странице"""
        # Создаем диалог поиска
        dialog = QDialog(self)
        dialog.setWindowTitle("Найти на странице")
        dialog.setFixedSize(400, 100)
        
        layout = QVBoxLayout(dialog)
        
        # Поле ввода
        find_layout = QHBoxLayout()
        find_label = QLabel("Найти:")
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Введите текст для поиска...")
        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Опции поиска
        options_layout = QHBoxLayout()
        self.case_sensitive_check = QCheckBox("С учетом регистра")
        self.whole_words_check = QCheckBox("Целые слова")
        options_layout.addWidget(self.case_sensitive_check)
        options_layout.addWidget(self.whole_words_check)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        find_next_btn = QPushButton("Найти далее")
        find_previous_btn = QPushButton("Найти предыдущее")
        close_btn = QPushButton("Закрыть")
        
        find_next_btn.clicked.connect(self.find_next)
        find_previous_btn.clicked.connect(self.find_previous)
        close_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(find_next_btn)
        buttons_layout.addWidget(find_previous_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Сохраняем ссылку на диалог
        self.find_dialog = dialog
        dialog.show()
    
    def find_next(self):
        """Поиск следующего совпадения"""
        if hasattr(self, 'find_input'):
            text = self.find_input.text()
            if text:
                web_view = self.tab_widget.current_web_view()
                if web_view:
                    options = QWebEnginePage.FindFlags()
                    if self.case_sensitive_check.isChecked():
                        options |= QWebEnginePage.FindCaseSensitively
                    if self.whole_words_check.isChecked():
                        options |= QWebEnginePage.FindWholeWords
                    
                    web_view.findText(text, options)
    
    def find_previous(self):
        """Поиск предыдущего совпадения"""
        if hasattr(self, 'find_input'):
            text = self.find_input.text()
            if text:
                web_view = self.tab_widget.current_web_view()
                if web_view:
                    options = QWebEnginePage.FindFlags()
                    options |= QWebEnginePage.FindBackward
                    if self.case_sensitive_check.isChecked():
                        options |= QWebEnginePage.FindCaseSensitively
                    if self.whole_words_check.isChecked():
                        options |= QWebEnginePage.FindWholeWords
                    
                    web_view.findText(text, options)
    
    def select_all(self):
        """Выделение всего текста"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.SelectAll)
    
    # ==================== Методы меню Вид ====================
    def toggle_toolbar(self, visible):
        """Переключение видимости панели инструментов"""
        self.toolbar.setVisible(visible)
    
    def toggle_statusbar(self, visible):
        """Переключение видимости строки состояния"""
        self.statusbar.setVisible(visible)
    
    def zoom_in(self):
        """Увеличение масштаба"""
        self.current_zoom += 0.1
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.setZoomFactor(self.current_zoom)
            self.statusbar.showMessage(f"Масштаб: {int(self.current_zoom * 100)}%", 2000)
    
    def zoom_out(self):
        """Уменьшение масштаба"""
        self.current_zoom = max(0.25, self.current_zoom - 0.1)
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.setZoomFactor(self.current_zoom)
            self.statusbar.showMessage(f"Масштаб: {int(self.current_zoom * 100)}%", 2000)
    
    def reset_zoom(self):
        """Сброс масштаба"""
        self.current_zoom = 1.0
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.setZoomFactor(self.current_zoom)
            self.statusbar.showMessage("Масштаб сброшен", 2000)
    
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def toggle_reading_mode(self):
        """Переключение режима чтения"""
        QMessageBox.information(self, "Режим чтения", 
                              "Функция режима чтения будет реализована в следующей версии")
    
    def set_page_style(self, style):
        """Установка стиля страницы"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            if style == "no_style":
                # Отключаем CSS
                js_code = """
                var links = document.querySelectorAll('link[rel="stylesheet"]');
                links.forEach(function(link) {
                    link.disabled = true;
                });
                
                var styles = document.querySelectorAll('style');
                styles.forEach(function(style) {
                    style.disabled = true;
                });
                """
            elif style == "dark":
                # Темный режим
                js_code = """
                var style = document.createElement('style');
                style.textContent = `
                    body {
                        background-color: #1a1a1a !important;
                        color: #ffffff !important;
                    }
                    * {
                        background-color: inherit !important;
                        color: inherit !important;
                    }
                    a {
                        color: #4da6ff !important;
                    }
                `;
                document.head.appendChild(style);
                """
            elif style == "high_contrast":
                # Высокая контрастность
                js_code = """
                var style = document.createElement('style');
                style.textContent = `
                    body {
                        background-color: #000000 !important;
                        color: #ffffff !important;
                    }
                    * {
                        background-color: inherit !important;
                        color: inherit !important;
                        border-color: #ffffff !important;
                    }
                    a {
                        color: #ffff00 !important;
                    }
                `;
                document.head.appendChild(style);
                """
            else:  # default
                # Восстанавливаем стили по умолчанию
                js_code = """
                var links = document.querySelectorAll('link[rel="stylesheet"]');
                links.forEach(function(link) {
                    link.disabled = false;
                });
                
                var styles = document.querySelectorAll('style');
                styles.forEach(function(style) {
                    style.disabled = false;
                });
                
                // Удаляем добавленные стили
                var addedStyles = document.querySelectorAll('style[data-added]');
                addedStyles.forEach(function(style) {
                    style.remove();
                });
                """
            
            web_view.page().runJavaScript(js_code)
            self.statusbar.showMessage(f"Стиль установлен: {style}", 2000)
    
    def open_devtools(self):
        """Открытие инструментов разработчика"""
        current_index = self.tab_widget.currentIndex()
        web_view = self.tab_widget.current_web_view()
        
        if web_view:
            if current_index not in self.devtools_windows:
                devtools = DevToolsWindow(web_view)
                devtools.closed.connect(lambda: self.on_devtools_closed(current_index))
                self.devtools_windows[current_index] = devtools
            
            devtools = self.devtools_windows[current_index]
            devtools.show()
            devtools.raise_()
            devtools.activateWindow()
    
    def on_devtools_closed(self, tab_index):
        """Обработчик закрытия DevTools"""
        if tab_index in self.devtools_windows:
            del self.devtools_windows[tab_index]
    
    def inspect_element(self):
        """Инспектирование элемента"""
        self.open_devtools()
        if self.tab_widget.currentIndex() in self.devtools_windows:
            self.devtools_windows[self.tab_widget.currentIndex()].activate_inspector()
    
    def view_source(self):
        """Просмотр исходного кода страницы"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.page().toHtml(self.show_source_dialog)
    
    def show_source_dialog(self, html):
        """Отображение исходного кода в диалоге"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Исходный код страницы")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Текстовое поле с кодом
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Courier New", 10))
        
        # Добавляем подсветку синтаксиса (простая версия)
        from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
        from PyQt5.QtCore import QRegExp
        
        class HtmlHighlighter(QSyntaxHighlighter):
            def __init__(self, document):
                super().__init__(document)
                
                # Форматы
                tag_format = QTextCharFormat()
                tag_format.setForeground(QColor(136, 18, 128))
                
                attribute_format = QTextCharFormat()
                attribute_format.setForeground(QColor(153, 69, 0))
                
                value_format = QTextCharFormat()
                value_format.setForeground(QColor(26, 26, 166))
                
                comment_format = QTextCharFormat()
                comment_format.setForeground(QColor(35, 110, 37))
                comment_format.setFontItalic(True)
                
                # Правила
                self.rules = []
                
                # Теги
                self.rules.append((QRegExp("&[a-zA-Z]+;"), tag_format))
                self.rules.append((QRegExp("<[^>]*>"), tag_format))
                
                # Атрибуты
                self.rules.append((QRegExp("\\b[A-Za-z_]+(?=\\=)"), attribute_format))
                
                # Значения атрибутов
                self.rules.append((QRegExp("\"[^\"]*\""), value_format))
                self.rules.append((QRegExp("'[^']*'"), value_format))
                
                # Комментарии
                self.rules.append((QRegExp("<!--[^>]*-->"), comment_format))
            
            def highlightBlock(self, text):
                for pattern, format in self.rules:
                    expression = QRegExp(pattern)
                    index = expression.indexIn(text)
                    while index >= 0:
                        length = expression.matchedLength()
                        self.setFormat(index, length, format)
                        index = expression.indexIn(text, index + length)
        
        highlighter = HtmlHighlighter(text_edit.document())
        
        layout.addWidget(text_edit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Копировать")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(html))
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_source_to_file(html))
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def save_source_to_file(self, html):
        """Сохранение исходного кода в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить исходный код", "",
            "HTML файлы (*.html);;Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                self.statusbar.showMessage(f"Исходный код сохранен: {file_path}", 3000)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    # ==================== Методы меню Переход ====================
    def go_back(self):
        """Переход назад"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.back()
    
    def go_forward(self):
        """Переход вперёд"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.forward()
    
    def reload_page(self):
        """Обновление страницы"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.reload()
    
    def force_reload(self):
        """Обновление страницы без кэша"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            # В PyQt5 нет прямой функции обновления без кэша,
            # но можно перезагрузить с текущим URL
            current_url = web_view.url()
            web_view.load(current_url)
    
    def stop_loading(self):
        """Остановка загрузки"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            web_view.stop()
    
    def go_home(self):
        """Переход на домашнюю страницу"""
        home_url = self.settings_manager.get_setting('home_page', 'https://www.google.com')
        self.load_url(QUrl(home_url))
    
    # ==================== Методы меню Закладки ====================
    def add_current_to_bookmarks(self):
        """Добавление текущей страницы в закладки"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            url = web_view.url().toString()
            title = web_view.title()
            
            if url and url != "about:blank":
                # Проверяем, есть ли уже в закладках
                if self.bookmarks_manager.is_bookmarked(url):
                    # Удаляем из закладок
                    reply = QMessageBox.question(
                        self, "Удалить закладку",
                        f"Удалить '{title}' из закладок?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        self.bookmarks_manager.remove_bookmark(url)
                        self.bookmark_action.setChecked(False)
                        self.statusbar.showMessage("Закладка удалена", 2000)
                else:
                    # Добавляем в закладки
                    name, ok = QInputDialog.getText(
                        self, "Добавить закладку",
                        "Название закладки:",
                        text=title
                    )
                    if ok and name:
                        self.bookmarks_manager.add_bookmark(url, name)
                        self.bookmark_action.setChecked(True)
                        self.statusbar.showMessage("Страница добавлена в закладки", 2000)
                
                # Обновляем меню
                self.update_bookmarks_menu()
    
    def show_bookmarks_manager(self):
        """Отображение диспетчера закладок"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Диспетчер закладок")
        dialog.resize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Панель инструментов
        toolbar_layout = QHBoxLayout()
        
        new_folder_btn = QPushButton("Новая папка")
        new_folder_btn.clicked.connect(lambda: self.create_bookmark_folder(dialog))
        toolbar_layout.addWidget(new_folder_btn)
        
        import_btn = QPushButton("Импорт")
        import_btn.clicked.connect(self.import_bookmarks)
        toolbar_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Экспорт")
        export_btn.clicked.connect(self.export_bookmarks)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Список закладок
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setAlternatingRowColors(True)
        
        # Заполняем список
        bookmarks = self.bookmarks_manager.get_bookmarks()
        for bookmark in bookmarks:
            item = QListWidgetItem(f"{bookmark['title']}")
            item.setData(Qt.UserRole, bookmark['url'])
            self.bookmarks_list.addItem(item)
        
        layout.addWidget(self.bookmarks_list)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        open_btn = QPushButton("Открыть")
        open_btn.clicked.connect(lambda: self.open_selected_bookmark())
        buttons_layout.addWidget(open_btn)
        
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(lambda: self.edit_selected_bookmark())
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.delete_selected_bookmark())
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def create_bookmark_folder(self, parent_dialog):
        """Создание папки для закладок"""
        name, ok = QInputDialog.getText(
            parent_dialog, "Новая папка",
            "Имя папки:"
        )
        if ok and name:
            self.bookmarks_manager.create_folder(name)
            self.update_bookmarks_menu()
            parent_dialog.close()
            self.show_bookmarks_manager()
    
    def open_selected_bookmark(self):
        """Открытие выбранной закладки"""
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            url = current_item.data(Qt.UserRole)
            self.load_url(QUrl(url))
    
    def edit_selected_bookmark(self):
        """Редактирование выбранной закладки"""
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            url = current_item.data(Qt.UserRole)
            bookmark = self.bookmarks_manager.get_bookmark_by_url(url)
            if bookmark:
                new_name, ok = QInputDialog.getText(
                    self, "Редактировать закладку",
                    "Новое название:",
                    text=bookmark['title']
                )
                if ok and new_name:
                    self.bookmarks_manager.edit_bookmark(url, new_name)
                    current_item.setText(new_name)
    
    def delete_selected_bookmark(self):
        """Удаление выбранной закладки"""
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            url = current_item.data(Qt.UserRole)
            bookmark = self.bookmarks_manager.get_bookmark_by_url(url)
            if bookmark:
                reply = QMessageBox.question(
                    self, "Удалить закладку",
                    f"Удалить '{bookmark['title']}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.bookmarks_manager.remove_bookmark(url)
                    self.bookmarks_list.takeItem(self.bookmarks_list.row(current_item))
    
    def toggle_bookmarks_bar(self, visible):
        """Переключение панели закладок"""
        QMessageBox.information(self, "Панель закладок", 
                              "Функция панели закладок будет реализована в следующей версии")
    
    def update_bookmarks_menu(self):
        """Обновление меню закладок"""
        # Очищаем динамические элементы
        actions = self.dynamic_bookmarks_menu.actions()
        for action in actions[4:]:  # Оставляем первые 4 статических действия
            self.dynamic_bookmarks_menu.removeAction(action)
        
        # Добавляем закладки
        bookmarks = self.bookmarks_manager.get_bookmarks()
        if bookmarks:
            self.dynamic_bookmarks_menu.addSeparator()
            
            for i, bookmark in enumerate(bookmarks[:15]):  # Первые 15 закладок
                title = bookmark['title']
                if len(title) > 40:
                    title = title[:37] + "..."
                
                action = QAction(title, self)
                action.setData(bookmark['url'])
                action.triggered.connect(lambda checked, url=bookmark['url']: 
                                       self.load_url(QUrl(url)))
                self.dynamic_bookmarks_menu.addAction(action)
            
            if len(bookmarks) > 15:
                more_action = QAction("Ещё...", self)
                more_action.triggered.connect(self.show_bookmarks_manager)
                self.dynamic_bookmarks_menu.addAction(more_action)
    
    # ==================== Методы меню История ====================
    def show_history(self):
        """Отображение истории"""
        dialog = QDialog(self)
        dialog.setWindowTitle("История")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Панель поиска
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Поиск в истории...")
        search_btn = QPushButton("Найти")
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Список истории
        history_list = QListWidget()
        
        # Заполняем список
        history = self.history_manager.get_history()
        for item in history:
            history_list.addItem(f"{item['visit_time']} - {item['title']}")
        
        layout.addWidget(history_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        open_btn = QPushButton("Открыть")
        open_btn.clicked.connect(lambda: self.open_selected_history(history_list, history))
        buttons_layout.addWidget(open_btn)
        
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history_dialog)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Подключение поиска
        def search_history():
            search_text = search_input.text().lower()
            for i in range(history_list.count()):
                item = history_list.item(i)
                item_text = item.text().lower()
                item.setHidden(search_text not in item_text)
        
        search_input.textChanged.connect(search_history)
        search_btn.clicked.connect(search_history)
        
        dialog.exec_()
    
    def open_selected_history(self, list_widget, history):
        """Открытие выбранного элемента истории"""
        index = list_widget.currentRow()
        if 0 <= index < len(history):
            self.load_url(QUrl(history[index]['url']))
            list_widget.parent().close()
    
    def show_recently_closed(self):
        """Показать недавно закрытые вкладки"""
        QMessageBox.information(self, "Недавно закрытые", 
                              "Функция недавно закрытых вкладок будет реализована в следующей версии")
    
    def clear_history_dialog(self):
        """Диалог очистки истории"""
        reply = QMessageBox.question(
            self, "Очистить историю",
            "Вы уверены, что хотите очистить всю историю посещений?\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            QMessageBox.information(self, "История", "История очищена")
    
    def update_history_menu(self):
        """Обновление меню истории"""
        # Очищаем динамические элементы
        actions = self.dynamic_history_menu.actions()
        for action in actions[3:]:  # Оставляем первые 3 статических действия
            self.dynamic_history_menu.removeAction(action)
        
        # Добавляем историю
        history = self.history_manager.get_history()[:10]  # Последние 10 посещений
        if history:
            self.dynamic_history_menu.addSeparator()
            
            for item in history:
                title = item['title']
                if len(title) > 40:
                    title = title[:37] + "..."
                
                action = QAction(f"{item['visit_time']} - {title}", self)
                action.setData(item['url'])
                action.triggered.connect(lambda checked, url=item['url']: 
                                       self.load_url(QUrl(url)))
                self.dynamic_history_menu.addAction(action)
    
    # ==================== Методы меню Инструменты ====================
    def show_downloads_manager(self):
        """Отображение менеджера загрузок"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Загрузки")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Информация о загрузках
        info_label = QLabel("Менеджер загрузок")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Здесь можно добавить список загрузок
        downloads_list = QListWidget()
        
        # Заполняем список
        downloads = getattr(self.download_manager, 'downloads', [])
        for download in downloads:
            downloads_list.addItem(f"{download.get('filename', 'Unknown')} - {download.get('progress', 0)}%")
        
        layout.addWidget(downloads_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        open_folder_btn = QPushButton("Открыть папку загрузок")
        open_folder_btn.clicked.connect(self.open_downloads_folder)
        buttons_layout.addWidget(open_folder_btn)
        
        clear_btn = QPushButton("Очистить список")
        clear_btn.clicked.connect(lambda: downloads_list.clear())
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def open_downloads_folder(self):
        """Открытие папки загрузок"""
        download_folder = self.settings_manager.get_setting('download_folder', '')
        if download_folder and os.path.exists(download_folder):
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                subprocess.Popen(f'explorer "{download_folder}"')
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', download_folder])
            else:  # Linux
                subprocess.Popen(['xdg-open', download_folder])
        else:
            QMessageBox.information(self, "Папка загрузок", 
                                  "Папка загрузок не указана или не существует")
    
    def show_extensions_manager(self):
        """Отображение менеджера расширений"""
        QMessageBox.information(self, "Расширения", 
                              "Менеджер расширений будет реализован в следующей версии")
    
    def show_password_manager(self):
        """Отображение менеджера паролей"""
        QMessageBox.information(self, "Менеджер паролей", 
                              "Менеджер паролей будет реализован в следующей версии")
    
    def show_settings_dialog(self):
        """Отображение диалога настроек"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.resize(500, 400)
        
        # Вкладки
        tabs = QTabWidget()
        
        # ==================== Вкладка Общие ====================
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Домашняя страница
        home_page_group = QGroupBox("Домашняя страница")
        home_page_layout = QVBoxLayout()
        
        home_page_input = QLineEdit()
        home_page_input.setText(self.settings_manager.get_setting('home_page', 'https://www.google.com'))
        home_page_layout.addWidget(QLabel("URL:"))
        home_page_layout.addWidget(home_page_input)
        
        home_page_buttons = QHBoxLayout()
        use_current_btn = QPushButton("Использовать текущую")
        use_current_btn.clicked.connect(lambda: self.set_current_as_home(home_page_input))
        use_default_btn = QPushButton("По умолчанию")
        use_default_btn.clicked.connect(lambda: home_page_input.setText('https://www.google.com'))
        home_page_buttons.addWidget(use_current_btn)
        home_page_buttons.addWidget(use_default_btn)
        home_page_layout.addLayout(home_page_buttons)
        
        home_page_group.setLayout(home_page_layout)
        general_layout.addWidget(home_page_group)
        
        # Внешний вид
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Системная", "Светлая", "Темная"])
        appearance_layout.addWidget(QLabel("Тема:"))
        appearance_layout.addWidget(theme_combo)
        
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 72)
        font_size_spin.setValue(16)
        appearance_layout.addWidget(QLabel("Размер шрифта:"))
        appearance_layout.addWidget(font_size_spin)
        
        appearance_group.setLayout(appearance_layout)
        general_layout.addWidget(appearance_group)
        
        general_layout.addStretch()
        
        # ==================== Вкладка Поиск ====================
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        
        search_engine_group = QGroupBox("Поисковая система")
        search_engine_layout = QVBoxLayout()
        
        search_engine_combo = QComboBox()
        search_engines = [
            ("Google", "https://www.google.com/search?q="),
            ("DuckDuckGo", "https://duckduckgo.com/?q="),
            ("Bing", "https://www.bing.com/search?q="),
            ("Яндекс", "https://yandex.ru/search/?text=")
        ]
        current_engine = self.settings_manager.get_setting('search_engine', 'https://www.google.com/search?q=')
        
        for name, url in search_engines:
            search_engine_combo.addItem(name, url)
            if url == current_engine:
                search_engine_combo.setCurrentText(name)
        
        search_engine_layout.addWidget(QLabel("Поисковая система по умолчанию:"))
        search_engine_layout.addWidget(search_engine_combo)
        
        search_engine_group.setLayout(search_engine_layout)
        search_layout.addWidget(search_engine_group)
        
        search_layout.addStretch()
        
        # ==================== Вкладка Загрузки ====================
        downloads_tab = QWidget()
        downloads_layout = QVBoxLayout(downloads_tab)
        
        downloads_group = QGroupBox("Настройки загрузок")
        downloads_form = QFormLayout()
        
        download_folder_input = QLineEdit()
        download_folder_input.setText(self.settings_manager.get_setting('download_folder', ''))
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(lambda: self.browse_download_folder(download_folder_input))
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(download_folder_input)
        folder_layout.addWidget(browse_btn)
        
        downloads_form.addRow("Папка загрузок:", folder_layout)
        
        ask_save_check = QCheckBox("Всегда спрашивать, куда сохранять файлы")
        ask_save_check.setChecked(True)
        downloads_form.addRow("", ask_save_check)
        
        downloads_group.setLayout(downloads_form)
        downloads_layout.addWidget(downloads_group)
        
        downloads_layout.addStretch()
        
        # ==================== Вкладка Конфиденциальность ====================
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)
        
        privacy_group = QGroupBox("Конфиденциальность")
        privacy_form = QFormLayout()
        
        clear_on_exit_check = QCheckBox("Очищать историю при выходе")
        clear_on_exit_check.setChecked(False)
        privacy_form.addRow("", clear_on_exit_check)
        
        block_cookies_check = QCheckBox("Блокировать сторонние cookies")
        block_cookies_check.setChecked(False)
        privacy_form.addRow("", block_cookies_check)
        
        do_not_track_check = QCheckBox("Отправлять запрос 'Do Not Track'")
        do_not_track_check.setChecked(False)
        privacy_form.addRow("", do_not_track_check)
        
        privacy_group.setLayout(privacy_form)
        privacy_layout.addWidget(privacy_group)
        
        privacy_layout.addStretch()
        
        # Добавляем вкладки
        tabs.addTab(general_tab, "Общие")
        tabs.addTab(search_tab, "Поиск")
        tabs.addTab(downloads_tab, "Загрузки")
        tabs.addTab(privacy_tab, "Конфиденциальность")
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(tabs)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_settings_from_dialog(
            home_page_input.text(),
            search_engine_combo.currentData(),
            download_folder_input.text(),
            dialog
        ))
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)
        buttons_layout.addWidget(cancel_btn)
        
        buttons_layout.addStretch()
        
        reset_btn = QPushButton("Сбросить настройки")
        reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec_()
    
    def set_current_as_home(self, input_widget):
        """Установка текущей страницы как домашней"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            current_url = web_view.url().toString()
            if current_url and current_url != "about:blank":
                input_widget.setText(current_url)
    
    def browse_download_folder(self, input_widget):
        """Выбор папки для загрузок"""
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку для загрузок"
        )
        if folder:
            input_widget.setText(folder)
    
    def save_settings_from_dialog(self, home_page, search_engine, download_folder, dialog):
        """Сохранение настроек из диалога"""
        self.settings_manager.set_setting('home_page', home_page)
        self.settings_manager.set_setting('search_engine', search_engine)
        self.settings_manager.set_setting('download_folder', download_folder)
        self.settings_manager.save_settings()
        
        # Обновляем менеджер загрузок
        self.download_manager.set_download_folder(download_folder)
        
        dialog.close()
        QMessageBox.information(self, "Настройки", "Настройки сохранены")
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(
            self, "Сброс настроек",
            "Вы уверены, что хотите сбросить все настройки?\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings_manager.reset_to_default()
            self.load_settings()
            QMessageBox.information(self, "Настройки", "Настройки сброшены к значениям по умолчанию")
    
    def open_js_console(self):
        """Открытие JavaScript консоли"""
        self.open_devtools()
        if self.tab_widget.currentIndex() in self.devtools_windows:
            devtools = self.devtools_windows[self.tab_widget.currentIndex()]
            devtools.tab_widget.setCurrentIndex(1)  # Console tab
    
    def show_page_info(self):
        """Показать информацию о странице"""
        web_view = self.tab_widget.current_web_view()
        if web_view:
            dialog = QDialog(self)
            dialog.setWindowTitle("Информация о странице")
            dialog.resize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Получаем информацию о странице
            url = web_view.url().toString()
            title = web_view.title()
            
            info_text = f"""
            <b>Заголовок:</b> {title}<br><br>
            <b>URL:</b> {url}<br><br>
            <b>Протокол:</b> {web_view.url().scheme()}<br>
            <b>Домен:</b> {web_view.url().host()}<br>
            <b>Путь:</b> {web_view.url().path()}<br><br>
            <b>Размер окна:</b> {web_view.width()}x{web_view.height()}<br>
            <b>Масштаб:</b> {int(web_view.zoomFactor() * 100)}%<br>
            """
            
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
            
            close_btn = QPushButton("Закрыть")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec_()
    
    # ==================== Методы меню Справка ====================
    def show_help(self):
        """Отображение справки"""
        help_text = """
        <h2>Python Browser - Справка</h2>
        
        <h3>Основные функции</h3>
        <ul>
        <li><b>Новая вкладка:</b> Ctrl+T</li>
        <li><b>Новое окно:</b> Ctrl+N</li>
        <li><b>Закрыть вкладку:</b> Ctrl+W</li>
        <li><b>Закрыть окно:</b> Ctrl+Shift+W</li>
        </ul>
        
        <h3>Навигация</h3>
        <ul>
        <li><b>Назад:</b> Alt+← или Backspace</li>
        <li><b>Вперёд:</b> Alt+→ или Shift+Backspace</li>
        <li><b>Обновить:</b> F5</li>
        <li><b>Обновить без кэша:</b> Ctrl+F5</li>
        <li><b>Остановить:</b> Esc</li>
        <li><b>Домашняя страница:</b> Alt+Home</li>
        </ul>
        
        <h3>Закладки</h3>
        <ul>
        <li><b>Добавить в закладки:</b> Ctrl+D</li>
        <li><b>Диспетчер закладок:</b> Ctrl+Shift+O</li>
        </ul>
        
        <h3>Поиск</h3>
        <ul>
        <li><b>Найти на странице:</b> Ctrl+F</li>
        <li><b>Найти далее:</b> F3</li>
        <li><b>Найти предыдущее:</b> Shift+F3</li>
        </ul>
        
        <h3>Инструменты разработчика</h3>
        <ul>
        <li><b>Инструменты разработчика:</b> F12</li>
        <li><b>Инспектировать элемент:</b> Ctrl+Shift+I</li>
        <li><b>Просмотр кода страницы:</b> Ctrl+U</li>
        </ul>
        
        <h3>Другие функции</h3>
        <ul>
        <li><b>Печать:</b> Ctrl+P</li>
        <li><b>Сохранить страницу:</b> Ctrl+S</li>
        <li><b>Загрузки:</b> Ctrl+J</li>
        <li><b>История:</b> Ctrl+H</li>
        <li><b>Увеличить масштаб:</b> Ctrl++</li>
        <li><b>Уменьшить масштаб:</b> Ctrl+-</li>
        <li><b>Сбросить масштаб:</b> Ctrl+0</li>
        <li><b>Полноэкранный режим:</b> F11</li>
        </ul>
        
        <h3>Управление вкладками</h3>
        <ul>
        <li><b>Следующая вкладка:</b> Ctrl+Tab или Ctrl+PgDown</li>
        <li><b>Предыдущая вкладка:</b> Ctrl+Shift+Tab или Ctrl+PgUp</li>
        <li><b>Перейти к вкладке 1-8:</b> Ctrl+1 до Ctrl+8</li>
        <li><b>Перейти к последней вкладке:</b> Ctrl+9</li>
        </ul>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Справка")
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setHtml(help_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def check_for_updates(self):
        """Проверка обновлений"""
        QMessageBox.information(self, "Обновления", 
                              "Функция проверки обновлений будет реализована в следующей версии")
    
    def report_bug(self):
        """Отчет об ошибке"""
        QMessageBox.information(self, "Сообщить об ошибке", 
                              "Функция отчета об ошибке будет реализована в следующей версии")
    
    def send_feedback(self):
        """Отправка отзыва"""
        QMessageBox.information(self, "Отзыв", 
                              "Функция отправки отзыва будет реализована в следующей версии")
    
    def show_about(self):
        """Отображение информации о программе"""
        about_text = """
        <h2>Python Browser</h2>
        
        <p><b>Версия:</b> 2.0.0</p>
        <p><b>Версия Qt:</b> 5.15.0</p>
        <p><b>Версия PyQt:</b> 5.15.0</p>
        
        <p>Простой, но мощный веб-браузер на Python с использованием PyQt5 и PyQtWebEngine.</p>
        
        <h3>Особенности:</h3>
        <ul>
        <li>Многопользовательские вкладки с предпросмотром</li>
        <li>Полноценные инструменты разработчика (DevTools)</li>
        <li>Управление закладками с поддержкой папок</li>
        <li>История посещений с поиском</li>
        <li>Менеджер загрузок</li>
        <li>Настраиваемый интерфейс</li>
        <li>Поддержка тем (светлая/темная)</li>
        <li>Масштабирование страниц</li>
        <li>Печать и сохранение как PDF</li>
        <li>Поиск по странице</li>
        </ul>
        
        <h3>Лицензия:</h3>
        <p>MIT License</p>
        
        <h3>Автор:</h3>
        <p>Python Browser Team</p>
        
        <p>© 2024 Все права защищены.</p>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setHtml(about_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    # ==================== Обработчики сигналов ====================
    def on_nav_url_changed(self, url):
        """Обработчик изменения URL в панели навигации"""
        self.load_url(url)
    
    def on_search_requested(self, query):
        """Обработчик поискового запроса"""
        if not query.strip():
            return
        
        # Проверяем, является ли запрос URL
        if '.' in query and ' ' not in query:
            if not query.startswith(('http://', 'https://')):
                query = 'https://' + query
            self.load_url(QUrl(query))
        else:
            # Поиск через поисковую систему
            search_engine = self.settings_manager.get_setting('search_engine', 'https://www.google.com/search?q=')
            search_url = f"{search_engine}{query}"
            self.load_url(QUrl(search_url))
    
    def on_bookmark_toggled(self):
        """Обработчик переключения закладки"""
        self.add_current_to_bookmarks()
    
    def on_url_changed(self, url):
        """Обработчик изменения URL"""
        self.nav_bar.update_url(url)
        
        # Обновляем состояние кнопки закладки
        if url.isValid():
            is_bookmarked = self.bookmarks_manager.is_bookmarked(url.toString())
            self.bookmark_action.setChecked(is_bookmarked)
    
    def on_title_changed(self, title):
        """Обработчик изменения заголовка"""
        self.setWindowTitle(f"{title} - Python Browser")
    
    def on_loading_progress(self, progress):
        """Обработчик прогресса загрузки"""
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(progress < 100)
    
    def on_loading_state(self, loading):
        """Обработчик состояния загрузки"""
        if loading:
            self.loading_label.setText("Загрузка...")
        else:
            self.loading_label.setText("Готово")
            self.progress_bar.setVisible(False)
    
    def on_icon_changed(self, icon):
        """Обработчик изменения иконки"""
        # Можно использовать иконку для вкладки
        pass
    
    def on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        if index >= 0:
            web_view = self.tab_widget.current_web_view()
            if web_view:
                # Обновляем URL в панели навигации
                self.nav_bar.update_url(web_view.url())
                
                # Обновляем заголовок окна
                self.setWindowTitle(f"{web_view.title()} - Python Browser")
                
                # Обновляем состояние кнопки закладки
                url_str = web_view.url().toString()
                is_bookmarked = self.bookmarks_manager.is_bookmarked(url_str)
                self.bookmark_action.setChecked(is_bookmarked)
    
    def on_download_progress(self, filename, progress):
        """Обработчик прогресса загрузки"""
        self.statusbar.showMessage(f"Загрузка {filename}: {progress}%", 2000)
    
    def on_download_finished(self, filename, filepath):
        """Обработчик завершения загрузки"""
        self.statusbar.showMessage(f"Загрузка завершена: {filename}", 3000)
    
    def on_download_error(self, filename, error):
        """Обработчик ошибки загрузки"""
        self.statusbar.showMessage(f"Ошибка загрузки {filename}: {error}", 3000)
    
    # ==================== Вспомогательные методы ====================
    def load_url(self, url):
        """Загрузка URL в текущей вкладке"""
        web_view = self.tab_widget.current_web_view()
        if web_view and url.isValid():
            web_view.load(url)
    
    def update_ui(self):
        """Периодическое обновление UI"""
        # Обновляем меню закладок и истории
        self.update_bookmarks_menu()
        self.update_history_menu()
        
        # Обновляем информацию в статусбаре
        web_view = self.tab_widget.current_web_view()
        if web_view:
            url = web_view.url().toString()
            if url and url != "about:blank":
                self.statusbar.showMessage(f"Загружено: {url}", 1000)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Сохраняем настройки
        self.save_settings()
        
        # Закрываем все DevTools
        for devtools in list(self.devtools_windows.values()):
            devtools.close()
        
        self.devtools_windows.clear()
        
        # Закрываем все вкладки
        self.tab_widget.close_all_tabs()
        
        # Останавливаем таймеры
        if hasattr(self, 'ui_update_timer'):
            self.ui_update_timer.stop()
        
        # Очищаем историю, если настроено
        if self.settings_manager.get_setting('clear_history_on_exit', False):
            self.history_manager.clear_history()
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Обработчик нажатия клавиш"""
        # Глобальные горячие клавиши
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_T:
                self.new_tab()
                event.accept()
                return
            elif event.key() == Qt.Key_W:
                self.close_current_tab()
                event.accept()
                return
            elif event.key() == Qt.Key_N:
                self.new_window()
                event.accept()
                return
            elif event.key() == Qt.Key_L:
                self.nav_bar.focus_url_bar()
                event.accept()
                return
            elif event.key() == Qt.Key_F:
                self.find_text()
                event.accept()
                return
            elif event.key() == Qt.Key_D:
                self.add_current_to_bookmarks()
                event.accept()
                return
            elif event.key() == Qt.Key_H:
                self.show_history()
                event.accept()
                return
            elif event.key() == Qt.Key_J:
                self.show_downloads_manager()
                event.accept()
                return
            elif event.key() == Qt.Key_P:
                self.print_page()
                event.accept()
                return
            elif event.key() == Qt.Key_S:
                self.save_page()
                event.accept()
                return
            elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key_0:
                self.reset_zoom()
                event.accept()
                return
            elif event.key() == Qt.Key_U:
                self.view_source()
                event.accept()
                return
        
        # Другие горячие клавиши
        elif event.key() == Qt.Key_F5:
            self.reload_page()
            event.accept()
            return
        elif event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
            event.accept()
            return
        elif event.key() == Qt.Key_F12:
            self.open_devtools()
            event.accept()
            return
        
        super().keyPressEvent(event)