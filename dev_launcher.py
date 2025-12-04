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
    window = webview.create_window("CA Document Manager", "http://localhost:5173")
    webview.start(debug=True)


def run():
    threading.Thread(target=start_backend, daemon=True).start()
    time.sleep(1)

    threading.Thread(target=start_frontend, daemon=True).start()
    time.sleep(2)

    start_webview()


if __name__ == "__main__":
    run()
