#!/usr/bin/env python3
"""
Desktop Application Launcher for Sri Vengamamba Food Court
Creates a standalone desktop application with embedded web interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import time
import sys
import os
import subprocess
import atexit
import requests
from tkinter import scrolledtext
import queue

class SriVengamambaFoodCourtDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sri Vengamamba Food Court")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap('static/favicon.ico')
        except:
            pass
        
        # Create main frame
        self.create_ui()
        
        # Start Flask server in background
        self.start_flask_server()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_ui(self):
        """Create the main UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#ff6b35', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🍽️ Sri Vengamamba Food Court", 
                              font=('Arial', 24, 'bold'), fg='white', bg='#ff6b35')
        title_label.pack(pady=20)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Status frame
        status_frame = tk.Frame(content_frame, bg='#f8f9fa')
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = tk.Label(status_frame, text="🔄 Starting application...", 
                                   font=('Arial', 12), bg='#f8f9fa', fg='#666')
        self.status_label.pack(side='left')
        
        # Web view frame
        web_frame = tk.Frame(content_frame, bg='#f8f9fa')
        web_frame.pack(fill='both', expand=True)
        
        # Instructions
        instructions = tk.Label(web_frame, 
                              text="🌐 The Sri Vengamamba Food Court will open in your default web browser.\n"
                                   "Click the button below to open the application.",
                              font=('Arial', 14), bg='#f8f9fa', fg='#333', justify='center')
        instructions.pack(pady=50)
        
        # Open button
        self.open_button = tk.Button(web_frame, text="🚀 Open Sri Vengamamba Food Court", 
                                  command=self.open_application,
                                  font=('Arial', 16, 'bold'), 
                                  bg='#ff6b35', fg='white',
                                  padx=30, pady=15,
                                  state='disabled')
        self.open_button.pack(pady=20)
        
        # Alternative access info
        info_frame = tk.Frame(web_frame, bg='#f8f9fa')
        info_frame.pack(fill='x', pady=20)
        
        info_text = tk.Label(info_frame, 
                            text="💡 Alternative: Open your web browser and go to http://localhost:5000",
                            font=('Arial', 12), bg='#f8f9fa', fg='#666')
        info_text.pack()
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#e9ecef', height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_text = tk.Label(footer_frame, text="© 2024 Sri Vengamamba Food Court - All Rights Reserved", 
                              font=('Arial', 10), bg='#e9ecef', fg='#666')
        footer_text.pack(pady=10)
        
    def start_flask_server(self):
        """Start Flask server in background thread"""
        def run_flask():
            try:
                from app import app
                app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Check if server is ready
        self.check_server_ready()
        
    def check_server_ready(self):
        """Check if Flask server is ready"""
        def check():
            try:
                response = requests.get('http://127.0.0.1:5000', timeout=1)
                if response.status_code == 200:
                    self.root.after(0, self.server_ready)
                else:
                    self.root.after(1000, check)
            except:
                self.root.after(1000, check)
        
        check()
        
    def server_ready(self):
        """Called when server is ready"""
        self.status_label.config(text="✅ Application ready!")
        self.open_button.config(state='normal')
        
    def open_application(self):
        """Open the web application"""
        try:
            webbrowser.open('http://127.0.0.1:5000')
            self.status_label.config(text="🌐 Application opened in browser")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {str(e)}")
            
    def show_error(self, error_msg):
        """Show error message"""
        messagebox.showerror("Sri Vengamamba Food Court", 
                           f"Failed to start application:\n{error_msg}\n\nPlease check if port 5000 is available.")
        self.root.quit()
        
    def on_closing(self):
        """Handle window closing"""
        try:
            # Kill Flask processes
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                          capture_output=True, shell=True)
        except:
            pass
        self.root.destroy()

def main():
    """Main function"""
    try:
        app = SriVengamambaFoodCourtDesktopApp()
        app.root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")

if __name__ == "__main__":
    main()
