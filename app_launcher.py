# app_launcher.py
import sys
import os
import threading
import time
import webview
from bottle import run as bottle_run
from backend.main import app
import clr

# 1. Determine Paths (Handles "Frozen" state for PyInstaller)
if getattr(sys, "frozen", False):
    # Running as compiled .exe
    BASE_DIR = sys._MEIPASS
    # In production, we point to the built "dist" folder
    FRONTEND_ENTRY = os.path.join(BASE_DIR, "frontend", "dist", "index.html")
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_ENTRY = os.path.join(BASE_DIR, "frontend", "dist", "index.html")

# 2. Define the JS API (Copied from your dev_launcher)
class JSApi:
    def save_file(self, content, filename):
        window = webview.windows[0]
        
        # Define default export directory
        user_docs = os.path.expanduser("~/Documents")
        export_dir = os.path.join(user_docs, "CA_Manager_Exports")
        
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except OSError:
                export_dir = ''

        try:
            mode = webview.FileDialog.SAVE
        except AttributeError:
            mode = webview.SAVE_DIALOG

        file_path = window.create_file_dialog(
            mode, 
            directory=export_dir, 
            save_filename=filename, 
            file_types=('CSV Files (*.csv)', 'All files (*.*)')
        )
        
        if file_path:
            if isinstance(file_path, (tuple, list)):
                file_path = file_path[0] if len(file_path) > 0 else None
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    return True
                except Exception as e:
                    print(f"Error: {e}")
                    return False
        return False

# 3. Threaded Backend Function
def start_backend():
    # Run Bottle on localhost
    bottle_run(app, host="localhost", port=8000, quiet=True)

def run():
    # Start Backend in a separate thread (Daemon so it dies when app closes)
    t = threading.Thread(target=start_backend)
    t.daemon = True
    t.start()
    
    # Give it a moment to spin up
    time.sleep(1)

    # Start the GUI
    api = JSApi()
    window = webview.create_window(
        "CA Document Manager", 
        url=FRONTEND_ENTRY, # Point to the HTML file, not localhost:5173
        js_api=api
    )
    webview.start(debug=False, gui="qt")

if __name__ == "__main__":
    run()