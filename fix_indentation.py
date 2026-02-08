import os

# Read the current file
with open('browser_pro.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the corrected methods block
corrected_block = '''    def open_settings(self):
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
            QMessageBox.information(self, "DevTools", "DevTools файл не найден")'''

# Replace the problematic block (lines 375-387)
lines = content.split('\n')
new_lines = lines[:374] + corrected_block.split('\n') + lines[388:]

# Write back the corrected file
with open('browser_pro.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Fixed indentation issues in browser_pro.py")