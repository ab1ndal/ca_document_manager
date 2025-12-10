# dev_launcher.py
import subprocess
import sys
import webview
import threading
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

IS_WINDOWS = sys.platform.startswith("win")
NPM = "npm.cmd" if IS_WINDOWS else "npm"
POETRY = "poetry.exe" if IS_WINDOWS else "poetry"

# 1. Define the API Class
class JSApi:
    def save_file(self, content, filename):
        """
        Opens a native 'Save File' dialog and writes the content.
        """
        # Access the active window
        window = webview.windows[0]

        try:
            mode = webview.FileDialog.SAVE
        except AttributeError:
            mode = webview.SAVE_DIALOG
        
        # Open Native Save Dialog
        file_path = window.create_file_dialog(
            mode, 
            directory='', 
            save_filename=filename, 
            file_types=('CSV Files (*.csv)', 'All files (*.*)')
        )
        
        if file_path:
            if isinstance(file_path, (tuple, list)):
                if len(file_path) > 0:
                    file_path = file_path[0]
                else:
                    return False # Empty selection
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                #print(f"Saved to {file_path}")
                return True
            except Exception as e:
                #print(f"Error saving file: {e}")
                return False
        return False

def start_backend():
    subprocess.Popen(
        [sys.executable, "-m", "backend.main"],
        cwd=BASE_DIR,
        shell=IS_WINDOWS,
    )


def start_frontend():
    subprocess.Popen(
        [NPM, "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=IS_WINDOWS,
    )


def start_webview():
    api = JSApi()
    window = webview.create_window("CA Document Manager", "http://localhost:5173", js_api=api)
    webview.start(debug=True)


def run():
    threading.Thread(target=start_backend, daemon=True).start()
    time.sleep(1)

    threading.Thread(target=start_frontend, daemon=True).start()
    time.sleep(2)

    start_webview()


if __name__ == "__main__":
    run()
