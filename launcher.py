#!/usr/bin/env python3
"""
Desktop Application Launcher for Sri Vengamamba Food Court
Creates a standalone desktop application with embedded web interface
"""

import webview
import threading
import time
import sys
import os
import subprocess
import atexit
import requests
from datetime import datetime

# Basic file logger for frozen builds (no console)
def log(message: str) -> None:
    try:
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(exe_dir, 'app_log.txt')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass

def show_native_message(title: str, message: str) -> None:
    """Show a native Windows message box without requiring tkinter."""
    try:
        import ctypes
        MB_ICONERROR = 0x00000010
        ctypes.windll.user32.MessageBoxW(0, message, title, MB_ICONERROR)
    except Exception:
        # Fallback to stdout (may not be visible if windowless)
        try:
            print(f"{title}: {message}")
        except Exception:
            pass

class SriVengamambaFoodCourtDesktopApp:
    def __init__(self):
        self.flask_thread = None
        # Ensure cwd is the executable directory so Flask finds templates/static
        try:
            base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            os.chdir(base_dir)
            log(f"CWD set to: {base_dir}")
        except Exception as e:
            log(f"Failed to set CWD: {e}")
        self.start_flask_server()
        
        # Wait for server to be ready
        self.wait_for_server()
        
        # Create desktop window with embedded web interface
        self.create_desktop_window()
        
    def start_flask_server(self):
        """Start Flask server in background thread"""
        def run_flask():
            try:
                from app import app
                log("Starting Flask server...")
                app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
            except Exception as e:
                log(f"Flask error: {e}")
        
        self.flask_thread = threading.Thread(target=run_flask, daemon=True)
        self.flask_thread.start()
        
    def wait_for_server(self):
        """Wait for Flask server to be ready"""
        max_attempts = 30  # 30 seconds timeout
        for i in range(max_attempts):
            try:
                response = requests.get('http://127.0.0.1:5000', timeout=1)
                if response.status_code == 200:
                    log("Flask server is ready!")
                    return
            except:
                pass
            time.sleep(1)
        
        log("Flask server failed to start")
        sys.exit(1)
        
    def create_desktop_window(self):
        """Create desktop window with embedded web interface"""
        try:
            # Create webview window
            log("Creating webview window...")
            webview.create_window(
                title='Sri Vengamamba Food Court',
                url='http://127.0.0.1:5000',
                width=1400,
                height=900,
                min_size=(800, 600),
                resizable=True,
                fullscreen=False,
                minimized=False,
                on_top=False,
                focus=True,
                text_select=True
            )
            
            # Start webview
            webview.start(debug=False)
            
        except Exception as e:
            log(f"Error creating desktop window: {e}")
            show_native_message(
                "Sri Vengamamba Food Court",
                "Failed to open desktop window.\n\n"
                "This app uses Microsoft Edge WebView2 runtime to render the interface.\n"
                "Please install 'Microsoft Edge WebView2 Runtime' and try again.\n\n"
                f"Error details: {str(e)}"
            )
            sys.exit(1)
            
    def cleanup(self):
        """Cleanup function"""
        try:
            # Kill Flask processes
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                          capture_output=True, shell=True)
        except:
            pass

def main():
    """Main function"""
    app = None
    try:
        # Create and run desktop app
        app = SriVengamambaFoodCourtDesktopApp()
        
    except Exception as e:
        log(f"Failed to start application: {e}")
        if app:
            app.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()
