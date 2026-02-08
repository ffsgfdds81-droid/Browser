import json
import os
import random
from PyQt5.QtCore import QUrl, QObject

class ErrorPageHandler(QObject):
    """Handler for serving error pages in the browser"""
    
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.error_pages_dir = "error_pages"
        self.load_error_mapping()
    
    def load_error_mapping(self):
        """Load mapping of error codes to HTML files"""
        self.error_mapping = {
            # Google 4xx Errors
            400: "google_errors/400.html",
            401: "google_errors/401.html", 
            402: "google_errors/402.html",
            403: "google_errors/403.html",
            404: "google_errors/404.html",
            405: "google_errors/405.html",
            406: "google_errors/406.html",
            407: "google_errors/407.html",
            408: "google_errors/408.html",
            409: "google_errors/409.html",
            410: "google_errors/410.html",
            411: "google_errors/411.html",
            412: "google_errors/412.html",
            413: "google_errors/413.html",
            414: "google_errors/414.html",
            415: "google_errors/415.html",
            416: "google_errors/416.html",
            417: "google_errors/417.html",
            418: "google_errors/418.html",
            421: "google_errors/421.html",
            422: "google_errors/422.html",
            423: "google_errors/423.html",
            424: "google_errors/424.html",
            425: "google_errors/425.html",
            426: "google_errors/426.html",
            428: "google_errors/428.html",
            429: "google_errors/429.html",
            431: "google_errors/431.html",
            451: "google_errors/451.html",
            
            # Server Errors
            500: "server_errors/500.html",
            501: "server_errors/501.html",
            502: "server_errors/502.html",
            503: "server_errors/503.html",
            504: "server_errors/504.html",
            505: "server_errors/505.html",
            506: "server_errors/506.html",
            507: "server_errors/507.html",
            508: "server_errors/508.html",
            510: "server_errors/510.html",
            511: "server_errors/511.html",
            
            # Chrome Network Errors
            "ERR_INTERNET_DISCONNECTED": "chrome_errors/ERR_INTERNET_DISCONNECTED.html",
            "ERR_CONNECTION_REFUSED": "chrome_errors/ERR_CONNECTION_REFUSED.html",
            "ERR_NAME_NOT_RESOLVED": "chrome_errors/ERR_NAME_NOT_RESOLVED.html",
            "ERR_SSL_PROTOCOL_ERROR": "chrome_errors/ERR_SSL_PROTOCOL_ERROR.html",
            "ERR_CONNECTION_TIMED_OUT": "chrome_errors/ERR_CONNECTION_TIMED_OUT.html",
            "ERR_EMPTY_RESPONSE": "chrome_errors/ERR_EMPTY_RESPONSE.html",
            "ERR_NETWORK_CHANGED": "chrome_errors/ERR_NETWORK_CHANGED.html",
            "ERR_CACHE_MISS": "chrome_errors/ERR_CACHE_MISS.html",
            "ERR_BLOCKED_BY_CLIENT": "chrome_errors/ERR_BLOCKED_BY_CLIENT.html",
            "ERR_SSL_VERSION_OR_CIPHER_MISMATCH": "chrome_errors/ERR_SSL_VERSION_OR_CIPHER_MISMATCH.html",
            "ERR_TOO_MANY_REDIRECTS": "chrome_errors/ERR_TOO_MANY_REDIRECTS.html",
            "ERR_CACHE_READ_FAILURE": "chrome_errors/ERR_CACHE_READ_FAILURE.html",
            "ERR_CONTENT_DECODING_FAILED": "chrome_errors/ERR_CONTENT_DECODING_FAILED.html",
            
            # Google Specific Errors
            "GOOGLE_CAPTCHA": "google_specific/google_captcha.html",
            "GOOGLE_ACCESS_DENIED": "google_specific/google_access_denied.html",
            "GOOGLE_SOMETHING_WENT_WRONG": "google_specific/google_something_went_wrong.html",
            "GOOGLE_UNUSUAL_TRAFFIC": "google_specific/google_unusual_traffic.html",
            "GOOGLE_QUOTA_EXCEEDED": "google_specific/google_quota_exceeded.html",
            
            # Chrome Specific
            "CHROME_OFFLINE": "chrome_specific/chrome_offline_page.html",
            "CHROME_DINO": "chrome_specific/chrome_dino_game.html",
            
            # Special Pages
            "INDEX": "index.html",
            "SEARCH": "search.html", 
            "TROUBLESHOOTING": "troubleshooting.html",
            "BOOKMARKS": "../bookmarks.html",
            "NEWTAB": "../newtab.html",
            "DEVTOOLS": "../devtools.html",
            "SETTINGS": "../settings.html"
        }
    
    def get_error_page_url(self, error_code, fallback_url=None):
        """Get the URL for a specific error page"""
        # Try server bridge first if available
        if hasattr(self.browser, 'server_bridge') and self.browser.use_local_server:
            try:
                if error_code in self.error_mapping:
                    return self.browser.server_bridge.get_error_page_url(self.error_mapping[error_code])
            except:
                pass  # Fall back to local files
        
        # Fallback to local files
        if error_code in self.error_mapping:
            page_path = os.path.join(self.error_pages_dir, self.error_mapping[error_code])
            if os.path.exists(page_path):
                return QUrl.fromLocalFile(os.path.abspath(page_path))
        
        # Fallback to a random error page or specific fallback
        if fallback_url and os.path.exists(fallback_url):
            return QUrl.fromLocalFile(os.path.abspath(fallback_url))
        
        # Default to 404 page
        default_page = os.path.join(self.error_pages_dir, "google_errors/404.html")
        if os.path.exists(default_page):
            return QUrl.fromLocalFile(os.path.abspath(default_page))
        
        # Final fallback - return blank
        return QUrl("about:blank")
    
    def get_random_error_page(self):
        """Get a random error page for testing"""
        all_pages = list(self.error_mapping.values())
        random_page = random.choice(all_pages)
        page_path = os.path.join(self.error_pages_dir, random_page)
        
        if os.path.exists(page_path):
            return QUrl.fromLocalFile(os.path.abspath(page_path))
        
        return self.get_error_page_url(404)
    
    def get_all_error_pages(self):
        """Get list of all available error pages"""
        pages = []
        for code, path in self.error_mapping.items():
            full_path = os.path.join(self.error_pages_dir, path)
            if os.path.exists(full_path):
                pages.append({
                    'code': str(code),
                    'path': path,
                    'url': QUrl.fromLocalFile(os.path.abspath(full_path)),
                    'title': self.extract_page_title(full_path)
                })
        return pages
    
    def extract_page_title(self, file_path):
        """Extract title from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple title extraction
                if '<title>' in content and '</title>' in content:
                    start = content.find('<title>') + 7
                    end = content.find('</title>')
                    return content[start:end].strip()
                elif 'data-title="' in content:
                    start = content.find('data-title="') + 12
                    end = content.find('"', start)
                    return content[start:end].strip()
        except:
            pass
        return os.path.basename(file_path)
    
    def handle_navigation_error(self, webview, error_code, error_string, url):
        """Handle navigation error by showing appropriate error page"""
        error_page_url = self.get_error_page_url(error_code)
        
        # Inject error details into the page
        error_details = {
            'error_code': error_code,
            'error_string': error_string,
            'failed_url': url.toString(),
            'timestamp': str(QDateTime.currentDateTime().toString())
        }
        
        # Load the error page
        webview.load(error_page_url)
        
        # Store error details for potential JavaScript injection
        if hasattr(webview, 'last_error_details'):
            webview.last_error_details = error_details
        else:
            setattr(webview, 'last_error_details', error_details)
    
    def create_error_page_menu_data(self):
        """Create data for error page navigation menu"""
        menu_data = {
            'Google HTTP Errors': [],
            'Server Errors': [], 
            'Chrome Network Errors': [],
            'Google Specific': [],
            'Chrome Specific': [],
            'Special Pages': []
        }
        
        for code, path in self.error_mapping.items():
            category = self.categorize_error(code)
            if category in menu_data:
                full_path = os.path.join(self.error_pages_dir, path)
                if os.path.exists(full_path):
                    menu_data[category].append({
                        'code': str(code),
                        'title': self.extract_page_title(full_path),
                        'url': QUrl.fromLocalFile(os.path.abspath(full_path))
                    })
        
        return menu_data
    
    def categorize_error(self, error_code):
        """Categorize error code into menu groups"""
        if isinstance(error_code, int):
            if 400 <= error_code < 500:
                return 'Google HTTP Errors'
            elif 500 <= error_code < 600:
                return 'Server Errors'
        elif isinstance(error_code, str):
            if error_code.startswith('ERR_'):
                return 'Chrome Network Errors'
            elif error_code.startswith('GOOGLE_'):
                return 'Google Specific'
            elif error_code.startswith('CHROME_'):
                return 'Chrome Specific'
            elif error_code in ['INDEX', 'SEARCH', 'TROUBLESHOOTING', 'BOOKMARKS', 'NEWTAB', 'DEVTOOLS', 'SETTINGS']:
                return 'Special Pages'
        
        return 'Other'