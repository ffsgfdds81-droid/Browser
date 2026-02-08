#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local HTTP server for error pages and browser assets
"""

import http.server
import socketserver
import os
import threading
import webbrowser
from PyQt5.QtCore import QUrl, QObject, pyqtSignal

class LocalFileServer(QObject):
    """Local file server for serving HTML pages"""
    
    server_started = pyqtSignal(int)
    server_stopped = pyqtSignal()
    
    def __init__(self, port=8080):
        super().__init__()
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.base_directory = os.getcwd()
    
    def start_server(self, port=None):
        """Start the local file server"""
        if self.is_running:
            return self.port
        
        if port:
            self.port = port
        
        try:
            # Create server
            handler = self.create_handler()
            self.server = socketserver.TCPServer(("", self.port), handler)
            
            # Start server in thread
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.is_running = True
            self.server_started.emit(self.port)
            
            print(f"Local server started on http://localhost:{self.port}")
            return self.port
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return None
    
    def stop_server(self):
        """Stop the local file server"""
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            self.server_stopped.emit()
            print("Local server stopped")
    
    def create_handler(self):
        """Create a custom request handler"""
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.base_directory, **kwargs)
            
            def end_headers(self):
                # Add CORS headers to allow loading from file://
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                super().end_headers()
            
            def do_GET(self):
                # Handle requests for error pages specially
                if self.path.startswith('/error_pages/'):
                    # Convert file path to local path
                    local_path = os.path.join(self.base_directory, self.path.lstrip('/'))
                    if os.path.exists(local_path):
                        self.path_info()
                        try:
                            with open(local_path, 'rb') as f:
                                content = f.read()
                                
                            # Determine content type
                            if local_path.endswith('.html'):
                                content_type = 'text/html; charset=utf-8'
                            elif local_path.endswith('.css'):
                                content_type = 'text/css; charset=utf-8'
                            elif local_path.endswith('.js'):
                                content_type = 'application/javascript; charset=utf-8'
                            else:
                                content_type = 'application/octet-stream'
                            
                            self.send_response(200)
                            self.send_header('Content-Type', content_type)
                            self.send_header('Content-Length', str(len(content)))
                            self.end_headers()
                            self.wfile.write(content)
                            return
                        except Exception as e:
                            print(f"Error serving file {local_path}: {e}")
                
                # Fall back to default handler
                super().do_GET()
            
            def log_message(self, format, *args):
                # Suppress log messages or customize them
                print(f"[Local Server] {format % args}")
        
        # Bind the base_directory to the handler
        handler_class = CustomHandler
        handler_class.base_directory = self.base_directory
        return handler_class
    
    def get_url(self, path=""):
        """Get full URL for a local path"""
        if not path.startswith('/'):
            path = '/' + path
        return f"http://localhost:{self.port}{path}"
    
    def get_error_page_url(self, error_path):
        """Get URL for an error page"""
        return self.get_url(f"error_pages/{error_path}")
    
    def serve_index(self):
        """Open the index page in browser"""
        index_url = self.get_url("error_pages/index.html")
        webbrowser.open(index_url)
        return index_url

class ErrorPageServerBridge:
    """Bridge between browser and local server for error pages"""
    
    def __init__(self, browser_window):
        self.browser = browser_window
        self.server = LocalFileServer()
        self.server_port = None
        
        # Connect signals
        self.server.server_started.connect(self.on_server_started)
        self.server.server_stopped.connect(self.on_server_stopped)
    
    def start_server(self):
        """Start the server for error pages"""
        self.server_port = self.server.start_server()
        return self.server_port is not None
    
    def stop_server(self):
        """Stop the server"""
        self.server.stop_server()
    
    def get_error_page_url(self, error_path):
        """Get server URL for error page"""
        if self.server_port:
            return QUrl(self.server.get_error_page_url(error_path))
        else:
            # Fallback to local file
            return QUrl.fromLocalFile(os.path.abspath(f"error_pages/{error_path}"))
    
    def on_server_started(self, port):
        """Handle server started"""
        print(f"Error page server started on port {port}")
    
    def on_server_stopped(self):
        """Handle server stopped"""
        print("Error page server stopped")

# Utility functions for easy integration
def start_error_server(port=8080):
    """Start error page server and return bridge"""
    server = LocalFileServer(port)
    server.start_server()
    return server

def get_server_error_page_bridge(browser_window):
    """Get server bridge for browser window"""
    return ErrorPageServerBridge(browser_window)

if __name__ == "__main__":
    # Test standalone server
    server = start_error_server(8080)
    if server.is_running:
        print("Server started successfully!")
        print(f"Open http://localhost:{server.port}/error_pages/index.html to view error pages")
        
        try:
            input("Press Enter to stop the server...\n")
        finally:
            server.stop_server()
    else:
        print("Failed to start server")