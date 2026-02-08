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